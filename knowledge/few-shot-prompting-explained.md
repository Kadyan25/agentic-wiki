# Few-Shot Prompting Explained

**Created**: 2026-06-01
**Updated**: 2026-06-01
**Tags**: prompting, machine learning, language models, ai techniques, in-context learning

## Summary
# Few-Shot Prompting

Few-shot prompting is a technique where you provide a language model with **a small number of input-output examples** within the prompt itself to guide the model's behavior and improve response quality — without updating model weights.

## Direct Answer

Few-shot prompting typically means providing **2–10 labeled examples** in the prompt to demonstrate the desired task format, style, or reasoning pattern before asking the model to respond to a new input. Examples act as **implicit instructions**, showing the model what a correct response looks like through in-context learning.

## Key Facts

- **Definition:** Including 2–10 labeled examples in the prompt to demonstrate the desired task format or reasoning pattern.
- **Origin:** Introduced prominently in OpenAI's GPT-3 paper (Brown et al., 2020) as a core in-context learning capability.
- **No training required:** The model learns the task pattern purely from context — no fine-tuning or gradient updates occur.
- **Performance insight:** Quality and relevance of examples matter more than quantity; performance generally improves up to a point as well-chosen examples increase.
- **Example structure:**
  ```
  Input: "The movie was fantastic!" → Sentiment: Positive
  Input: "I hated every minute."    → Sentiment: Negative
  Input: "It was okay, I guess."    → Sentiment: ???
  ```

## Variants

| Type | Examples Provided |
|---|---|
| **Zero-shot** | 0 (instruction only) |
| **One-shot** | 1 example |
| **Few-shot** | 2–10 examples |
| **Many-shot** | 10+ examples |

## How It Works

1. Craft a prompt with example pairs: `Input → Output`
2. Append the new, unanswered input
3. The model infers the pattern and completes the response

## ✅ Benefits

- Improves accuracy on structured or domain-specific tasks
- Reduces ambiguity in expected output format
- Requires no additional compute for training
- Low-cost strategy compared to fine-tuning

## ⚠️ Limitations

- Consumes valuable context window tokens
- Performance is sensitive to example selection and ordering
- Can mislead if examples are poorly chosen
- May not generalize well if examples are unrepresentative
- Less effective for tasks requiring deep reasoning

## 🎯 Best Practices

- Use diverse, representative examples that cover edge cases
- Keep formatting consistent across all examples
- Place the most relevant examples closest to the query
- Avoid examples that introduce bias or ambiguity
- Experiment with example count — more isn't always better

## Use Cases

- Text classification and sentiment analysis
- Translation and reformatting
- Code generation
- Question answering
- Structured data extraction

## 🔗 Related Techniques

| Technique | Description |
|---|---|
| Chain-of-Thought (CoT) | Few-shot examples include reasoning steps |
| Retrieval-Augmented Prompting | Examples pulled dynamically from a database |
| Instruction Tuning | Fine-tuning on examples instead of prompting |

Few-shot prompting is a simple yet powerful tool that bridges the gap between a raw model and a task-specific one, making it a foundational technique in prompt engineering.

## Key Points
- See summary above for detailed points.

## Related Topics

