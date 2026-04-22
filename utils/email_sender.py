import smtplib
import streamlit as st
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

def send_email(recipient, subject, body, attachment=None):
    try:
        sender_email = st.secrets["SENDER_EMAIL"]
        sender_password = st.secrets["EMAIL_PASSWORD"]
        smtp_server = st.secrets.get("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = st.secrets.get("SMTP_PORT", 587)

        message = MIMEMultipart()
        message['From'] = sender_email
        message['To'] = recipient
        message['Subject'] = subject

        message.attach(MIMEText(body, "plain"))

        if attachment is not None:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={attachment.name}",
            )
            message.attach(part)

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(message)
        server.quit()

        return True

    except Exception as e:
        print("Error sending email:", e)
        return False
