# Dropout Regularization Technique

**Created**: 2026-06-01
**Updated**: 2026-06-01
**Tags**: machine learning, neural networks, regularization, dropout, deep learning

## Summary
# Dropout Regularisation

## Direct Answer
Dropout regularisation is a technique used in training neural networks to **prevent overfitting** by randomly "dropping out" (deactivating) a proportion of neurons during each training step, forcing the network to learn more robust, generalised representations.

---

## Key Facts

- **Proposed by**: Srivastava et al. (2014) in the paper *"Dropout: A Simple Way to Prevent Neural Networks from Overfitting"*
- **Mechanism**: During each training iteration, each neuron is independently set to zero with a probability **p** (commonly 0.5 for hidden layers, 0.1–0.2 for input layers)
- **At inference time**: All neurons are active, but their weights are scaled down by factor **(1 − p)** to compensate for the larger number of active units
- **Effect**: Acts as training an **ensemble** of many different network architectures simultaneously
- **No computational overhead** at inference time

---

## How It Works

1. For each training batch, randomly select neurons to deactivate
2. Forward and backward passes are performed with the reduced network
3. Dropped neurons contribute **no gradient** updates in that pass
4. Each training step uses a **different sub-network**

---

## Key Subtopics

### Why It Prevents Overfitting
- Prevents neurons from **co-adapting** too strongly to each other
- Forces individual neurons to learn **independently useful** features
- Acts as implicit **model averaging**

### Variants
| Variant | Description |
|---|---|
| **Standard Dropout** | Random neuron deactivation |
| **Inverted Dropout** | Scales activations during training (most common in practice) |
| **DropConnect** | Drops individual weights rather than neurons |
| **Spatial Dropout** | Drops entire feature maps (used in CNNs) |
| **Variational Dropout** | Bayesian interpretation of dropout |

### Hyperparameter: Drop Rate (p)
- Too **high**: underfitting (too much information lost)
- Too **low**: insufficient regularisation effect
- Typical values: **0.2–0.5**

---

## Limitations
- Increases **training time** (requires more epochs to converge)
- Less effective in **small datasets** or shallow networks
- Largely **superseded by batch normalisation** in some modern architectures

---

## Summary
Dropout is a simple yet powerful regularisation method that improves generalisation by introducing noise during training, effectively preventing neural networks from memorising training data.

## Key Points
- See summary above for detailed points.

## Related Topics

