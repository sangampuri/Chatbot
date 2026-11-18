import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)

response = client.interactions.create(
    model="gemini-3.8-flash",
    input="Explain Python in simple words.",
    generation_config={
        "thinking_level": "low"
    },
    stream=True
)

for event in response:
    if event.event_type == "step.delta" and hasattr(event.delta, "text"):
        print(event.delta.text, end="", flush=True)

print()