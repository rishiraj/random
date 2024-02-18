from typing import List
from indexify_extractor_sdk.embedding.base_embedding import BaseEmbeddingExtractor
from sentence_transformers import SentenceTransformer


class PDFExtractor(BaseEmbeddingExtractor):
    name = "pdf-extractor"
    description = "PDF Extractor with GIST-Embedding-v0 embedding model"
    python_dependencies = ["torch","sentence_transformers"]
    system_dependencies = []

    def __init__(self):
        super(PDFExtractor, self).__init__(max_context_length=512)
        self._model = SentenceTransformer("avsolatorio/GIST-Embedding-v0")

    def extract_embeddings(self, texts: List[str]) -> List[List[float]]:
        return self._model.encode(texts)


if __name__ == "__main__":
    PDFExtractor().extract_sample_input()