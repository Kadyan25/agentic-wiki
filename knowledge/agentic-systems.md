# Agentic Systems

**Created**: 2026-04-13  
**Updated**: 2026-04-13  
**Tags**: agents, orchestration, llm, autonomy, tools, planning

## Summary
Agentic systems are AI architectures where one or more language models autonomously plan, decide, and act to accomplish complex goals — often using tools, memory, and multi-step reasoning. Unlike single-shot LLM calls, agents operate in loops, observe results, and adapt their behavior.

## Key Points
- An agent = LLM + tools + memory + a goal/loop
- Orchestrator agents coordinate multiple specialized sub-agents (multi-agent systems)
- Agents can use tools: web search, code execution, file I/O, API calls
- Memory types: in-context (prompt), external (files, databases), episodic (conversation history)
- Key patterns: ReAct (Reason + Act), Plan-and-Execute, Reflexion, and tool-use loops
- Challenges: hallucination, infinite loops, tool errors, and context window limits
- Examples: AutoGPT, Claude Code, Devin, and custom orchestration pipelines

## Related Topics
[[Artificial Intelligence]], [[Large Language Models]]
