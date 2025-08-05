import streamlit as st
import openai

# Manually paste API key just to test
client = openai.OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def generate_email_response(email_text, tone):
    prompt = f"""
You are an AI assistant. Write a reply to the following email using a {tone.lower()} tone:

Email:
{email_text}

Reply:
"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # change to gpt-4 if you know it's available
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error: {e}"

# Simple UI
st.title("Email Reply Generator")
email_text = st.text_area("Email:")
tone = st.selectbox("Tone:", ["Formal", "Friendly", "Professional", "Casual"])

if st.button("Generate Reply"):
    result = generate_email_response(email_text, tone)
    st.write(result)
