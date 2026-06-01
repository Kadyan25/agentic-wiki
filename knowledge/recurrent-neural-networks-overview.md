# Recurrent [[Neural Networks Overview]]

**Created**: 2026-06-01
**Updated**: 2026-06-01
**Tags**: recurrent neural networks, deep learning, machine learning, neural architecture, sequence processing

## Summary
# Recurrent Neural Networks (RNNs)

## Direct Answer
A **Recurrent Neural Network (RNN)** is a type of artificial neural network designed to process **sequential or time-series data** by maintaining a hidden "memory" state that captures information from previous inputs in the sequence.

---

## Key Facts
- **Core Mechanism:** Unlike feedforward networks, RNNs have **feedback loops** — the output from a previous step is fed back as input to the current step.
- **Hidden State:** A hidden state vector `h_t` is updated at each time step, acting as the network's short-term memory.
- **Weight Sharing:** The same weights are applied at every time step, making the network parameter-efficient.
- **Training:** Trained using **Backpropagation Through Time (BPTT)**, which unrolls the network across time steps.
- **Common Challenges:**
  - **Vanishing gradients** — gradients shrink exponentially over long sequences, limiting long-term memory.
  - **Exploding gradients** — gradients grow uncontrollably (mitigated by gradient clipping).

---

## Key Variants
| Variant | Purpose |
|---|---|
| **LSTM** (Long Short-Term Memory) | Solves vanishing gradients with gating mechanisms |
| **GRU** (Gated Recurrent Unit) | Simplified LSTM with fewer parameters |
| **Bidirectional RNN** | Processes sequences in both forward and backward directions |

---

## Common Applications
- Natural Language Processing (NLP): text generation, translation, sentiment analysis
- Speech recognition
- Time-series forecasting
- Music generation
- Video analysis

---

## Simple Formula
At each time step `t`:

> **h_t = f(W · h_(t-1) + U · x_t + b)**

Where:
- `h_t` = current hidden state
- `x_t` = current input
- `W`, `U` = learned weight matrices
- `b` = bias
- `f` = activation function (e.g., tanh)

---

## Key Takeaway
RNNs are powerful for **sequential data** because they maintain context across time steps. However, due to vanishing gradient issues, **LSTMs and GRUs** are more commonly used in modern applications, with **Transformer-based models** now dominating many sequence tasks.

## Key Points
- See summary above for detailed points.

## Related Topics
[[Neural Networks Overview]]