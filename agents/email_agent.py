import streamlit as st
from openai import OpenAI
import openai
import time
from datetime import datetime, timedelta

def generate_email_response(email_text, tone, max_retries=2, use_fallback=True):
    """
    Generate an email response using OpenAI's GPT model with smart fallback
    
    Args:
        email_text (str): The original email to respond to
        tone (str): The desired tone for the response
        max_retries (int): Maximum number of retry attempts
        use_fallback (bool): Whether to use offline fallback on failure
    
    Returns:
        str: Generated email response or fallback template
    """
    # Input validation
    if not email_text or not email_text.strip():
        st.warning("Please provide an email to respond to.")
        return None
    
    if not tone or not tone.strip():
        tone = "professional"
    
    # Check if we should skip API entirely due to recent failures
    if 'consecutive_failures' in st.session_state and st.session_state.consecutive_failures >= 3:
        st.info("🚀 Using smart template generator (API temporarily disabled due to rate limits)")
        return generate_smart_email_response(email_text, tone)
    
    # Rate limiting check
    if 'last_request_time' in st.session_state:
        time_since_last = time.time() - st.session_state.last_request_time
        if time_since_last < 60:  # Wait 60 seconds between attempts
            remaining_time = 60 - time_since_last
            st.warning(f"⏳ Please wait {remaining_time:.0f} seconds before next API request")
            if use_fallback:
                st.info("🚀 Using smart template generator instead...")
                return generate_smart_email_response(email_text, tone)
            return None
    
    for attempt in range(max_retries):
        try:
            if "OPENAI_API_KEY" not in st.secrets:
                st.error("OpenAI API key not found in secrets.")
                if use_fallback:
                    return generate_smart_email_response(email_text, tone)
                return None
                
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
            
            # Shorter, more efficient prompt
            prompt = f"Write a {tone.lower()} email reply to: {email_text[:300]}..."
            
            st.session_state.last_request_time = time.time()
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=250,  # Reduced further
                temperature=0.5   # Lower for consistency
            )
            
            # Reset failure counter on success
            st.session_state.consecutive_failures = 0
            return response.choices[0].message.content
            
        except openai.RateLimitError:
            # Track consecutive failures
            if 'consecutive_failures' not in st.session_state:
                st.session_state.consecutive_failures = 0
            st.session_state.consecutive_failures += 1
            
            if attempt < max_retries - 1:
                wait_time = 30 * (attempt + 1)  # 30, 60 seconds
                st.warning(f"⏳ Rate limit hit. Waiting {wait_time} seconds... (Attempt {attempt + 1}/{max_retries})")
                time.sleep(wait_time)
                continue
            else:
                st.error("❌ Rate limit exceeded. Your OpenAI account needs:")
                st.markdown("""
                🔥 **URGENT: Add billing to your OpenAI account**
                - Free accounts: 3 requests/minute ❌
                - Paid accounts: 3,500+ requests/minute ✅
                - Even $5 credit removes most limits
                
                [Add billing here →](https://platform.openai.com/account/billing)
                """)
                
                if use_fallback:
                    st.success("🚀 Switching to smart offline generator...")
                    return generate_smart_email_response(email_text, tone)
                return None
                
        except Exception as e:
            st.error(f"❌ API Error: {str(e)}")
            if use_fallback and attempt == max_retries - 1:
                return generate_smart_email_response(email_text, tone)
            
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

def generate_smart_email_response(email_text, tone):
    """
    Smart offline email generator that analyzes the input email and creates contextual responses
    """
    import re
    
    # Extract key information from the email
    email_lower = email_text.lower()
    
    # Detect email type and key phrases
    is_meeting_request = any(word in email_lower for word in ['meeting', 'call', 'schedule', 'appointment', 'available'])
    is_question = '?' in email_text or any(word in email_lower for word in ['question', 'help', 'how', 'what', 'when', 'where', 'why'])
    is_complaint = any(word in email_lower for word in ['problem', 'issue', 'wrong', 'error', 'disappointed', 'unhappy'])
    is_request = any(word in email_lower for word in ['please', 'could you', 'would you', 'can you', 'need'])
    is_thank_you = any(word in email_lower for word in ['thank', 'grateful', 'appreciate'])
    
    # Extract names (simple detection)
    potential_names = re.findall(r'\b[A-Z][a-z]+\b', email_text)
    sender_name = potential_names[0] if potential_names else "there"
    
    # Generate contextual response based on tone and email type
    responses = {
        'professional': {
            'meeting_request': f"""Subject: Re: Meeting Request

Dear {sender_name},

Thank you for reaching out regarding a meeting. I would be happy to schedule time to discuss this further.

I am available [insert your availability here] and can accommodate either in-person or virtual meetings as needed.

Please let me know what works best for your schedule, and I'll send a calendar invitation.

Best regards,
[Your Name]""",
            
            'question': f"""Subject: Re: Your Inquiry

Dear {sender_name},

Thank you for your email and for bringing this to my attention.

Regarding your question about [main topic], I'd be happy to provide the information you need. [Insert your detailed response here]

Please don't hesitate to reach out if you need any clarification or have additional questions.

Best regards,
[Your Name]""",
            
            'complaint': f"""Subject: Re: Your Concern

Dear {sender_name},

Thank you for bringing this matter to my attention. I understand your concerns and take them seriously.

I would like to address this issue promptly and ensure we find a satisfactory resolution. [Insert specific response to their complaint]

I will personally follow up on this matter and keep you updated on our progress.

Sincerely,
[Your Name]""",
            
            'request': f"""Subject: Re: Your Request

Dear {sender_name},

Thank you for your email regarding [their request topic].

I have reviewed your request and [will be able to accommodate/need to discuss alternatives]. [Insert specific response about their request]

I will [follow up/provide the requested information/schedule time to discuss] by [timeframe].

Best regards,
[Your Name]""",
            
            'thank_you': f"""Subject: Re: Thank You

Dear {sender_name},

Thank you for your kind words. I'm glad I could be of assistance.

It was a pleasure working with you on this matter. Please don't hesitate to reach out if you need anything else in the future.

Best regards,
[Your Name]""",
            
            'general': f"""Subject: Re: [Original Subject]

Dear {sender_name},

Thank you for your email. I appreciate you taking the time to reach out.

[Insert your main response addressing their points here]

Please let me know if you have any questions or need further information.

Best regards,
[Your Name]"""
        },
        
        'friendly': {
            'meeting_request': f"""Subject: Re: Let's Meet!

Hi {sender_name}!

Thanks for reaching out about meeting up! I'd love to chat about this.

I'm pretty flexible this week - how about [suggest specific times]? We could grab coffee or just do a quick call, whatever works better for you.

Let me know what you think!

Best,
[Your Name]""",
            
            'question': f"""Subject: Re: Your Question

Hi {sender_name}!

Great question! I'm happy to help with this.

[Insert your helpful response here]. I hope that clears things up, but feel free to ask if you need more details!

Hope you're doing well!

[Your Name]""",
            
            'general': f"""Subject: Re: [Original Subject]

Hi {sender_name}!

Thanks for your email! 

[Insert your friendly response here]

Hope to hear from you soon!

Best,
[Your Name]"""
        }
    }
    
    # Determine response type
    if is_meeting_request:
        response_type = 'meeting_request'
    elif is_complaint:
        response_type = 'complaint'
    elif is_question:
        response_type = 'question'
    elif is_request:
        response_type = 'request'
    elif is_thank_you:
        response_type = 'thank_you'
    else:
        response_type = 'general'
    
    # Get appropriate response
    tone_key = tone.lower()
    if tone_key not in responses:
        tone_key = 'professional'
    
    if response_type not in responses[tone_key]:
        response_type = 'general'
    
    return responses[tone_key][response_type]
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
        if st.button("🚀 Smart Generator (No API)", type="secondary"):
            if email_input:
                smart_response = generate_smart_email_response(email_input, selected_tone)
                st.success("✅ Smart response generated!")
                st.text_area(
                    "🎯 Smart Email Response:",
                    value=smart_response,
                    height=300,
                    help="This contextual response was generated without API calls!"
                )
            else:
                st.warning("Please enter an email to respond to.")

# Uncomment the line below if you want to run the test interface
# test_email_agent()
