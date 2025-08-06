import streamlit as st
import requests
import smtplib
from email.mime.text import MIMEText
import os

# -----------------------------
# 🔐 Load secrets (Streamlit or ENV)
# -----------------------------
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
SENDER_EMAIL = st.secrets.get("SENDER_EMAIL", os.getenv("SENDER_EMAIL"))
EMAIL_PASSWORD = st.secrets.get("EMAIL_PASSWORD", os.getenv("EMAIL_PASSWORD"))
SMTP_SERVER = st.secrets.get("SMTP_SERVER", os.getenv("SMTP_SERVER", "smtp.gmail.com"))
SMTP_PORT = int(st.secrets.get("SMTP_PORT", os.getenv("SMTP_PORT", 587)))

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama3-70b-8192"  # Free & powerful

# -----------------------------
# 🤖 Generate reply with Groq LLaMA‑3
# -----------------------------

def generate_email_response(email_text: str, tone: str, sender_name: str = "") -> str:
    """Call Groq API to generate an email reply."""
    if not GROQ_API_KEY:
        return "⚠ Groq API key not configured."

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    sender_instruction = f"\nSender name: {sender_name}" if sender_name else ""

    prompt = f"""
You are an AI assistant. Write ONLY the email reply content using a {tone.lower()} tone.

IMPORTANT: 
- Do NOT include any introductory phrases like "Here is a potential reply to the email:" or "Here's a reply:"
- Start directly with the email salutation (Dear/Hi/Hello)
- End with "Best regards," followed by the sender's name if provided, otherwise use [Your Name]
- Write ONLY the email content, nothing else

{sender_instruction}

Email:
{email_text}

Email Reply (content only):
"""

    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    }

    try:
        res = requests.post(GROQ_API_URL, json=payload, headers=headers, timeout=60)
        res.raise_for_status()
        response_text = res.json()["choices"][0]["message"]["content"].strip()
        
        # Clean up any unwanted introductory phrases
        unwanted_phrases = [
            "Here is a potential reply to the email:",
            "Here's a potential reply to the email:",
            "Here is a reply to the email:",
            "Here's a reply to the email:",
            "Here is the reply:",
            "Here's the reply:",
            "Reply:",
            "Email Reply:",
        ]
        
        for phrase in unwanted_phrases:
            if response_text.startswith(phrase):
                response_text = response_text[len(phrase):].strip()
                break
        
        # Replace [Your Name] with actual sender name if provided
        if sender_name and "[Your Name]" in response_text:
            response_text = response_text.replace("[Your Name]", sender_name)
        
        return response_text
    except requests.exceptions.HTTPError as e:
        return f"⚠ Groq API error: {e.response.status_code} – {e.response.text}"
    except requests.exceptions.RequestException as e:
        return f"⚠ Network error when contacting Groq API: {e}"

# -----------------------------
# ✉ Send email via Gmail SMTP
# -----------------------------

def send_email(recipient: str, subject: str, body: str) -> str:
    """Send an email using Gmail SMTP with an App Password."""
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

# -----------------------------
# 🖼 Streamlit UI
# -----------------------------

st.set_page_config(page_title="Email Reply Assistant", page_icon="✉")
st.title("✉ Email Reply Assistant (LLaMA‑3 @ Groq)")

# Add sender name input
sender_name = st.text_input("Your Name (optional)", placeholder="Enter your name")

col1, col2 = st.columns(2)
with col1:
    recipient_email = st.text_input("Recipient Email", placeholder="example@domain.com")
with col2:
    email_subject = st.text_input("Email Subject", placeholder="Re: Your recent email")

email_text = st.text_area("📩 Paste the received email here:")
tone = st.selectbox("🎯 Desired tone for reply", ["Formal", "Friendly", "Professional", "Casual"])

if st.button("Generate Reply"):
    if not email_text.strip():
        st.warning("Please paste the email content first.")
    else:
        with st.spinner("Generating reply..."):
            reply_text = generate_email_response(email_text, tone, sender_name)
        st.subheader("Generated Reply")
        st.write(reply_text)

        if st.button("Send Email"):
            if not recipient_email or not email_subject:
                st.warning("Please fill recipient email and subject before sending.")
            else:
                status = send_email(recipient_email, email_subject, reply_text)
                if status.startswith("✅"):
                    st.success(status)
                else:
                    st.error(status)
