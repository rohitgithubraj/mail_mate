import streamlit as st
import requests
import smtplib
from email.mime.text import MIMEText
import os

GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
SENDER_EMAIL = st.secrets.get("SENDER_EMAIL", os.getenv("SENDER_EMAIL"))
EMAIL_PASSWORD = st.secrets.get("EMAIL_PASSWORD", os.getenv("EMAIL_PASSWORD"))
SMTP_SERVER = st.secrets.get("SMTP_SERVER", os.getenv("SMTP_SERVER", "smtp.gmail.com"))
SMTP_PORT = int(st.secrets.get("SMTP_PORT", os.getenv("SMTP_PORT", 587)))

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama3-70b-8192"

def generate_email_response(email_text: str, tone: str, sender_name: str = "") -> str:
    if not GROQ_API_KEY:
        return "⚠ Groq API key not configured."

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    sender_instruction = f"\nSender name: {sender_name}" if sender_name else ""

    prompt = f"""
You are an AI assistant. Write ONLY the email reply content using a {tone.lower()} tone.

- Start directly with the email salutation
- End with Best regards and sender name if provided

{sender_instruction}

Email:
{email_text}

Email Reply:
"""

    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }

    try:
        res = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=60)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"].strip()
    except requests.exceptions.RequestException as e:
        return f"⚠ Error: {e}"

def send_email(recipient: str, subject: str, body: str):
    if not (SENDER_EMAIL and EMAIL_PASSWORD):
        return "⚠ Email credentials not configured."

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = recipient

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.send_message(msg)
        return "✅ Email sent successfully."
    except smtplib.SMTPException as e:
        return f"⚠ Failed to send email: {e}"

def init_session():
    if "reply" not in st.session_state:
        st.session_state.reply = ""

def render_ui():
    st.set_page_config(page_title="Email Reply Assistant", page_icon="✉")
    st.title("✉ Email Reply Assistant (LLaMA-3 @ Groq)")

    sender_name = st.text_input("Your Name")
    col1, col2 = st.columns(2)

    with col1:
        recipient_email = st.text_input("Recipient Email")
    with col2:
        email_subject = st.text_input("Email Subject")

    email_text = st.text_area("Paste email content")
    tone = st.selectbox("Tone", ["Formal", "Friendly", "Professional", "Casual"])

    if st.button("Generate Reply"):
        if email_text.strip():
            with st.spinner("Generating..."):
                st.session_state.reply = generate_email_response(email_text, tone, sender_name)

    edited_reply = st.text_area("Edit Reply", st.session_state.reply, height=250)

    if st.button("Send Email"):
        if not recipient_email or not email_subject:
            st.warning("Fill all fields")
        else:
            status = send_email(recipient_email, email_subject, edited_reply)
            if status.startswith("✅"):
                st.success(status)
            else:
                st.error(status)

def main():
    init_session()
    render_ui()

if __name__ == "__main__":
    main()
