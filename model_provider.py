"""
model_provider.py — Unified interface for multiple AI model providers
Supports: Google Gemini, OpenAI (GPT), Anthropic (Claude), Ollama
"""

from abc import ABC, abstractmethod
from typing import Optional
import os


class GenerateConfig:
    """Unified config for text generation across providers."""
    def __init__(self, temperature: float = 0.1, max_output_tokens: int = 4096):
        self.temperature = temperature
        self.max_output_tokens = max_output_tokens


class ModelProvider(ABC):
    """Base class for all AI model providers."""

    @abstractmethod
    def generate_content(
        self,
        model: str,
        prompt: str,
        config: GenerateConfig,
    ) -> str:
        """Generate content using the specified model and configuration."""
        pass

    @abstractmethod
    def validate_api_key(self) -> bool:
        """Validate that the API key is properly configured."""
        pass


class GeminiProvider(ModelProvider):
    """Google Gemini API provider."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from google import genai
            from google.genai import types
            self._types = types
            self._client = genai.Client(api_key=self.api_key)
        return self._client

    def generate_content(
        self,
        model: str,
        prompt: str,
        config: GenerateConfig,
    ) -> str:
        from google.genai import types
        cfg = types.GenerateContentConfig(
            temperature=config.temperature,
            max_output_tokens=config.max_output_tokens,
        )
        response = self.client.models.generate_content(
            model=model,
            contents=prompt,
            config=cfg,
        )
        return response.text.strip()

    def validate_api_key(self) -> bool:
        try:
            from google import genai
            client = genai.Client(api_key=self.api_key)
            # Try a simple call to validate
            client.models.list()
            return True
        except Exception:
            return False

    @staticmethod
    def get_available_models() -> list[str]:
        """Return list of available Gemini models."""
        return [
            "gemini-2.5-flash",
            "gemini-2.5-pro",
            "gemini-2.0-flash",
            "gemini-2.0-flash-lite",
            "gemini-1.5-pro",
            "gemini-1.5-flash",
        ]


class OpenAIProvider(ModelProvider):
    """OpenAI API provider."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from openai import OpenAI
            self._client = OpenAI(api_key=self.api_key)
        return self._client

    def generate_content(
        self,
        model: str,
        prompt: str,
        config: GenerateConfig,
    ) -> str:
        response = self.client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=config.temperature,
            max_tokens=config.max_output_tokens,
        )
        return response.choices[0].message.content.strip()

    def validate_api_key(self) -> bool:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            # Try a simple call to validate
            client.models.list()
            return True
        except Exception:
            return False

    @staticmethod
    def get_available_models() -> list[str]:
        """Return list of available OpenAI models."""
        return [
            "gpt-4o",
            "gpt-4-turbo",
            "gpt-4",
            "gpt-3.5-turbo",
        ]


class AnthropicProvider(ModelProvider):
    """Anthropic Claude API provider."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from anthropic import Anthropic
            self._client = Anthropic(api_key=self.api_key)
        return self._client

    def generate_content(
        self,
        model: str,
        prompt: str,
        config: GenerateConfig,
    ) -> str:
        message = self.client.messages.create(
            model=model,
            max_tokens=config.max_output_tokens,
            system="You are a helpful assistant.",
            messages=[
                {"role": "user", "content": prompt},
            ],
            temperature=config.temperature,
        )
        return message.content[0].text.strip()

    def validate_api_key(self) -> bool:
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=self.api_key)
            # Try a simple call to validate
            client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1,
                messages=[{"role": "user", "content": "test"}],
            )
            return True
        except Exception:
            return False

    @staticmethod
    def get_available_models() -> list[str]:
        """Return list of available Claude models."""
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20250219",
        ]


class OllamaProvider(ModelProvider):
    """Local Ollama API provider."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self._client = None

    @property
    def client(self):
        if self._client is None:
            from ollama import Client
            self._client = Client(host=self.base_url)
        return self._client

    def generate_content(
        self,
        model: str,
        prompt: str,
        config: GenerateConfig,
    ) -> str:
        response = self.client.generate(
            model=model,
            prompt=prompt,
            temperature=config.temperature,
            stream=False,
        )
        return response.get("response", "").strip()

    def validate_api_key(self) -> bool:
        try:
            from ollama import Client
            client = Client(host=self.base_url)
            # Try to list models to validate connection
            client.list()
            return True
        except Exception:
            return False

    @staticmethod
    def get_available_models() -> list[str]:
        """Return list of commonly available Ollama models."""
        return [
            "llama2",
            "mistral",
            "neural-chat",
            "starling-lm",
            "openhermes",
        ]


# ── Provider Factory ──────────────────────────────────────────────────────────

def get_provider(
    provider_name: str,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
) -> ModelProvider:
    """
    Factory function to get the appropriate model provider.

    Args:
        provider_name: One of "gemini", "openai", "anthropic", "ollama", "mock"
        api_key: API key for the provider
        base_url: Base URL for Ollama or custom endpoints

    Returns:
        An instance of the appropriate ModelProvider

    Raises:
        ValueError: If provider is not recognized
    """
    provider_name = provider_name.lower()

    if provider_name == "gemini":
        if not api_key:
            raise ValueError("Gemini provider requires api_key")
        return GeminiProvider(api_key)

    elif provider_name == "openai":
        if not api_key:
            raise ValueError("OpenAI provider requires api_key")
        return OpenAIProvider(api_key)

    elif provider_name == "anthropic":
        if not api_key:
            raise ValueError("Anthropic provider requires api_key")
        return AnthropicProvider(api_key)

    elif provider_name == "ollama":
        return OllamaProvider(base_url=base_url or "http://localhost:11434")

    elif provider_name == "mock":
        return MockProvider()

    else:
        raise ValueError(
            f"Unknown provider: {provider_name}. "
            "Supported: gemini, openai, anthropic, ollama, mock"
        )


def get_available_models(provider_name: str) -> list[str]:
    """Get list of available models for a given provider."""
    provider_name = provider_name.lower()

    if provider_name == "gemini":
        return GeminiProvider.get_available_models()
    elif provider_name == "openai":
        return OpenAIProvider.get_available_models()
    elif provider_name == "anthropic":
        return AnthropicProvider.get_available_models()
    elif provider_name == "ollama":
        return OllamaProvider.get_available_models()
    elif provider_name == "mock":
        return MockProvider.get_available_models()
    else:
        raise ValueError(f"Unknown provider: {provider_name}")


class MockProvider(ModelProvider):
    """Mock provider for testing without API keys."""

    def __init__(self):
        pass

    def generate_content(
        self,
        model: str,
        prompt: str,
        config: GenerateConfig,
    ) -> str:
        # Simulate different responses based on prompt content
        if "Answer the question" in prompt or "answer using" in prompt.lower():
            return "This is a mock generated answer based on the provided context. It demonstrates that the system works without real API calls."
        elif "hallucination" in prompt.lower() or "audit" in prompt.lower():
            return """{
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
  "final_verdict": "Mock audit: This answer appears mostly reliable based on the provided context."
}"""
        elif "misleading" in prompt.lower():
            return "The Eiffel Tower was completed in 1885 and stands 340 metres tall."
        elif "consistency" in prompt.lower():
            return """{
  "is_consistent": true,
  "issues": [],
  "summary": "Mock: Answer is internally consistent."
}"""
        elif "rewrite" in prompt.lower() or "fix" in prompt.lower():
            return "Mock fixed answer: The information has been grounded in the provided context."
        else:
            return f"Mock response to: {prompt[:100]}..."

    def validate_api_key(self) -> bool:
        return True

    @staticmethod
    def get_available_models() -> list[str]:
        """Return list of mock models."""
        return [
            "mock-fast",
            "mock-standard",
            "mock-detailed",
        ]


SUPPORTED_PROVIDERS = ["gemini", "openai", "anthropic", "ollama", "mock"]
