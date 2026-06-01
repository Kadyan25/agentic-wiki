# Retrieval Augmented Generation Explained

**Created**: 2026-06-01
**Updated**: 2026-06-01
**Tags**: rag, llm, information-retrieval, ai-architecture, natural-language-processing

## Summary
# Retrieval Augmented Generation (RAG)

## Direct Answer
Retrieval Augmented Generation (RAG) is an AI technique that enhances [[Large Language Models]] (LLMs) by dynamically retrieving relevant external information at query time before generating a response, combining the strengths of retrieval systems and generative AI.

---

## Key Facts
- **Problem it solves:** LLMs have static knowledge cutoffs and can hallucinate; RAG grounds responses in current, verifiable data
- **Core components:** A **retriever** (finds relevant documents) + a **generator** (LLM that produces the final answer)
- **Workflow:** User query → search knowledge base → retrieved chunks injected into prompt → LLM generates informed response
- **Knowledge base:** Documents are pre-processed into chunks, converted to vector embeddings, and stored in a vector database (e.g., Pinecone, FAISS, Weaviate)
- **Retrieval method:** Semantic similarity search using embeddings is most common; keyword (BM25) or hybrid search also used
- **No retraining required:** External knowledge can be updated without fine-tuning the model

---

## How It Works (Step-by-Step)
1. **Indexing** – Source documents are chunked and embedded into a vector store
2. **Retrieval** – User query is embedded; top-K most similar chunks are retrieved
3. **Augmentation** – Retrieved chunks are added to the LLM prompt as context
4. **Generation** – The LLM generates a response grounded in the retrieved context

---

## Key Subtopics

### Benefits
- Reduces hallucinations by anchoring outputs to real sources
- Enables up-to-date responses beyond training cutoff
- Improves transparency (sources can be cited)

### Limitations
- Retrieval quality directly impacts answer quality ("garbage in, garbage out")
- Latency overhead from retrieval step
- Struggles with complex multi-hop reasoning across documents

### Common Use Cases
- Enterprise Q&A over internal documents
- Customer support chatbots
- Legal/medical document analysis
- Code documentation assistants

### Advanced Variants
| Variant | Description |
|---|---|
| **Self-RAG** | Model decides when to retrieve |
| **Corrective RAG** | Validates and refines retrieved docs |
| **Graph RAG** | Uses knowledge graphs for retrieval |

---

## Summary
RAG bridges the gap between static LLM knowledge and dynamic, domain-specific information needs — making AI responses more **accurate, current, and trustworthy** without expensive model retraining.

## Key Points
- See summary above for detailed points.

## Related Topics
[[Large Language Models]]