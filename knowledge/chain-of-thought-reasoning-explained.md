# Chain-of-Thought Reasoning Explained

**Created**: 2026-06-01
**Updated**: 2026-06-01
**Tags**: reasoning, ai, llm, cognitive-process, problem-solving

## Summary
# Chain-of-Thought Reasoning

## Direct Answer
Chain-of-thought (CoT) reasoning is a prompting technique for [[Large Language Models]] (LLMs) that encourages the model to produce **intermediate reasoning steps** before arriving at a final answer, mimicking human step-by-step problem solving.

---

## Key Facts

- **Introduced** by Wei et al. (Google Brain, 2022) in the paper *"Chain-of-Thought Prompting Elicits Reasoning in Large Language Models"*
- **Core idea:** Instead of jumping directly to an answer, the model generates a logical sequence of thoughts (a "reasoning chain") that leads to the solution
- **Two main variants:**
  - **Few-shot CoT** – Provide example problems with worked-out reasoning steps in the prompt
  - **Zero-shot CoT** – Simply append a trigger phrase like *"Let's think step by step"* to the prompt
- **Most effective** on large models (typically 100B+ parameters); smaller models show limited benefit
- **Improves performance** on tasks requiring arithmetic, commonsense reasoning, symbolic manipulation, and multi-step logic

---

## Subtopics

### Why It Works
- Forces the model to decompose complex problems into manageable sub-steps
- Reduces errors by making intermediate logic explicit and checkable
- Aligns with how humans externalize reasoning to avoid cognitive overload

### Key Extensions
| Technique | Description |
|---|---|
| **Self-Consistency** | Sample multiple reasoning chains, select the most common answer |
| **Tree of Thoughts (ToT)** | Explore multiple reasoning branches simultaneously |
| **ReAct** | Combines reasoning chains with external tool/action calls |
| **Program-of-Thought** | Generates code as the reasoning chain instead of natural language |

### Limitations
- Can produce **plausible-sounding but incorrect** reasoning ("hallucinated" steps)
- Increased **token usage** raises computational cost
- Model may arrive at the right answer via **flawed reasoning**
- Performance gains are less consistent on non-reasoning tasks

### Applications
- Math word problems
- Multi-hop question answering
- Code generation and debugging
- Scientific and logical reasoning benchmarks (e.g., GSM8K, MATH, BigBench)

---

## Summary
Chain-of-thought reasoning enhances LLM outputs by making the reasoning process transparent and structured. It is one of the most impactful prompting strategies developed for improving AI performance on complex, multi-step tasks.

## Key Points
- See summary above for detailed points.

## Related Topics
[[Large Language Models]]