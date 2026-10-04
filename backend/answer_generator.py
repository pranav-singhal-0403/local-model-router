from typing import List, Tuple

from backend.ollama_client import OllamaClient
from backend.prompt_builder import build_prompt
from backend.models import RetrievedChunk


class AnswerGenerator:

    def __init__(self):
        self.ollama = OllamaClient()

    async def generate(
        self,
        query: str,
        chunks: List[RetrievedChunk],
    ) -> Tuple[str, List[RetrievedChunk]]:

        if not chunks:

            return (
                "I could not find relevant information in the "
                "uploaded documents.",
                [],
            )

        prompt = build_prompt(
            query=query,
            chunks=chunks,
        )

        answer = await self.ollama.generate(
            prompt
        )

        return answer, chunks