import streamlit as st
from openai import OpenAI
import openai
import time
from datetime import datetime, timedelta

def generate_email_response(email_text, tone, max_retries=3):
    """
    Generate an email response using OpenAI's GPT model with rate limit handling
    
    Args:
        email_text (str): The original email to respond to
        tone (str): The desired tone for the response (e.g., professional, casual, friendly)
        max_retries (int): Maximum number of retry attempts for rate limit errors
    
    Returns:
        str: Generated email response or None if error occurs
    """
    # Input validation
    if not email_text or not email_text.strip():
        st.warning("Please provide an email to respond to.")
        return None
    
    if not tone or not tone.strip():
        tone = "professional"  # Default tone
    
    # Check rate limiting (simple session-based)
    if 'last_request_time' in st.session_state:
        time_since_last = time.time() - st.session_state.last_request_time
        if time_since_last < 3:  # Wait at least 3 seconds between requests
            wait_time = 3 - time_since_last
            st.info(f"⏳ Rate limiting: Please wait {wait_time:.1f} seconds before next request")
            time.sleep(wait_time)
    
    for attempt in range(max_retries):
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
            
            # Record request time
            st.session_state.last_request_time = time.time()
            
            # Make API call with conservative settings
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,  # Reduced to save quota
                temperature=0.7,
                timeout=30  # Add timeout
            )
            
            return response.choices[0].message.content
            
        except openai.AuthenticationError:
            st.error("❌ Invalid OpenAI API key. Please check your credentials in secrets.toml")
            return None
        except openai.RateLimitError as e:
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) * 5  # Exponential backoff: 5, 10, 20 seconds
                st.warning(f"⏳ Rate limit hit. Retrying in {wait_time} seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            else:
                st.error("❌ Rate limit exceeded after multiple attempts. Solutions:")
                st.markdown("""
                **Immediate fixes:**
                - Wait 1 minute and try again
                - Use shorter emails (reduces token usage)
                
                **Long-term solutions:**
                - Check your [OpenAI usage](https://platform.openai.com/usage)
                - Upgrade your OpenAI plan if needed
                - Add billing information to your OpenAI account
                """)
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
    
    return None

def check_usage_and_limits():
    """
    Display current usage information and rate limit guidelines
    """
    st.info("""
    📊 **Rate Limit Information:**
    
    **Free Tier Limits:**
    - 3 requests per minute
    - 200 requests per day
    - 40,000 tokens per minute
    
    **Solutions:**
    1. **Wait between requests** (at least 20 seconds)
    2. **Upgrade to paid plan** for higher limits
    3. **Reduce token usage** with shorter prompts
    4. **Check your usage:** [OpenAI Usage Dashboard](https://platform.openai.com/usage)
    
    **Paid Tier Limits (much higher):**
    - 3,500+ requests per minute
    - 90,000+ tokens per minute
    """)

def generate_simple_email_template(email_text, tone):
    """
    Fallback function that creates email templates without API calls
    """
    templates = {
        "professional": f"""
Subject: Re: [Your Subject]

Dear [Name],

Thank you for your email regarding [main topic from: {email_text[:100]}...].

I appreciate you reaching out and would like to address your points:

[Your response to their main points]

Please let me know if you have any questions or need further clarification.

Best regards,
[Your Name]
        """,
        "friendly": f"""
Subject: Re: [Your Subject]

Hi [Name]!

Thanks for your email about [main topic from: {email_text[:100]}...].

I'd be happy to help with this! Here are my thoughts:

[Your response to their main points]

Let me know if you need anything else!

Best,
[Your Name]
        """,
        "casual": f"""
Subject: Re: [Your Subject]

Hey [Name],

Got your message about [main topic from: {email_text[:100]}...].

Here's what I think:

[Your response to their main points]

Talk soon!
[Your Name]
        """
    }
    
    return templates.get(tone.lower(), templates["professional"])
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
    
    # Rate limit info
    if st.checkbox("📊 Show rate limit info"):
        check_usage_and_limits()
    
    # Debug option
    if st.checkbox("🔧 Show available models (debug)"):
        list_available_models()
    
    # Two options for generation
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✨ Generate with AI", type="primary"):
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
    
    with col2:
        if st.button("📝 Generate Template (No API)", type="secondary"):
            if email_input:
                template = generate_simple_email_template(email_input, selected_tone)
                st.success("✅ Template generated!")
                st.text_area(
                    "📋 Email Template:",
                    value=template,
                    height=300,
                    help="Fill in the bracketed sections with your specific content"
                )
            else:
                st.warning("Please enter an email to respond to.")

# Uncomment the line below if you want to run the test interface
# test_email_agent()
