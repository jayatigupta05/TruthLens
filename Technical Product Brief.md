# TruthLens — Technical Product Brief
### AI Trust Layer: Hallucination Detection, Claim Verification & Reliability Scoring for LLM Outputs

---

## 1. Problem Statement

Large Language Models generate fluent, authoritative-sounding text regardless of factual accuracy. In production deployments — customer support, legal summarisation, medical Q&A, RAG pipelines — a hallucinated answer is indistinguishable from a correct one at the surface level. Standard evaluation methods (BLEU, ROUGE, human review) are either post-hoc, expensive, or not grounded in the specific document the model was supposed to use.

**The core gap:** there is no lightweight, real-time mechanism that can cross-reference an LLM's output against a user-supplied source document, quantify trust, classify the failure mode, and surface that information in a human-readable UI — without requiring a separate labelled dataset or fine-tuned evaluator model.

TruthLens closes that gap.

---

## 2. System Overview

TruthLens is a two-layer Python application:

| Layer | Technology | Responsibility |
|---|---|---|
| **Backend logic** | `auditor.py` (pure Python) | All LLM calls, JSON parsing, scoring, analytics |
| **Frontend UI** | `app.py` (Streamlit) | User interaction, state management, rendering |

The system is stateless per-request. There is no database. All computation is driven by Gemini API calls and deterministic Python functions.

---

## 3. LLM Integration — `google-genai` SDK

TruthLens uses the **`google-genai` SDK (v1.73+)** via the `genai.Client` interface — the current production SDK, not the deprecated `google-generativeai` package.

```python
client = genai.Client(api_key=api_key)
response = client.models.generate_content(
    model=model,
    contents=prompt,
    config=types.GenerateContentConfig(temperature=0.1, max_output_tokens=4096),
)
```

Two generation configs are defined globally:

- **`LOW_TEMP` (0.1)** — used for all audit and fix operations. Low temperature is critical for deterministic, fact-bound judgements.
- **`HIGH_TEMP` (0.9)** — used only for adversarial answer generation, where creative plausible-sounding fabrication is the desired behaviour.

Supported models: `gemini-2.5-flash`, `gemini-2.5-pro`, `gemini-2.0-flash`, `gemini-2.0-flash-lite`. The model is user-selectable at runtime with no code changes required.

---

## 4. Core Audit Pipeline

### 4.1 Prompt Architecture

The audit is driven by a single structured prompt (`AUDIT_PROMPT`) that instructs Gemini to act as a **Context-Aware Hallucination Auditor**. The key design constraints baked into the prompt:

- **Strict grounding:** the model is explicitly told not to use external knowledge — only the provided context.
- **Structured output:** the model is required to return valid JSON with a defined schema. No markdown, no prose.
- **Dual-mode operation:** a `mode` field switches between `NORMAL` (balanced judgement, allows reasonable implications) and `STRICT` (treats anything not explicitly stated as `Not Found`).

The required JSON schema:

```json
{
  "claims": [
    {
      "claim": "string",
      "classification": "Supported | Not Found | Contradicts",
      "reason": "string",
      "snippet": "exact quote from context or null"
    }
  ],
  "trust_score": "integer",
  "hallucination_risk": "Low | Medium | High",
  "overconfidence_issues": ["string"],
  "risky_sections": ["string"],
  "final_verdict": "string"
}
```

### 4.2 Robust JSON Parsing

LLMs occasionally wrap JSON in markdown fences or emit minor formatting errors. The `_safe_parse_json()` function handles this with a two-pass strategy:

1. Strip leading/trailing code fences with regex, then parse.
2. If that fails, use `re.search(r'\{.*\}', raw, re.DOTALL)` to extract the JSON object by braces, then parse.

This makes the parser resilient to common Gemini output artifacts without depending on constrained decoding.

### 4.3 Score Recomputation

The model's returned `trust_score` is discarded after parsing. It is always recomputed deterministically in Python via `compute_score_from_claims()`:

```
score = 100
score -= 25 × count(Contradicts claims)
score -= 10 × count(Not Found claims)
score -= 5  × len(overconfidence_issues)
score = max(0, score)
```

This is intentional: it decouples the scoring logic from the model's internal arithmetic, ensuring the score is always consistent, reproducible, and auditable independent of model version drift.

---

## 5. Multi-Pass Audit & Stability Analysis

When multi-pass mode is enabled, the system runs two independent audit calls — one in NORMAL mode and one in STRICT mode — against the same answer. This produces:

- **Normal score** and **Strict score**
- **Confidence Gap** (`confidence_gap_label()`): `Low / Medium / High` based on the absolute point difference (thresholds: 15 and 30)
- **Audit Stability** (`audit_stability_indicator()`): a qualitative label (`High / Medium / Low Stability`) derived from the same gap, displayed as a colour-coded badge

High score divergence between modes indicates the answer relies heavily on implied rather than explicit facts — a meaningful signal for downstream trust decisions.

---

## 6. Analytical Functions

All analytical functions in `auditor.py` are pure Python — no additional LLM calls.

### 6.1 `classify_failure_type(claims, overconfidence_issues)`
Maps the claim distribution to one of five mutually-exclusive labels:
- `"Contradiction with Context"` — only contradictions present
- `"Unsupported Claim"` — only ungrounded claims
- `"Overconfidence Bias"` — only overconfidence signals
- `"Mixed Issues"` — two or more issue types
- `"No Issues Detected"` — clean answer

### 6.2 `detect_confidence_calibration(answer, trust_score)`
Scans the answer text for 12 high-confidence linguistic markers. Compares detected tone against the computed trust score to identify **calibration mismatch** — where a model expresses certainty it has not earned. Returns a structured dict with `model_confidence`, `actual_reliability`, `is_overconfident`, and a human-readable verdict string.

### 6.3 `score_breakdown(claims, overconfidence_issues)`
Returns an itemised dict of per-category deductions (with counts), matching exactly the arithmetic in `compute_score_from_claims()`. Used to render the transparent score breakdown table in the UI.

### 6.4 `explain_risk(claims, overconfidence_issues, trust_score)`
Generates dynamic `risk_bullets` and `action_bullets` lists from the audit state. No LLM call — purely conditional logic over the claim counts and score ranges. Output is tailored: if contradictions dominate, actions emphasise verification; if overconfidence is the issue, actions emphasise re-prompting strategy.

---

## 7. Inline Claim Highlighting

`build_highlighted_answer()` produces an HTML-annotated version of the answer with colour-coded `<mark>` spans per claim classification.

**Technical challenges solved:**

1. **Partial matching** — LLM-extracted claims rarely match the answer verbatim (e.g. paraphrasing, punctuation differences). The `_partial_match_span()` helper first attempts exact match, then performs a sliding-window word-subsequence search (minimum 3-word window) to find the longest verbatim fragment of the claim that appears in the answer. This dramatically increases the proportion of claims that get visually highlighted.

2. **HTML corruption prevention** — a `already_marked` set prevents the same span from being wrapped twice. Overconfidence word highlighting uses a word-boundary-aware regex (`(?<![>\w])...(?![\w<])`) to avoid injecting `<mark>` tags inside existing HTML attributes.

3. **Placeholder strategy** — claim spans are replaced with opaque tokens (`__HL_0__`, etc.) before overconfidence highlighting runs. This prevents overconfidence regex from matching text inside claim spans and corrupting the HTML structure.

---

## 8. Self-Consistency Check

An independent Gemini call (`check_consistency()`) analyses the answer *in isolation* — without any context — for internal logical contradictions. This is distinct from grounding: an answer can be fully grounded in the context but still be internally inconsistent (e.g. stating both that a tower was built in 1887 and that construction started in 1889 in different sentences). Returns `is_consistent` (bool), `issues` (list), and `summary` (string).

---

## 9. Adversarial Testing Mode

`generate_misleading_answer()` uses `HIGH_TEMP` and a red-team prompt instructing the model to produce a convincing answer with subtle factual errors: wrong dates, swapped names, fabricated numbers. The output is then immediately passed to `run_audit()` in strict mode. This provides:

- A ground-truth adversarial test case for benchmarking auditor sensitivity
- A demonstration tool for stakeholders to see hallucinations detected in real time

---

## 10. Side-by-Side Model Comparison

The Compare tab generates and audits the same question with two independently selected Gemini models. Each model runs its own `generate_answer()` + `run_audit()` pipeline. Results are displayed in parallel columns with score, risk level, coverage percentage, and final verdict. A diff callout highlights the winning model and point differential.

---

## 11. Fix Answer

`fix_answer()` passes the original context, question, and flawed answer to Gemini with a strict rewriting prompt. The model is instructed to:
- Remove any claim not found in context
- Correct any claim that contradicts context
- Not add any information not present in context

The output is a grounded rewrite, not a summary — preserving the answer's structure while replacing hallucinated content.

---

## 12. State Management

The application is built in Streamlit with explicit session state management. All widget keys (`ctx_main`, `q_main`, etc.) are declared at widget instantiation. Example pre-population uses `on_click` callbacks — the only Streamlit-safe pattern for writing to widget-bound session state keys, as callbacks execute before the next render cycle.

---

## 13. Deployment Requirements

```
Python         >= 3.11   (uses X | Y union type hints)
streamlit      >= 1.35.0
google-genai   >= 0.8.0  (NOT google-generativeai)
```

No database. No vector store. No embedding model. No external API beyond Gemini. The entire system runs locally against the Gemini API with a single key. Horizontally scalable by running multiple Streamlit instances behind a load balancer.

---

## 14. Extension Points

| Capability | How to Extend |
|---|---|
| Custom scoring weights | Modify deduction constants in `compute_score_from_claims()` |
| New overconfidence vocabulary | Append to `OVERCONFIDENCE_WORDS` list in `auditor.py` |
| Additional audit modes | Add new `mode` / `mode_instruction` branches to `run_audit()` |
| Batch auditing | Wrap `run_audit()` in a loop; Streamlit UI is independent |
| API endpoint | Expose `run_audit()` via FastAPI — `auditor.py` has zero UI dependency |
| Persistent results | Serialise `result` dict to JSON/database after `run_audit()` returns |

---

*TruthLens is designed to be embedded, extended, and productionised. The clean separation between `auditor.py` (pure logic) and `app.py` (pure UI) means the entire audit engine can be extracted and deployed as a microservice with no refactoring.*
