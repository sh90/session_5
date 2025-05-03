
import openai
import time
from tqdm import tqdm
import data_info
openai.api_key = data_info.open_ai_key

news_article = """PayPal (PYUSD) has officially been cleared of regulatory scrutiny, with the U.S. Securities and Exchange Commission (SEC) dropping its investigation into the company’s U.S. dollar-pegged stablecoin, according to a regulatory filing made on April 29.

The payment giant, which had received a subpoena from the SEC’s Division of Enforcement in November 2023, said it was notified in February that the agency was “closing this inquiry without enforcement action”, reports Cointelegraph.

The regulatory green light marks a notable shift for stablecoins in the U.S., as PayPal becomes one of the few traditional finance players to operate a stablecoin free of enforcement hurdles in an otherwise cautious regulatory climate.

PYUSD growth remains modest but improving
Despite the positive news, PayPal USD (PYUSD) still trails behind dominant stablecoin players like Tether (USDT) and Circle’s USD Coin (USDC). PYUSD currently has a market cap of $880 million, according to CoinGecko — less than 1% of Tether’s $148.5 billion.

However, PYUSD circulation has risen 75% since the beginning of 2025, suggesting growing user interest amid new incentives.

On April 23, PayPal introduced a 3.7% annual reward program for U.S. users who hold PYUSD on its platform — a move designed to boost retail adoption and liquidity.

Strategic alliance with Coinbase
In a further push to increase visibility, PayPal has partnered with Coinbase to integrate PYUSD across the crypto ecosystem. The collaboration, announced April 24, is expected to broaden use cases for the stablecoin and deepen its integration into everyday crypto transactions.

“We are excited to drive new, exciting, and innovative use cases together with Coinbase,” said Alex Chriss, PayPal’s President and CEO, noting the goal to place PYUSD “at the center” of digital financial experiences.

Financials and market outlook
PayPal also reported strong Q1 2025 results, beating analyst expectations. The firm posted earnings of $1.33 per share, ahead of the expected $1.16. Revenue rose slightly to $7.8 billion, and the company completed significant share buybacks, signaling investor confidence.

Though PYUSD adoption remains limited compared to competitors, PayPal’s recent moves — regulatory clearance, yield incentives, and strategic partnerships — suggest a long-term commitment to stablecoins and broader Web3 integration.

With a clean bill from the SEC and Coinbase now onboard, PayPal is positioning PYUSD as a credible, compliant, and competitive asset in the evolving digital dollar economy.

Recently we wrote that ​leading officials from the U.S. Securities and Exchange Commission (SEC) gathered in Washington, D.C., on April 25 for the Crypto Task Force’s third roundtable to discuss the growing concerns over crypto asset custody."""

def generate_report(article, iteration=1):
    prompt = f"""
    Act as a regulatory compliance analyst.
    Your task is to extract regulatory risks from the article below, categorize them (e.g., SEC, GDPR, AML), and summarize them in a formal report.

    Article:
    {article}

    Iteration {iteration}:
    - Extracted Risks:
    - Categories:
    - Executive Summary:
    """
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    return response.choices[0].message.content

def critique_response(response):
    prompt = f"""
    Review the following risk assessment report:
    {response}

    Critique it: Did it miss any potential risks? Is the categorization appropriate? Suggest improvements.
    """
    response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
    return response.choices[0].message.content

# Self-improving loop
iterations = 3
report = ""
for i in range(1, iterations + 1):
    if i == 1:
        report = generate_report(news_article, i)
    else:
        feedback = critique_response(report)
        report = generate_report(news_article + "\n\nCritique Feedback:\n" + feedback, i)
    print(f"\n[Iteration {i}] Report:\n", report)
    time.sleep(2)



