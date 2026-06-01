# Word Embedding Fundamentals

**Created**: 2026-06-01
**Updated**: 2026-06-01
**Tags**: nlp, word-embedding, machine-learning, vector-representation, deep-learning

## Summary
# Word Embedding

## Direct Answer
Word embedding is a technique in natural language processing (NLP) that represents words as **dense numerical vectors** in a continuous vector space, where semantically similar words are mapped to nearby points.

---

## Key Facts
- **Core idea:** Converts words (text) into lists of numbers (vectors) that capture meaning and relationships
- **Dimensionality:** Vectors typically range from 50 to 300+ dimensions
- **Semantic property:** Similar words (e.g., "king" and "queen") have similar vector representations
- **Arithmetic property:** Vector relationships encode meaning — the classic example:
  `king − man + woman ≈ queen`
- **Learned from data:** Embeddings are trained on large text corpora, learning context-based associations
- **Replaces sparse representations:** Improves upon older methods like one-hot encoding, which produce large, sparse vectors with no semantic meaning

---

## Common Algorithms & Models
| Model | Key Feature |
|-------|-------------|
| **Word2Vec** | Predicts words from context (CBOW) or context from words (Skip-gram) |
| **GloVe** | Uses global word co-occurrence statistics |
| **FastText** | Extends Word2Vec by using subword (character n-gram) information |
| **BERT/Transformers** | Produces **contextual** embeddings — same word gets different vectors in different contexts |

---

## Subtopics

### Static vs. Contextual Embeddings
- **Static** (Word2Vec, GloVe): Each word has one fixed vector regardless of context
- **Contextual** (BERT, GPT): Word vectors change based on surrounding words

### Applications
- Sentiment analysis
- Machine translation
- Text classification
- Information retrieval
- Recommendation systems

### Limitations
- Static embeddings cannot handle **polysemy** (words with multiple meanings)
- Embeddings can inherit **biases** present in training data
- Rare or out-of-vocabulary words may be poorly represented

---

## Summary
> Word embeddings are the foundational building block of modern NLP, enabling machines to process and understand human language by translating words into meaningful numerical representations.

## Key Points
- See summary above for detailed points.

## Related Topics

