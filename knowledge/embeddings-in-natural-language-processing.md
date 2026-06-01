# Embeddings in Natural Language Processing

**Created**: 2026-06-01
**Updated**: 2026-06-01
**Tags**: embeddings, nlp, word-representations, machine-learning, language-models

## Summary
# Embeddings in NLP: Overview

Embeddings are dense, continuous vector representations of text (words, sentences, or documents) that capture semantic meaning and relationships, enabling machines to process language mathematically. They convert discrete tokens into low-dimensional continuous vectors where similar meanings map to nearby points in vector space.

## Core Concepts

**What They Do:** Transform language into meaningful numerical representations far smaller than sparse one-hot encodings (typically 50 to 1,536+ dimensions). Vectors encode semantic relationships—the classic example: `king − man + woman ≈ queen`.

**How They're Trained:** Learned from large text corpora via self-supervised objectives such as predicting neighboring words or masked tokens. Pre-trained embeddings are transferable and can be fine-tuned or reused across downstream NLP tasks.

## Evolution of Embedding Models

### Static Embeddings
- **Word2Vec (2013):** Google's breakthrough using skip-gram and CBOW architectures; enabled vector arithmetic
- **GloVe (2014):** Stanford's model using global word co-occurrence statistics
- **FastText (2016):** Facebook's extension using subword (character n-gram) information; handles rare and unknown words
- **Limitation:** One fixed vector per word regardless of context (polysemy problem—"bank" as river vs. finance uses same vector)

### Contextual Embeddings
- **ELMo (2018):** Bidirectional LSTM generating dynamic, context-sensitive vectors
- **BERT (2018):** Transformer-based model with deep bidirectional context; widely used for fine-tuning
- **GPT Series:** Unidirectional transformer embeddings excelling at generative tasks

### Sentence & Document-Level
- **Sentence-BERT (SBERT):** Optimized for semantically meaningful sentence vectors
- **Doc2Vec:** Extends Word2Vec to paragraph/document level
- **OpenAI Embeddings API:** High-dimensional embeddings for semantic search and clustering

## Applications

Embeddings power semantic search and information retrieval, text classification and sentiment analysis, machine translation, question answering, clustering, recommendation systems, and retrieval-augmented generation (RAG) pipelines.

## Key Limitations

Static embeddings cannot handle polysemy. Large contextual models require significant computational resources. Embeddings may encode social biases present in training data.

Embeddings remain the foundational bridge between raw text and machine learning models, progressively evolving from static word vectors to rich, context-aware representations that improve semantic understanding across all NLP tasks.

## Key Points
- See summary above for detailed points.

## Related Topics

