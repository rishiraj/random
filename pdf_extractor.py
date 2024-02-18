import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import json
import os
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
from indexify_extractor_sdk.base_extractor import Extractor

class PDFExtractor(Extractor):
    name = "pdf-extractor"
    description = "PDF Extractor with GIST-Embedding-v0 embedding model & phi-2 language model"
    python_dependencies = ["torch","pypdf","sentence_transformers","transformers"]
    system_dependencies = []

    def __init__(self):
        super(PDFExtractor, self).__init__()
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.model = AutoModelForCausalLM.from_pretrained("microsoft/phi-2", torch_dtype="auto", trust_remote_code=True)
        self.tokenizer = AutoTokenizer.from_pretrained("microsoft/phi-2", trust_remote_code=True)
        self.embed_model = SentenceTransformer("avsolatorio/GIST-Embedding-v0")
    
    def extract_chunks(self, directory):
        self.texts = []
        # Iterate through all files in the directory
        for filename in os.listdir(directory):
            if filename.endswith('.pdf'):  # Check if it's a PDF file
                filepath = os.path.join(directory, filename)
                # Open the PDF file in read-binary mode
                with open(filepath, 'rb') as pdf_file:
                    self.extract_text_from_pdf(pdf_file)

        print("No. of pages: ", len(self.texts))
        self.split_long_strings(self.texts)
        print("No. of chunks: ", len(self.texts))

    def extract_text_from_pdf(self, pdf_file):
        reader = PdfReader(pdf_file)
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text = page.extract_text()
            (self.texts).append(text)
    
    def split_long_strings(self, string_list, max_words=128):
        new_list = []
        for string in string_list:
            words = string.split()  # Split the string into words
            if len(words) > max_words:
                # Split into chunks based on max_words
                for i in range(0, len(words), max_words):
                    chunk = ' '.join(words[i:i + max_words])
                    new_list.append(chunk)
            else:
                new_list.append(string)
        self.texts = new_list

    def passage_embeddings(self, p_texts):
        # Compute embeddings
        embeddings = self.embed_model.encode(p_texts, convert_to_tensor=True)

        # print("Passage Embeddings: ", embeddings)
        return embeddings

    def query_embeddings(self, q_text):
        texts = [q_text]
        # Compute embeddings
        embeddings = self.embed_model.encode(texts, convert_to_tensor=True)

        # print("Query Embeddings: ", embeddings)
        return embeddings

    def calculate_scores(self, q_embeddings, p_embeddings):
        # Compute cosine-similarity for each pair of sentences
        scores = F.cosine_similarity(q_embeddings.unsqueeze(1), p_embeddings.unsqueeze(0), dim=-1)

        # print("Scores: ", scores)
        return scores

    def find_passage(self, q_text, p_texts):
        p_embeddings = self.passage_embeddings(p_texts)
        q_embeddings = self.query_embeddings(q_text)
        scores = (self.calculate_scores(q_embeddings, p_embeddings))[0].tolist()
        return p_texts[scores.index(max(scores))]

    def chat(self, question):
        passage = self.find_passage(question, self.texts)
        query = "Instruct: " + passage + ". " + question + "\nOutput:"
        inputs = self.tokenizer(query, return_tensors="pt", return_attention_mask=False)

        outputs = self.model.generate(**inputs, max_length=512)
        text = self.tokenizer.batch_decode(outputs)[0]
        return text
    
    def extract(self, content) -> str:
        query, directory = content
        self.extract_chunks(directory)
        result = self.chat(query)
        print(result)
        return result
    
    def sample_input(self):
        return "What is Zephyr?", "/Users/rishiraj/tensorlake/project2/papers"

if __name__ == "__main__":
    PDFExtractor().extract_sample_input()