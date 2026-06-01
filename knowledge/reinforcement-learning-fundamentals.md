# Reinforcement Learning Fundamentals

**Created**: 2026-06-01
**Updated**: 2026-06-01
**Tags**: machine learning, reinforcement learning, [[Artificial Intelligence]], algorithms, decision making

## Summary
# Reinforcement Learning

## Direct Answer
Reinforcement learning (RL) is a type of machine learning where an **agent learns to make decisions** by interacting with an environment, receiving feedback in the form of rewards or penalties, with the goal of maximizing cumulative reward over time.

---

## Key Facts
- **Learning paradigm**: Falls between supervised and unsupervised learning — no labeled data, but feedback is provided via a reward signal
- **Core components**:
  - **Agent** — the learner/decision-maker
  - **Environment** — what the agent interacts with
  - **State** — the current situation of the agent
  - **Action** — choices the agent can make
  - **Reward** — feedback signal (positive or negative) after each action
  - **Policy** — the agent's strategy for choosing actions
- **Objective**: Learn an optimal policy that maximizes **cumulative (long-term) reward**
- **Trial and error**: The agent explores actions, observes outcomes, and updates its strategy accordingly
- **Delayed rewards**: Consequences of actions may not be immediately apparent, requiring long-term planning

---

## Key Subtopics

### 🔹 Major Algorithms
- **Q-Learning** — learns the value of actions in given states
- **SARSA** — similar to Q-learning but updates based on the actual action taken
- **Policy Gradient Methods** — directly optimize the policy (e.g., REINFORCE)
- **Actor-Critic Methods** — combines value-based and policy-based approaches (e.g., PPO, A3C)

### 🔹 Exploration vs. Exploitation
A fundamental challenge: the agent must **explore** new actions to discover better rewards while **exploiting** known actions that yield high rewards.

### 🔹 Key Concepts
- **Markov Decision Process (MDP)** — the mathematical framework underlying most RL problems
- **Value Function** — estimates expected future reward from a given state
- **Discount Factor (γ)** — weights future rewards relative to immediate ones

### 🔹 Real-World Applications
- Game playing (Chess, Go, video games)
- Robotics and autonomous control
- Recommendation systems
- Drug discovery and resource management

---

## Summary
> Reinforcement learning enables machines to **learn optimal behavior through experience**, making it powerful for sequential decision-making tasks where explicit instructions are unavailable.

## Key Points
- See summary above for detailed points.

## Related Topics
[[Artificial Intelligence]]