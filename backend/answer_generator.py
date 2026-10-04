from typing import List, Tuple

from backend.models import RetrievedChunk
from backend.ollama_client import OllamaClient
from backend.prompt_builder import build_prompt


class AnswerGenerator:

    def __init__(
        self,
        ollama_client: OllamaClient,
    ):
        self.ollama = ollama_client

    async def generate(
        self,
        query: str,
        chunks: List[RetrievedChunk],
    ) -> Tuple[str, List[RetrievedChunk]]:

        if not chunks:

            return (
                "I could not find relevant information in "
                "the uploaded documents.",
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