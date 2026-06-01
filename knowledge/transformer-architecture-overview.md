# Transformer Architecture Overview

**Created**: 2026-06-01
**Updated**: 2026-06-01
**Tags**: transformers, attention-mechanism, neural-networks, deep-learning, nlp

## Summary
# Transformer Architecture: "Attention Is All You Need"

The Transformer (Vaswani et al., 2017) is a neural network architecture that **replaces recurrence and convolutions entirely with self-attention mechanisms**, enabling parallelizable, highly scalable sequence modeling. Originally designed for sequence-to-sequence tasks like machine translation, it has become the foundation for modern LLMs and multimodal models.

## Core Innovation
Self-attention allows each token to directly attend to all other tokens regardless of distance, with no sequential dependency. This enables full parallelization during training and captures long-range dependencies with O(1) path length between any two positions (versus O(n) for RNNs).

## Architecture Components

The Transformer uses an **encoder–decoder structure**:
- **Encoder**: Stack of N identical layers (N=6 in original) mapping input sequences to continuous representations
- **Decoder**: Stack of N identical layers with masked self-attention to prevent attending to future tokens, plus cross-attention over encoder output

### Core Sub-Layers
Each layer contains:
1. **Multi-Head Self-Attention** — runs h parallel attention heads capturing diverse relational patterns, then concatenates outputs
2. **Feed-Forward Network (FFN)** — position-wise transformation (two linear layers + ReLU)
3. **Layer Normalization + Residual Connections** — stabilizes training and enables deep networks

### Positional Encoding
Since attention has no inherent sequential awareness, **sinusoidal or learned positional encodings** inject sequence order information.

## Attention Mechanism

**Scaled Dot-Product Attention**: `Attention(Q, K, V) = softmax(QKᵀ / √dₖ) · V`

Multi-head attention runs h heads in parallel, allowing the model to jointly attend to information from different representation subspaces.

## Base Model Hyperparameters
- Layers: 6
- Model dimension: 512
- Attention heads: 8
- FFN inner dimension: 2048

## Key Advantages
- **Parallelizable** — no sequential dependency enables faster training
- **Long-range dependencies** — direct attention paths between all tokens
- **Interpretability** — attention weights are inspectable
- **Scalable** — foundation for models of any size

## Limitations
- **Quadratic complexity** — O(n²) memory and compute with sequence length
- **Requires positional encoding** — no built-in positional awareness

## Impact & Variants
The Transformer became the dominant paradigm in modern AI, directly enabling BERT (encoder-only, bidirectional), GPT series (decoder-only, autoregressive), T5 and BART (full encoder-decoder), Vision Transformer (applied to image patches), and virtually all contemporary [[Large Language Models]].

## Key Points
- See summary above for detailed points.

## Related Topics
[[Large Language Models]]