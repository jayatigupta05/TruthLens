"""
app.py — AI Trust Layer: Streamlit UI (Multi-Provider Edition)
Run with: streamlit run app.py
"""

import streamlit as st
from auditor import (
    generate_answer,
    run_audit,
    fix_answer,
    generate_misleading_answer,
    check_consistency,
    compute_context_coverage,
    confidence_gap_label,
    trust_recommendation,
    build_highlighted_answer,
    classify_failure_type,
    detect_confidence_calibration,
    score_breakdown,
    audit_stability_indicator,
    explain_risk,
    DEFAULT_MODEL,
    DEFAULT_PROVIDER,
)
from model_provider import get_available_models, SUPPORTED_PROVIDERS

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="AI Trust Layer",
    page_icon="🛡️",
    layout="wide",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0f1117; }
[data-testid="stSidebar"]          { background: #161b22; }

.score-box {
    text-align: center; padding: 1.2rem; border-radius: 14px;
    background: #161b22; border: 1px solid #30363d; margin-bottom: 0.75rem;
}
.score-number { font-size: 3.5rem; font-weight: 800; line-height: 1; }

.risk-badge {
    display: inline-block; padding: 0.25rem 0.9rem;
    border-radius: 999px; font-weight: 700; font-size: 0.85rem; margin-top: 0.4rem;
}
.risk-Low    { background:#1a3a2a; color:#3fb950; border:1px solid #3fb950; }
.risk-Medium { background:#3a2e1a; color:#d29922; border:1px solid #d29922; }
.risk-High   { background:#3a1a1a; color:#f85149; border:1px solid #f85149; }

.claim-card {
    padding: 0.9rem 1.1rem; border-radius: 10px;
    margin-bottom: 0.65rem; border-left: 4px solid transparent;
}
.clf-Supported   { background:#0d2818; border-color:#3fb950; }
.clf-NotFound    { background:#2a2200; border-color:#d29922; }
.clf-Contradicts { background:#2a0a0a; border-color:#f85149; }

.claim-label { font-size:0.7rem; font-weight:700; letter-spacing:0.08em;
               text-transform:uppercase; margin-bottom:0.25rem; }
.lbl-Supported   { color:#3fb950; }
.lbl-NotFound    { color:#d29922; }
.lbl-Contradicts { color:#f85149; }

.snippet-box {
    background:#0d1117; border:1px solid #30363d; border-radius:6px;
    padding:0.4rem 0.7rem; font-family:monospace; font-size:0.8rem;
    color:#8b949e; margin-top:0.4rem;
}

.section-hdr {
    font-size:1rem; font-weight:700; color:#e6edf3;
    border-bottom:1px solid #30363d; padding-bottom:0.35rem;
    margin:1.4rem 0 0.9rem 0;
}

.verdict-box {
    background:#161b22; border:1px solid #f85149; border-radius:10px;
    padding:1.1rem 1.4rem; color:#ffa198; font-style:italic; line-height:1.7;
}

.insight-box {
    background:#161b22; border:1px solid #30363d; border-radius:10px;
    padding:1rem 1.3rem; margin-bottom:0.75rem; line-height:1.8;
}

.highlight-box {
    background:#161b22; border:1px solid #30363d; border-radius:10px;
    padding:1.1rem 1.4rem; margin-bottom:0.75rem;
}

.fix-box {
    background:#0d2010; border:1px solid #3fb950; border-radius:10px;
    padding:1.1rem 1.4rem; color:#7ee787; line-height:1.8; white-space:pre-wrap;
}

.tag-pill {
    display:inline-block; background:#21262d; border:1px solid #30363d;
    border-radius:999px; padding:0.2rem 0.7rem; font-size:0.8rem;
    color:#c9d1d9; margin:0.15rem;
}

.compare-col {
    background:#161b22; border:1px solid #30363d; border-radius:12px;
    padding:1.2rem; margin-bottom:0.5rem;
}

.failure-badge {
    display:inline-block; padding:0.3rem 1rem;
    border-radius:999px; font-weight:700; font-size:0.85rem; margin-top:0.4rem;
}
.failure-contradiction { background:#3a0a0a; color:#f85149; border:1px solid #f85149; }
.failure-unsupported   { background:#2a2200; color:#d29922; border:1px solid #d29922; }
.failure-overconfidence{ background:#2a1a00; color:#e3b341; border:1px solid #e3b341; }
.failure-mixed         { background:#1a1a3a; color:#79c0ff; border:1px solid #79c0ff; }
.failure-none          { background:#0d2818; color:#3fb950; border:1px solid #3fb950; }

.calibration-box {
    background:#161b22; border:1px solid #30363d; border-radius:10px;
    padding:1rem 1.3rem; margin-bottom:0.75rem;
    display:flex; gap:2rem; flex-wrap:wrap; align-items:center;
}
.cal-item { text-align:center; }
.cal-label { font-size:0.7rem; color:#8b949e; text-transform:uppercase; letter-spacing:0.08em; }
.cal-value { font-size:1.1rem; font-weight:700; margin-top:0.2rem; }

.breakdown-box {
    background:#161b22; border:1px solid #30363d; border-radius:10px;
    padding:1rem 1.3rem; margin-bottom:0.75rem; font-size:0.9rem;
}
.breakdown-row { display:flex; justify-content:space-between;
    padding:0.3rem 0; border-bottom:1px solid #21262d; color:#c9d1d9; }
.breakdown-row:last-child { border-bottom:none; font-weight:700; color:#e6edf3; }

.risk-explain-box {
    background:#1e1015; border:1px solid #f85149; border-radius:10px;
    padding:1rem 1.3rem; margin-bottom:0.75rem; line-height:1.8;
}
.action-box {
    background:#0d1a10; border:1px solid #3fb950; border-radius:10px;
    padding:1rem 1.3rem; margin-bottom:0.75rem; line-height:1.8;
}
.stability-badge {
    display:inline-block; padding:0.25rem 0.8rem;
    border-radius:999px; font-weight:700; font-size:0.85rem;
}
.stab-High   { background:#0d2818; color:#3fb950; border:1px solid #3fb950; }
.stab-Medium { background:#3a2e1a; color:#d29922; border:1px solid #d29922; }
.stab-Low    { background:#3a1a1a; color:#f85149; border:1px solid #f85149; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    
    # Provider selection
    provider_choice = st.selectbox(
        "🤖 Model Provider",
        SUPPORTED_PROVIDERS,
        index=SUPPORTED_PROVIDERS.index(DEFAULT_PROVIDER),
        help="Choose which AI model provider to use",
    )

    # provider = "mock"
    # provider_choice = "mock"
    
    # Store provider in session state for consistent use
    st.session_state.provider = provider_choice
    
    # API Key input based on provider
    if provider_choice == "ollama":
        ollama_url = st.text_input(
            "Ollama Base URL",
            value="http://localhost:11434",
            placeholder="http://localhost:11434",
            help="URL where Ollama is running",
        )
        st.session_state.ollama_url = ollama_url
        api_key = "ollama"  # Dummy key for Ollama
    else:
        provider_names = {
            "gemini": "Google Gemini",
            "openai": "OpenAI",
            "anthropic": "Anthropic Claude",
        }
        api_key = st.text_input(
            f"{provider_names.get(provider_choice, provider_choice)} API Key",
            type="password",
            placeholder={
                "gemini": "AIza...",
                "openai": "sk-...",
                "anthropic": "sk-ant-...",
            }.get(provider_choice, "Enter API key..."),
            help={
                "gemini": "Get your key at https://aistudio.google.com/",
                "openai": "Get your key at https://platform.openai.com/api-keys",
                "anthropic": "Get your key at https://console.anthropic.com/",
            }.get(provider_choice, ""),
        )
        st.session_state.ollama_url = None
    
    # Model selection based on provider
    try:
        available_models = get_available_models(provider_choice)
        model_choice = st.selectbox(
            "Model",
            available_models,
            index=0,
        )
    except Exception as e:
        st.error(f"Could not load models: {e}")
        model_choice = DEFAULT_MODEL
    
    # Store choices in session state
    st.session_state.model = model_choice
    st.session_state.api_key = api_key
    
    st.markdown("---")
    
    # Optional: Evaluation API Key (for using different provider for evaluation)
    st.markdown("### 🔍 Evaluation Settings")
    use_separate_eval = st.checkbox(
        "Use different provider for evaluation",
        value=False,
        help="Use a different API key/model for the audit step"
    )
    
    if use_separate_eval:
        eval_provider = st.selectbox(
            "Evaluation Provider",
            SUPPORTED_PROVIDERS,
            index=SUPPORTED_PROVIDERS.index(DEFAULT_PROVIDER),
            key="eval_provider_select",
        )
        if eval_provider == "ollama":
            eval_url = st.text_input(
                "Evaluation Ollama URL",
                value="http://localhost:11434",
                key="eval_ollama_url",
            )
            eval_api_key = "ollama"
        else:
            eval_api_key = st.text_input(
                f"{eval_provider.capitalize()} API Key for Evaluation",
                type="password",
                key="eval_api_key_input",
            )  # Fallback to main API key if eval key not provided
            eval_url = None
        st.session_state.eval_provider = eval_provider
        st.session_state.eval_api_key = eval_api_key
        st.session_state.eval_url = eval_url
    else:
        st.session_state.eval_provider = None
        st.session_state.eval_api_key = None
        st.session_state.eval_url = None
    
    st.markdown("---")
    st.markdown("**Score deductions**")
    st.markdown("− 25 per contradiction  \n− 10 per unsupported claim  \n− 5 per overconfidence signal")
    st.markdown("---")
    st.markdown("**Highlight legend**")
    st.markdown("""
<span class="tag-pill" style="border-color:#3fb950;color:#3fb950">✅ Supported</span><br>
<span class="tag-pill" style="border-color:#d29922;color:#d29922">⚠️ Not Found</span><br>
<span class="tag-pill" style="border-color:#f85149;color:#f85149">❌ Contradicts</span><br>
<span class="tag-pill" style="border-color:#e3b341;color:#e3b341">🔶 Overconfidence</span>
""", unsafe_allow_html=True)


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# 🛡️ AI Trust Layer")
st.markdown("*Generate, audit, stress-test and correct LLM outputs — grounded in your context.*")
st.markdown("---")


# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_main, tab_compare, tab_adversarial = st.tabs([
    "🔍 Audit", "⚖️ Compare Models", "🧨 Adversarial Test"
])


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — MAIN AUDIT
# ═══════════════════════════════════════════════════════════════════════════════
with tab_main:
    left, right = st.columns([3, 2], gap="large")

    with left:
        context_input = st.text_area(
            "📄 Context",
            height=200,
            placeholder="Paste the source context here — the ground truth...",
            key="ctx_main",
        )
        question_input = st.text_area(
            "❓ Question",
            height=80,
            placeholder="What question should the AI answer?",
            key="q_main",
        )

        manual_override = st.toggle("✏️ Manual answer override (advanced)", value=False)
        if manual_override:
            answer_override = st.text_area(
                "🤖 Paste your own answer to audit",
                height=150,
                key="ans_override",
            )
        else:
            answer_override = ""

        run_btn = st.button("🚀 Generate & Audit", type="primary", use_container_width=True)

    with right:
        st.markdown("#### 💡 Load Example")

        def _load_eiffel_example():
            st.session_state["ctx_main"] = (
                "The Eiffel Tower was constructed between 1887 and 1889 as the entrance arch "
                "for the 1889 World's Fair. It was designed by engineer Gustave Eiffel. "
                "The tower stands 330 metres tall and is located in Paris, France. "
                "It was initially criticised by some French artists and intellectuals."
            )
            st.session_state["q_main"] = "When was the Eiffel Tower built and who designed it?"

        st.button("Load Eiffel Tower Example", use_container_width=True,
                  on_click=_load_eiffel_example)

        st.markdown("---")
        st.markdown("#### 🔧 Audit Options")
        show_evidence  = st.toggle("Show Evidence Snippets", value=True)
        run_multipass  = st.toggle("Multi-Pass Audit (Normal + Strict)", value=True)
        run_consistency = st.toggle("Self-Consistency Check", value=True)

    # ── Run audit ─────────────────────────────────────────────────────────────
    if run_btn:
        ctx = context_input.strip()
        q   = question_input.strip()

        # Get values from session state
        api_key = st.session_state.get("api_key")
        model_choice = st.session_state.get("model", DEFAULT_MODEL)
        provider_choice = st.session_state.get("provider", DEFAULT_PROVIDER)
        ollama_url = st.session_state.get("ollama_url")

        if provider_choice != "mock" and not api_key:
            st.error(f"🔑 Please enter your {provider_choice.capitalize()} API key in the sidebar.")
            st.stop()
        if not ctx or not q:
            st.warning("⚠️ Context and Question are required.")
            st.stop()

        # Step 1: Generate or use override
        if manual_override and answer_override.strip():
            answer = answer_override.strip()
            st.info("Using manually provided answer.")
        else:
            with st.spinner(f"✍️ Generating using {provider_choice} ({model_choice})..."):
                try:
                    answer = generate_answer(
                        api_key, ctx, q,
                        model=model_choice,
                        provider=provider_choice,
                        base_url=ollama_url,
                    )
                    if isinstance(answer, str) and "ERROR" in answer:
                        st.warning("⚠️ Gemini is busy, switching to mock mode for demo")

                        provider_choice = "mock"
                        answer = generate_answer(
                            api_key, ctx, q,
                            model="mock-standard",
                            provider="mock",
                            base_url=ollama_url,
                        )

                except Exception as e:
                    st.error(f"❌ Answer generation failed: {e}")
                    st.stop()

        # Determine which provider to use for evaluation
        eval_provider = st.session_state.get("eval_provider", provider_choice)
        eval_api_key = st.session_state.get("eval_api_key_input")
        if not eval_api_key:
            eval_api_key = api_key
        eval_url = st.session_state.get("eval_url", ollama_url)

        # Step 2: Normal audit
        with st.spinner("🔬 Running hallucination audit..."):
            try:
                result = run_audit(
                    eval_api_key, ctx, q, answer,
                    model_name=model_choice,
                    provider=eval_provider or provider_choice,
                    strict=False,
                    base_url=eval_url,
                )
                if not isinstance(result, dict):
                    st.error("Audit failed or returned invalid response")
                    st.stop()
            except Exception as e:
                st.error(f"❌ Audit failed: {e}")
                st.stop()

        claims   = result.get("claims", [])
        score    = result.get("trust_score", 0)
        risk     = result.get("hallucination_risk", "High")
        overconf = result.get("overconfidence_issues", [])
        risky    = result.get("risky_sections", [])
        verdict  = result.get("final_verdict", "")
        coverage = compute_context_coverage(claims)
        rec_label, rec_color = trust_recommendation(score, risk)

        sup    = sum(1 for c in claims if c["classification"] == "Supported")
        notfnd = sum(1 for c in claims if c["classification"] == "Not Found")
        contra = sum(1 for c in claims if c["classification"] == "Contradicts")

        # ── New analytical data ───────────────────────────────────────────────
        failure_type  = classify_failure_type(claims, overconf)
        calibration   = detect_confidence_calibration(answer, score)
        sbd           = score_breakdown(claims, overconf)
        risk_explain  = explain_risk(claims, overconf, score)

        st.markdown("---")

        # ── Generated answer ──────────────────────────────────────────────────
        st.markdown('<div class="section-hdr">✍️ Generated Answer</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insight-box" style="color:#e6edf3;">{answer}</div>',
                    unsafe_allow_html=True)

        # ── Summary insight block + Failure Type ─────────────────────────────
        st.markdown('<div class="section-hdr">📊 Summary</div>', unsafe_allow_html=True)

        # Map failure type to CSS class
        _ft_css = {
            "Contradiction with Context": "failure-contradiction",
            "Unsupported Claim":          "failure-unsupported",
            "Overconfidence Bias":        "failure-overconfidence",
            "Mixed Issues":               "failure-mixed",
            "No Issues Detected":         "failure-none",
        }
        ft_class = _ft_css.get(failure_type, "failure-none")

        st.markdown(f"""
<div class="insight-box">
  This answer contains:<br>
  &nbsp;&nbsp;• <span style="color:#f85149;font-weight:700">{contra} contradiction(s)</span><br>
  &nbsp;&nbsp;• <span style="color:#d29922;font-weight:700">{notfnd} unsupported claim(s)</span><br>
  &nbsp;&nbsp;• <span style="color:#3fb950;font-weight:700">{sup} supported claim(s)</span><br>
  &nbsp;&nbsp;• Risk Level: <span style="font-weight:700">
        <span class="risk-badge risk-{risk}">{risk.upper()}</span></span><br>
  &nbsp;&nbsp;• Primary Failure Type:&nbsp;
        <span class="failure-badge {ft_class}">{failure_type}</span>
</div>""", unsafe_allow_html=True)

        # ── Score cards ───────────────────────────────────────────────────────
        c1, c2, c3, c4 = st.columns(4)
        score_color = "#3fb950" if score >= 80 else "#d29922" if score >= 50 else "#f85149"

        with c1:
            st.markdown(f"""
<div class="score-box">
  <div style="color:#8b949e;font-size:0.75rem">TRUST SCORE</div>
  <div class="score-number" style="color:{score_color}">{score}</div>
  <div style="color:#8b949e;font-size:0.75rem">/ 100</div>
</div>""", unsafe_allow_html=True)

        with c2:
            st.markdown(f"""
<div class="score-box">
  <div style="color:#8b949e;font-size:0.75rem">RISK LEVEL</div>
  <div style="margin-top:0.7rem">
    <span class="risk-badge risk-{risk}">{risk.upper()}</span>
  </div>
</div>""", unsafe_allow_html=True)

        with c3:
            st.markdown(f"""
<div class="score-box">
  <div style="color:#8b949e;font-size:0.75rem">CONTEXT COVERAGE</div>
  <div class="score-number" style="color:#58a6ff">{coverage}%</div>
  <div style="color:#8b949e;font-size:0.75rem">of claims supported</div>
</div>""", unsafe_allow_html=True)

        with c4:
            st.markdown(f"""
<div class="score-box">
  <div style="color:#8b949e;font-size:0.75rem">TRUST VERDICT</div>
  <div style="margin-top:0.5rem;font-size:1rem;font-weight:700;color:{rec_color}">{rec_label}</div>
</div>""", unsafe_allow_html=True)

        # ── Score Breakdown ───────────────────────────────────────────────────
        st.markdown('<div class="section-hdr">🧮 Score Breakdown</div>', unsafe_allow_html=True)
        st.markdown(f"""
<div class="breakdown-box">
  <div class="breakdown-row">
    <span>Starting score</span><span style="color:#3fb950">100</span>
  </div>
  <div class="breakdown-row">
    <span>Contradictions&nbsp;
      <span style="color:#8b949e;font-size:0.8rem">({sbd['contradiction_count']} × −25)</span></span>
    <span style="color:#f85149">{sbd['contradictions_deduction']}</span>
  </div>
  <div class="breakdown-row">
    <span>Unsupported claims&nbsp;
      <span style="color:#8b949e;font-size:0.8rem">({sbd['unsupported_count']} × −10)</span></span>
    <span style="color:#d29922">{sbd['unsupported_deduction']}</span>
  </div>
  <div class="breakdown-row">
    <span>Overconfidence signals&nbsp;
      <span style="color:#8b949e;font-size:0.8rem">({sbd['overconfidence_count']} × −5)</span></span>
    <span style="color:#e3b341">{sbd['overconfidence_deduction']}</span>
  </div>
  <div class="breakdown-row">
    <span>Final Score</span>
    <span style="color:{score_color}">{sbd['final_score']}</span>
  </div>
</div>""", unsafe_allow_html=True)

        # ── Confidence Calibration ────────────────────────────────────────────
        st.markdown('<div class="section-hdr">🎯 Confidence Calibration</div>',
                    unsafe_allow_html=True)
        cal = calibration
        conf_color = "#f85149" if cal["model_confidence"] == "High" else "#3fb950"
        rel_color  = (
            "#3fb950" if cal["actual_reliability"] == "High"
            else "#d29922" if cal["actual_reliability"] == "Medium"
            else "#f85149"
        )
        calib_verdict_color = "#f85149" if cal["is_overconfident"] else "#3fb950"
        st.markdown(f"""
<div class="calibration-box">
  <div class="cal-item">
    <div class="cal-label">Model Confidence</div>
    <div class="cal-value" style="color:{conf_color}">{cal['model_confidence']}</div>
  </div>
  <div class="cal-item">
    <div class="cal-label">Actual Reliability</div>
    <div class="cal-value" style="color:{rel_color}">{cal['actual_reliability']}</div>
  </div>
  <div class="cal-item" style="flex:1;text-align:left;border-left:1px solid #30363d;padding-left:1.5rem">
    <div style="font-size:1rem;font-weight:700;color:{calib_verdict_color}">{cal['label']}</div>
  </div>
</div>""", unsafe_allow_html=True)

        # ── Why This Is Risky + Suggested Action ─────────────────────────────
        re_data = risk_explain
        if re_data["risk_bullets"] and re_data["risk_bullets"] != ["No significant risks identified"]:
            st.markdown('<div class="section-hdr">⚠️ Why This Is Risky</div>',
                        unsafe_allow_html=True)
            bullets_html = "".join(
                f'<span style="color:#ffa198">• {b}</span><br>' for b in re_data["risk_bullets"]
            )
            st.markdown(f'<div class="risk-explain-box">{bullets_html}</div>',
                        unsafe_allow_html=True)

        st.markdown('<div class="section-hdr">💡 Suggested Action</div>',
                    unsafe_allow_html=True)
        action_html = "".join(
            f'<span style="color:#7ee787">• {a}</span><br>' for a in re_data["action_bullets"]
        )
        st.markdown(f'<div class="action-box">{action_html}</div>',
                    unsafe_allow_html=True)

        # ── Multi-pass ────────────────────────────────────────────────────────
        if run_multipass:
            with st.spinner("🔁 Running strict audit pass..."):
                try:
                    strict_result = run_audit(
                        eval_api_key, ctx, q, answer,
                        model_name=model_choice,
                        provider=eval_provider or provider_choice,
                        strict=True,
                        base_url=eval_url,
                    )
                    strict_score = strict_result.get("trust_score", 0)
                    gap = confidence_gap_label(score, strict_score)
                    gap_color = "#f85149" if gap == "High" else "#d29922" if gap == "Medium" else "#3fb950"
                    stability = audit_stability_indicator(score, strict_score)
                    stab_css  = f"stab-{stability['stability']}"

                    st.markdown('<div class="section-hdr">🔁 Multi-Pass Audit</div>',
                                unsafe_allow_html=True)
                    mp1, mp2, mp3, mp4 = st.columns(4)
                    with mp1:
                        st.markdown(f"""
<div class="score-box">
  <div style="color:#8b949e;font-size:0.75rem">NORMAL SCORE</div>
  <div class="score-number" style="color:{score_color}">{score}</div>
</div>""", unsafe_allow_html=True)
                    with mp2:
                        strict_color = "#3fb950" if strict_score >= 80 else "#d29922" if strict_score >= 50 else "#f85149"
                        st.markdown(f"""
<div class="score-box">
  <div style="color:#8b949e;font-size:0.75rem">STRICT SCORE</div>
  <div class="score-number" style="color:{strict_color}">{strict_score}</div>
</div>""", unsafe_allow_html=True)
                    with mp3:
                        st.markdown(f"""
<div class="score-box">
  <div style="color:#8b949e;font-size:0.75rem">CONFIDENCE GAP</div>
  <div style="margin-top:0.5rem;font-size:1.4rem;font-weight:800;color:{gap_color}">{gap}</div>
</div>""", unsafe_allow_html=True)
                    with mp4:
                        st.markdown(f"""
<div class="score-box">
  <div style="color:#8b949e;font-size:0.75rem">AUDIT STABILITY</div>
  <div style="margin-top:0.6rem">
    <span class="stability-badge {stab_css}">{stability['label']}</span>
  </div>
</div>""", unsafe_allow_html=True)
                except Exception as e:
                    st.warning(f"Multi-pass audit failed: {e}")

        # ── Self-consistency ──────────────────────────────────────────────────
        if run_consistency:
            with st.spinner("🔄 Checking internal consistency..."):
                try:
                    cons = check_consistency(
                        api_key, answer,
                        model=model_choice,
                        provider=provider_choice,
                        base_url=ollama_url,
                    )
                    st.markdown('<div class="section-hdr">🔄 Self-Consistency Check</div>',
                                unsafe_allow_html=True)
                    is_c = cons.get("is_consistent")
                    issues = cons.get("issues", [])
                    summary = cons.get("summary", "")
                    cons_color = "#3fb950" if is_c else "#f85149" if is_c is False else "#8b949e"
                    cons_label = "✅ Internally Consistent" if is_c else "❌ Inconsistencies Detected" if is_c is False else "❓ Unknown"
                    st.markdown(f"""
<div class="insight-box">
  <span style="color:{cons_color};font-weight:700">{cons_label}</span><br>
  <span style="color:#8b949e;font-size:0.88rem">{summary}</span>
  {"".join(f'<br><span style="color:#f85149;font-size:0.85rem">• {i}</span>' for i in issues)}
</div>""", unsafe_allow_html=True)
                except Exception as e:
                    st.warning(f"Consistency check failed: {e}")

        # ── Highlighted answer ────────────────────────────────────────────────
        st.markdown('<div class="section-hdr">🎨 Highlighted Answer</div>', unsafe_allow_html=True)
        highlighted = build_highlighted_answer(answer, claims)
        st.markdown(f'<div class="highlight-box">{highlighted}</div>', unsafe_allow_html=True)

        # ── Claims analysis ───────────────────────────────────────────────────
        st.markdown('<div class="section-hdr">🔬 Claims Analysis</div>', unsafe_allow_html=True)

        clf_css   = {"Supported": "clf-Supported", "Not Found": "clf-NotFound", "Contradicts": "clf-Contradicts"}
        lbl_css   = {"Supported": "lbl-Supported", "Not Found": "lbl-NotFound", "Contradicts": "lbl-Contradicts"}
        icon_map  = {"Supported": "✅", "Not Found": "⚠️", "Contradicts": "❌"}

        for i, c in enumerate(claims, 1):
            clf     = c.get("classification", "Not Found")
            icon    = icon_map.get(clf, "❓")
            snippet = c.get("snippet")
            snippet_html = ""
            if show_evidence:
                if snippet and str(snippet).lower() not in ("none", "null", ""):
                    snippet_html = f'<div class="snippet-box">"{snippet}"</div>'
                else:
                    snippet_html = '<div class="snippet-box" style="color:#484f58">No supporting snippet</div>'
            st.markdown(f"""
<div class="claim-card {clf_css.get(clf, '')}">
  <div class="claim-label {lbl_css.get(clf, '')}">{icon} Claim {i} — {clf}</div>
  <div style="color:#e6edf3;margin-bottom:0.35rem"><strong>{c.get('claim', '')}</strong></div>
  <div style="color:#8b949e;font-size:0.87rem">{c.get('reason', '')}</div>
  {snippet_html}
</div>""", unsafe_allow_html=True)

        # ── Overconfidence ────────────────────────────────────────────────────
        if overconf:
            st.markdown('<div class="section-hdr">😤 Overconfidence Signals</div>',
                        unsafe_allow_html=True)
            for oc in overconf:
                st.markdown(f"- {oc}")

        # ── Risky sections ────────────────────────────────────────────────────
        if risky:
            st.markdown('<div class="section-hdr">🚩 Risky Sections</div>', unsafe_allow_html=True)
            pills = "".join(
                f'<span class="tag-pill" style="border-color:#f85149;color:#ffa198;">"{r}"</span>'
                for r in risky
            )
            st.markdown(pills, unsafe_allow_html=True)

        # ── Final verdict ─────────────────────────────────────────────────────
        st.markdown('<div class="section-hdr">⚖️ Final Verdict</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="verdict-box">{verdict}</div>', unsafe_allow_html=True)

        # ── Fix answer ────────────────────────────────────────────────────────
        st.markdown('<div class="section-hdr">🔧 Fix Answer</div>', unsafe_allow_html=True)
        if st.button("✨ Generate Grounded Fix", use_container_width=True):
            with st.spinner("Rewriting answer strictly from context..."):
                try:
                    fixed = fix_answer(
                        api_key, ctx, q, answer,
                        model=model_choice,
                        provider=provider_choice,
                        base_url=ollama_url,
                    )
                    st.markdown(f'<div class="fix-box">{fixed}</div>', unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"❌ Fix failed: {e}")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — COMPARE MODELS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_compare:
    st.markdown("### ⚖️ Side-by-Side Model Comparison")
    st.markdown("Generate and audit the same question with two different models.")

    cmp_ctx = st.text_area("📄 Context", height=160, key="cmp_ctx",
                           placeholder="Paste context...")
    cmp_q   = st.text_area("❓ Question", height=70, key="cmp_q",
                           placeholder="Question...")

    col_a, col_b = st.columns(2)
    
    # Get API key and provider for comparison
    cmp_api_key = st.session_state.get("api_key")
    cmp_provider = st.session_state.get("provider", DEFAULT_PROVIDER)
    cmp_url = st.session_state.get("ollama_url")
    
    with col_a:
        try:
            available_models_a = get_available_models(cmp_provider)
            model_a = st.selectbox(
                f"Model A ({cmp_provider})",
                available_models_a,
                index=0,
                key="model_a"
            )
        except:
            model_a = DEFAULT_MODEL
    with col_b:
        try:
            available_models_b = get_available_models(cmp_provider)
            model_b = st.selectbox(
                f"Model B ({cmp_provider})",
                available_models_b,
                index=min(1, len(available_models_b)-1),
                key="model_b"
            )
        except:
            model_b = DEFAULT_MODEL

    cmp_btn = st.button("🔄 Compare Models", type="primary", use_container_width=True)

    if cmp_btn:
        if not cmp_api_key:
            st.error("🔑 API key required in sidebar.")
            st.stop()
        if not cmp_ctx.strip() or not cmp_q.strip():
            st.warning("Context and Question required.")
            st.stop()

        results = {}
        for label, model in [("A", model_a), ("B", model_b)]:
            with st.spinner(f"Running Model {label} ({model})..."):
                try:
                    ans = generate_answer(
                        cmp_api_key, cmp_ctx, cmp_q,
                        model=model,
                        provider=cmp_provider,
                        base_url=cmp_url,
                    )
                    audit = run_audit(
                        cmp_api_key, cmp_ctx, cmp_q, ans,
                        model_name=model,
                        provider=cmp_provider,
                        base_url=cmp_url,
                    )
                    results[label] = {"model": model, "answer": ans, "audit": audit}
                except Exception as e:
                    st.error(f"Model {label} failed: {e}")

        if len(results) == 2:
            col_a2, col_b2 = st.columns(2)
            for col, label in [(col_a2, "A"), (col_b2, "B")]:
                r = results[label]
                audit = r["audit"]
                score = audit.get("trust_score", 0)
                risk  = audit.get("hallucination_risk", "High")
                cov   = compute_context_coverage(audit.get("claims", []))
                s_col = "#3fb950" if score >= 80 else "#d29922" if score >= 50 else "#f85149"
                with col:
                    st.markdown(f"""
<div class="compare-col">
  <div style="color:#8b949e;font-size:0.8rem;margin-bottom:0.5rem">MODEL {label}: {r['model']}</div>
  <div style="color:#e6edf3;margin-bottom:0.8rem;font-size:0.9rem">{r['answer']}</div>
  <div style="display:flex;gap:1rem;flex-wrap:wrap;">
    <div><span style="color:#8b949e;font-size:0.75rem">SCORE</span><br>
         <span style="font-size:1.8rem;font-weight:800;color:{s_col}">{score}</span></div>
    <div><span style="color:#8b949e;font-size:0.75rem">RISK</span><br>
         <span class="risk-badge risk-{risk}" style="margin-top:0.3rem;display:inline-block">{risk}</span></div>
    <div><span style="color:#8b949e;font-size:0.75rem">COVERAGE</span><br>
         <span style="font-size:1.8rem;font-weight:800;color:#58a6ff">{cov}%</span></div>
  </div>
  <div style="margin-top:0.8rem;color:#8b949e;font-size:0.82rem;font-style:italic">
    {audit.get('final_verdict','')}
  </div>
</div>""", unsafe_allow_html=True)

            # Difference callout
            diff = results["A"]["audit"]["trust_score"] - results["B"]["audit"]["trust_score"]
            winner = "A" if diff > 0 else "B" if diff < 0 else None
            if winner:
                st.info(
                    f"Model {winner} scored {abs(diff)} points higher. "
                    f"({results[winner]['model']})"
                )
            else:
                st.info("Both models scored equally.")


# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — ADVERSARIAL TEST
# ═══════════════════════════════════════════════════════════════════════════════
with tab_adversarial:
    st.markdown("### 🧨 Adversarial Testing Mode")
    st.markdown(
        "Generates a *convincing but subtly incorrect* answer, then audits it. "
        "Useful for stress-testing the auditor."
    )

    adv_ctx = st.text_area("📄 Context", height=160, key="adv_ctx",
                           placeholder="Paste context...")
    adv_q   = st.text_area("❓ Question", height=70, key="adv_q",
                           placeholder="Question...")

    adv_btn = st.button("🎯 Generate Misleading Answer & Audit", type="primary",
                        use_container_width=True)

    if adv_btn:
        # Get values from session state
        adv_api_key = st.session_state.get("api_key")
        adv_model = st.session_state.get("model", DEFAULT_MODEL)
        adv_provider = st.session_state.get("provider", DEFAULT_PROVIDER)
        adv_url = st.session_state.get("ollama_url")
        
        # Evaluation provider
        eval_provider_adv = st.session_state.get("eval_provider", adv_provider)
        eval_api_key_adv = st.session_state.get("eval_api_key", adv_api_key)
        eval_url_adv = st.session_state.get("eval_url", adv_url)
        
        if not adv_api_key:
            st.error("🔑 API key required in sidebar.")
            st.stop()
        if not adv_ctx.strip() or not adv_q.strip():
            st.warning("Context and Question required.")
            st.stop()

        with st.spinner("🎭 Generating misleading answer..."):
            try:
                misleading = generate_misleading_answer(
                    adv_api_key, adv_ctx, adv_q,
                    model=adv_model,
                    provider=adv_provider,
                    base_url=adv_url,
                )
            except Exception as e:
                st.error(f"❌ Generation failed: {e}")
                st.stop()

        st.markdown('<div class="section-hdr">🎭 Misleading Answer</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="insight-box" style="border-color:#f85149;color:#ffa198;">'
            f'{misleading}</div>',
            unsafe_allow_html=True,
        )

        with st.spinner("🔬 Auditing misleading answer..."):
            try:
                adv_result = run_audit(
                    eval_api_key_adv, adv_ctx, adv_q, misleading,
                    model_name=adv_model,
                    provider=eval_provider_adv or adv_provider,
                    strict=True,
                    base_url=eval_url_adv,
                )
            except Exception as e:
                st.error(f"❌ Audit failed: {e}")
                st.stop()

        adv_claims  = adv_result.get("claims", [])
        adv_score   = adv_result.get("trust_score", 0)
        adv_risk    = adv_result.get("hallucination_risk", "High")
        adv_verdict = adv_result.get("final_verdict", "")
        adv_cov     = compute_context_coverage(adv_claims)

        st.markdown('<div class="section-hdr">📊 Adversarial Audit Results</div>',
                    unsafe_allow_html=True)

        a1, a2, a3 = st.columns(3)
        a_color = "#3fb950" if adv_score >= 80 else "#d29922" if adv_score >= 50 else "#f85149"
        with a1:
            st.markdown(f"""
<div class="score-box">
  <div style="color:#8b949e;font-size:0.75rem">TRUST SCORE</div>
  <div class="score-number" style="color:{a_color}">{adv_score}</div>
</div>""", unsafe_allow_html=True)
        with a2:
            st.markdown(f"""
<div class="score-box">
  <div style="color:#8b949e;font-size:0.75rem">RISK</div>
  <div style="margin-top:0.5rem">
    <span class="risk-badge risk-{adv_risk}">{adv_risk.upper()}</span>
  </div>
</div>""", unsafe_allow_html=True)
        with a3:
            st.markdown(f"""
<div class="score-box">
  <div style="color:#8b949e;font-size:0.75rem">COVERAGE</div>
  <div class="score-number" style="color:#58a6ff">{adv_cov}%</div>
</div>""", unsafe_allow_html=True)

        st.markdown('<div class="section-hdr">🎨 Highlighted Misleading Answer</div>',
                    unsafe_allow_html=True)
        st.markdown(
            f'<div class="highlight-box">{build_highlighted_answer(misleading, adv_claims)}</div>',
            unsafe_allow_html=True,
        )

        st.markdown('<div class="section-hdr">⚖️ Verdict</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="verdict-box">{adv_verdict}</div>', unsafe_allow_html=True)
