from typing import List
from backend.models import RetrievedChunk
from backend.config import (
    SYSTEM_PROMPT,
)

def build_prompt(
    query: str,
    chunks: List[RetrievedChunk],
) -> str:

    context_parts = []

    for index, chunk in enumerate(chunks, start=1):

        context_parts.append(
            f"""SOURCE {index}
Document: {chunk.document_name}
Page: {chunk.page_number}
Relevance Score: {chunk.score:.4f}

{chunk.text}
"""
        )

    context = "\n\n".join(context_parts)

    prompt = f"""{SYSTEM_PROMPT}

RETRIEVED CONTEXT
=================
{context}

USER QUESTION
=============
{query}

ANSWER
=======
"""

    return prompt