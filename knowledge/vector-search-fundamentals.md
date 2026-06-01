# Vector Search Fundamentals

**Created**: 2026-06-01
**Updated**: 2026-06-01
**Tags**: vector-search, semantic-search, embeddings, machine-learning, information-retrieval

## Summary
# Vector Search

Vector search is a technique for finding similar or relevant data by comparing **mathematical representations (vectors)** of content, rather than matching exact keywords or text strings.

## How It Works

1. **Encode** – Convert data (text, images, audio, etc.) into **high-dimensional numerical vectors** called **embeddings** using machine learning models. These vectors capture the **semantic meaning** or features of the data.
2. **Index** – Store vectors in a vector database (e.g., Pinecone, Weaviate, Qdrant, Milvus, pgvector, Chroma).
3. **Query** – Convert the user's query into a vector using the same model.
4. **Search** – Find the *k* nearest vectors (k-NN) to the query vector using distance metrics.
5. **Return** – Retrieve the corresponding original data items.

## Distance Metrics

Similarity is measured using:
- **Cosine Similarity** – Measures the angle between vectors
- **Euclidean Distance** – Measures straight-line distance
- **Dot Product** – Measures directional alignment

## Key Concepts

- **Embeddings** — Dense numerical representations (e.g., 768 or 1536 dimensions) encoding semantic meaning
- **ANN (Approximate Nearest Neighbor)** — Algorithms (e.g., HNSW, IVF, FAISS) that enable fast, scalable search at the cost of minor accuracy trade-offs. Most production systems use ANN instead of exhaustive comparisons.
- **Vector Databases** — Specialized storage systems optimized for indexing and querying high-dimensional vectors

## Vector Search vs. Keyword Search

| Feature | Keyword Search | Vector Search |
|---|---|---|
| Matching | Exact terms | Semantic similarity |
| Understands synonyms | ❌ | ✅ |
| Language-aware | Limited | ✅ |
| Works on images/audio | ❌ | ✅ |
| Speed at scale | Fast | Requires ANN indexing |

## Common Use Cases

- **Semantic search** — Find documents by meaning, not just words
- **Recommendation systems** — Suggest similar products, content, or users
- **RAG (Retrieval-Augmented Generation)** — Enhance LLMs with relevant context from knowledge bases
- **Image/audio search** — Find visually or acoustically similar content
- **Duplicate detection** — Identify similar or redundant items
- **Anomaly detection** — Identify outliers in data

## Key Takeaway

Vector search enables **meaning-based, similarity-based retrieval** across any type of data by leveraging AI-generated embeddings, making it foundational to modern AI applications like semantic search, recommendation systems, and LLM-powered systems.

## Key Points
- See summary above for detailed points.

## Related Topics

