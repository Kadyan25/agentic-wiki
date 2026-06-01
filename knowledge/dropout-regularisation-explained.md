# Dropout Regularisation Explained

**Created**: 2026-06-01
**Updated**: 2026-06-01
**Tags**: dropout, regularization, neural-networks, deep-learning, overfitting

## Summary
# Dropout Regularisation

## Direct Answer
Dropout regularisation is a technique used in training neural networks to **prevent overfitting** by randomly "dropping out" (deactivating) a proportion of neurons during each training step, forcing the network to learn more robust, generalised representations.

---

## How It Works
- During **training**, each neuron is independently set to zero with a probability *p* (the dropout rate), typically between 0.2 and 0.5.
- During **inference/testing**, all neurons are active, but their outputs are scaled down by factor *(1 − p)* to compensate for the larger number of active units.
- This process is **random and different** for each training batch.

---

## Key Facts
- **Introduced by**: Srivastava et al. (2014) in *"Dropout: A Simple Way to Prevent Neural Networks from Overfitting"*
- **Common dropout rates**: 0.5 for hidden layers; 0.2 for input layers
- **Effect**: Acts as an ensemble method — training many different "thinned" networks simultaneously
- **Prevents co-adaptation**: Neurons cannot rely on specific other neurons, encouraging independent feature learning
- **Inverted dropout**: A common modern variant that scales activations *during training* (rather than at test time) for cleaner implementation

---

## Why It Reduces Overfitting
- Reduces complex co-dependencies between neurons
- Introduces **noise** into the training process, acting as a form of data augmentation
- Approximates averaging over an exponential number of different network architectures

---

## Relevant Subtopics
| Subtopic | Description |
|---|---|
| **Overfitting** | The problem dropout is designed to solve |
| **Regularisation** | Broader family of techniques (L1, L2, dropout) |
| **Batch Normalisation** | Another normalisation technique, sometimes used instead of/alongside dropout |
| **Monte Carlo Dropout** | Using dropout at inference time to estimate model uncertainty |
| **Spatial Dropout** | Variant for CNNs that drops entire feature maps |

---

## Limitations
- Increases **training time** (requires more epochs to converge)
- Less effective in **small datasets** or shallow networks
- Can be **suboptimal for CNNs** compared to other regularisation methods (e.g., batch norm)

## Key Points
- See summary above for detailed points.

## Related Topics

