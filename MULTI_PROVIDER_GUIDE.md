# 🤖 Multi-Provider Support Guide

TruthLens now supports **multiple AI model providers** for generating answers. You can use your choice of AI models from different providers and test them within TruthLens.

## 📋 Supported Providers

| Provider | Models | Setup |
|----------|--------|-------|
| **Google Gemini** | `gemini-2.5-flash`, `gemini-2.5-pro`, `gemini-2.0-flash`, `gemini-1.5-pro` | [Get API Key](https://aistudio.google.com/) |
| **OpenAI** | `gpt-4o`, `gpt-4-turbo`, `gpt-4`, `gpt-3.5-turbo` | [Get API Key](https://platform.openai.com/api-keys) |
| **Anthropic Claude** | `claude-3-5-sonnet-20241022`, `claude-3-5-haiku-20241022`, `claude-3-opus-20250219` | [Get API Key](https://console.anthropic.com/) |
| **Ollama (Local)** | `llama2`, `mistral`, `neural-chat`, `starling-lm`, `openhermes` | [Run Ollama](https://ollama.ai/) locally |

---

## 🚀 Getting Started

### 1. Install Dependencies

Install the provider SDKs you plan to use:

```bash
# For OpenAI
pip install openai>=1.0.0

# For Anthropic
pip install anthropic>=0.7.0

# For Ollama (optional, for local models)
pip install ollama>=0.0.30

# Or install all at once
pip install -r requirements.txt
```

### 2. Launch TruthLens

```bash
streamlit run app.py
```

### 3. Configure Your Provider

In the **⚙️ Configuration** sidebar:

1. **Select Provider**: Choose from `gemini`, `openai`, `anthropic`, or `ollama`
2. **Enter API Key**: Provide your API key (hidden input for security)
3. **Select Model**: Choose from available models for the selected provider
4. **Optional - Evaluation Provider**: If you want to use a different provider for auditing answers

---

## 💡 Usage Examples

### Example 1: Generate with GPT-4, Evaluate with Gemini

```
Sidebar Configuration:
  - Provider: openai
  - API Key: sk-...
  - Model: gpt-4o
  - Use different provider for evaluation: ✓
    - Evaluation Provider: gemini
    - Evaluation API Key: AIza...
```

In this setup:
- **Generate step** uses OpenAI GPT-4o
- **Audit step** uses Google Gemini (your evaluation model)
- You can compare how different models evaluate answers

### Example 2: Local Ollama Model

```
Sidebar Configuration:
  - Provider: ollama
  - Ollama Base URL: http://localhost:11434
  - Model: mistral
```

Prerequisites:
```bash
# Run Ollama locally (requires Ollama installed)
ollama run mistral
```

### Example 3: Multi-Model Comparison

Use the **⚖️ Compare Models** tab to test two models from the same provider:

```
Main Config:
  - Provider: openai
  - Model: gpt-4o
  
Compare Tab:
  - Model A: gpt-4o
  - Model B: gpt-3.5-turbo
```

---

## 🔑 Getting API Keys

### Google Gemini
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Click "Get API key" in the left sidebar
3. Create a new API key
4. Copy and paste into TruthLens

### OpenAI
1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Sign in to your account
3. Click "Create new secret key"
4. Copy and paste into TruthLens

### Anthropic Claude
1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Navigate to API keys section
3. Create a new key
4. Copy and paste into TruthLens

### Ollama (Local - No API Key Needed)
1. [Install Ollama](https://ollama.ai/)
2. Run: `ollama run <model-name>` (e.g., `ollama run mistral`)
3. Use base URL: `http://localhost:11434`

---

## 🔄 Dual API Key Setup

**Scenario**: Generate answers with your own OpenAI key, but evaluate with a Gemini key you control.

In the sidebar:
1. **Main Provider** (for generation):
   - Provider: `openai`
   - API Key: Your OpenAI API key

2. **Separate Evaluation Provider** (optional):
   - Enable: "Use different provider for evaluation"
   - Evaluation Provider: `gemini`
   - Evaluation API Key: Your Gemini API key

**Benefit**: Separate cost tracking and model control for generation vs. evaluation.

---

## ⚙️ Architecture

### New Files

- **`model_provider.py`**: Unified abstraction layer for all providers
  - `GenerateConfig`: Unified configuration (temperature, max tokens)
  - `ModelProvider`: Base class for all providers
  - `GeminiProvider`, `OpenAIProvider`, `AnthropicProvider`, `OllamaProvider`: Provider implementations
  - `get_provider()`: Factory function to instantiate providers

### Updated Files

- **`auditor.py`**: 
  - Now accepts `provider` and `base_url` parameters
  - Uses provider abstraction instead of hardcoded Gemini SDK
  - All functions (generate_answer, run_audit, fix_answer, etc.) support multi-provider

- **`app.py`**:
  - Enhanced sidebar with provider selection
  - Dynamic model list based on selected provider
  - Optional separate evaluation provider
  - All tabs (Audit, Compare, Adversarial) support multi-provider

---

## 🛠️ Advanced: Custom Provider Implementation

To add a new provider, create a new class in `model_provider.py`:

```python
class MyProvider(ModelProvider):
    def __init__(self, api_key: str):
        self.api_key = api_key

    def generate_content(
        self,
        model: str,
        prompt: str,
        config: GenerateConfig,
    ) -> str:
        # Your implementation here
        pass

    def validate_api_key(self) -> bool:
        # Test if API key is valid
        pass

    @staticmethod
    def get_available_models() -> list[str]:
        return ["model-1", "model-2"]
```

Then register it in `get_provider()`:

```python
elif provider_name == "myprovider":
    return MyProvider(api_key)
```

---

## 📊 Comparison: Provider Costs & Speed

| Provider | Cost (Typical) | Speed | Best For |
|----------|---|---|---|
| **Gemini** | ~$0.075/1M tokens | ⚡ Fast | Research, experimentation |
| **OpenAI GPT-4** | ~$30/1M tokens | Medium | Production, accuracy |
| **Claude 3.5 Sonnet** | ~$3/1M tokens | Medium | Balanced performance |
| **Ollama Local** | $0 | Variable | Privacy, offline usage |

---

## ⚠️ Troubleshooting

### "Could not parse audit JSON"
- **Cause**: Model didn't return valid JSON
- **Fix**: Try a different model or provider; some models have formatting issues

### "API key invalid"
- **Cause**: Wrong API key or no permission
- **Fix**: Double-check your key; ensure the API is enabled in your account

### Ollama "Connection refused"
- **Cause**: Ollama service not running
- **Fix**: Start Ollama with `ollama run <model>`

### "Model not found"
- **Cause**: Model isn't available for the selected provider
- **Fix**: Check model list in sidebar; pull model with `ollama pull <name>` if using Ollama

---

## 🎯 Best Practices

1. **Use Gemini for evaluation** - It's most cost-effective for the auditing step
2. **Test multiple models** - Use the Compare tab to see how different models perform
3. **Monitor costs** - Different providers have different pricing; track usage
4. **Validate API keys** - Set up once, then test with a simple question first
5. **Use Ollama for privacy** - If you're testing sensitive documents, run Ollama locally

---

## 📝 Example Workflow

```
1. Set Provider to "openai", Model to "gpt-4o"
2. Enter your OpenAI API key
3. Paste context and question
4. Click "Generate & Audit"
   ↓
5. OpenAI generates answer
6. Gemini audits answer (if using separate eval provider)
7. View results: trust score, claims breakdown, highlighted answer
8. Use "Compare Models" to test gpt-3.5-turbo on same question
```

---

## 🚀 Next Steps

- Try different providers to compare quality
- Experiment with the Adversarial Test tab
- Use Multi-Pass Audit for comprehensive analysis
- Share findings and model comparisons

Happy auditing! 🛡️
