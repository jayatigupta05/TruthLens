"""
auditor.py — Core hallucination audit logic using Google Gemini API
"""

import json
import re
from google import genai
from google.genai import types


AUDIT_PROMPT = """You are a Context-Aware Hallucination Auditor.
Your task is to evaluate whether an AI-generated answer is strictly grounded in the provided CONTEXT.
Do NOT use any external knowledge — only the context below.

---
CONTEXT:
{context}

QUESTION:
{question}

ANSWER TO AUDIT:
{answer}
---

PROCESS:
1. Break the answer into individual factual claims.
2. For each claim, evaluate ONLY using the provided CONTEXT.
3. Classify each claim as:
   - "Supported" → clearly present or directly implied in the context
   - "Not Found" → not present in the context (potential hallucination)
   - "Contradicts" → conflicts with the context (severe hallucination)

SCORING RULES:
- Start at 100
- Deduct 25 for each "Contradicts" claim
- Deduct 10 for each "Not Found" claim
- Deduct 5 for each overconfidence signal
- Minimum score is 0

Hallucination Risk:
- 80–100 → Low
- 50–79 → Medium
- 0–49 → High

Respond ONLY with a valid JSON object — no markdown, no extra text — in this exact schema:
{{
  "claims": [
    {{
      "claim": "string",
      "classification": "Supported" | "Not Found" | "Contradicts",
      "reason": "string",
      "snippet": "exact quote from context or None"
    }}
  ],
  "trust_score": integer (0-100),
  "hallucination_risk": "Low" | "Medium" | "High",
  "overconfidence_issues": ["string", ...],
  "risky_sections": ["string", ...],
  "final_verdict": "string (2-3 sentences harsh critique)"
}}
"""


def run_audit(api_key: str, context: str, question: str, answer: str, model_name: str = "gemini-2.5-flash") -> dict:
    """
    Calls Gemini to audit the answer against the context.
    Returns a parsed dict with the full audit result.
    """
    client = genai.Client(api_key=api_key)

    prompt = AUDIT_PROMPT.format(
        context=context.strip(),
        question=question.strip(),
        answer=answer.strip(),
    )

    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.1,
            max_output_tokens=4096,
        ),
    )

    raw = response.text.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)

    return json.loads(raw)

def compute_score_from_claims(claims: list) -> tuple[int, str]:
    """
    Recomputes trust score and risk level from claim list.
    (Fallback if model returns wrong score.)
    """
    score = 100
    for c in claims:
        clf = c.get("classification", "")
        if clf == "Contradicts":
            score -= 25
        elif clf == "Not Found":
            score -= 10
    score = max(0, score)

    if score >= 80:
        risk = "Low"
    elif score >= 50:
        risk = "Medium"
    else:
        risk = "High"

    return score, risk
