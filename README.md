<div align="center">

# 🛡️ TruthLens

### *AI Trust Layer — Hallucination Detection & Reliability Auditing for LLM Outputs*

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Multi-Provider](https://img.shields.io/badge/Multi%20Provider-5-4285F4?style=for-the-badge&logo=anthropic&logoColor=white)](https://github.com/yourname/TruthLens)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)

---

### 🚀 **Try it live (no setup required)**  
👉 **https://truthlens-jayati.streamlit.app/**

---

> **"Don't trust. Verify. Quantify."**  
> TruthLens doesn’t take AI outputs at face value — it interrogates them.

</div>

---

## ⚡ What is TruthLens?

TruthLens is a **context-aware hallucination detection system** that acts like a forensic auditor for AI responses.

Instead of asking *“Is this answer good?”*, it asks:  
👉 *“Which exact parts are true, false, or unsupported — and how risky is it to trust this?”*

It breaks AI answers into **atomic claims**, verifies each one **strictly against your provided context**, and returns a **trust score, failure diagnosis, and actionable fixes**.

No external knowledge.  
No guessing.  
Just **your context vs reality**.

---

## 🔍 Why This Matters

Most AI tools:
- Sound confident  
- Look correct  
- Fail silently  

TruthLens exposes:
- ❌ Hidden hallucinations  
- ⚠️ Overconfident language  
- 🔍 Unsupported claims  
- 🧠 Logical inconsistencies  

---

## 🧠 Core Capabilities

| Feature | What it actually does |
|---|---|
| 🔬 **Claim-Level Auditing** | Splits answers into facts → verifies each individually |
| 📊 **Trust Score (0–100)** | Quantifies reliability — not vibes |
| 🎯 **Failure Classification** | Pinpoints *why* the answer is unreliable |
| 🎭 **Overconfidence Detection** | Flags misleading certainty in weak answers |
| 🧮 **Transparent Scoring** | Shows exactly how the score was calculated |
| 🔁 **Multi-Pass Audit** | Normal vs Strict → measures answer stability |
| 🔄 **Self-Consistency Check** | Finds contradictions *inside* the answer |
| 🎨 **Inline Highlighting** | Visual claim-by-claim truth mapping |
| ⚠️ **Risk Explanation** | Explains consequences of trusting the output |
| 💡 **Actionable Fixes** | Tells you what to do next (verify, re-prompt, fix) |
| ✨ **Grounded Rewrite** | Produces a clean, context-only corrected answer |
| ⚖️ **Model Comparison** | Compare outputs across providers side-by-side |
| 🧨 **Adversarial Testing** | Stress-test AI with convincing wrong answers |
| 🤖 **Multi-Provider Support** | Gemini, OpenAI, Claude, Ollama, Mock |

---

## 🧪 Try It Instantly

Skip setup entirely:

👉 **Live App:** https://truthlens-jayati.streamlit.app/

Test it with:
- Your own context + question
- Any model output
- Even intentionally wrong answers

---

## 🏗️ How It Works (Simple View)

1. **Input**
   - Context (source of truth)
   - Question
   - AI Answer  

2. **TruthLens Engine**
   - Breaks answer into claims  
   - Verifies each claim  
   - Detects tone vs truth mismatch  
   - Scores and classifies risk  

3. **Output**
   - Trust score  
   - Highlighted answer  
   - Failure diagnosis  
   - Suggested fixes  

---

## 📐 Scoring Model

```text
Trust Score = 100
             − 25 × [Contradictions]
             − 10 × [Unsupported Claims]
             −  5 × [Overconfidence Signals]
