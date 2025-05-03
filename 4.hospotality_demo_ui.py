import streamlit as st
import pandas as pd
import data_info
import openai
# 🔑 Set your API key here
openai.api_key = data_info.open_ai_key

st.set_page_config(page_title="AI Review Improvement Dashboard", layout="wide")

st.title("Hospitality AI Agent – Self-Improving Review Analysis")

# Load data
df = pd.read_csv("review_analysis_log.csv")

# Show iteration summary
st.write("### Iteration Log")
st.dataframe(df, use_container_width=True)

# Trend of improvements
st.write("### Top Issues and Suggestions Over Time")
selected_iter = st.slider("Select Iteration", 1, len(df), len(df))
selected_data = df[df["Iteration"] == selected_iter].iloc[0]

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top_Issues")
    st.success(selected_data["Top_Issues"])

with col2:
    st.subheader("Actionable Suggestions")
    st.info(selected_data["Suggestions"])

# Optional: Critique Evolution
st.write("### Critique Feedback")
st.text_area("Critique Notes", selected_data["Critique"], height=200)

