# Efficient and supercharged RAG for mixed context texts with Indexify's framework, Gemini's 2M context & Arctic's embeddings

## Introduction

Retrieval-augmented generation (RAG) systems have emerged as a groundbreaking approach in natural language processing, enabling the generation of accurate and contextually relevant responses by leveraging external knowledge. These systems have the potential to revolutionize various applications, from question answering and content generation to dialogue systems and beyond. However, despite their immense promise, modern RAG systems face a significant challenge when it comes to efficiently processing large mixed context texts.

In this blog post, we delve into the intricacies of this problem and explore how Indexify, an Open Source data framework, has developed an innovative pipeline to overcome these limitations. We will discuss the challenges posed by mixed context texts, the shortcomings of existing chunking algorithms, and how Indexify's solution combines advanced data extraction, intelligent text restructuring, enhanced chunking, and state-of-the-art embedding creation to deliver highly efficient and accurate RAG systems.

## The Complexity of Mixed Context Texts

Mixed context texts, such as research papers, technical documents, or even web pages, often contain a diverse range of information spanning multiple domains. For instance, a single document might include random sentences from physics, chemistry, biology, and computer science, scattered throughout its content. This heterogeneous nature of the text poses a significant challenge for RAG systems, which rely on identifying and retrieving relevant information to generate accurate responses.

When a user asks a question related to a specific topic, such as the various systems of the human body, RAG systems need to efficiently locate and extract the relevant information from the mixed context text. However, popular chunking algorithms, like LangChain's RecursiveCharacterTextSplitter, struggle to handle such texts effectively.

These algorithms typically create chunks based on a fixed number of characters or tokens, without considering the semantic coherence of the sentences within each chunk. As a result, the generated chunks often contain a lot of unnecessary information from unrelated domains, as sentences from different topics are placed together haphazardly. This leads to a waste of precious tokens when these chunks are passed to subsequent API calls to Large Language Models (LLMs), which are often limited in their context length.

Moreover, if the mixed context text mentions four different systems of the human body at different places, a similarity search with a top-k value of 2 would fetch at most two relevant chunks. This limitation sacrifices the quality of the produced output when these chunks are passed as context to an LLM in subsequent API calls, as the model may not have access to all the necessary information to generate a comprehensive response.

## LLM Assisted Restructuring for RAG (LLMARRAG) Pipeline

At Indexify, we recognized the need for a more efficient and accurate approach to processing mixed context texts in RAG systems. Our team has developed an innovative pipeline that combines cutting-edge technologies and techniques to overcome the limitations of existing solutions.

### Step 1: Data Extraction with Robust Extractors

The first step in Indexify's pipeline is to extract data, such as text, from various sources like PDF files and other documents. We understand that unstructured data poses a significant challenge, which is why we have developed a fast real-time extraction engine and a collection of robust pre-built extractors.

One notable integration in our pipeline is Vik Paruchuri's Marker, a powerful tool for extracting structured data from unstructured sources. By leveraging Marker, we ensure that we can comprehensively extract text data from a wide range of documents, providing a solid foundation for the subsequent steps in our pipeline.

### Step 2: Intelligent Text Restructuring with Gemini 1.5 Flash LLM

Once the text data is extracted, the next crucial step is to restructure it in a way that facilitates efficient processing and retrieval. This is where Indexify's pipeline truly shines, as we leverage Google's state-of-the-art Gemini 1.5 Flash LLM, which was recently unveiled at Google I/O 2024.

The Gemini 1.5 Flash LLM boasts an impressive 2M context length, making it exceptionally well-suited for processing large mixed context texts. By harnessing the power of this advanced language model, we can intelligently restructure the entire text of a PDF or other document, grouping sentences from similar topics together.

This semantic restructuring is a game-changer, as it ensures that related information is placed in close proximity, creating topic-coherent segments within the text. By bringing together sentences that discuss the same subject matter, we lay the groundwork for more accurate and efficient chunking in the subsequent steps of our pipeline.

### Step 3: Enhanced Chunking with RecursiveCharacterTextSplitter

With the text restructured into topic-coherent segments, Indexify's pipeline proceeds to perform chunking using the RecursiveCharacterTextSplitter algorithm. This algorithm has been specifically designed to handle large texts and create meaningful chunks based on a specified maximum chunk size.

Thanks to the intelligent restructuring performed in the previous step, the RecursiveCharacterTextSplitter can now generate chunks that are more information-dense and focused on specific domains. This enhanced chunking process greatly improves the efficiency of RAG systems by providing chunks that are highly relevant to the question at hand.

By eliminating the inclusion of unnecessary information from unrelated domains, our pipeline saves valuable tokens in subsequent API calls to LLMs. This optimization ensures that the LLMs receive only the most pertinent information, enabling them to generate accurate and contextually relevant responses without wasting computational resources on irrelevant data.

### Step 4: Embedding Creation with Snowflake's Arctic Model

The final step in Indexify's pipeline is the creation of embeddings using Snowflake's Arctic embedding model. Embeddings are critical for enabling efficient similarity search and retrieval of relevant information from the chunked text.

Snowflake's Arctic model is a state-of-the-art embedding model that captures the semantic meaning of text chunks with remarkable accuracy. By representing each chunk as a high-dimensional vector, the Arctic model allows for fast and precise similarity comparisons between the query and the available chunks.

Indexify's pipeline leverages the power of the Arctic model to create high-quality embeddings for each chunk generated in the previous step. These embeddings serve as the basis for retrieving the most relevant chunks when a user poses a question to the RAG system.

By utilizing Snowflake's Arctic model, Indexify ensures that the RAG system can effectively identify and retrieve the chunks that are most pertinent to the given query. This enhances the accuracy of the generated responses and greatly improves the overall performance of the RAG system.

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

Indexify's innovative pipeline has the potential to revolutionize the way RAG systems process and utilize mixed context texts. By addressing the limitations of existing approaches and leveraging cutting-edge technologies, our solution offers several key benefits:

1. **Efficient Processing**: By intelligently restructuring the text and performing enhanced chunking, Indexify's pipeline enables RAG systems to process mixed context texts efficiently. The topic-coherent segments and information-dense chunks minimize the inclusion of irrelevant information, saving valuable computational resources and reducing token waste in subsequent API calls to LLMs.

2. **Improved Accuracy**: The combination of intelligent text restructuring, enhanced chunking, and state-of-the-art embedding creation using Snowflake's Arctic model significantly improves the accuracy of RAG systems. By retrieving the most relevant chunks for a given query, the LLMs can generate responses that are more contextually appropriate and precise, enhancing the overall quality of the generated output.

3. **Scalability**: Indexify's pipeline is designed to handle large mixed context texts effectively. With the Gemini 1.5 Flash LLM's 2M context length and the efficient chunking algorithm, our solution can scale to process extensive documents and datasets, making it suitable for a wide range of applications and domains.

4. **Flexibility and Customization**: As an Open Source data framework, Indexify provides users with the flexibility to customize and extend the pipeline according to their specific needs. Researchers and developers can leverage our robust extractors, integrate their own models and algorithms, and adapt the pipeline to suit their particular use cases, fostering innovation and collaboration within the community.

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

Indexify's innovative pipeline presents a comprehensive solution to the challenges faced by modern RAG systems when processing mixed context texts. By combining advanced data extraction, intelligent text restructuring using Google's Gemini 1.5 Flash LLM, enhanced chunking with RecursiveCharacterTextSplitter, and embedding creation using Snowflake's Arctic model, our approach enables efficient and accurate retrieval-augmented generation.

The pipeline's ability to handle large mixed context texts, reduce token wastage, and improve the accuracy of generated responses makes it a valuable tool for organizations and researchers seeking to unlock the full potential of RAG systems. With Indexify's Open Source data framework and robust extractors, users can easily integrate our solution into their existing workflows and benefit from its powerful capabilities.

As the field of natural language processing continues to evolve, Indexify remains committed to driving innovation and pushing the boundaries of what is possible with RAG systems. We believe that our pipeline represents a significant step forward in enabling the efficient processing of complex, unstructured data and generating high-quality outputs that meet the diverse needs of users.

We invite researchers, developers, and organizations to explore Indexify's pipeline, contribute to its development, and join us in shaping the future of retrieval-augmented generation. Together, we can unlock the immense potential of RAG systems and revolutionize the way we interact with and derive insights from mixed context texts.
