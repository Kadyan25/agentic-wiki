# Transformer Neural Network Architecture

**Created**: 2026-06-01
**Updated**: 2026-06-01
**Tags**: deep learning, transformers, attention mechanism, neural networks, nlp

## Summary
# Transformer (Deep Learning) — Summary

## Direct Answer
A **transformer** is a deep learning neural network architecture based on the **multi-head attention mechanism**, designed to model sequential data (e.g., text). It has become the dominant architecture for [[Large Language Models]] (LLMs) and many other AI applications.

---

## Key Facts

- **Core mechanism:** Multi-head self-attention, which contextualizes each token relative to all other tokens in a context window
- **Input processing:** Text → numerical tokens → vectors via a word embedding lookup table
- **Positional awareness:** Since self-attention is permutation-invariant, positional encodings or learned positional embeddings are added to preserve token order
- **No recurrence:** Unlike RNNs/LSTMs, transformers have no recurrent units, enabling **faster, more parallelizable training**
- **Introduced:** Originally described in 2017 (the "Attention Is All You Need" paper)
- **Two main components:** An **encoder** and a **decoder** (modern designs are often encoder-only or decoder-only)

---

## Key Subtopics

### Architecture Variants
- **Encoder-only** (e.g., BERT) — suited for classification, understanding tasks
- **Decoder-only** (e.g., GPT) — suited for text generation
- **Encoder-decoder** (original design) — suited for translation, summarization

### Advantages Over Earlier Architectures
| Feature | Transformer | RNN/LSTM |
|---|---|---|
| Parallelization | ✅ High | ❌ Sequential |
| Training speed | ✅ Faster | ❌ Slower |
| Long-range dependencies | ✅ Strong | ⚠️ Weaker |

### Applications
- Large Language Models (LLMs) trained on massive datasets
- Vision transformers, multimodal models, and more

---

## Summary
Transformers revolutionized deep learning by replacing recurrent designs with attention-based, parallelizable architectures, enabling efficient training at scale and powering modern AI systems like ChatGPT and BERT.

## Key Points
- See summary above for detailed points.

## Related Topics
[[Large Language Models]]