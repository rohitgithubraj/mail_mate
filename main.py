import streamlit as st
from agents.email_agent import generate_email_response
from utils.email_sender import send_email

st.set_page_config(page_title="Auto Email Responder", layout="wide")

def init_session():
    if "generated_reply" not in st.session_state:
        st.session_state.generated_reply = ""

def generate_reply(email_text, tone):
    return generate_email_response(email_text, tone)

def render_ui():
    st.title("📧 MailMate – Let AI Handle Your Inbox")

    email_text = st.text_area("Paste the email content you received:", height=300)
    recipient_email = st.text_input("Recipient Email Address")
    subject = st.text_input("Subject")

    tone = st.selectbox(
        "Select response tone",
        ["Professional", "Friendly", "Apologetic", "Persuasive"]
    )

    if st.button("Generate Reply"):
        if not email_text.strip():
            st.warning("Please enter email content.")
        else:
            with st.spinner("Generating reply..."):
                st.session_state.generated_reply = generate_reply(email_text, tone)

    edited_reply = st.text_area(
        "Edit your reply before sending:",
        st.session_state.generated_reply,
        height=250
    )

    attachment = st.file_uploader("Attach file")

    if st.button("Send Email"):
        if not recipient_email or not subject:
            st.warning("Please enter recipient email and subject.")
        else:
            with st.spinner("Sending email..."):
                status = send_email(recipient_email, subject, edited_reply, attachment)

            if status:
                st.success(f"Email sent successfully to {recipient_email}")
            else:
                st.error("Failed to send the email.")

def main():
    init_session()
    render_ui()

if __name__ == "__main__":
    main()
