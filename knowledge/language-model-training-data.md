# Language Model Training Data

**Created**: 2026-06-01
**Updated**: 2026-06-01
**Tags**: [[Large Language Models]], training, text corpora, machine learning, nlp

## Summary
# Large Language Models: Training on Vast Text Corpora

## Direct Answer
Large language models (LLMs) are trained on massive datasets of text collected from diverse sources across the internet and other repositories, enabling them to learn language patterns, factual knowledge, and reasoning capabilities at scale.

---

## Key Facts

- **Scale of data**: Training corpora often range from **hundreds of billions to trillions of tokens** (e.g., GPT-3 trained on ~300B tokens; LLaMA 2 on 2T tokens)
- **Data sources** typically include:
  - Web crawls (e.g., Common Crawl)
  - Books and academic literature
  - Wikipedia and curated encyclopedias
  - Code repositories (e.g., GitHub)
  - News articles and forums
- **Preprocessing** is critical — data is filtered for quality, deduplicated, and cleaned to remove toxic or low-quality content
- **Tokenization** converts raw text into numerical tokens before training begins
- Training uses **self-supervised learning**, primarily *next-token prediction* (causal LMs) or *masked token prediction* (e.g., BERT-style models)
- Larger and more diverse corpora generally improve **generalization** across tasks

---

## Relevant Subtopics

### 📦 Data Curation & Quality
Careful selection and filtering of training data significantly impacts model behavior, bias, and performance. Poor-quality data can introduce harmful outputs or misinformation.

### ⚖️ Bias & Ethical Concerns
Training on human-generated text inherits **societal biases**, stereotypes, and potentially copyrighted material, raising legal and ethical questions.

### 🔁 Training Objectives
- **Causal Language Modeling (CLM)**: Predict the next word given prior context (GPT-style)
- **Masked Language Modeling (MLM)**: Predict masked words in context (BERT-style)

### 💻 Computational Requirements
Training LLMs on large corpora demands enormous **compute resources** — thousands of GPUs/TPUs over weeks or months — making it expensive and energy-intensive.

### 🔄 Fine-Tuning vs. Pre-Training
After initial corpus-based pre-training, models are often **fine-tuned** on smaller, task-specific datasets or aligned with human preferences via RLHF (Reinforcement Learning from Human Feedback).

---

## Summary
The breadth and quality of training corpora are foundational to LLM capability. While scale drives performance, responsible data collection, curation, and transparency remain active areas of research and concern.

## Key Points
- See summary above for detailed points.

## Related Topics
[[Large Language Models]]