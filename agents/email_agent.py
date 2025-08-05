import streamlit as st
import requests
import os
import smtplib
from email.message import EmailMessage

# Load from Streamlit secrets
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
SENDER_EMAIL = st.secrets["SENDER_EMAIL"]
EMAIL_PASSWORD = st.secrets["EMAIL_PASSWORD"]
SMTP_SERVER = st.secrets.get("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = st.secrets.get("SMTP_PORT", 587)

# Constants
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama3-70b-8192"

# Function to generate reply
def generate_email_response(email_text, tone):
    prompt = f"""
You are an AI assistant. Write a reply to the following email using a {tone.lower()} tone.
Only return the body of the email. Do NOT include any extra explanation or commentary.

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
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        reply = response.json()['choices'][0]['message']['content'].strip()
        return reply
    except requests.exceptions.RequestException as e:
        return f"⚠️ Error contacting Groq API: {e}"

# Function to send email
def send_email(receiver_email, subject, body):
    try:
        msg = EmailMessage()
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = receiver_email
        msg.set_content(body)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.send_message(msg)
        return "✅ Email sent successfully!"
    except Exception as e:
        return f"❌ Failed to send the email: {e}"

# Streamlit UI
st.title("📧 AI Email Reply Assistant (Free Model)")

email_text = st.text_area("Paste the email content here:")
tone = st.selectbox("Select reply tone:", ["Formal", "Friendly", "Polite"])
receiver_email = st.text_input("Recipient Email")
subject = st.text_input("Email Subject", value="Clarification Regarding Email Received")

if st.button("Generate Reply"):
    if email_text and tone:
        reply = generate_email_response(email_text, tone)
        st.subheader("✉️ Generated Reply:")
        st.write(reply)

        if receiver_email:
            result = send_email(receiver_email, subject, reply)
            st.info(result)
        else:
            st.warning("Enter the recipient email to send.")
    else:
        st.warning("Please enter the email content and select a tone.")
