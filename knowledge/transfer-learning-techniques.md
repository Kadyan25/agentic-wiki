# Transfer Learning Techniques

**Created**: 2026-06-01
**Updated**: 2026-06-01
**Tags**: machine learning, deep learning, model reuse, neural networks, feature extraction

## Summary
# Transfer Learning Techniques

Transfer learning is a machine learning approach where a model trained on one task is **reused as the starting point** for a model on a different but related task, saving time and computational resources while improving performance.

## Key Facts
- **Core Idea:** Leverage knowledge from pre-trained models rather than training from scratch
- **Most common in:** Computer vision (CNNs) and NLP (transformers like BERT, GPT)
- **Primary benefit:** Works exceptionally well with **limited labeled data**
- **Two components:** A *source domain* (where knowledge comes from) and a *target domain* (where it's applied)
- Reduces training time and data requirements significantly
- Popular pre-trained models include ImageNet-trained CNNs and [[Large Language Models]] like GPT

## Main Techniques

### Feature Extraction
- Freeze all pre-trained model weights
- Use the model as a **fixed feature extractor**
- Only train a new output layer/classifier for the new task
- Best when: target dataset is small and similar to source domain

### Fine-Tuning
- Unfreeze some or all layers of the pre-trained model
- **Retrain with a low learning rate** on the new dataset
- Allows the model to adapt deeper representations to the new domain
- Best when: you have moderate data and need higher accuracy or face moderate domain differences

### Frozen Base + Trainable Head
- A hybrid approach: freeze early layers, unfreeze later layers
- Early layers capture **general features** (edges, shapes); later layers capture **task-specific features** (objects)
- Common pattern in CNNs

### Domain Adaptation
- Addresses **domain shift** between source and target data
- Techniques include adversarial training (e.g., DANN) and distribution alignment
- Common in cross-lingual NLP tasks and synthetic-to-real vision applications
- Example: Model trained on synthetic images adapted to real-world images

### Multi-Task Learning
- Train a single model on **multiple related tasks simultaneously**
- Shared layers learn general representations; task-specific heads specialize
- Improves generalization across all tasks

### Zero-Shot / Few-Shot Learning
- Model generalizes to **new tasks with little or no labeled data**
- Relies on strong pre-training (e.g., GPT-4, CLIP)
- Prompted or conditioned at inference time

## Popular Pre-Trained Models
**Vision:** ResNet, VGG, EfficientNet, ViT  
**NLP:** BERT, GPT, RoBERTa, T5  
**Multimodal:** CLIP, Flamingo, DALL·E

## When to Use Transfer Learning
✅ Small or medium-sized target dataset  
✅ Limited computational resources  
✅ Source and target tasks share meaningful structure  
❌ Avoid if domains are highly dissimilar (risk of negative transfer)

Transfer learning dramatically **reduces the cost of building AI systems** by reusing learned knowledge, making it one of the most practical and widely adopted techniques in modern deep learning.

## Key Points
- See summary above for detailed points.

## Related Topics
[[Large Language Models]]