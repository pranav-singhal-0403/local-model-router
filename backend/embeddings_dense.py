from typing import List
from sentence_transformers import SentenceTransformer
from backend.config import EMBEDDING_CONFIG

class DenseEmbedder:
    def __init__(self):
        model_name = EMBEDDING_CONFIG["model"]
        self.model = SentenceTransformer(model_name)
        self.dimension = self.model.get_embedding_dimension()

    def encode(self,texts: List[str],) -> List[List[float]]:
        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

        return embeddings.tolist()

    def encode_query(self, query: str) -> List[float]:
        embedding = self.model.encode(
            query,
            normalize_embeddings=True,
            show_progress_bar=True,
        )

        return embedding.tolist()