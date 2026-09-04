import os
from ..config import settings
from groq import Groq
from langchain_core.messages import HumanMessage, SystemMessage

class LLMClient:
    def __init__(self):
        self.mock_mode = settings.mock_llm_mode or not settings.groq_api_key or settings.groq_api_key == "gsk_placeholder"
        if not self.mock_mode:
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
            return "Based on the evidence, the primary typology is STRUCTURING, due to consecutive sub-threshold deposits."
        if "plan" in system_prompt.lower():
            return "1. Review counterparty flows.\n2. Verify KYC occupation.\n3. Ascertain source of funds."
        if "dossier" in system_prompt.lower() or "SAR" in system_prompt.lower():
            return "## Suspicious Activity Report Draft\n\nThe entity engaged in rapid velocity pass-throughs indicative of layering."
        
        return "Mock response generated (Offline mode)."
