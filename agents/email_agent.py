import streamlit as st
import requests
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- Configuration ---
GROQ_API_KEY = "your_groq_api_key_here"  # Replace with your actual key
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama3-70b-8192"

SENDER_EMAIL = "your_email@gmail.com"
EMAIL_PASSWORD = "your_app_password"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# --- Email Reply Generator ---
def generate_email_response(email_text, tone, user_name):
    prompt = f"""
You are an AI assistant. Write a reply to the following email using a {tone.lower()} tone.
Make sure the reply ends with: "Best regards, {user_name}".
Do not start with "Here is a potential reply to the email".

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
        ]
    }

    response = requests.post(GROQ_API_URL, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        st.error(f"⚠️ Error contacting Groq API: {response.status_code} - {response.text}")
        return None

# --- Send Email Function ---
def send_email(to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.send_message(msg)

        return "✅ Email sent successfully."
    except Exception as e:
        return f"❌ Failed to send the email: {e}"

# --- Streamlit UI ---
st.title("📧 AI Email Responder")

email_text = st.text_area("📩 Paste the received email here:")
tone = st.selectbox("🎯 Select response tone:", ["Formal", "Friendly", "Apologetic", "Excited", "Curious"])
user_name = st.text_input("✍️ Your name:")
receiver_email = st.text_input("📬 Recipient's Email:")
subject = st.text_input("📝 Subject of Reply Email")

if st.button("Generate and Send Reply"):
    if email_text and tone and user_name and receiver_email and subject:
        reply = generate_email_response(email_text, tone, user_name)
        if reply:
            st.subheader("✉️ Generated Reply:")
            st.write(reply)

            result = send_email(receiver_email, subject, reply)
            st.info(result)
    else:
        st.warning("⚠️ Please fill in all fields before generating the reply.")

