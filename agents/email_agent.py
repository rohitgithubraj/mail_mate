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

MODEL_NAME = "llama-3.1-8b-instant"

def generate_email_response(email_text: str, tone: str, sender_name: str = "") -> str:
    if not GROQ_API_KEY:
        return "⚠ Groq API key not configured."

    if not email_text.strip():
        return "⚠ Email content is empty."

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    prompt = f"""
Write a {tone.lower()} email reply.

Start with greeting.
End with Best regards.

Sender: {sender_name if sender_name else "[Your Name]"}

Email:
{email_text}
"""

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }

    try:
        res = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=60)

        if res.status_code != 200:
            return f"⚠ Error {res.status_code}: {res.text}"

        return res.json()["choices"][0]["message"]["content"].strip()

    except Exception as e:
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
    st.set_page_config(page_title="MailMate AI", page_icon="📧")
    st.title("📧 MailMate – Think Less. Reply Smart.")

    sender_name = st.text_input("Your Name")

    col1, col2 = st.columns(2)
    with col1:
        recipient_email = st.text_input("Recipient Email")
    with col2:
        email_subject = st.text_input("Email Subject")

    email_text = st.text_area("Paste email content", height=200)

    tone = st.selectbox(
        "Tone",
        ["Professional", "Friendly", "Apologetic", "Persuasive"]
    )

    if st.button("Generate Reply"):
        if not email_text.strip():
            st.warning("Please enter email content.")
        else:
            with st.spinner("Generating reply..."):
                st.session_state.reply = generate_email_response(email_text, tone, sender_name)

    edited_reply = st.text_area(
        "Edit your reply before sending",
        st.session_state.reply,
        height=250
    )

    if st.button("Send Email"):
        if not recipient_email or not email_subject:
            st.warning("Please fill all fields.")
        else:
            with st.spinner("Sending email..."):
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
