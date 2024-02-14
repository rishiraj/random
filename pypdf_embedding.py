from pypdf import PdfReader
import torch
from typing import List
from sentence_transformers import SentenceTransformer
from indexify_extractor_sdk.embedding.base_embedding import BaseEmbeddingExtractor

class PyPDFExtractor(BaseEmbeddingExtractor):
    name = "pypdf-embedding"
    description = "PyPDF Embedding Extractor"
    python_dependencies = ["torch","pypdf","sentence_transformers","transformers"]
    system_dependencies = []
    input_mime_types = ["text/plain", "application/pdf"]

    def __init__(self):
        super(PyPDFExtractor, self).__init__(max_context_length=512)
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.embedding_model = SentenceTransformer("avsolatorio/GIST-Embedding-v0")
    
    def _extract_text_from_pdf(self, pdf_data):
        reader = PdfReader(pdf_data)
        texts = []

        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text = page.extract_text()
            texts.append(text)
        
        return texts
    
    def _process_pdf(self, texts):
        embeddings = self.embedding_model.encode(texts)
        return embeddings

    def extract_embeddings(self, content) -> List[List[float]]:
        with open(content, "rb") as file:
            texts = self._extract_text_from_pdf(file)
            embeddings = self._process_pdf(texts)
            return embeddings
    
    def extract(self, content) -> List[List[float]]:
        embeddings = self.extract_embeddings(content)
        print(embeddings)
        return embeddings
    
    def sample_input(self):
        return "/Users/rishiraj/tensorlake/project2/papers/2310.16944.pdf"

if __name__ == "__main__":
    PyPDFExtractor().extract_sample_input()

# # Testing block
# if __name__ == "__main__":
#     pdf_file_path = "/Users/rishiraj/tensorlake/project2/papers/2310.16944.pdf"  # Replace with your PDF file path

#     extractor = PyPDFExtractor()

#     pdf_results = extractor.extract_embeddings(pdf_file_path)
#     print("PDF Embedding Extraction Results:", pdf_results)