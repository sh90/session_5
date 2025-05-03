#pip install seaborn openai streamlit matplotlib gymnasium
"""
A working RL agent solving FrozenLake with GPT-4o as a reflective coach.

GPT’s natural language feedback guides exploration dynamically.

Visualization of reward trends and the learned policy grid.

Tabular history of feedback for analysis.

"""


import streamlit as st
import gymnasium as gym
import numpy as np
import openai
import matplotlib.pyplot as plt
import seaborn as sns
import time
import pandas as pd
import data_info

# ---- OpenAI API Key ----
openai.api_key = data_info.open_ai_key

# ---- Reward Shaping Wrapper ----
class RewardShapingWrapper(gym.Wrapper):
    def __init__(self, env):
        super().__init__(env)

    def step(self, action):
        obs, reward, terminated, truncated, info = self.env.step(action)
        if reward == 0.0:  # No reward if the agent doesn't reach the goal
            reward = -0.01  # Small negative reward for each non-terminal action
        return obs, reward, terminated, truncated, info

# ---- Environment Setup ----
base_env = gym.make("FrozenLake-v1", is_slippery=False, map_name="4x4")  # Make environment non-slippery
env = RewardShapingWrapper(base_env)  # Apply reward shaping

n_states = env.observation_space.n
n_actions = env.action_space.n
action_names = ["←", "↓", "→", "↑"]

# ---- Hyperparameters ----
episodes = st.sidebar.slider("Episodes", 1, 100, 20)
max_steps = st.sidebar.slider("Max Steps", 10, 200, 100)
alpha = 0.1
gamma = 0.99
epsilon = st.sidebar.slider("Initial ε (exploration)", 0.1, 1.0, 0.8)
epsilon = round(epsilon, 2)

q_table = np.zeros((n_states, n_actions))
rewards = []
feedback_history = []

# ---- GPT Feedback and Adjustment ----
def gpt_reflect_and_adjust(log):
    global epsilon
    prompt = f"""
You're coaching a reinforcement learning agent navigating a frozen lake grid (goal: reach G without falling into holes).

Episode Summary:
- Reward: {log['reward']}
- Steps: {log['steps']}
- Outcome: {"Success" if log['reward'] > 0 else "Failure"}

Should the agent explore more (increase ε) or exploit more (decrease ε)? Give feedback and suggest a next step.
"""
    try:

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )

        feedback = response.choices[0].message.content.strip()

        # Adjust epsilon based on feedback
        if "explore more" in feedback.lower():
            epsilon = min(1.0, epsilon + 0.05)
        elif "be more greedy" in feedback.lower() or "exploit more" in feedback.lower():
            epsilon = max(0.01, epsilon - 0.05)

        return feedback
    except Exception as e:
        return f"GPT Error: {e}"

# ---- Streamlit UI ----
st.title("GPT-Guided Reinforcement Learning on FrozenLake")

# ---- Training Loop ----
for ep in range(episodes):
    state, _ = env.reset()
    total_reward = 0

    for step in range(max_steps):
        if np.random.rand() < epsilon:
            action = env.action_space.sample()
        else:
            action = np.argmax(q_table[state])

        next_state, reward, terminated, truncated, _ = env.step(action)
        done = terminated or truncated

        # Q-learning update
        q_table[state, action] += alpha * (
            reward + gamma * np.max(q_table[next_state]) - q_table[state, action]
        )

        total_reward += reward
        state = next_state

        with st.empty():
            st.text(f"Episode {ep + 1}, Step {step + 1} | State: {state}, ε: {epsilon:.2f}")
            time.sleep(0.05)

        if done:
            break

    log = {"episode": ep + 1, "reward": total_reward, "steps": step + 1}
    reflection = gpt_reflect_and_adjust(log)
    feedback_history.append({
        "Episode": ep + 1,
        "Reward": total_reward,
        "Steps": step + 1,
        "ε After GPT": round(epsilon, 2),
        "GPT Reflection": reflection
    })
    rewards.append(total_reward)

    with st.expander(f"📘 Episode {ep + 1} Summary"):
        st.write(f"**Reward**: {total_reward}")
        st.write(f"**Steps**: {step + 1}")
        st.write(f"**ε after GPT**: {epsilon:.2f}")
        st.info(f"🧠 GPT-4o Feedback: {reflection}")

# ---- Plot Reward Trend ----
fig, ax = plt.subplots()
ax.plot(rewards, marker='o')
ax.set_title("Reward Over Episodes")
ax.set_xlabel("Episode")
ax.set_ylabel("Reward")
st.pyplot(fig)

# ---- Show GPT Reflection Table ----
df_feedback = pd.DataFrame(feedback_history)
st.subheader("🗂 GPT Reflection History")
st.dataframe(df_feedback)

# ---- Visualize Final Policy ----
def get_policy(q_table):
    policy = np.argmax(q_table, axis=1)
    return np.array([action_names[a] for a in policy]).reshape(4, 4)

policy_grid = get_policy(q_table)
fig2, ax2 = plt.subplots()
sns.heatmap(np.max(q_table, axis=1).reshape(4, 4), annot=policy_grid, fmt='', cmap="YlGnBu", cbar=True, ax=ax2)
ax2.set_title("🧭 Final Policy (Best Action per Cell)")
st.pyplot(fig2)
