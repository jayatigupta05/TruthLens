"""
app.py — Hallucination Auditor Streamlit UI
Run with: streamlit run app.py
"""

import streamlit as st
from auditor import run_audit, compute_score_from_claims

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Hallucination Auditor",
    page_icon="🔍",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Main background */
[data-testid="stAppViewContainer"] { background: #0f1117; }
[data-testid="stSidebar"] { background: #161b22; }

/* Score ring area */
.score-box {
    text-align: center;
    padding: 1.5rem;
    border-radius: 16px;
    background: #161b22;
    border: 1px solid #30363d;
    margin-bottom: 1rem;
}
.score-number {
    font-size: 4rem;
    font-weight: 800;
    line-height: 1;
}
.risk-badge {
    display: inline-block;
    padding: 0.3rem 1rem;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.9rem;
    margin-top: 0.5rem;
}
.risk-Low  { background: #1a3a2a; color: #3fb950; border: 1px solid #3fb950; }
.risk-Medium { background: #3a2e1a; color: #d29922; border: 1px solid #d29922; }
.risk-High { background: #3a1a1a; color: #f85149; border: 1px solid #f85149; }

/* Claim cards */
.claim-card {
    padding: 1rem 1.2rem;
    border-radius: 10px;
    margin-bottom: 0.75rem;
    border-left: 4px solid transparent;
}
.claim-Supported  { background: #0d2818; border-color: #3fb950; }
.claim-Not\ Found { background: #2a2200; border-color: #d29922; }
.claim-Contradicts { background: #2a0a0a; border-color: #f85149; }

.claim-label {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 0.3rem;
}
.label-Supported   { color: #3fb950; }
.label-Not\ Found  { color: #d29922; }
.label-Contradicts { color: #f85149; }

.snippet-box {
    background: #0d1117;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 0.5rem 0.8rem;
    font-family: monospace;
    font-size: 0.82rem;
    color: #8b949e;
    margin-top: 0.5rem;
}

/* Section headers */
.section-header {
    font-size: 1rem;
    font-weight: 700;
    color: #e6edf3;
    border-bottom: 1px solid #30363d;
    padding-bottom: 0.4rem;
    margin: 1.5rem 0 1rem 0;
}

/* Verdict box */
.verdict-box {
    background: #161b22;
    border: 1px solid #f85149;
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    color: #ffa198;
    font-style: italic;
    line-height: 1.7;
}

/* Tag pills */
.tag-pill {
    display: inline-block;
    background: #21262d;
    border: 1px solid #30363d;
    border-radius: 999px;
    padding: 0.25rem 0.8rem;
    font-size: 0.82rem;
    color: #c9d1d9;
    margin: 0.2rem;
}
</style>
""", unsafe_allow_html=True)


# ── Sidebar: API key + model ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    api_key = st.text_input(
        "Google Gemini API Key",
        type="password",
        placeholder="AIza...",
        help="Get your key at https://aistudio.google.com/",
    )
    model_choice = st.selectbox(
        "Gemini Model",
        ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash", "gemini-2.0-flash-lite"],
        index=0,
        help="Flash is faster & cheaper; Pro is more thorough.",
    )
    st.markdown("---")
    st.markdown("""
**How it works**
1. Paste your context, question & answer
2. Hit **Run Audit**
3. Get a trust score + claim-by-claim breakdown

**Score deductions**
- −25 per contradiction  
- −10 per unsupported claim  
- −5 per overconfidence signal
""")


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 🔍 Hallucination Auditor")
st.markdown("*Evaluate whether an AI-generated answer is grounded in the provided context.*")
st.markdown("---")

# ── Input form ────────────────────────────────────────────────────────────────
col1, col2 = st.columns([3, 2], gap="large")

with col1:
    context_input = st.text_area(
        "📄 Context",
        height=220,
        placeholder="Paste the source context here — the ground truth the answer should be based on...",
    )
    question_input = st.text_area(
        "❓ Question",
        height=90,
        placeholder="What question was the AI answering?",
    )
    answer_input = st.text_area(
        "🤖 AI-Generated Answer (to audit)",
        height=180,
        placeholder="Paste the AI answer you want to fact-check against the context...",
    )

    run_btn = st.button("🚀 Run Audit", type="primary", use_container_width=True)

# ── Example loader ────────────────────────────────────────────────────────────
with col2:
    st.markdown("#### 💡 Try an Example")
    if st.button("Load Sample Inputs", use_container_width=True):
        st.session_state["ex_context"] = (
            "The Eiffel Tower was constructed between 1887 and 1889 as the entrance arch "
            "for the 1889 World's Fair. It was designed by engineer Gustave Eiffel. "
            "The tower stands 330 metres tall and is located in Paris, France. "
            "It was initially criticised by some French artists and intellectuals."
        )
        st.session_state["ex_question"] = "When was the Eiffel Tower built and who designed it?"
        st.session_state["ex_answer"] = (
            "The Eiffel Tower was built in 1885 by the famous architect Gustave Eiffel. "
            "It stands 330 metres tall and was constructed as the centrepiece of the 1889 World's Fair in Paris. "
            "Experts say it is the most visited monument in the world, attracting over 7 million visitors annually. "
            "It was universally praised by the French public upon its completion."
        )
        st.rerun()

    if "ex_context" in st.session_state:
        st.info("✅ Sample loaded — scroll left and paste, or just hit **Run Audit** after filling the fields with the sample data shown below.")
        st.markdown("**Context:**")
        st.code(st.session_state["ex_context"], language=None)
        st.markdown("**Question:**")
        st.code(st.session_state["ex_question"], language=None)
        st.markdown("**Answer:**")
        st.code(st.session_state["ex_answer"], language=None)

    st.markdown("---")
    st.markdown("#### 📊 Legend")
    st.markdown("""
<span class="tag-pill" style="border-color:#3fb950;color:#3fb950">✅ Supported</span> Claim is in context<br><br>
<span class="tag-pill" style="border-color:#d29922;color:#d29922">⚠️ Not Found</span> Potential hallucination<br><br>
<span class="tag-pill" style="border-color:#f85149;color:#f85149">❌ Contradicts</span> Conflicts with context
""", unsafe_allow_html=True)


# ── Run audit ─────────────────────────────────────────────────────────────────
if run_btn:
    # Prefill from example if loaded
    ctx  = context_input  or st.session_state.get("ex_context", "")
    q    = question_input or st.session_state.get("ex_question", "")
    ans  = answer_input   or st.session_state.get("ex_answer", "")

    if not api_key:
        st.error("🔑 Please enter your Gemini API key in the sidebar.")
    elif not ctx or not q or not ans:
        st.warning("⚠️ Please fill in Context, Question, and Answer before running.")
    else:
        with st.spinner("🔬 Auditing claims against context..."):
            try:
                result = run_audit(api_key, ctx, q, ans, model_name=model_choice)

                claims   = result.get("claims", [])
                score    = result.get("trust_score", 0)
                risk     = result.get("hallucination_risk", "High")
                overconf = result.get("overconfidence_issues", [])
                risky    = result.get("risky_sections", [])
                verdict  = result.get("final_verdict", "")

                # Recompute score as a safety net
                computed_score, computed_risk = compute_score_from_claims(claims)
                if abs(computed_score - score) > 20:
                    score = computed_score
                    risk  = computed_risk

                st.markdown("---")

                # ── Score & Risk ──────────────────────────────────────────────
                r1, r2, r3 = st.columns(3)

                score_color = "#3fb950" if score >= 80 else "#d29922" if score >= 50 else "#f85149"
                with r1:
                    st.markdown(f"""
<div class="score-box">
  <div style="color:#8b949e;font-size:0.8rem;margin-bottom:0.3rem">TRUST SCORE</div>
  <div class="score-number" style="color:{score_color}">{score}</div>
  <div style="color:#8b949e;font-size:0.8rem">/ 100</div>
</div>""", unsafe_allow_html=True)

                with r2:
                    st.markdown(f"""
<div class="score-box">
  <div style="color:#8b949e;font-size:0.8rem;margin-bottom:0.3rem">HALLUCINATION RISK</div>
  <div style="margin-top:0.8rem">
    <span class="risk-badge risk-{risk}">{risk.upper()}</span>
  </div>
</div>""", unsafe_allow_html=True)

                with r3:
                    total   = len(claims)
                    sup     = sum(1 for c in claims if c["classification"] == "Supported")
                    notfnd  = sum(1 for c in claims if c["classification"] == "Not Found")
                    contra  = sum(1 for c in claims if c["classification"] == "Contradicts")
                    st.markdown(f"""
<div class="score-box">
  <div style="color:#8b949e;font-size:0.8rem;margin-bottom:0.6rem">CLAIMS BREAKDOWN</div>
  <div style="font-size:0.88rem;line-height:2">
    <span style="color:#3fb950">✅ {sup} Supported</span><br>
    <span style="color:#d29922">⚠️ {notfnd} Not Found</span><br>
    <span style="color:#f85149">❌ {contra} Contradicts</span>
  </div>
</div>""", unsafe_allow_html=True)

                # ── Claims Analysis ───────────────────────────────────────────
                st.markdown('<div class="section-header">🔬 Claims Analysis</div>', unsafe_allow_html=True)

                icon_map = {"Supported": "✅", "Not Found": "⚠️", "Contradicts": "❌"}
                css_class_map = {
                    "Supported":  "claim-Supported",
                    "Not Found":  "claim-Not Found",
                    "Contradicts":"claim-Contradicts",
                }
                label_class_map = {
                    "Supported":  "label-Supported",
                    "Not Found":  "label-Not Found",
                    "Contradicts":"label-Contradicts",
                }

                for i, c in enumerate(claims, 1):
                    clf     = c.get("classification", "Not Found")
                    icon    = icon_map.get(clf, "❓")
                    snippet = c.get("snippet", "None")
                    snippet_html = (
                        f'<div class="snippet-box">"{snippet}"</div>'
                        if snippet and snippet.lower() != "none"
                        else '<div class="snippet-box" style="color:#484f58">No supporting snippet</div>'
                    )
                    st.markdown(f"""
<div class="claim-card {css_class_map.get(clf,'')}">
  <div class="claim-label {label_class_map.get(clf,'')}">{icon} Claim {i} — {clf}</div>
  <div style="color:#e6edf3;margin-bottom:0.4rem"><strong>{c.get('claim','')}</strong></div>
  <div style="color:#8b949e;font-size:0.88rem">{c.get('reason','')}</div>
  {snippet_html}
</div>""", unsafe_allow_html=True)

                # ── Overconfidence ────────────────────────────────────────────
                if overconf:
                    st.markdown('<div class="section-header">😤 Overconfidence Signals</div>', unsafe_allow_html=True)
                    for oc in overconf:
                        st.markdown(f"- {oc}")

                # ── Risky Sections ────────────────────────────────────────────
                if risky:
                    st.markdown('<div class="section-header">🚩 Risky Sections</div>', unsafe_allow_html=True)
                    for rs in risky:
                        st.markdown(f'<span class="tag-pill" style="border-color:#f85149">"{rs}"</span>', unsafe_allow_html=True)

                # ── Final Verdict ─────────────────────────────────────────────
                st.markdown('<div class="section-header">⚖️ Final Verdict</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="verdict-box">{verdict}</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ Audit failed: {e}")
                st.exception(e)
