# Recurrent Neural Networks Explained

**Created**: 2026-06-01
**Updated**: 2026-06-01
**Tags**: deep learning, neural networks, machine learning, rnn, architecture

## Summary
# Recurrent Neural Networks (RNNs)

## Direct Answer
A **Recurrent Neural Network (RNN)** is a type of artificial neural network designed to process **sequential or time-series data** by maintaining a hidden "memory" state that captures information from previous inputs, allowing it to recognize patterns across time.

---

## Key Facts

- **Core Mechanism:** Unlike standard feedforward networks, RNNs have **feedback loops** — the output from a previous step is fed back as input to the current step.
- **Hidden State:** A vector called the *hidden state* acts as the network's memory, updated at each time step.
- **Shared Weights:** The same weights are applied at every time step, making the model parameter-efficient for sequences.
- **Input Types:** Well-suited for text, speech, audio, video, and time-series data.
- **Training:** Trained using **Backpropagation Through Time (BPTT)**, an extension of standard backpropagation.

---

## Key Subtopics

### ⚠️ Common Challenges
- **Vanishing Gradient Problem:** Gradients shrink exponentially over long sequences, making it hard to learn long-range dependencies.
- **Exploding Gradient Problem:** Gradients can grow uncontrollably, destabilizing training.

### 🔧 Popular Variants
| Variant | Purpose |
|---|---|
| **LSTM** (Long Short-Term Memory) | Handles long-range dependencies via gating mechanisms |
| **GRU** (Gated Recurrent Unit) | Simplified version of LSTM, computationally lighter |
| **Bidirectional RNN** | Processes sequences in both forward and backward directions |

### 🚀 Common Applications
- Natural Language Processing (NLP)
- Machine translation
- Speech recognition
- Sentiment analysis
- Time-series forecasting

### 📉 Modern Context
- RNNs have been **largely superseded** by **Transformer-based models** (e.g., GPT, BERT) in NLP tasks, as Transformers handle long-range dependencies more effectively and parallelize better during training.

---

## Summary
> An RNN is a neural network with loops that allow information to persist across time steps, making it powerful for sequential data — though its limitations with long sequences led to the development of LSTMs, GRUs, and eventually Transformers.

## Key Points
- See summary above for detailed points.

## Related Topics

