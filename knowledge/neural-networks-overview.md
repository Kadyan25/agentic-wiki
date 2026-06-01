# Neural Networks Overview

**Created**: 2026-06-01
**Updated**: 2026-06-01
**Tags**: machine learning, [[Artificial Intelligence]], deep learning, neural networks, algorithms

## Summary
# Neural Networks: A Brief Overview

A neural network is a computational model inspired by the human brain, consisting of interconnected layers of nodes (neurons) that learn patterns from data to make predictions or decisions.

## Key Facts

- **Inspired by biology**: Mimics the structure of biological neurons and synaptic connections in the brain
- **Basic unit**: A single neuron receives inputs, applies a weight, adds a bias, and passes the result through an activation function
- **Learning mechanism**: Networks learn by adjusting weights using backpropagation and an optimization algorithm like gradient descent
- **Loss function**: Measures how far predictions are from correct answers; the network minimizes this during training
- **Universal approximators**: Theoretically capable of approximating any continuous function given enough neurons
- **Activation functions**: Non-linear functions (ReLU, Sigmoid, Tanh) that allow networks to learn complex patterns

## Core Structure

**Input Layer** → receives raw data | **Hidden Layer(s)** → extracts and transforms features | **Output Layer** → produces final prediction

The depth of hidden layers defines "deep learning."

## Types of Neural Networks

| Type | Primary Use |
|------|------------|
| **ANN (Feedforward)** | General classification/regression |
| **CNN** | Image recognition |
| **RNN/LSTM** | Sequential and time-series data |
| **Transformer** | Natural language processing |

## Training Process

1. Forward pass → compute predictions
2. Calculate loss/error
3. Backward pass → compute gradients via backpropagation
4. Update weights via optimizer

## Key Challenges

- **Overfitting**: When a model memorizes training data but fails on new data; addressed with dropout and regularization
- **Vanishing gradients**: Gradients shrink in deep networks; solved by ReLU and batch normalization
- **Computational cost**: Requires significant hardware (GPUs/TPUs)

## Quick Summary

Neural networks are powerful, flexible models that learn representations from data through layered transformations. They form the foundation of modern AI applications, from image recognition to language generation. Think of them as a chain of filters—each layer refines raw information into increasingly abstract and useful representations.

## Key Points
- See summary above for detailed points.

## Related Topics
[[Artificial Intelligence]]