from backend.retreiver_dense import DenseRetriever


retriever = DenseRetriever()

query = "What are Pranav's technical skills?"

results = retriever.retrieve(
    query=query,
    top_k=3,
)

for index, result in enumerate(results, start=1):

    print()
    print(f"Result {index}")
    print("-" * 60)
    print(f"Score: {result.score:.4f}")
    print(f"Document: {result.document_name}")
    print(f"Page: {result.page_number}")
    print(f"Chunk: {result.chunk_id}")
    print()
    print(result.text)