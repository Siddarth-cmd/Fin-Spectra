import os
from ..config import settings

try:
    from groq import Groq
    HAS_GROQ = True
except ImportError:
    HAS_GROQ = False

class LLMClient:
    def __init__(self):
        self.mock_mode = (
            settings.mock_llm_mode
            or not settings.groq_api_key
            or settings.groq_api_key == "gsk_placeholder"
            or not HAS_GROQ
        )
        if not self.mock_mode and HAS_GROQ:
            self.client = Groq(api_key=settings.groq_api_key)
        self.model = settings.groq_model

    def generate(self, system_prompt: str, user_prompt: str) -> str:
        if self.mock_mode:
            return self._mock_generate(system_prompt, user_prompt)
            
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=1024,
        )
        return completion.choices[0].message.content

    def _mock_generate(self, system_prompt: str, user_prompt: str) -> str:
        # Simple offline deterministic mock fallback based on keywords
        if "typology" in system_prompt.lower():
            return '{\n  "typology": "LAYERING",\n  "rationale": "High-velocity multi-account pass-through transfers and rapid transaction dispersion."\n}'
        if "plan" in system_prompt.lower():
            return "1. Review counterparty flows.\n2. Verify KYC occupation.\n3. Ascertain source of funds."
        if "dossier" in system_prompt.lower() or "sar" in system_prompt.lower():
            return "## Suspicious Activity Report (SAR) Draft\n\n### Executive Summary\nThe entity engaged in rapid velocity pass-throughs indicative of layering and multi-device transaction dispersion."
        
        return "Mock response generated (Offline mode)."
