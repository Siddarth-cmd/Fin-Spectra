import sys
from unittest.mock import patch, MagicMock
from app.config import settings
import app.agents.llm_client as llm_client_module
from app.agents.llm_client import LLMClient

def test_llm_client_reliability():
    print("=" * 70)
    print(" 🧪 TESTING LLM CLIENT RELIABILITY & PRODUCTION MOCK GUARD")
    print("=" * 70)

    # 1. Test Production + Missing API Key -> RuntimeError
    print(" -> Testing Production Guard on Missing/Placeholder API Key...")
    with patch.object(settings, "env", "production"), patch.object(settings, "groq_api_key", "gsk_placeholder"):
        caught = False
        try:
            LLMClient()
        except RuntimeError as exc:
            caught = True
            assert "Cannot run in mock mode in production" in str(exc)
        assert caught, "Production mode failed to raise RuntimeError on missing API key!"
        print("   ✓ Production mode explicitly raised RuntimeError as expected!")

    # 2. Test Development + Missing API Key -> Mock Mode Works
    print("\n -> Testing Development Mode Mock Fallback...")
    with patch.object(settings, "env", "development"), patch.object(settings, "groq_api_key", "gsk_placeholder"):
        client = LLMClient()
        assert client.mock_mode is True
        res = client.generate("typology system prompt", "user prompt")
        assert "LAYERING" in res
        print("   ✓ Development mode seamlessly uses mock mode!")

    # 3. Test Groq Client Timeout & Max Retries Configuration
    print("\n -> Testing Groq Client Initialization Parameters (timeout=20.0, max_retries=3)...")
    mock_groq_cls = MagicMock()
    with patch.object(settings, "env", "development"), \
         patch.object(settings, "groq_api_key", "gsk_valid_test_key_12345"), \
         patch.object(llm_client_module, "HAS_GROQ", True), \
         patch.object(llm_client_module, "Groq", mock_groq_cls, create=True):
        
        client = LLMClient()
        mock_groq_cls.assert_called_once_with(
            api_key="gsk_valid_test_key_12345",
            timeout=20.0,
            max_retries=3
        )
        print("   ✓ Groq client initialized with timeout=20.0 and max_retries=3!")

    # 4. Test Configurable max_tokens Pass-through
    print("\n -> Testing Configurable max_tokens Pass-Through...")
    mock_groq_cls = MagicMock()
    mock_groq_instance = mock_groq_cls.return_value
    mock_completion = MagicMock()
    mock_completion.choices[0].message.content = "Custom completion output"
    mock_groq_instance.chat.completions.create.return_value = mock_completion

    with patch.object(settings, "env", "development"), \
         patch.object(settings, "groq_api_key", "gsk_valid_test_key_12345"), \
         patch.object(llm_client_module, "HAS_GROQ", True), \
         patch.object(llm_client_module, "Groq", mock_groq_cls, create=True):

        client = LLMClient()
        res = client.generate("system prompt", "user prompt", max_tokens=2048)

        call_kwargs = mock_groq_instance.chat.completions.create.call_args[1]
        assert call_kwargs["max_tokens"] == 2048
        assert res == "Custom completion output"
        print("   ✓ Custom max_tokens=2048 passed through to chat.completions.create!")

    print("=" * 70)
    print("✅ ALL LLM CLIENT RELIABILITY TESTS PASSED!")
    print("=" * 70)

if __name__ == "__main__":
    test_llm_client_reliability()
