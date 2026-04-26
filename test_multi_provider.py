#!/usr/bin/env python
"""
test_multi_provider.py — Test script for multi-provider support
Run without API keys using the Mock provider
Usage: python test_multi_provider.py
"""

import sys
from model_provider import get_provider, get_available_models, SUPPORTED_PROVIDERS, GenerateConfig


def test_mock_provider():
    """Test the mock provider (requires no API keys)."""
    print("\n" + "="*70)
    print("🧪 TEST 1: Mock Provider (No API Keys Needed)")
    print("="*70)
    
    try:
        provider = get_provider("mock")
        print("✅ Mock provider initialized successfully")
        
        # Test available models
        models = get_available_models("mock")
        print(f"✅ Available mock models: {models}")
        
        # Test generation
        config = GenerateConfig(temperature=0.1, max_output_tokens=100)
        response = provider.generate_content(
            "mock-standard",
            "Answer the question using ONLY the provided context: What is 2+2?",
            config
        )
        print(f"✅ Mock generation response:\n   {response[:100]}...\n")
        
        # Test audit response
        response = provider.generate_content(
            "mock-standard",
            "You are a hallucination auditor. Evaluate this answer.",
            config
        )
        print(f"✅ Mock audit response (JSON):\n   {response[:150]}...\n")
        
        return True
    except Exception as e:
        print(f"❌ Mock provider test failed: {e}")
        return False


def test_provider_abstraction():
    """Test that all providers are registered."""
    print("\n" + "="*70)
    print("🧪 TEST 2: Provider Registration")
    print("="*70)
    
    print(f"✅ Supported providers: {SUPPORTED_PROVIDERS}")
    
    for provider_name in SUPPORTED_PROVIDERS:
        try:
            if provider_name in ["openai", "anthropic", "gemini"]:
                print(f"   ⏭️  {provider_name.capitalize()}: Skipped (requires API key)")
            elif provider_name == "ollama":
                print(f"   ⏭️  {provider_name.capitalize()}: Skipped (requires local service)")
            elif provider_name == "mock":
                models = get_available_models(provider_name)
                print(f"   ✅ {provider_name.capitalize()}: {len(models)} mock models available")
        except Exception as e:
            print(f"   ❌ {provider_name.capitalize()}: {e}")
    
    return True


def test_auditor_integration():
    """Test that auditor module works with mock provider."""
    print("\n" + "="*70)
    print("🧪 TEST 3: Auditor Integration with Mock Provider")
    print("="*70)
    
    try:
        from auditor import generate_answer, run_audit, DEFAULT_PROVIDER, DEFAULT_MODEL
        
        print(f"✅ Auditor module imported successfully")
        print(f"   Default provider: {DEFAULT_PROVIDER}")
        print(f"   Default model: {DEFAULT_MODEL}")
        
        # Test with mock provider
        context = "The Eiffel Tower was built in 1889 and is located in Paris."
        question = "When was the Eiffel Tower built?"
        
        print(f"\n📝 Testing with mock provider...")
        answer = generate_answer(
            api_key="mock-key",
            context=context,
            question=question,
            model="mock-standard",
            provider="mock",
        )
        print(f"✅ Generated answer:\n   {answer[:80]}...\n")
        
        # Test audit
        audit_result = run_audit(
            api_key="mock-key",
            context=context,
            question=question,
            answer=answer,
            model_name="mock-standard",
            provider="mock",
            strict=False,
        )
        print(f"✅ Audit result:")
        print(f"   Trust Score: {audit_result.get('trust_score', 'N/A')}")
        print(f"   Risk Level: {audit_result.get('hallucination_risk', 'N/A')}")
        print(f"   Claims Count: {len(audit_result.get('claims', []))}\n")
        
        return True
    except Exception as e:
        print(f"❌ Auditor integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_gemini_if_available():
    """Test Gemini provider if API key is set in environment."""
    print("\n" + "="*70)
    print("🧪 TEST 4: Gemini Provider (If API Key Available)")
    print("="*70)
    
    import os
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("⏭️  Gemini API key not found in environment variables")
        print("   Set GOOGLE_API_KEY or GEMINI_API_KEY to test Gemini\n")
        return None
    
    try:
        provider = get_provider("gemini", api_key=api_key)
        print(f"✅ Gemini provider initialized successfully")
        
        models = get_available_models("gemini")
        print(f"✅ Available Gemini models: {models}")
        
        config = GenerateConfig(temperature=0.1, max_output_tokens=50)
        response = provider.generate_content(
            "gemini-2.5-flash",
            "Answer in one sentence: What is 2+2?",
            config
        )
        print(f"✅ Gemini response: {response}\n")
        
        return True
    except Exception as e:
        print(f"❌ Gemini provider test failed: {e}")
        print(f"   This is expected if the API key is invalid or quota exceeded\n")
        return False


def main():
    """Run all tests."""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "🛡️  TruthLens Multi-Provider Test Suite" + " "*13 + "║")
    print("╚" + "="*68 + "╝")
    
    results = {
        "Mock Provider": test_mock_provider(),
        "Provider Registration": test_provider_abstraction(),
        "Auditor Integration": test_auditor_integration(),
        "Gemini Provider": test_gemini_if_available(),
    }
    
    print("\n" + "="*70)
    print("📊 TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for r in results.values() if r is True)
    skipped = sum(1 for r in results.values() if r is None)
    failed = sum(1 for r in results.values() if r is False)
    
    for name, result in results.items():
        status = "✅ PASS" if result is True else "⏭️  SKIP" if result is None else "❌ FAIL"
        print(f"{status:12} {name}")
    
    print("="*70)
    print(f"Results: {passed} passed, {skipped} skipped, {failed} failed\n")
    
    if failed == 0:
        print("🎉 All critical tests passed! Multi-provider system is working.\n")
        return 0
    else:
        print("⚠️  Some tests failed. Check the output above.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
