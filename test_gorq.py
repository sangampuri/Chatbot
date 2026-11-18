
import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env
load_dotenv()

# Retrieve Groq API key
api_key = os.getenv("GROQ_API_KEY")

# Create Groq client
client = Groq(api_key=api_key)

# Send a message to the AI model
response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {
            "role": "user",
            "content": "Explain Python in simple words."
        }
    ],
    max_completion_tokens=200
)

# Display AI response
print(response.choices[0].message.content)
