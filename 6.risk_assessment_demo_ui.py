
import streamlit as st
import openai
import time
import pandas as pd
from datetime import datetime
import data_info
# --- Streamlit Sidebar ---
st.sidebar.title("⚙️ Settings")
iterations = st.sidebar.slider("Iterations", 1, 5, 3)
openai.api_key = data_info.open_ai_key

# --- Input Article ---
st.title("📄 Regulatory Risk Analyzer (Agentic AI Loop)")
news_article = st.text_area("Paste a news article below:", height=300, value="""PayPal (PYUSD) has officially been cleared of regulatory scrutiny...""")
run_analysis = st.button("🔍 Run Analysis")

# --- Logs ---
log_data = []

def generate_report(article, iteration=1):
    prompt = f"""Act as a regulatory compliance analyst.
Your task is to extract regulatory risks from the article below, categorize them (e.g., SEC, GDPR, AML), and summarize them in a formal report.

Article:
{article}

Iteration {iteration}:
- Extracted Risks:
- Categories:
- Executive Summary:
"""
    start_time = time.time()
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    end_time = time.time()
    tokens_used = response.usage.total_tokens
    return response.choices[0].message.content, tokens_used, end_time - start_time

def critique_response(response):
    prompt = f"""Review the following risk assessment report:
{response}

Critique it: Did it miss any potential risks? Is the categorization appropriate? Suggest improvements."""
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    return response.choices[0].message.content, response.usage.total_tokens

if run_analysis:
    report = ""
    feedback = ""
    total_tokens = 0

    with st.spinner("Analyzing..."):
        for i in range(1, iterations + 1):
            iteration_log = {"Iteration": i, "Timestamp": datetime.now().isoformat()}

            if i == 1:
                report, tokens, duration = generate_report(news_article, i)
                iteration_log["Action"] = "Initial Report"
            else:
                feedback, tokens_fb = critique_response(report)
                report, tokens, duration = generate_report(news_article + "\n\nCritique Feedback:\n" + feedback, i)
                iteration_log["Action"] = "Refined w/ Critique"
                total_tokens += tokens_fb
                iteration_log["Feedback"] = feedback

            iteration_log["Report"] = report
            iteration_log["Tokens"] = tokens
            iteration_log["Time"] = round(duration, 2)
            total_tokens += tokens
            log_data.append(iteration_log)

            with st.expander(f"📘 Iteration {i} Summary"):
                st.write(report)
                if i > 1:
                    st.info(f"🧠 GPT Feedback:{feedback}")

    # --- Show Logs ---
    df = pd.DataFrame(log_data)
    st.subheader("📊 Iteration Metrics")
    st.dataframe(df[["Iteration", "Action", "Tokens", "Time"]])

    st.success(f"✅ Completed {iterations} iterations. Total Tokens Used: {total_tokens}")
