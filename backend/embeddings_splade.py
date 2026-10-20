
from typing import List, Tuple

import torch
from transformers import AutoModelForMaskedLM, AutoTokenizer


class SpladeEmbedder:
    def __init__(
        self,
        model_name: str = "naver/splade-cocondenser-ensembledistil",
        max_length: int = 256,
        max_terms: int = 128,
    ):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForMaskedLM.from_pretrained(model_name)
        self.model.eval()
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        self.model.to(self.device)
        self.max_length = max_length
        self.max_terms = max_terms

    def encode(
        self,
        texts: List[str],
        batch_size: int = 16,
    ) -> List[Tuple[List[int], List[float]]]:
        results = []

        for start in range(0, len(texts), batch_size):
            batch = texts[start:start + batch_size]

            inputs = self.tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=self.max_length,
                return_tensors="pt",
            ).to(self.device)

            with torch.inference_mode():
                logits = self.model(**inputs).logits
                token_weights = torch.log1p(torch.relu(logits))
                token_weights = token_weights * inputs[
                    "attention_mask"
                ].unsqueeze(-1)
                sparse_vectors = token_weights.max(dim=1).values

            for vector in sparse_vectors:
                nonzero_indices = torch.nonzero(
                    vector > 0,
                    as_tuple=True,
                )[0]

                if nonzero_indices.numel() > self.max_terms:
                    values = vector[nonzero_indices]
                    selected = torch.topk(
                        values,
                        k=self.max_terms,
                    ).indices
                    nonzero_indices = nonzero_indices[selected]

                values = vector[nonzero_indices]
                order = torch.argsort(nonzero_indices)
                nonzero_indices = nonzero_indices[order]
                values = values[order]

                results.append(
                    (
                        nonzero_indices.cpu().tolist(),
                        values.cpu().tolist(),
                    )
                )

        return results

    def encode_query(
        self,
        query: str,
    ) -> Tuple[List[int], List[float]]:
        return self.encode([query])[0]
