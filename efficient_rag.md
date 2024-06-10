# Efficient RAG for mixed context texts with Indexify's framework, Gemini's 2M context & Arctic's embeddings

## Why We Built Indexify

Retrieval-augmented generation (RAG) systems have become the most popular method for natural language processing because RAG can quickly and effectively generate accurate and relevant responses. The effectiveness of RAG promises to create more accurate, precise, and efficient AI-powered applications across all domains, enabling easy and democratic access to Q&A systems, content generation, and dialogue systems. Despite how impressive current RAG systems are, they struggle to process large mixed-context texts. There are issues with chunking algorithms and inherent problems with mixed context information, no matter the medium.

## The Complexity of Mixed Context Texts

Mixed-context texts, such as research papers, technical documents, or even web pages, often contain cross-domain information. A single document might include information from physics, chemistry, biology, and computer science throughout its content. This heterogeneous nature of the text poses a challenge for RAG systems, which rely on identifying and retrieving relevant information to generate accurate responses.

Chunking algorithms divide data into smaller, more workable parts called chunks. Chunks are based on tokens, and their size and effectiveness are governed by the model and task you're trying to perform. However, these chunks don't consider the semantic coherence of the information. As a result, in a mixed context, text-generated chunks often contain irrelevant information, and sentences are mashed together with no regard for their content. This wastes valuable tokens as these chunks are passed to subsequent API calls to Large Language Models (LLMs), which often have limited context lengths. 

## LLM Assisted Restructuring for RAG (LLMARRAG) Pipeline

At Indexify, we recognized the need for faster and more accurate approaches to processing mixed context texts in RAG systems. To remedy this problem, our team has developed an innovative pipeline that addresses these limitations.

When it comes to tackling mixed-context text Indexify uses the following workflow: 

1. Data Extraction - Fast real-time extraction of any data source
2. Text Restructuring - Semantic restructuring to prepare the text for chunking
3. Enhanced Chunking  - Producing relevant and information-dense chunks 
4. Embedding Creation - High-quality embeddings for your chunks

### 1. Data Extraction with Robust Extractors

The first step in Indexify's pipeline is to extract data from various sources like PDF files, or text documents. Unstructured data poses a significant challenge, so we have developed a fast real-time extraction engine and a collection of robust pre-built extractors such as [Marker](https://github.com/VikParuchuri/marker).

### 2. Text Restructuring with Gemini 1.5 Flash LLM

The extracted text requires restructuring to enhance processing and retrieval efficiency.Indexify leverages Google's recently unveiled state-of-the-art Gemini 1.5 Flash LLM.
The Gemini 1.5 Flash LLM boasts an impressive 2M context length, making it ideal for processing large mixed-context texts. By harnessing the power of this advanced language model, we can intelligently restructure the entire text of a document to group sentences from similar topics together.

Semantic restructuring ensures that relevant information is placed together, creating topic-coherent segments within the text. By presorting subject-specific text content together, Indexify allows for more accurate and efficient chunking throughout the rest of our pipeline. The restructuring process eliminates chunking inefficiencies before chunks are passed to API calls and ensures users aren't wasting their time or their tokens.

### 3. Enhanced Chunking with RecursiveCharacterTextSplitter

With the text restructured into topic-coherent segments, Indexify's pipeline performs chunking using the RecursiveCharacterTextSplitter algorithm. This algorithm has been designed to handle large texts and create meaningful chunks based on a specified size.

Thanks to the intelligent restructuring performed in the previous step, the RecursiveCharacterTextSplitter can now generate chunks that are more information-dense and domain-specific. This enhanced chunking process greatly improves the efficiency of RAG systems by producing highly relevant chunks to the task at hand. This optimization ensures that the LLMs receive relevant and digestible input, enabling them to generate more accurate responses using fewer resources. 

### 4. Embedding Creation with Snowflake's Arctic Model

The final step in Indexify's pipeline is creating embeddings using Snowflake's Arctic embedding model. Embeddings enable efficient similarity search and retrieval of relevant information from the chunked text.Snowflake's Arctic model is a leading embedding model that accurately captures the semantic meaning of text chunks. By representing each chunk as a high-dimensional vector, the Arctic model allows for fast and precise similarity comparisons between the query and the available chunks.

Indexify's pipeline leverages the power of the Arctic model to create high-quality embeddings for each chunk generated in the previous step. These embeddings serve as the basis for retrieving the most relevant chunks when a user poses a question to the RAG system.

## Creating LLMARRAG Pipeline is Simple with Indexify

#### Install Indexify, Start the Server & Download the Extractors

```bash
!pip install -q -U indexify indexify-extractor-sdk
```
```bash
curl https://getindexify.ai | sh
./indexify server -d
```
```bash
!indexify-extractor download hub://pdf/marker
!indexify-extractor download hub://text/llm
!indexify-extractor download hub://text/chunking
!indexify-extractor download hub://embedding/arctic

!indexify-extractor join-server
```

#### Create a Client, Define Extraction Graph & Ingest Contents

```python
from indexify import IndexifyClient
client = IndexifyClient()
```
```python
from indexify import ExtractionGraph

extraction_graph_spec = """
name: 'llmarrag'
extraction_policies:
   - extractor: 'tensorlake/marker'
     name: 'mdextractor'
   - extractor: 'tensorlake/llm'
     name: 'txtprocessor'
     input_params:
        service: 'gemini'
        prompt: 'Rearrange and rewrite the following text by grouping similar topics together while preserving the original sentences.'
     content_source: 'mdextractor'
   - extractor: 'tensorlake/chunk-extractor'
     name: 'chunker'
     input_params:
        chunk_size: 1000
        overlap: 100
     content_source: 'txtprocessor'
   - extractor: 'tensorlake/arctic'
     name: 'embedder'
     content_source: 'chunker'
"""

extraction_graph = ExtractionGraph.from_yaml(extraction_graph_spec)
client.create_extraction_graph(extraction_graph)
```
```python
client.upload_file("llmarrag", "random_topics.pdf")
```

## The Impact of LLMARRAG Pipeline

Indexify was designed to address the limitations in existing tools and pipelines. Our pipeline has the potential to rethink the way RAG systems process mixed context text. 
This is because our framework was designed for comptability with industry leading tools and libraries. 

Indexify is able to quickly set up nimble and dynamic extraction pipelines that directly address the complexities of mixed context text which offers several key benefits:

- **Efficient Processing**: Indexify's pipeline enables RAG systems to better process mixed context texts by intelligently restructuring the text and performing enhanced chunking. The topic-coherent segments and information-dense chunks allow for more resource-efficient processing, saving computer resources and tokens.

- **Improved Accuracy**: By retrieving the most relevant chunks for a given query, the LLMs can generate more contextually appropriate and precise responses, enhancing the output's overall quality.

- **Scalability**: Indexify's pipeline is designed to handle large mixed-context texts effectively. With the Gemini 1.5 Flash LLM's 2M context length and the efficient chunking algorithm, our solution can scale to process extensive documents and datasets, making it suitable for any project.

- **Flexibility and Customization**: As an Open-Source data framework, Indexify allows users to customize and extend the pipeline according to their specific needs. Developers can use our prebuilt extractors or connect to their own models and algorithms. 


## Benchmarking

| Metrics                                                                          | Scores |
| -------------------------------------------------------------------------------- | ------ |
| Number of chunks required by traditional RAG to include all relevant information | 5      |
| Number of chunks required by LLMARRAG to include all relevant information        | 2      |
|                                                                                  |        |
| Number of tokens required by traditional RAG to include all relevant information | 651    |
| Number of tokens required by LLMARRAG to include all relevant information        | 255    |
|                                                                                  |        |
| Number of irrelevant tokens in the most relevant chunk by traditional RAG        | 100    |
| Number of irrelevant tokens in the most relevant chunk by LLMARRAG               | 6      |
|                                                                                  |        |
| Difference between least relevant and irrelevant chunks by traditional RAG       | 5.59%  |
| Difference between least relevant and irrelevant chunks by LLMARRAG              | 12.81% |

## Conclusion

Indexify's innovative LLMARRAG pipeline revolutionizes how RAG systems process mixed context texts. By combining robust data extraction, intelligent text restructuring with Gemini 1.5 Flash LLM, optimized chunking using RecursiveCharacterTextSplitter, and accurate similarity search powered by Snowflake's Arctic embeddings, Indexify enables efficient, accurate, and scalable processing of large, heterogeneous documents. This open-source data framework empowers developers to create customized, high-performance RAG systems for various applications, democratizing access to advanced natural language processing capabilities and paving the way for more accurate and efficient AI-powered solutions across all domains.

Do you have any ideas about where we should go or what we should build next?

Join our Discord to connect with us directly and build the future of open-source data processing for Generative AI with us!

Indexify’s website — https://getindexify.ai

Stay in touch with us by following us on [Twitter](https://twitter.com/tensorlake) and [LinkedIn](https://www.linkedin.com/company/tensorlake/)!
