# Transformer Deep Learning Architecture

**Created**: 2026-06-01
**Updated**: 2026-06-01
**Tags**: transformer, neural networks, attention mechanism, deep learning, nlp

## Summary
# Transformer (Deep Learning) – Summary

## Direct Answer
A **transformer** is a family of deep learning neural network architectures built around the **multi-head attention mechanism**, widely used for processing sequential data (especially text) and forming the backbone of modern [[Large Language Models]] (LLMs).

---

## Key Facts

- **Input processing:** Text is converted into numerical **tokens**, each transformed into a vector via a **word embedding** table lookup.
- **Core mechanism:** At each layer, tokens are **contextualized** within a context window using **parallel multi-head attention**, amplifying important signals and diminishing less relevant ones.
- **Positional awareness:** Since self-attention is permutation-invariant, transformers inject **positional information** via positional encodings or learned positional embeddings to preserve token order.
- **No recurrence:** Unlike RNNs/LSTMs, transformers have **no recurrent units**, leading to faster training times.
- **LLM foundation:** Transformer variants are the dominant architecture for training **large language models (LLMs)** on large datasets.

---

## Key Subtopics

### Architecture Types
- **Encoder-only** – optimized for understanding tasks (e.g., BERT)
- **Decoder-only** – optimized for generation tasks (e.g., GPT)
- **Encoder-Decoder** – used for sequence-to-sequence tasks (e.g., translation)

### Advantages Over Prior Architectures
| Feature | Transformers | RNNs/LSTMs |
|---|---|---|
| Parallelism | ✅ High | ❌ Sequential |
| Training speed | ✅ Faster | ❌ Slower |
| Long-range context | ✅ Strong | ⚠️ Limited |

### Historical Note
- Originally proposed in the landmark **2017 paper** *"Attention Is All You Need"*
- Modern designs often use **pre-LN** (pre-layer normalization) convention, differing from the original **post-LN** design

---

*Sources: Wikipedia – Transformer (deep learning)*

## Key Points
- See summary above for detailed points.

## Related Topics
[[Large Language Models]]