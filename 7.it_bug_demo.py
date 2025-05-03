import openai
import pandas as pd
import os
import time
import data_info

openai.api_key = data_info.open_ai_key

#  Sample error log
error_log = """
Traceback (most recent call last):
  File "server.py", line 42, in <module>
    result = handler.process(request)
  File "handler.py", line 88, in process
    db.write(data)
ConnectionError: Failed to connect to database.
"""

#  CSV log file
log_file = "bug_diagnosis_log.csv"

# 📊 Initialize the log file if needed
if not os.path.exists(log_file):
    df_init = pd.DataFrame(columns=[
        "Iteration", "Root_Cause", "Suggested_Fix", "Critique",
        "Prompt_Tokens", "Completion_Tokens", "Total_Tokens"
    ])
    df_init.to_csv(log_file, index=False)


# ✍️ Function to run AI diagnosis and fix suggestion
def diagnose_bug(log, iteration=1, feedback=""):
    prompt = f"""
You are a senior backend engineer. Analyze the following error log, identify the root cause, and suggest a fix.

Error Log:
{log}

{'Here is a critique of the previous output that should be addressed:' + feedback if feedback else ''}

Iteration {iteration}:
- Root Cause:
- Suggested Fix:
"""
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    content = response.choices[0].message.content
    usage = response.usage
    return content, usage


# 🔍 Function for critique analysis of diagnosis/fix
def critique_bug_fix(response):
    prompt = f"""
Analyze the following diagnosis and fix:
{response}

Critique: Is the fix safe and efficient? Are edge cases handled? Suggest improvements.
"""
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    content = response.choices[0].message.content
    return content


#  Function to extract root cause and suggested fix from AI output
def extract_bug_sections(text):
    parts = {"Root Cause": "", "Suggested Fix": ""}
    current = None
    for line in text.split("\n"):
        line = line.strip()
        if "Root Cause" in line:
            current = "Root Cause"
        elif "Suggested Fix" in line:
            current = "Suggested Fix"
        elif current:
            parts[current] += line + " "
    return parts["Root Cause"].strip(), parts["Suggested Fix"].strip()


# 📦 Log the results of each iteration into CSV
def log_iteration(iteration, root_cause, suggested_fix, critique, usage):
    df = pd.read_csv(log_file)
    new_row = {
        "Iteration": iteration,
        "Root_Cause": root_cause,
        "Suggested_Fix": suggested_fix,
        "Critique": critique,
        "Prompt_Tokens": usage.prompt_tokens,
        "Completion_Tokens": usage.completion_tokens,
        "Total_Tokens": usage.total_tokens
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(log_file, index=False)


# 🔁 Self-improvement loop: Multiple iterations of AI diagnosis
feedback = ""
for i in range(1, 4):  # 3 iterations
    print(f"\n--- Iteration {i} ---")
    diagnosis, usage = diagnose_bug(error_log, i, feedback)
    print("\n[Diagnosis Output]:\n", diagnosis)

    root_cause, suggested_fix = extract_bug_sections(diagnosis)

    feedback = critique_bug_fix(diagnosis)
    print("\n[Critique Feedback]:\n", feedback)

    log_iteration(i, root_cause, suggested_fix, feedback, usage)

    time.sleep(2)  # To avoid API rate limit
