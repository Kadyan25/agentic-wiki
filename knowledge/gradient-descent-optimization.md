# Gradient Descent Optimization

**Created**: 2026-06-01
**Updated**: 2026-06-01
**Tags**: machine learning, optimization, algorithms, neural networks, calculus

## Summary
# Gradient Descent Optimisation

Gradient descent is an iterative optimisation algorithm used to minimise a function (typically a loss/cost function in machine learning) by repeatedly updating parameters in the direction of the **negative gradient** — the direction of steepest descent.

## Core Mechanism

The algorithm works by following these steps:
1. **Initialise** parameters (weights) randomly
2. **Compute the gradient** (partial derivatives) of the loss function with respect to each parameter
3. **Update parameters** using the rule: `θ = θ - α · ∇J(θ)`
   - `θ` = model parameters
   - `α` = learning rate (step size)
   - `∇J(θ)` = gradient of the loss function
4. **Repeat** until convergence (parameter updates become negligibly small)

The core principle is that moving opposite to the gradient direction leads toward a local minimum.

## Key Concepts

**Learning Rate (α):** Controls step size. Too large causes overshooting and instability; too small causes slow convergence. Tuning this hyperparameter is critical.

**Loss Surface:** The multidimensional landscape being navigated; gradient descent explores this space seeking the global minimum.

**Differentiability:** Requires loss functions to be differentiable to compute gradients.

**Convergence:** Success depends on whether the algorithm reaches optimal or near-optimal solutions.

## Main Variants

| Variant | Description | Trade-off |
|---|---|---|
| **Batch GD** | Uses entire dataset per update | Stable but slow; memory-heavy |
| **Stochastic GD (SGD)** | Uses one sample per update | Fast but noisy updates |
| **Mini-Batch GD** | Uses small subsets (32–256 samples) | Best balance; most widely used |

## Key Challenges

- **Local Minima & Saddle Points:** Non-convex loss surfaces (common in deep learning) can trap the algorithm in suboptimal regions
- **Vanishing/Exploding Gradients:** Gradients become too small or large to drive effective learning, especially in deep networks
- **Learning Rate Tuning:** Requires careful hyperparameter selection
- **Convergence Speed:** Varies significantly with problem structure and variant choice

## Advanced Optimisers

Built on gradient descent principles, these improve performance:
- **Momentum:** Accumulates velocity to accelerate through flat regions and escape local minima
- **RMSProp:** Adapts learning rate per parameter using a running average of squared gradients
- **Adam:** Combines momentum and RMSProp; the most popular optimizer in modern deep learning

## Key Takeaway

Gradient descent is the backbone of training neural networks and most machine learning models. The choice of variant (SGD, Adam, etc.), learning rate, and potentially learning rate schedules significantly impact both training speed and model quality. For practical applications, mini-batch gradient descent combined with Adam optimization is the standard approach.

## Key Points
- See summary above for detailed points.

## Related Topics

