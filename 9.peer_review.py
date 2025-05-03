import openai
import pandas as pd
import os
import time
import data_info
#  Set your OpenAI API key
openai.api_key = data_info.open_ai_key

# Sample error log (e.g., bug in database connection)
error_log = """
Traceback (most recent call last):
  File "server.py", line 42, in <module>
    result = handler.process(request)
  File "handler.py", line 88, in process
    db.write(data)
ConnectionError: Failed to connect to database.
"""

# Sample initial fix (new employee's submission)
initial_code_fix = """
def connect_to_db():
    try:
        connection = db.connect()
    except ConnectionError:
        print("Connection failed. Retrying...")
        time.sleep(5)
        connection = db.connect()
    return connection
"""

#  CSV log file for storing results
log_file = "peer_review_log.csv"

#  Initialize the log file if needed
if not os.path.exists(log_file):
    df_init = pd.DataFrame(columns=[
        "Iteration", "Root_Cause", "Suggested_Fix", "Peer_Review", "Critique",
        "Prompt_Tokens", "Completion_Tokens", "Total_Tokens"
    ])
    df_init.to_csv(log_file, index=False)


# ️ Function to diagnose bug and suggest a fix
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


#  Peer review function: AI reviews the fix
def peer_review_code(fix):
    prompt = f"""
Review the following code fix and suggest improvements. Provide a detailed critique of its efficiency, safety, and handling of edge cases.

Code Fix:
{fix}
"""
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    content = response.choices[0].message.content
    return content


#  Extract root cause and suggested fix from the AI output
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


#  Log the iteration results into CSV
def log_iteration(iteration, root_cause, suggested_fix, peer_review, critique, usage):
    df = pd.read_csv(log_file)
    new_row = {
        "Iteration": iteration,
        "Root_Cause": root_cause,
        "Suggested_Fix": suggested_fix,
        "Peer_Review": peer_review,
        "Critique": critique,
        "Prompt_Tokens": usage.prompt_tokens,
        "Completion_Tokens": usage.completion_tokens,
        "Total_Tokens": usage.total_tokens
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(log_file, index=False)


# Loop for iterative diagnosis, fix, and peer review
feedback = ""
for i in range(1, 4):  # 3 iterations
    print(f"\n--- Iteration {i} ---")

    # Step 1: Bug diagnosis and fix suggestion
    diagnosis, usage = diagnose_bug(error_log, i, feedback)
    print("\n[Diagnosis Output]:\n", diagnosis)

    root_cause, suggested_fix = extract_bug_sections(diagnosis)

    # Step 2: Peer review the suggested fix
    peer_review = peer_review_code(suggested_fix)
    print("\n[Peer Review Feedback]:\n", peer_review)

    # Step 3: Critique the peer-reviewed fix for improvement
    critique = peer_review  # In this case, we use peer review as the critique

    # Log results for each iteration
    log_iteration(i, root_cause, suggested_fix, peer_review, critique, usage)

    feedback = peer_review  # Pass the peer review feedback to the next iteration for improvement

    time.sleep(2)  # To avoid API rate limit
