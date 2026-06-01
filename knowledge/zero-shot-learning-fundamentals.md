# Zero-Shot Learning Fundamentals

**Created**: 2026-06-01
**Updated**: 2026-06-01
**Tags**: machine learning, classification, transfer learning, [[Artificial Intelligence]], deep learning

## Summary
# Zero-Shot Learning

## Direct Answer
Zero-shot learning (ZSL) is a machine learning paradigm where a model can recognize or classify objects/concepts it has **never seen during training**, by leveraging auxiliary information (such as semantic descriptions or attributes) to bridge known and unknown categories.

---

## Key Facts
- **Core Idea:** Instead of learning from labeled examples of every class, the model learns to generalize using *side information* (e.g., word embeddings, attribute vectors, or textual descriptions).
- **Training vs. Inference Gap:** The model is trained on *seen* classes but evaluated on *unseen* classes at test time.
- **Semantic Transfer:** Knowledge is transferred via a shared semantic space (e.g., "a zebra is like a horse with stripes").
- **No Task-Specific Examples Needed:** Unlike few-shot learning, zero-shot requires *zero* examples of the target class.
- **Common Auxiliary Information Types:**
  - Attribute vectors (e.g., color, shape, size)
  - Word embeddings (Word2Vec, GloVe)
  - Natural language descriptions
  - Knowledge graphs

---

## Key Subtopics

### 🔁 How It Works
1. Learn a mapping from visual/input features → semantic space during training.
2. At test time, match new inputs to unseen class descriptions in that shared space.

### 📌 Generalized Zero-Shot Learning (GZSL)
A harder variant where the model must classify among **both seen and unseen classes** at inference time, avoiding bias toward seen classes.

### 🧠 Related Concepts
| Concept | Difference from ZSL |
|---|---|
| Few-Shot Learning | Uses a small number of examples per new class |
| Transfer Learning | Fine-tunes on target domain data |
| One-Shot Learning | Uses exactly one example per new class |

### 🛠️ Common Applications
- Image classification (e.g., recognizing rare animal species)
- Natural Language Processing (e.g., zero-shot text classification)
- [[Large Language Models]] (e.g., GPT-style prompting without task fine-tuning)

### ⚠️ Challenges
- **Hubness problem:** Some points in semantic space act as universal nearest neighbors.
- **Domain shift:** Gap between seen and unseen class distributions.
- **Bias toward seen classes** in GZSL settings.

---

## Summary
Zero-shot learning enables AI models to handle novel categories without retraining, making it a powerful tool for scalable, flexible AI systems — especially relevant in the era of large foundation models.

## Key Points
- See summary above for detailed points.

## Related Topics
[[Artificial Intelligence]], [[Large Language Models]]