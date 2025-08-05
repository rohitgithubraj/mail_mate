import streamlit as st
import requests
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama3-70b-8192"  # Free Groq model

# Email configuration (use your secure credentials or environment)
SENDER_EMAIL = st.secrets.get("SENDER_EMAIL", os.getenv("SENDER_EMAIL"))
EMAIL_PASSWORD = st.secrets.get("EMAIL_PASSWORD", os.getenv("EMAIL_PASSWORD"))
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Function to generate reply
def generate_email_response(email_text, tone, user_name):
    prompt = f"""
You are an AI assistant. Write a reply to the following email using a {tone.lower()} tone.
Only return the body of the reply email. Do NOT include any extra explanation or commentary.

Sign the email with the sender's name: {user_name}.

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
        response = requests.post(GROQ_API_URL, headers=headers, json=payload)
        response.raise_for_status()
        reply = response.json()['choices'][0]['message']['content'].strip()
        return reply
    except requests.exceptions.RequestException as e:
        return f"⚠️ Error contacting Groq API: {e}"

# Function to send email
def send_email(to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

        return f"✅ Email sent successfully to {to_email}"
    except Exception as e:
        return f"❌ Failed to send the email: {e}"

# Streamlit UI
st.title("📧 Smart Email Responder (Free GPT-4 Alternative)")

email_text = st.text_area("Paste the email you received:", height=200)
tone = st.selectbox("Choose the tone for your reply:", ["Formal", "Friendly", "Professional", "Polite"])
user_name = st.text_input("Your Name (Sender)", value="Your Name")
receiver_email = st.text_input("Recipient's Email")
subject = st.text_input("Subject")

if st.button("Generate and Send Reply"):
    if email_text and tone and user_name and receiver_email and subject:
        reply = generate_email_response(email_text, tone, user_name)
        st.subheader("✉️ Generated Reply:")
        st.write(reply)

        result = send_email(receiver_email, subject, reply)
        st.info(result)
    else:
        st.warning("Please fill in all fields before generating the reply.")
