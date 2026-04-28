"""
auditor.py — AI Trust Layer: Core LLM logic with multi-provider support
Supports: Google Gemini, OpenAI, Anthropic Claude, Ollama
"""
# NOTE: New exports: classify_failure_type, detect_confidence_calibration,
#       score_breakdown, audit_stability_indicator, explain_risk

import json
import re
import html
from model_provider import get_provider, GenerateConfig, SUPPORTED_PROVIDERS

# ── Default model & provider ──────────────────────────────────────────────────
DEFAULT_PROVIDER = "gemini"
DEFAULT_MODEL = "gemini-2.5-flash"

# ── Shared generation configs ─────────────────────────────────────────────────
LOW_TEMP = GenerateConfig(temperature=0.1, max_output_tokens=4096)
HIGH_TEMP = GenerateConfig(temperature=0.9, max_output_tokens=1024)


# ── Internal helpers ──────────────────────────────────────────────────────────

def _get_provider_instance(provider: str, api_key: str, base_url: str = None):
    """Get a provider instance, handling both old-style calls and new style."""
    return get_provider(provider, api_key=api_key, base_url=base_url)


def _call(provider_name: str, api_key: str, model: str, prompt: str,
          cfg: GenerateConfig = None, base_url: str = None) -> str:
    try:
        provider = _get_provider_instance(provider_name, api_key, base_url)
        config = cfg or LOW_TEMP

        response = provider.generate_content(model, prompt, config)

        if not response:
            return "ERROR: Empty response from model"

        return response

    except Exception as e:
        return f"ERROR: {str(e)}"


def _parse_json(raw: str) -> dict:
    raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
    raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw)


def _safe_parse_json(raw: str) -> dict | None:
    try:
        return _parse_json(raw)
    except (json.JSONDecodeError, ValueError):
        match = re.search(r'\{.*\}', raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except (json.JSONDecodeError, ValueError):
                return None
        return None


# ── Prompts ───────────────────────────────────────────────────────────────────

AUDIT_PROMPT = """You are a Context-Aware Hallucination Auditor.
Evaluate whether this AI answer is strictly grounded in the CONTEXT below.
Do NOT use any external knowledge — only what is in the context.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER TO AUDIT:
{answer}

MODE: {mode}
{mode_instruction}

PROCESS:
1. Break the answer into individual factual claims.
2. Classify each claim ONLY using the provided context:
   - "Supported"   → present or directly implied in context
   - "Not Found"   → not present in context (potential hallucination)
   - "Contradicts" → conflicts with context (severe hallucination)

SCORING:
- Start at 100
- Deduct 25 per "Contradicts" claim
- Deduct 10 per "Not Found" claim
- Deduct 5 per overconfidence signal
- Minimum 0

Overconfidence signals to detect: "definitely", "always", "never", "certainly",
"obviously", "experts say", "proven", "everyone knows", "without a doubt",
"undeniably", "absolutely", "it is clear that"

Hallucination Risk: 80-100 → Low | 50-79 → Medium | 0-49 → High

Respond ONLY with valid JSON. No markdown. No extra text. Exact schema:
{{
  "claims": [
    {{
      "claim": "string — the exact claim from the answer",
      "classification": "Supported" | "Not Found" | "Contradicts",
      "reason": "string",
      "snippet": "exact quote from context, or null"
    }}
  ],
  "trust_score": integer,
  "hallucination_risk": "Low" | "Medium" | "High",
  "overconfidence_issues": ["string"],
  "risky_sections": ["string — exact phrase from the answer"],
  "final_verdict": "string — 2-3 sentences harsh critique"
}}"""

GENERATE_PROMPT = """Answer the question using ONLY the provided context.
Do not add any information from outside the context.
If the answer is not in the context, respond exactly: "Not found in context."

CONTEXT:
{context}

QUESTION:
{question}

Answer:"""

MISLEADING_PROMPT = """You are generating a test case for a hallucination detector.
Using the context below, write a CONVINCING but SUBTLY INCORRECT answer to the question.
Introduce plausible-sounding wrong details: wrong dates, swapped names, fabricated numbers.
Sound confident and authoritative. Do not say it is incorrect.

CONTEXT:
{context}

QUESTION:
{question}

Misleading answer (no preamble):"""

FIX_PROMPT = """Rewrite the answer so it is STRICTLY grounded in the provided context.
Remove or correct any claims not found in or contradicted by the context.
Do not add information not present in the context.
If a claim cannot be grounded, omit it.

CONTEXT:
{context}

QUESTION:
{question}

ORIGINAL ANSWER:
{answer}

Corrected grounded answer (no preamble):"""

CONSISTENCY_PROMPT = """Analyze the following answer for internal logical consistency.
Look for contradictions or logical conflicts WITHIN the answer itself.
Do not use any external knowledge.

ANSWER:
{answer}

Respond ONLY with valid JSON. No markdown:
{{
  "is_consistent": true | false,
  "issues": ["string describing each inconsistency found"],
  "summary": "one sentence summary"
}}"""


# ── Public API ────────────────────────────────────────────────────────────────

def generate_answer(
    api_key: str,
    context: str,
    question: str,
    model: str = DEFAULT_MODEL,
    provider: str = DEFAULT_PROVIDER,
    base_url: str = None,
) -> str:
    """Generate an answer using the specified provider and model."""
    prompt = GENERATE_PROMPT.format(context=context.strip(), question=question.strip())
    return _call(provider, api_key, model, prompt, LOW_TEMP, base_url)


def run_audit(
    api_key: str,
    context: str,
    question: str,
    answer: str,
    model_name: str = DEFAULT_MODEL,
    provider: str = DEFAULT_PROVIDER,
    strict: bool = False,
    base_url: str = None,
) -> dict:
    """Run a hallucination audit using the specified provider and model."""
    mode = "STRICT" if strict else "NORMAL"
    mode_instruction = (
        "Assume the answer is likely wrong. Be highly critical. "
        "Flag anything not explicitly stated in context as 'Not Found'."
        if strict else
        "Apply balanced judgement. Allow reasonable direct implications from context."
    )
    prompt = AUDIT_PROMPT.format(
        context=context.strip(),
        question=question.strip(),
        answer=answer.strip(),
        mode=mode,
        mode_instruction=mode_instruction,
    )
    raw = _call(provider, api_key, model_name, prompt, LOW_TEMP, base_url)
    result = _safe_parse_json(raw)
    if result is None:
        raise ValueError(f"Could not parse audit JSON.\nRaw:\n{raw[:500]}")

    # Always recompute score for consistency
    score, risk = compute_score_from_claims(
        result.get("claims", []),
        result.get("overconfidence_issues", []),
    )
    result["trust_score"] = score
    result["hallucination_risk"] = risk
    return result


def fix_answer(
    api_key: str,
    context: str,
    question: str,
    answer: str,
    model: str = DEFAULT_MODEL,
    provider: str = DEFAULT_PROVIDER,
    base_url: str = None,
) -> str:
    """Fix an answer to be grounded in context using the specified provider."""
    prompt = FIX_PROMPT.format(
        context=context.strip(),
        question=question.strip(),
        answer=answer.strip(),
    )
    return _call(provider, api_key, model, prompt, LOW_TEMP, base_url)


def generate_misleading_answer(
    api_key: str,
    context: str,
    question: str,
    model: str = DEFAULT_MODEL,
    provider: str = DEFAULT_PROVIDER,
    base_url: str = None,
) -> str:
    """Generate a misleading answer for adversarial testing."""
    prompt = MISLEADING_PROMPT.format(context=context.strip(), question=question.strip())
    return _call(provider, api_key, model, prompt, HIGH_TEMP, base_url)


def check_consistency(
    api_key: str,
    answer: str,
    model: str = DEFAULT_MODEL,
    provider: str = DEFAULT_PROVIDER,
    base_url: str = None,
) -> dict:
    """Check consistency of an answer using the specified provider."""
    prompt = CONSISTENCY_PROMPT.format(answer=answer.strip())
    raw = _call(provider, api_key, model, prompt, LOW_TEMP, base_url)
    result = _safe_parse_json(raw)
    if result is None:
        return {"is_consistent": None, "issues": [], "summary": "Could not parse consistency check."}
    return result


# ── Scoring & metrics ─────────────────────────────────────────────────────────

def compute_score_from_claims(claims: list, overconfidence_issues: list = None) -> tuple[int, str]:
    score = 100
    for c in claims:
        clf = c.get("classification", "")
        if clf == "Contradicts":
            score -= 25
        elif clf == "Not Found":
            score -= 10
    if overconfidence_issues:
        score -= 5 * len(overconfidence_issues)
    score = max(0, score)
    risk = "Low" if score >= 80 else "Medium" if score >= 50 else "High"
    return score, risk


def compute_context_coverage(claims: list) -> float:
    if not claims:
        return 0.0
    supported = sum(1 for c in claims if c.get("classification") == "Supported")
    return round((supported / len(claims)) * 100, 1)


def confidence_gap_label(normal_score: int, strict_score: int) -> str:
    diff = abs(normal_score - strict_score)
    if diff >= 30:
        return "High"
    elif diff >= 15:
        return "Medium"
    return "Low"


def trust_recommendation(score: int, risk: str) -> tuple[str, str]:
    if score >= 80 and risk == "Low":
        return "✔ Safe to Use", "#3fb950"
    elif score >= 50 or risk == "Medium":
        return "⚠ Use with Caution", "#d29922"
    return "❌ Not Reliable", "#f85149"


# ── Inline highlighting ───────────────────────────────────────────────────────

OVERCONFIDENCE_WORDS = [
    "definitely", "always", "never", "certainly", "obviously",
    "experts say", "proven", "everyone knows", "without a doubt",
    "undeniably", "absolutely", "it is clear that",
]

_COLOR_MAP = {
    "Supported":   ("#0d2818", "#3fb950"),
    "Not Found":   ("#2a2200", "#d29922"),
    "Contradicts": ("#2a0a0a", "#f85149"),
}


def _partial_match_span(escaped_answer: str, claim_text: str) -> str | None:
    """
    Try exact match first, then fall back to matching the longest contiguous
    word-sequence from the claim that still appears verbatim in the answer.
    Returns the matched substring or None.
    """
    if claim_text in escaped_answer:
        return claim_text
    # Tokenise and search for the longest contiguous sub-sequence
    words = claim_text.split()
    best: str | None = None
    for size in range(len(words), 2, -1):          # at least 3-word matches
        for start in range(len(words) - size + 1):
            candidate = " ".join(words[start:start + size])
            if candidate in escaped_answer:
                if best is None or len(candidate) > len(best):
                    best = candidate
        if best:
            return best
    return None


def build_highlighted_answer(answer: str, claims: list) -> str:
    """
    Return HTML of answer with claim spans highlighted by classification.
    Supports partial / sub-sequence matching so more claims get coloured.
    Overconfidence words are additionally highlighted in amber.
    """
    escaped = html.escape(answer)

    # Build (matched_span, classification) pairs
    annotated = []
    for c in claims:
        claim_text = html.escape(c.get("claim", "").strip())
        clf = c.get("classification", "Not Found")
        if not claim_text:
            continue
        matched = _partial_match_span(escaped, claim_text)
        if matched:
            annotated.append((matched, clf))

    # Longest-first to avoid partial-match clobbering
    annotated.sort(key=lambda x: len(x[0]), reverse=True)

    result = escaped
    placeholders: dict[str, str] = {}
    already_marked: set[str] = set()

    for idx, (span, clf) in enumerate(annotated):
        if span in already_marked:
            continue
        bg, border = _COLOR_MAP.get(clf, ("#21262d", "#30363d"))
        tag = (
            f'<mark style="background:{bg};border-bottom:2px solid {border};'
            f'border-radius:3px;padding:1px 3px;cursor:help;" title="{clf}">'
            f'{span}</mark>'
        )
        ph = f"__HL_{idx}__"
        placeholders[ph] = tag
        result = result.replace(span, ph, 1)
        already_marked.add(span)

    for ph, tag in placeholders.items():
        result = result.replace(ph, tag)

    # Overconfidence words — only outside existing <mark> tags
    for word in OVERCONFIDENCE_WORDS:
        esc_word = html.escape(word)
        result = re.sub(
            r'(?<![>\w])' + re.escape(esc_word) + r'(?![\w<])',
            f'<mark style="background:#3a1f00;border-bottom:2px solid #e3b341;'
            f'border-radius:3px;padding:1px 3px;" title="Overconfidence">'
            f'{esc_word}</mark>',
            result,
            flags=re.IGNORECASE,
        )

    return (
        '<div style="line-height:1.9;font-size:0.95rem;color:#e6edf3;'
        f'white-space:pre-wrap;font-family:inherit;">{result}</div>'
    )


# ── New analytical helpers ────────────────────────────────────────────────────

def classify_failure_type(claims: list, overconfidence_issues: list) -> str:
    """
    Derive a single primary failure type label from claim classifications
    and overconfidence signals.

    Returns one of:
        "Contradiction with Context"
        "Unsupported Claim"
        "Overconfidence Bias"
        "Mixed Issues"
        "No Issues Detected"
    """
    has_contradiction = any(c.get("classification") == "Contradicts" for c in claims)
    has_unsupported   = any(c.get("classification") == "Not Found"   for c in claims)
    has_overconf      = bool(overconfidence_issues)

    issue_count = sum([has_contradiction, has_unsupported, has_overconf])

    if issue_count == 0:
        return "No Issues Detected"
    if issue_count > 1:
        return "Mixed Issues"
    if has_contradiction:
        return "Contradiction with Context"
    if has_unsupported:
        return "Unsupported Claim"
    return "Overconfidence Bias"


def detect_confidence_calibration(
    answer: str, trust_score: int
) -> dict:
    """
    Compare linguistic confidence of the answer against the computed trust score.

    Returns a dict with:
        model_confidence   : "High" | "Low"
        actual_reliability : "High" | "Medium" | "Low"
        is_overconfident   : bool
        label              : human-readable verdict string
    """
    answer_lower = answer.lower()
    high_conf_signals = [
        "definitely", "always", "never", "certainly", "obviously",
        "proven", "undeniably", "absolutely", "without a doubt",
        "it is clear that", "everyone knows", "experts say",
    ]
    model_confidence = "High" if any(w in answer_lower for w in high_conf_signals) else "Low"

    if trust_score >= 80:
        actual_reliability = "High"
    elif trust_score >= 50:
        actual_reliability = "Medium"
    else:
        actual_reliability = "Low"

    is_overconfident = (model_confidence == "High" and actual_reliability == "Low")

    if is_overconfident:
        label = "→ Overconfidence Detected"
    elif model_confidence == "High" and actual_reliability == "Medium":
        label = "→ Mild Overconfidence"
    else:
        label = "→ Well Calibrated"

    return {
        "model_confidence":   model_confidence,
        "actual_reliability": actual_reliability,
        "is_overconfident":   is_overconfident,
        "label":              label,
    }


def score_breakdown(claims: list, overconfidence_issues: list) -> dict:
    """
    Return an itemised score breakdown matching the deduction logic in
    compute_score_from_claims.

    Returns:
        contradictions_deduction  : int (negative)
        unsupported_deduction     : int (negative)
        overconfidence_deduction  : int (negative)
        final_score               : int
    """
    contra_count  = sum(1 for c in claims if c.get("classification") == "Contradicts")
    notfnd_count  = sum(1 for c in claims if c.get("classification") == "Not Found")
    overconf_count = len(overconfidence_issues) if overconfidence_issues else 0

    contra_ded  = contra_count  * 25
    notfnd_ded  = notfnd_count  * 10
    overconf_ded = overconf_count * 5

    final = max(0, 100 - contra_ded - notfnd_ded - overconf_ded)

    return {
        "contradictions_deduction":  -contra_ded,
        "unsupported_deduction":     -notfnd_ded,
        "overconfidence_deduction":  -overconf_ded,
        "final_score":               final,
        "contradiction_count":       contra_count,
        "unsupported_count":         notfnd_count,
        "overconfidence_count":      overconf_count,
    }


def audit_stability_indicator(normal_score: int, strict_score: int) -> dict:
    """
    Classify audit result stability based on the gap between normal and strict scores.

    Returns:
        stability : "High" | "Medium" | "Low"
        label     : emoji-prefixed human label
        diff      : absolute score difference
    """
    diff = abs(normal_score - strict_score)
    if diff >= 30:
        stability = "Low"
        label     = "⚠️ Low Stability"
    elif diff >= 15:
        stability = "Medium"
        label     = "🟡 Medium Stability"
    else:
        stability = "High"
        label     = "✅ High Stability"
    return {"stability": stability, "label": label, "diff": diff}


def explain_risk(claims: list, overconfidence_issues: list, trust_score: int) -> dict:
    """
    Generate dynamic 'Why this is risky' bullets and 'Suggested Action' bullets.

    Returns:
        risk_bullets   : list[str]
        action_bullets : list[str]
    """
    contra_count = sum(1 for c in claims if c.get("classification") == "Contradicts")
    notfnd_count = sum(1 for c in claims if c.get("classification") == "Not Found")

    risk_bullets: list[str] = []
    if contra_count:
        risk_bullets.append(
            f"Contains {contra_count} claim(s) that directly contradict the source context"
        )
    if notfnd_count:
        risk_bullets.append(
            f"Includes {notfnd_count} unsupported claim(s) with no backing in the context"
        )
    if overconfidence_issues:
        risk_bullets.append(
            "Uses confident language (e.g. 'definitely', 'always') without sufficient evidence"
        )
    if trust_score < 50:
        risk_bullets.append("Overall reliability is low — may actively mislead users")
    elif trust_score < 80:
        risk_bullets.append("Moderate reliability — verify key claims before acting on them")

    if not risk_bullets:
        risk_bullets = ["No significant risks identified"]

    # Suggested actions
    action_bullets: list[str] = []
    if contra_count or notfnd_count:
        action_bullets.append("Verify specific claims with external or primary sources")
    if notfnd_count:
        action_bullets.append("Ask the model to cite evidence for each claim")
    if overconfidence_issues:
        action_bullets.append("Use stricter prompting to reduce confident but unverified statements")
    if trust_score < 80:
        action_bullets.append("Consider using the 'Fix Answer' feature to get a grounded rewrite")

    if not action_bullets:
        action_bullets = ["Answer appears reliable — standard review recommended"]

    return {"risk_bullets": risk_bullets, "action_bullets": action_bullets}
