import asyncio

from backend.answer_generator import AnswerGenerator
from backend.retreiver_dense import DenseRetriever


async def main():

    query = "What are Pranav's technical skills?"

    retriever = DenseRetriever()

    chunks = retriever.retrieve(
        query=query,
        top_k=3,
    )

    generator = AnswerGenerator()

    answer, sources = await generator.generate(
        query=query,
        chunks=chunks,
    )

    print()
    print("=" * 80)
    print("ANSWER")
    print("=" * 80)
    print(answer)

    print()
    print("=" * 80)
    print("SOURCES")
    print("=" * 80)

    for source in sources:

        print(
            f"{source.document_name} | "
            f"Page {source.page_number} | "
            f"Score {source.score:.4f}"
        )


if __name__ == "__main__":
    asyncio.run(main())