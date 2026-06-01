# Large Language Model Training Data

**Created**: 2026-06-01
**Updated**: 2026-06-01
**Tags**: [[Large Language Models]], training, text corpora, machine learning, nlp

## Summary
# Large Language Models: Training on Vast Text Corpora

## Direct Answer
Large language models (LLMs) are trained on massive collections of text data sourced from the internet, books, and other repositories, enabling them to learn language patterns, reasoning, and world knowledge at scale.

---

## Key Facts

- **Scale of data**: Training corpora often range from **hundreds of billions to trillions of tokens** (e.g., GPT-3 trained on ~300B tokens; LLaMA 2 on 2T tokens).
- **Data sources** typically include:
  - Web crawls (e.g., Common Crawl)
  - Books and academic papers
  - Code repositories (e.g., GitHub)
  - Wikipedia and curated datasets
- **Tokenization**: Raw text is broken into tokens (words or subword units) before training.
- **Training objective**: Most LLMs use **next-token prediction** (autoregressive) or **masked language modeling** to learn from text.
- **Compute requirements**: Training requires thousands of GPUs/TPUs over weeks or months, costing millions of dollars.
- **Data quality matters**: Filtering, deduplication, and curation significantly impact model performance.

---

## Relevant Subtopics

### 🔹 Data Curation & Preprocessing
Raw corpora undergo cleaning to remove duplicates, low-quality content, and harmful material before training begins.

### 🔹 Model Architecture
Most modern LLMs use the **Transformer architecture**, which leverages self-attention to process and relate tokens across long contexts.

### 🔹 Emergent Capabilities
Training on diverse, large-scale corpora enables emergent abilities such as reasoning, summarization, translation, and code generation — often without task-specific training.

### 🔹 Limitations of Corpus-Based Training
- Models may learn **biases** present in source data.
- Knowledge has a **cutoff date** — models don't learn from events after training.
- No guaranteed factual accuracy (**hallucination** risk).

### 🔹 Notable Models & Their Corpora
| Model | Approx. Training Tokens |
|-------|------------------------|
| GPT-3 | ~300 billion |
| LLaMA 2 | ~2 trillion |
| Gemini Ultra | Undisclosed (multimodal) |

---

## Summary
The breadth and quality of training corpora are foundational to LLM capability. More data generally improves performance, but responsible curation, diversity, and preprocessing are equally critical to building robust, reliable models.

## Key Points
- See summary above for detailed points.

## Related Topics
[[Large Language Models]]