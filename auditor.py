"""
auditor.py — AI Trust Layer: Core LLM logic using google-genai SDK v1.73+
"""

import json
import re
import html
from google import genai
from google.genai import types

# ── Default model ─────────────────────────────────────────────────────────────
DEFAULT_MODEL = "gemini-2.5-flash"

# ── Shared generation configs ─────────────────────────────────────────────────
LOW_TEMP  = types.GenerateContentConfig(temperature=0.1, max_output_tokens=4096)
HIGH_TEMP = types.GenerateContentConfig(temperature=0.9, max_output_tokens=1024)


# ── Internal helpers ──────────────────────────────────────────────────────────

def _make_client(api_key: str) -> genai.Client:
    return genai.Client(api_key=api_key)


def _call(client: genai.Client, model: str, prompt: str,
          cfg: types.GenerateContentConfig = None) -> str:
    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config=cfg or LOW_TEMP,
    )
    return response.text.strip()


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

def generate_answer(api_key: str, context: str, question: str,
                    model: str = DEFAULT_MODEL) -> str:
    client = _make_client(api_key)
    prompt = GENERATE_PROMPT.format(context=context.strip(), question=question.strip())
    return _call(client, model, prompt, LOW_TEMP)


def run_audit(api_key: str, context: str, question: str, answer: str,
              model_name: str = DEFAULT_MODEL, strict: bool = False) -> dict:
    client = _make_client(api_key)
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
    raw = _call(client, model_name, prompt, LOW_TEMP)
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


def fix_answer(api_key: str, context: str, question: str, answer: str,
               model: str = DEFAULT_MODEL) -> str:
    client = _make_client(api_key)
    prompt = FIX_PROMPT.format(
        context=context.strip(),
        question=question.strip(),
        answer=answer.strip(),
    )
    return _call(client, model, prompt, LOW_TEMP)


def generate_misleading_answer(api_key: str, context: str, question: str,
                               model: str = DEFAULT_MODEL) -> str:
    client = _make_client(api_key)
    prompt = MISLEADING_PROMPT.format(context=context.strip(), question=question.strip())
    return _call(client, model, prompt, HIGH_TEMP)


def check_consistency(api_key: str, answer: str,
                      model: str = DEFAULT_MODEL) -> dict:
    client = _make_client(api_key)
    prompt = CONSISTENCY_PROMPT.format(answer=answer.strip())
    raw = _call(client, model, prompt, LOW_TEMP)
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


def build_highlighted_answer(answer: str, claims: list) -> str:
    """
    Return HTML of answer with claim spans highlighted by classification.
    Overconfidence words are additionally highlighted in amber.
    """
    escaped = html.escape(answer)

    # Build (span, classification) pairs where the span appears in the answer
    annotated = []
    for c in claims:
        claim_text = html.escape(c.get("claim", "").strip())
        clf = c.get("classification", "Not Found")
        if claim_text and claim_text in escaped:
            annotated.append((claim_text, clf))

    # Longest-first to avoid partial-match clobbering
    annotated.sort(key=lambda x: len(x[0]), reverse=True)

    result = escaped
    placeholders: dict[str, str] = {}

    for idx, (span, clf) in enumerate(annotated):
        bg, border = _COLOR_MAP.get(clf, ("#21262d", "#30363d"))
        tag = (
            f'<mark style="background:{bg};border-bottom:2px solid {border};'
            f'border-radius:3px;padding:1px 3px;cursor:help;" title="{clf}">'
            f'{span}</mark>'
        )
        ph = f"__HL_{idx}__"
        placeholders[ph] = tag
        result = result.replace(span, ph, 1)

    for ph, tag in placeholders.items():
        result = result.replace(ph, tag)

    # Overconfidence words
    for word in OVERCONFIDENCE_WORDS:
        esc_word = html.escape(word)
        result = re.sub(
            re.escape(esc_word),
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
