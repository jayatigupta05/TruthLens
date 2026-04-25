# 🔍 Hallucination Auditor

A Streamlit app that uses Google Gemini to evaluate whether an AI-generated answer is grounded in a provided context.

## Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Get a Gemini API key
- Go to https://aistudio.google.com/
- Create a free API key

### 3. Run the app
```bash
streamlit run app.py
```

### 4. Use the app
- Paste your **Context** (the source of truth)
- Paste the **Question** that was asked
- Paste the **AI Answer** to audit
- Enter your API key in the sidebar
- Click **Run Audit**

## Output

| Field | Description |
|---|---|
| Trust Score | 0–100, starts at 100 and deducts per issue |
| Hallucination Risk | Low / Medium / High |
| Claims Analysis | Each factual claim classified + snippet |
| Overconfidence Signals | Vague authority claims, unsupported certainty |
| Risky Sections | Exact phrases to watch out for |
| Final Verdict | 2–3 sentence harsh critique |

## Score Deductions
- −25 per **Contradicts** claim
- −10 per **Not Found** claim  
- −5 per overconfidence signal

## Models
- `gemini-1.5-flash` — Fast, cheap, great for most use cases
- `gemini-1.5-pro` — More thorough, slower
- `gemini-2.0-flash` — Latest generation
