"""

What the Dashboard Displays:
Iteration Log Table: Displays all iterations with their root cause, suggested fix, peer review, critique, and token usage.

Iteration Selector: A slider allows you to select and view the detailed output of a specific iteration.

Token Usage Plot: A graph that shows the total tokens used per iteration.

Detailed Breakdown: For the selected iteration, the dashboard shows:

Root Cause

Suggested Fix

Peer Review Feedback

Critique

Token Usage Details

"""



import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV log file
log_file = "peer_review_log.csv"
df = pd.read_csv(log_file)

# Set up the page layout
st.set_page_config(page_title="Peer Review Dashboard", layout="wide")

# Title of the dashboard
st.title("🛠️ Peer Review Process – New Employee Code Review")

# Show overview of the iterations
st.write("### Iteration Log")
st.write("The following table shows the details for each iteration of bug diagnosis and code review.")

# Display the iteration logs in a table
st.dataframe(df, use_container_width=True)

# Display detailed output for the selected iteration
st.write("### Detailed Analysis of Each Iteration")
iteration = st.slider("Select Iteration", 1, len(df), len(df))  # Slider to select iteration
selected_data = df[df["Iteration"] == iteration].iloc[0]

st.subheader(f"Iteration {iteration} Analysis")
col1, col2 = st.columns(2)

with col1:
    st.write("**Root Cause**")
    st.success(selected_data["Root_Cause"])

with col2:
    st.write("**Suggested Fix**")
    st.info(selected_data["Suggested_Fix"])

st.write("**Peer Review**")
st.warning(selected_data["Peer_Review"])

st.write("**Critique**")
st.warning(selected_data["Critique"])

# Plot token usage over iterations
st.write("### Token Usage Trend Over Iterations")
fig, ax = plt.subplots(figsize=(8, 5))

# Plotting token usage
iterations = df["Iteration"]
total_tokens = df["Total_Tokens"]

ax.plot(iterations, total_tokens, marker='o', linestyle='-', color='b', label='Total Tokens Used')
ax.set_xlabel("Iterations")
ax.set_ylabel("Total Tokens Used")
ax.set_title("Token Usage per Iteration")
ax.legend()

# Display the plot in the Streamlit app
st.pyplot(fig)

# Display token usage details for the selected iteration
st.write("### Token Usage Details for the Selected Iteration")
st.write(f"**Prompt Tokens**: {selected_data['Prompt_Tokens']}")
st.write(f"**Completion Tokens**: {selected_data['Completion_Tokens']}")
st.write(f"**Total Tokens**: {selected_data['Total_Tokens']}")
