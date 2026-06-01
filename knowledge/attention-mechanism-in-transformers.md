# Attention Mechanism in Transformers

**Created**: 2026-06-01
**Updated**: 2026-06-01
**Tags**: transformers, attention, neural networks, deep learning, nlp

## Summary
# Attention in Transformer Models

Attention is a mechanism that enables transformer models to dynamically weigh the relevance of all tokens in a sequence relative to each other, allowing the model to focus on the most contextually important information regardless of positional distance.

## Core Mechanism

For each token, attention computes a weighted sum of all other tokens' values, where weights reflect pairwise relevance. The process follows four steps:

1. **Project** inputs into Query (Q), Key (K), and Value (V) vectors
2. **Score** relevance via dot product between Q and K
3. **Normalize** scores with softmax to produce attention weights (sum to 1)
4. **Aggregate** by applying weights to V vectors to produce final output

## The Q, K, V Framework

Each token is projected into three vectors:
- **Query (Q):** What the token is looking for
- **Key (K):** What the token offers/contains
- **Value (V):** The actual information to aggregate

## Mathematical Foundation

The attention formula is: `Attention(Q, K, V) = softmax(QKᵀ / √dₖ) · V`

The scaling factor `√dₖ` prevents dot products from growing too large in high dimensions, stabilizing gradients during training.

## Key Variants

**Multi-Head Attention:** Runs multiple attention operations in parallel, with each head learning different types of relationships. Outputs are concatenated and linearly projected.

**Self-Attention:** Tokens in the same sequence attend to all other tokens, capturing intra-sequence dependencies like pronoun-antecedent relationships.

**Cross-Attention:** Used in encoder-decoder models where queries come from the decoder and keys/values come from the encoder (e.g., machine translation).

**Masked Attention:** Used in decoder-only models to prevent tokens from attending to future positions, enforcing causal dependencies.

**Soft vs. Hard Attention:** Soft attention uses differentiable weighted averages; hard attention selects one input strictly (non-differentiable).

## Why It Matters

Attention replaces the sequential bottlenecks of RNNs with a direct, learnable mechanism for relating any two positions in a sequence. It captures long-range dependencies without vanishing gradients, enables parallelizable computation for faster training, and provides dynamic, context-sensitive representations. This foundational innovation is the key to modern transformers and [[Large Language Models]].

## Key Points
- See summary above for detailed points.

## Related Topics
[[Large Language Models]]