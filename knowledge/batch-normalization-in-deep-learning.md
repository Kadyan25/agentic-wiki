# Batch Normalization in Deep Learning

**Created**: 2026-06-01
**Updated**: 2026-06-01
**Tags**: batch normalization, neural networks, deep learning, training, normalization techniques

## Summary
# Batch Normalisation in Deep Learning

Batch Normalisation (BatchNorm) is a technique that normalises the inputs to each layer within a mini-batch during training, stabilising and accelerating the learning process in deep neural networks.

## How It Works
1. **Compute mini-batch statistics** – Calculate the mean (μ) and variance (σ²) of each feature across the current mini-batch.
2. **Normalise** – Subtract the mean and divide by the standard deviation plus a small constant ε for numerical stability: `x̂ = (x − μ_B) / √(σ²_B + ε)`
3. **Scale & Shift** – Apply learnable parameters γ (scale) and β (shift) to restore representational power: `y = γx̂ + β`. This allows the network to undo normalisation if needed.

## Key Benefits
- **Faster training** – Allows higher learning rates and faster convergence.
- **Reduces internal covariate shift** – Stabilises the distribution of layer inputs during training.
- **Mitigates vanishing/exploding gradients** – Improves gradient flow through the network.
- **Acts as regularisation** – Reduces dependency on dropout and makes networks less sensitive to weight initialisation.

## Training vs. Inference
During training, mean and variance are computed per mini-batch. During inference, a running (population) mean and variance—accumulated during training—are used instead.

## Placement in Networks
Batch normalisation is typically applied after a linear/convolutional layer and before the activation function, though post-activation placement is also commonly used.

## Limitations
- Performance degrades with very small batch sizes, as mean/variance estimates become noisy.
- Introduces batch dependency, making it less effective for recurrent neural networks (RNNs).

## Related Normalisation Techniques
| Technique | Normalises Over |
|---|---|
| **Batch Norm** | Batch dimension |
| **Layer Norm** | Feature dimension (per sample) |
| **Instance Norm** | Spatial dimensions (per sample) |
| **Group Norm** | Groups of channels |

Layer Norm and Group Norm are preferred for RNNs, Transformers, and scenarios with small batch sizes, while Instance Norm is particularly useful for style transfer tasks.

## Key Takeaway
Introduced by Ioffe & Szegedy in 2015, Batch Normalisation is a foundational technique in modern deep learning that makes training deeper networks more stable and efficient by controlling the statistical properties of intermediate layer activations with minimal computational overhead.

## Key Points
- See summary above for detailed points.

## Related Topics

