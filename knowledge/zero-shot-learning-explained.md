# Zero-Shot Learning Explained

**Created**: 2026-06-01
**Updated**: 2026-06-01
**Tags**: machine learning, zero-shot learning, classification, [[Artificial Intelligence]], neural networks

## Summary
# Zero-Shot Learning

## Direct Answer
Zero-shot learning (ZSL) is a machine learning paradigm where a model can recognize or classify **objects/categories it has never seen during training**, by leveraging semantic knowledge (e.g., attributes, descriptions, or embeddings) to bridge known and unknown classes.

---

## Key Facts

- **Core idea:** Transfer knowledge from *seen* (training) classes to *unseen* (test) classes without any labeled examples of the unseen classes.
- **Semantic embeddings:** Models use auxiliary information — such as word vectors, attribute vectors, or textual descriptions — to relate new classes to learned ones.
- **Example:** A model trained on "horses" and "zebras" can recognize a "mule" by understanding shared attributes (four legs, mane, hooves).
- **Contrast with few-shot learning:** Few-shot learning requires a *small* number of examples; zero-shot requires *none*.
- **Common approaches include:**
  - Attribute-based models (e.g., predicting visual attributes)
  - Embedding-space alignment (mapping visual and semantic spaces together)
  - Generative models (synthesizing features for unseen classes)
- **Evaluation:** Models are tested on classes entirely absent from the training set.

---

## Relevant Subtopics

### Generalized Zero-Shot Learning (GZSL)
A harder, more realistic variant where the model must classify among **both seen and unseen classes** at test time — not just unseen ones.

### Semantic Spaces
Auxiliary information is critical. Common sources include:
- **Word embeddings** (Word2Vec, GloVe)
- **Human-defined attributes** (color, shape, texture)
- **Natural language descriptions**

### Key Challenges
- **Hubness problem:** Some points in high-dimensional embedding space become nearest neighbors too frequently.
- **Domain shift:** The semantic-to-visual mapping learned on seen classes may not transfer perfectly.
- **Bias toward seen classes** in GZSL settings.

### Real-World Applications
- Image classification with novel categories
- Natural language processing (e.g., classifying unseen intents)
- Medical diagnosis (rare diseases with no training samples)
- Object detection in robotics

---

## Summary Table

| Aspect | Detail |
|---|---|
| Training data needed | Only for *seen* classes |
| Key requirement | Semantic/auxiliary descriptions |
| Goal | Classify unseen categories |
| Related paradigms | Few-shot, transfer learning |

> **Bottom line:** Zero-shot learning enables AI models to generalize beyond their training data by reasoning about semantic relationships — a step toward more human-like generalization.

## Key Points
- See summary above for detailed points.

## Related Topics
[[Artificial Intelligence]]