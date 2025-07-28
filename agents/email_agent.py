import streamlit as st
import openai
import time
from openai import RateLimitError, OpenAI

# Setup OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def generate_email_response(email_text, tone):
    prompt = f"""
You are an AI assistant. Write a reply to the following email using a {tone.lower()} tone:

Email:
{email_text}

Reply:
"""

    delay = 5  # Initial wait time on rate limit
    for attempt in range(3):  # Retry up to 3 times
        try:
            response = client.chat.completions.create(
                model = "gpt-3.5-turbo",  # If available to your key

                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content

        except RateLimitError:
            st.warning(f"Rate limit reached. Retrying in {delay} seconds...")
            time.sleep(delay)
            delay *= 2  # Exponential backoff

        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
            break

    return "⚠️ Sorry, the system is currently overloaded. Please try again later."
