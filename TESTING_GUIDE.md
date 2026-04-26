# 🧪 Testing Guide — Multi-Provider TruthLens

You can test TruthLens **right now without API keys** using the Mock provider. Here are your options:

---

## 🚀 Option 1: Test with Mock Provider (No API Keys!)

The **Mock provider** simulates all LLM functionality without making real API calls. Perfect for development and testing.

### Run the Test Suite

```bash
python test_multi_provider.py
```

**Output:**
```
✅ Mock provider initialized successfully
✅ Available mock models: ['mock-fast', 'mock-standard', 'mock-detailed']
✅ Auditor integration works
✅ All critical tests passed!
```

### Use Mock Provider in the UI

1. Run: `streamlit run app.py`
2. In sidebar:
   - **Provider**: Select `mock`
   - **Model**: Choose any (they're all mock)
   - **API Key**: Enter any text (not validated)
3. Test all features!

**What it simulates:**
- ✅ Answer generation
- ✅ Hallucination auditing (returns realistic JSON)
- ✅ Misleading answer generation
- ✅ Consistency checking
- ✅ Answer fixing

---

## 💡 Option 2: Test with Gemini (If You Have Key)

If you have a **Google Gemini API key**, set it as an environment variable:

### Windows (PowerShell)
```powershell
$env:GOOGLE_API_KEY = "your-api-key-here"
python test_multi_provider.py
```

### Mac/Linux (Bash)
```bash
export GOOGLE_API_KEY="your-api-key-here"
python test_multi_provider.py
```

Then in Streamlit:
1. Provider: `gemini`
2. API Key: Paste your Gemini key
3. Test!

---

## 🦙 Option 3: Free Local Models with Ollama

**Ollama** lets you run open-source models locally — **completely free, no API key needed**.

### Install & Run Ollama

1. [Download Ollama](https://ollama.ai/)
2. Install and start it
3. Pull a model:
   ```bash
   ollama pull mistral
   # or
   ollama pull llama2
   ```
4. Ollama will run on `http://localhost:11434`

### Use in TruthLens

In Streamlit sidebar:
- **Provider**: `ollama`
- **Ollama Base URL**: `http://localhost:11434` (default)
- **Model**: `mistral` or `llama2` (or any you've pulled)
- No API key needed!

### Available Models (Free)

| Model | Size | Speed | Quality |
|-------|------|-------|---------|
| `mistral` | 4.1 GB | ⚡ Fast | 🟢 Good |
| `llama2` | 3.8 GB | ⚡ Fast | 🟢 Good |
| `neural-chat` | 4.1 GB | ⚡ Fast | 🟢 Good |
| `openchat` | 3.8 GB | ⚡ Fast | 🟢 Good |

---

## 🧪 Scenario-Based Testing

### Scenario 1: Full End-to-End Test (No API Keys)

```bash
python test_multi_provider.py
# ✅ All tests pass with mock provider
```

### Scenario 2: Test Audit Tab (Mock)

```bash
streamlit run app.py
# In sidebar: Provider=mock, Model=mock-standard
# Paste any context and question
# Click "Generate & Audit" → See mock results
```

### Scenario 3: Compare Models (Local)

```bash
# Terminal 1: Start Ollama
ollama run mistral

# Terminal 2: Start TruthLens
streamlit run app.py
# In sidebar: Provider=ollama, Model=mistral
# Use Compare tab to test same question multiple times
```

### Scenario 4: Dual-Provider Setup

```bash
streamlit run app.py
# Main provider: mock (for testing)
# Evaluation provider: mock (no API keys needed)
# Test all functionality!
```

---

## 📝 Test Cases

### Test Case 1: Basic Generation

```
Context: "Paris is the capital of France."
Question: "What is the capital of France?"
Provider: mock
Expected: Mock answer generated ✅
```

### Test Case 2: Hallucination Detection

```
Context: "The Eiffel Tower is in Paris."
Question: "Where is the Eiffel Tower?"
Provider: mock
Expected: Audit returns trust score and claims ✅
```

### Test Case 3: Model Comparison

```
Use Compare tab with mock provider
Model A: mock-fast
Model B: mock-standard
Expected: See side-by-side results ✅
```

### Test Case 4: Adversarial Testing

```
Use Adversarial Test tab with mock
Expected: See mock misleading answer ✅
```

---

## 🎯 When to Use Each Provider for Testing

| Use Case | Recommended | Why |
|----------|-------------|-----|
| **Quick UI testing** | Mock | Instant, no setup, no cost |
| **Full functionality test** | Mock | All features work identically |
| **Real LLM behavior** | Gemini (if you have key) | Actual AI responses |
| **No internet needed** | Ollama | Runs locally, fully private |
| **Cost-sensitive testing** | Ollama or Mock | Free |
| **Production-like testing** | Gemini or OpenAI | Real API behavior |

---

## 🚀 Quick Start Commands

### Test Everything with Mock (Recommended)

```bash
# Run test suite
python test_multi_provider.py

# Launch UI with mock
streamlit run app.py
# Select "mock" in sidebar
```

### Test with Ollama (Free, Local)

```bash
# Install: https://ollama.ai/
ollama pull mistral
ollama run mistral

# In another terminal:
streamlit run app.py
# Select "ollama" in sidebar, model "mistral"
```

### Test with Your Gemini Key

```bash
# Set environment variable
$env:GOOGLE_API_KEY = "your-key"

# Run tests
python test_multi_provider.py

# Or launch UI
streamlit run app.py
# Select "gemini" in sidebar
```

---

## ✅ Validation Checklist

After testing, verify:

- [ ] Mock provider works without API keys
- [ ] Test suite passes
- [ ] Streamlit UI launches
- [ ] All tabs work (Audit, Compare, Adversarial)
- [ ] Mock models appear in dropdown
- [ ] Can generate mock answers
- [ ] Mock audits return JSON correctly
- [ ] No errors in console

---

## 🐛 Troubleshooting

### "Could not parse audit JSON"
- **Cause**: Response format incorrect
- **Fix**: Try with mock provider, check JSON format

### "Module not found: anthropic"
- **Cause**: Optional dependencies not installed
- **Fix**: You don't need them! Mock provider works without any API SDKs

### "Connection refused" (Ollama)
- **Cause**: Ollama not running
- **Fix**: Run `ollama run mistral` in another terminal first

### "Streamlit not found"
- **Cause**: streamlit not installed
- **Fix**: `pip install streamlit`

---

## 🎓 Learning Path

1. **First**: Run `python test_multi_provider.py` ← Validates setup
2. **Second**: `streamlit run app.py` with mock ← UI familiarization
3. **Third**: Try Ollama if you want real models
4. **Fourth**: Add real API keys (Gemini, OpenAI, etc.) when ready

---

## 📊 What Mock Provider Returns

### Generation Request
```
"This is a mock generated answer based on the provided context."
```

### Audit Request
```json
{
  "claims": [
    {
      "claim": "The Eiffel Tower is in Paris",
      "classification": "Supported",
      "reason": "Mentioned in context",
      "snippet": "located in Paris, France"
    }
  ],
  "trust_score": 85,
  "hallucination_risk": "Low",
  "overconfidence_issues": [],
  "risky_sections": [],
  "final_verdict": "Mock audit: Answer appears reliable."
}
```

### Misleading Generation
```
"The Eiffel Tower was completed in 1885 and stands 340 metres tall."
```

### Consistency Check
```json
{
  "is_consistent": true,
  "issues": [],
  "summary": "Mock: Answer is internally consistent."
}
```

---

## 🚀 Next Steps

✅ Run the test suite right now:
```bash
python test_multi_provider.py
```

✅ Then launch the UI:
```bash
streamlit run app.py
```

✅ Select **"mock"** in the Provider dropdown

✅ Try all features with mock provider

✅ Once confident, add real API keys for one provider

---

**Happy testing! 🛡️**
