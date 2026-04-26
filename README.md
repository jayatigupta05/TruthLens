<div align="center">

# 🛡️ TruthLens

### *AI Trust Layer — Hallucination Detection & Reliability Auditing for LLM Outputs*

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Gemini](https://img.shields.io/badge/Google%20Gemini-2.5-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://aistudio.google.com)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](LICENSE)

> **"Don't trust. Verify. Quantify."**  
> TruthLens intercepts LLM outputs and subjects them to a multi-layer forensic audit — grounded entirely in your own context.

</div>

---

## ⚡ What is TruthLens?

TruthLens is a **context-aware hallucination detection system** built on top of Google Gemini. It takes an AI-generated answer, deconstructs it into individual factual claims, and cross-references every single one against a provided source document — assigning trust scores, classifying failure modes, and producing actionable human-readable verdicts.

No external knowledge. No assumptions. Just your context vs. the model's output.

---

## 🧠 Core Capabilities

| Feature | Description |
|---|---|
| 🔬 **Claim-Level Auditing** | Decomposes answers into atomic factual claims and classifies each as `Supported`, `Not Found`, or `Contradicts` |
| 📊 **Trust Scoring** | Deterministic 0–100 score computed from contradiction/hallucination deductions |
| 🎯 **Failure Type Classification** | Automatically labels the primary failure mode: *Contradiction · Unsupported Claim · Overconfidence Bias · Mixed Issues* |
| 🎭 **Confidence Calibration** | Detects linguistic overconfidence — flags answers using strong language (`"definitely"`, `"always"`) despite low factual grounding |
| 🧮 **Score Breakdown** | Transparent per-category deduction table: contradictions, unsupported claims, overconfidence signals |
| 🔁 **Multi-Pass Audit** | Runs Normal + Strict audit modes in parallel; computes score divergence and **Audit Stability** rating |
| 🔄 **Self-Consistency Check** | Independent pass to detect internal logical contradictions *within* the answer itself |
| 🎨 **Inline Highlighting** | HTML-rendered answer with color-coded claim spans and overconfidence word detection |
| ⚠️ **Risk Explanation** | Dynamic "Why This Is Risky" bullets generated from audit results |
| 💡 **User Guidance** | Contextual suggested actions (verify, cite, re-prompt, fix) tailored to the specific failure type |
| ✨ **Grounded Fix** | Rewrites the answer strictly from context, removing or correcting every ungrounded claim |
| ⚖️ **Side-by-Side Model Comparison** | Audit the same question across two Gemini models simultaneously |
| 🧨 **Adversarial Testing** | Generates convincing-but-incorrect answers to stress-test the auditor's detection limits |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        TruthLens Pipeline                       │
│                                                                 │
│  ┌──────────┐    ┌────────────┐    ┌──────────────────────────┐ │
│  │ Context  │    │  Question  │    │    Answer (AI or Manual)  │ │
│  └────┬─────┘    └─────┬──────┘    └────────────┬─────────────┘ │
│       │                │                        │               │
│       └────────────────┴────────────────────────┘               │
│                                │                                │
│                    ┌───────────▼───────────┐                    │
│                    │  Gemini Audit Engine   │                    │
│                    │  (Normal + Strict)     │                    │
│                    └───────────┬───────────┘                    │
│                                │                                │
│         ┌──────────────────────┼──────────────────────┐         │
│         │                      │                      │         │
│  ┌──────▼──────┐    ┌──────────▼──────┐    ┌──────────▼──────┐ │
│  │   Claims    │    │  Overconfidence  │    │ Consistency      │ │
│  │  Analysis   │    │   Detection      │    │   Check          │ │
│  └──────┬──────┘    └──────────┬──────┘    └──────────┬──────┘ │
│         │                      │                      │         │
│         └──────────────────────┼──────────────────────┘         │
│                                │                                │
│                    ┌───────────▼───────────┐                    │
│                    │    Trust Score +        │                   │
│                    │  Failure Classification │                   │
│                    │  Calibration + Guidance │                   │
│                    └───────────┬───────────┘                    │
│                                │                                │
│                    ┌───────────▼───────────┐                    │
│                    │   Streamlit UI Render  │                    │
│                    └───────────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Clone & set up environment

```bash
git clone https://github.com/yourname/TruthLens.git
cd TruthLens
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux
pip install -r requirements.txt
```

### 2. Get a Gemini API key

Head to [Google AI Studio](https://aistudio.google.com/) → **Create API Key**.

You can either:
- Paste it directly into the sidebar at runtime, **or**
- Add it to a `.env` file:

```env
GEMINI_API_KEY=AIza...
```

### 3. Launch

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## 📐 Scoring Model

```
Trust Score = 100
             − 25 × [Contradictions]
             − 10 × [Unsupported Claims]
             −  5 × [Overconfidence Signals]
             (floor: 0)

Risk Level:   80–100 → Low
              50–79  → Medium
               0–49  → High
```

### Overconfidence Signals Detected

`definitely` · `always` · `never` · `certainly` · `obviously` · `proven` ·  
`undeniably` · `absolutely` · `without a doubt` · `it is clear that` · `everyone knows` · `experts say`

---

## 📁 Project Structure

```
TruthLens/
├── app.py              # Streamlit UI — all tabs, rendering, interactivity
├── auditor.py          # Core logic — Gemini calls, scoring, highlighting, analytics
├── requirements.txt    # Python dependencies
└── tests.py            # Basic smoke tests
```

### Key modules in `auditor.py`

| Function | Role |
|---|---|
| `run_audit()` | Main audit pipeline — calls Gemini, parses JSON, recomputes score |
| `classify_failure_type()` | Derives primary failure label from claim mix |
| `detect_confidence_calibration()` | Compares linguistic tone vs. actual trust score |
| `score_breakdown()` | Per-category deduction breakdown |
| `audit_stability_indicator()` | Normal vs. strict score gap → stability rating |
| `explain_risk()` | Dynamic risk + action bullets from audit results |
| `build_highlighted_answer()` | HTML-annotated answer with partial-match claim highlighting |
| `check_consistency()` | Intra-answer logical contradiction detection |

---

## 🎛️ Models Supported

| Model | Best For |
|---|---|
| `gemini-2.5-flash` | Fast audits, default |
| `gemini-2.5-pro` | Deep reasoning, complex contexts |
| `gemini-2.0-flash` | Balanced speed/quality |
| `gemini-2.0-flash-lite` | High-volume, lightweight checks |

---

## 🧪 Adversarial Mode

TruthLens ships with a built-in **red-teaming tool**. It instructs Gemini to generate a *convincing but subtly incorrect* answer — wrong dates, swapped names, fabricated numbers — then immediately audits it under strict mode. Use it to:

- Benchmark the auditor's sensitivity
- Demonstrate hallucination risks to stakeholders
- Tune your prompting strategy

---

## 🤝 Contributing

Pull requests are welcome. For major changes, open an issue first.  
Please ensure new audit logic is covered in `tests.py`.

---

<div align="center">

Built with 🛡️ by humans who don't blindly trust AI outputs.

</div>
