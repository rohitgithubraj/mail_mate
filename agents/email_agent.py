import streamlit as st
from openai import OpenAI
import openai

def generate_email_response(email_text, tone):
    """
    Generate an email response using OpenAI's GPT model
    
    Args:
        email_text (str): The original email to respond to
        tone (str): The desired tone for the response (e.g., professional, casual, friendly)
    
    Returns:
        str: Generated email response or None if error occurs
    """
    # Input validation
    if not email_text or not email_text.strip():
        st.warning("Please provide an email to respond to.")
        return None
    
    if not tone or not tone.strip():
        tone = "professional"  # Default tone
    
    try:
        # Check if API key exists
        if "OPENAI_API_KEY" not in st.secrets:
            st.error("OpenAI API key not found in secrets. Please add it to your .streamlit/secrets.toml file.")
            return None
            
        # Initialize the OpenAI client
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        
        # Create the prompt
        prompt = f"""
You are an AI assistant. Write a professional and appropriate reply to the following email using a {tone.lower()} tone:

Email:
{email_text}

Please write a complete email reply that includes:
- Appropriate greeting
- Response to the main points
- Professional closing

Reply:
"""
        
        # Make API call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using gpt-3.5-turbo for better compatibility
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except openai.AuthenticationError:
        st.error("❌ Invalid OpenAI API key. Please check your credentials in secrets.toml")
        return None
    except openai.RateLimitError:
        st.error("❌ OpenAI API rate limit exceeded. Please try again later or check your usage quota.")
        return None
    except openai.NotFoundError:
        st.error("❌ Model not found. Your API key may not have access to gpt-3.5-turbo.")
        return None
    except openai.APIError as e:
        st.error(f"❌ OpenAI API error: {str(e)}")
        return None
    except Exception as e:
        st.error(f"❌ Unexpected error: {str(e)}")
        return None

def list_available_models():
    """
    Debug function to list available OpenAI models for your API key
    """
    try:
        if "OPENAI_API_KEY" not in st.secrets:
            st.error("OpenAI API key not found in secrets.")
            return
            
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        models = client.models.list()
        available_models = [model.id for model in models.data if 'gpt' in model.id.lower()]
        st.write("🔍 Available GPT models for your API key:")
        for model in sorted(available_models):
            st.write(f"  • {model}")
    except Exception as e:
        st.error(f"Error listing models: {e}")

# Example usage function (optional - for testing)
def test_email_agent():
    """
    Test function to demonstrate usage
    """
    st.title("📧 Email Response Generator")
    
    # Input fields
    email_input = st.text_area(
        "📝 Paste the email you want to respond to:",
        placeholder="Enter the original email here...",
        height=200
    )
    
    tone_options = ["Professional", "Friendly", "Casual", "Formal", "Apologetic"]
    selected_tone = st.selectbox("🎭 Select response tone:", tone_options)
    
    # Debug option
    if st.checkbox("🔧 Show available models (debug)"):
        list_available_models()
    
    # Generate response button
    if st.button("✨ Generate Response", type="primary"):
        if email_input:
            with st.spinner("Generating response..."):
                response = generate_email_response(email_input, selected_tone)
                
            if response:
                st.success("✅ Response generated successfully!")
                st.text_area(
                    "📤 Generated Response:",
                    value=response,
                    height=300,
                    help="You can copy this response and edit as needed"
                )
        else:
            st.warning("Please enter an email to respond to.")

# Uncomment the line below if you want to run the test interface
# test_email_agent()
