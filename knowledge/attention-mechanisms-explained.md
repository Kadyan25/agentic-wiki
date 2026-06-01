# Attention Mechanisms Explained

**Created**: 2026-06-01
**Updated**: 2026-06-01
**Tags**: attention, neural networks, deep learning, transformers, machine learning

## Summary
# Attention Mechanisms in Neural Networks

Attention mechanisms allow neural networks to **selectively focus on relevant parts of the input** when producing an output, rather than processing all information equally. They assign learned weights to different input elements, enabling models to dynamically prioritize what matters most for a given task.

## Core Concept

The fundamental idea is to compute a **weighted sum of input representations**, where weights reflect relevance to the current output step. This replaces fixed context vectors with dynamic, context-sensitive representations that adapt based on what the model needs to process.

## How It Works

Attention operates through four key steps:

1. **Query (Q), Key (K), Value (V):** Each input is projected into three vectors representing what we're looking for (Q), what each element offers (K), and the actual content to retrieve (V).
2. **Similarity scoring:** A dot product between Q and K determines the relevance of each element.
3. **Softmax normalization:** Scores are converted to probabilities (attention weights) that sum to 1.
4. **Weighted sum:** Weights are applied to V vectors to produce the final output.

**Scaled Dot-Product Attention Formula:**
```
Attention(Q, K, V) = softmax(QKᵀ / √d_k) · V
```

## Types of Attention

**Self-Attention:** Each element attends to all others in the same sequence, capturing long-range dependencies efficiently.

**Cross-Attention:** Queries from one sequence attend to keys/values from another sequence.

**Multi-Head Attention:** Runs multiple attention operations in parallel, with each head learning different relationship types. Outputs are concatenated and projected.

**Soft vs. Hard Attention:** Soft attention uses weighted averages (differentiable), while hard attention selects one input strictly (non-differentiable).

## Historical Development

Attention was introduced by Bahdanau et al. (2015) to improve sequence-to-sequence models for machine translation. The **Transformer architecture** (Vaswani et al., 2017) built entirely on attention mechanisms, removing recurrence and enabling full parallelization.

## Why It Matters

Attention mechanisms solve the **vanishing gradient problem** that plagued RNNs, enabling models to efficiently learn long-range dependencies. They provide **interpretability** through attention weights and enable **parallelization** during training. Attention is the foundation of modern [[Large Language Models]] including GPT, BERT, and T5.

**Computational Note:** Standard attention has O(n²) complexity relative to sequence length. Efficient variants (Sparse, Linear, Flash Attention) address scalability for longer sequences.

## Key Points
- See summary above for detailed points.

## Related Topics
[[Large Language Models]]