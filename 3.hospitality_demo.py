
import openai
import pandas as pd
import os
import time
import data_info
#  Set your API key here
openai.api_key = data_info.open_ai_key


# CSV log file
log_file = "review_analysis_log.csv"

# 📊 Create the log file if it doesn't exist
if not os.path.exists(log_file):
    df_init = pd.DataFrame(columns=[
        "Iteration", "Sentiment_Summary", "Top_Issues", "Suggestions", "Critique"
    ])
    df_init.to_csv(log_file, index=False)


# ✍️ Function to run the AI analysis
def analyze_reviews(reviews, iteration=1, feedback=""):
    prompt = f"""
    You are a hotel operations analyst. Analyze the following guest reviews. Categorize sentiments by theme (e.g., service, cleanliness, amenities), and suggest actionable improvements.
    
    Guest Reviews:
    {reviews}
    
    {'Here is a critique of the previous output that should be addressed:' + feedback if feedback else ''}
    
    Iteration {iteration}:
    - Sentiment Summary by Theme:
    - Top Issues:
    - Actionable Suggestions:
    """
    response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )

    return response.choices[0].message.content


# 🔍 Function to generate critique
def critique_analysis(response):
    prompt = f"""
Review the following sentiment analysis report and critique it:
{response}

Evaluate: Are the themes well captured? Are the suggestions truly actionable and practical? What is missing or inaccurate?
"""
    response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )

    return response.choices[0].message.content


# 🧠 Simple parser to split response into sections
def extract_sections(text):
    parts = {"Sentiment Summary": "", "Top Issues": "", "Actionable Suggestions": ""}
    current = None
    for line in text.split("\n"):
        line = line.strip()
        if "Sentiment Summary" in line:
            current = "Sentiment Summary"
        elif "Top Issues" in line:
            current = "Top Issues"
        elif "Actionable Suggestions" in line:
            current = "Actionable Suggestions"
        elif current:
            parts[current] += line + " "
    return parts["Sentiment Summary"].strip(), parts["Top Issues"].strip(), parts["Actionable Suggestions"].strip()


# 📦 Save iteration to CSV
def log_iteration(iteration, summary, issues, suggestions, critique):
    df = pd.read_csv(log_file)
    new_row = {
        "Iteration": iteration,
        "Sentiment_Summary": summary,
        "Top_Issues": issues,
        "Suggestions": suggestions,
        "Critique": critique
    }
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(log_file, index=False)

#  Sample customer reviews
customer_reviews = """
1.I had an amazing time staying here! The room was spacious and clean, with all the amenities I needed. The staff was incredibly friendly and went out of their way to make sure I had everything I needed.
2.The hotel was okay. The room was clean, and the staff was nice, but nothing stood out to me. The location was convenient, though it wasn’t as central as I would have liked.
3.I’m really disappointed with my stay. The room was not as clean as I expected, and the bathroom had some issues with plumbing.
4.The hotel was fantastic! Everything from check-in to check-out was seamless. The rooms were large, very comfortable, and had a beautiful view.
5.The location was convenient, but I wish the service could have been more attentive.
6.The air conditioning didn’t work properly, and the room smelled musty. The service was unprofessional.
7.The room was cozy, and the service was excellent. The breakfast was great, and the location was perfect for exploring the area.
8.Overall, a solid choice. The room was nice and clean, the location was great, but the Wi-Fi could have been faster.
9.The staff was rude, and the room was filthy. I had to ask for new sheets, and the bathroom was in terrible condition.
10.The staff really made the experience amazing. The room was pristine, and the amenities were top-notch. Highly recommend!
11.The hotel was decent. Nothing too fancy but it served its purpose. The breakfast was standard, and the room was just fine.

"""

# Read from excel optional
# data = pd.read_excel("hospitality_reviews_demo.xlsx")
#  Self-improvement loop
feedback = ""
for i in range(1, 4):  # 3 iterations
    print(f"\n--- Iteration {i} ---")
    analysis = analyze_reviews(customer_reviews, i, feedback)
    print("\n[Analysis Output]:\n", analysis)

    summary, issues, suggestions = extract_sections(analysis)

    feedback = critique_analysis(analysis)
    print("\n[Critique Feedback]:\n", feedback)

    log_iteration(i, summary, issues, suggestions, feedback)

    time.sleep(2)  # To avoid rate limits
