# Word Embedding Definition

**Created**: 2026-06-01
**Updated**: 2026-06-01
**Tags**: nlp, embeddings, word-vectors, machine-learning, terminology

## Summary
# Word Embedding

## Direct Answer
Word embedding is a technique in natural language processing (NLP) that represents words as **dense numerical vectors** in a continuous vector space, where semantically similar words are mapped to nearby points.

---

## Key Facts
- **Core idea:** Converts words (discrete symbols) into real-valued vectors of fixed dimensions (e.g., 50, 100, 300 dimensions)
- **Captures meaning:** Similar words (e.g., *king* and *queen*) have similar vector representations
- **Learns from context:** Embeddings are trained based on how words appear together in large text corpora
- **Enables math on words:** Famous example — `vector("king") - vector("man") + vector("woman") ≈ vector("queen")`
- **Dense vs. sparse:** Unlike one-hot encoding (sparse, high-dimensional), embeddings are compact and information-rich

---

## Popular Methods

| Method | Description |
|--------|-------------|
| **Word2Vec** | Uses neural networks (CBOW or Skip-gram) to learn embeddings from context |
| **GloVe** | Based on global word co-occurrence statistics |
| **FastText** | Extends Word2Vec by considering subword (character n-gram) information |
| **Contextual (BERT, ELMo)** | Generates dynamic embeddings that change based on sentence context |

---

## Subtopics

### Why Word Embeddings Matter
- Enable ML models to understand language relationships
- Reduce dimensionality compared to one-hot encoding
- Transferable — pre-trained embeddings can be reused across tasks

### Static vs. Contextual Embeddings
- **Static** (Word2Vec, GloVe): One fixed vector per word regardless of context
- **Contextual** (BERT, GPT): Vectors shift based on surrounding words, handling polysemy (e.g., *bank* as river vs. financial)

### Common Applications
- Sentiment analysis
- Machine translation
- Text classification
- Named entity recognition (NER)
- Recommendation systems

---

## Summary
> Word embeddings bridge the gap between human language and machine understanding by encoding semantic meaning into numerical vectors, forming a foundational building block of modern NLP systems.

## Key Points
- See summary above for detailed points.

## Related Topics

