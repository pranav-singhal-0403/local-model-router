import httpx

from backend.config import (
    LLM_CONFIG,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
)


class OllamaClient:

    def __init__(self):

        self.base_url = OLLAMA_BASE_URL.rstrip("/")
        self.model = OLLAMA_MODEL

        self.temperature = LLM_CONFIG.get(
            "temperature",
            0.1,
        )

        self.max_tokens = LLM_CONFIG.get(
            "max_tokens",
            2048,
        )

        self.client = httpx.AsyncClient(
            timeout=180.0
        )

    async def generate(
        self,
        prompt: str,
    ) -> str:

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
            },
        }

        response = await self.client.post(
            f"{self.base_url}/api/generate",
            json=payload,
        )

        response.raise_for_status()

        data = response.json()

        return data.get(
            "response",
            "",
        ).strip()

    async def health_check(self) -> bool:

        try:

            response = await self.client.get(
                f"{self.base_url}/api/tags"
            )

            response.raise_for_status()

            return True

        except Exception:

            return False

    async def close(self):

        await self.client.aclose()