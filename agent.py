"""Simple Groq-powered agent that runs NDVI computations."""
import re
from groq import Groq
from config import GROQ_API_KEY, KENYA_COUNTIES, DEFAULT_COUNTY, DEFAULT_YEAR
from ndvi import initialize_gee, plot_ndvi

client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = f"""You are an NDVI assistant for Kenya. Extract a county and year
from the user's request. Valid counties: {", ".join(KENYA_COUNTIES)}.
Reply in EXACTLY this format (nothing else):
COUNTY: <county>
YEAR: <year>
If the user is vague, use county {DEFAULT_COUNTY} and year {DEFAULT_YEAR}.
"""

def extract_params(user_text: str) -> tuple[str, int]:
    chat = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_text},
        ],
        temperature=0.1,
    )
    reply = chat.choices[0].message.content
    county = re.search(r"COUNTY:\s*(.+)", reply).group(1).strip()
    year = int(re.search(r"YEAR:\s*(\d{4})", reply).group(1))
    return county, year

def run() -> None:
    initialize_gee()
    while True:
        user_text = input("\n🗣️  Which county and year? (e.g. 'NDVI for Turkana in 2021', or 'q' to quit): ").strip()
        if user_text.lower() in {"q", "quit", "exit"}:
            break
        county, year = extract_params(user_text)
        print(f"🤖 Agent decided: {county}, {year}")
        try:
            plot_ndvi(county, year)
        except ValueError as e:
            print(f"⚠️  {e}")

if __name__ == "__main__":
    run()