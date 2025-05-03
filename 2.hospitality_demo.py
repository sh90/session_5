import time
import data_info
import openai
# 🔑 Set your API key here
openai.api_key = data_info.open_ai_key

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

def analyze_reviews(reviews, iteration=1):
    prompt = f"""
    You are a hotel operations analyst. Analyze the guest reviews below. Categorize sentiments by theme (e.g., service, cleanliness, amenities), and suggest actionable improvements.

    Reviews:
    {reviews}

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

def critique_analysis(response):
    prompt = f"""
    Review the following sentiment analysis:
    {response}

    Critique it: Are themes well captured? Are suggestions actionable? Suggest what can be improved.
    """
    response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )

    return response.choices[0].message.content

analysis = ""
for i in range(1, 3):
    if i == 1:
        analysis = analyze_reviews(customer_reviews, i)
    else:
        feedback = critique_analysis(analysis)
        print(f"\n[Iteration {i}] Feedback:\n")
        print(feedback)
        analysis = analyze_reviews(customer_reviews + "\n\nCritique Feedback:\n" + feedback, i)
    print(f"\n[Iteration {i}] Review Analysis:\n", analysis)
    time.sleep(2)
