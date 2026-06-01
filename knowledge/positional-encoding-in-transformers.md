# Positional Encoding in Transformers

**Created**: 2026-06-01
**Updated**: 2026-06-01
**Tags**: transformers, positional-encoding, nlp, deep-learning, attention-mechanism

## Summary
# Positional Encoding in Transformers

Positional encoding is a technique used in Transformer models to inject information about the **order/position of tokens** in a sequence, since the self-attention mechanism itself is inherently order-agnostic.

## Why It's Needed

Transformers process all tokens **simultaneously in parallel**, unlike RNNs which process sequentially. Without positional information, the model treats input as a **bag of words** — order is lost. Self-attention cannot distinguish *"cat sat"* from *"sat cat"* without explicit position signals. Positional encodings give the model a sense of *where* each token sits in the sequence.

## How It Works

A positional vector is **added** to each token's embedding before feeding it into the Transformer. The vectors have the same dimensionality as token embeddings so they can be summed directly.

### Sinusoidal Positional Encoding (Original — Vaswani et al., 2017)

Uses fixed, deterministic sine and cosine functions of varying frequencies:
- `PE(pos, 2i) = sin(pos / 10000^(2i/d_model))`
- `PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))`

Where `pos` = position, `i` = dimension index, `d_model` = embedding size.

This approach generates a unique encoding for each position and allows the model to potentially generalize to sequence lengths longer than those seen during training. Nearby positions have similar encodings, capturing relative proximity, and relative positions can be inferred via linear transformations.

### Learned Positional Encoding

Position vectors are **trained as parameters** alongside the model, used in BERT and GPT. This is simpler and more flexible but may not generalize well to sequence lengths unseen during training.

## Modern Variants

| Variant | Description | Used In |
|---|---|---|
| **RoPE** (Rotary PE) | Encodes relative positions via rotation matrices applied to query/key vectors | LLaMA, GPT-NeoX |
| **ALiBi** | Adds linear biases to attention scores based on distance; no explicit vectors | BLOOM |
| **Relative PE** | Encodes distance *between* tokens rather than absolute positions | T5, Transformer-XL |

## Key Properties

- Each position gets a **unique encoding** that is consistent across training
- Nearby positions have **similar encodings**, capturing relative proximity
- The choice of encoding method significantly impacts model performance, long-context handling, and generalization to new sequence lengths

**Bottom line:** Positional encoding solves the order-blindness of attention mechanisms and is essential for Transformers to understand sequence structure.

## Key Points
- See summary above for detailed points.

## Related Topics

