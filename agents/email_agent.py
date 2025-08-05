import streamlit as st
import requests
import os

# Load from Streamlit secrets or environment
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama3-70b-8192"  # Free & powerful

def generate_email_response(email_text, tone):
    prompt = f"""
You are an AI assistant. Write a reply to the following email using a {tone.lower()} tone.

Email:
{email_text}

Reply:
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    try:
        res = requests.post(GROQ_API_URL, json=payload, headers=headers)
        res.raise_for_status()
        return res.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        return f"⚠️ Error contacting Groq API: {e}"
    except Exception as e:
        return f"⚠️ Unexpected error: {e}"

# --- Streamlit UI ---
st.set_page_config(page_title="Email Reply Generator", page_icon="✉️")
st.title("✉️ Email Reply Assistant (Powered by LLaMA3 @ Groq)")

email_text = st.text_area("📩 Enter received email:")
tone = st.selectbox("🎯 Choose reply tone:", ["Formal", "Informal", "Friendly", "Professional"])

if st.button("🚀 Generate Reply"):
    if not email_text.strip():
        st.warning("Please enter an email.")
    else:
        with st.spinner("Generating reply..."):
            reply = generate_email_response(email_text, tone)
            st.success("✅ Reply Generated:")
            st.write(reply)

