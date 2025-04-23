import streamlit as st
from together import Together
import os

# Initialize the Together client with your API key
TOGETHER_API_KEY = "tgp_v1_iDEzFWxeK_DmiYCbTRjWy89gRflopp-1jHGRYZGI1o0"
client = Together(api_key=TOGETHER_API_KEY)

# Set page config
st.set_page_config(
    page_title="Llama 3.3 Chat Bot",
    page_icon="🤖",
    layout="wide"
)

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Custom CSS for better chat interface
st.markdown("""
<style>
    .stTextInput>div>div>input {
        background-color: #f0f2f6;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .chat-message.user {
        background-color: #2b313e;
        color: white;
    }
    .chat-message.bot {
        background-color: #f0f2f6;
    }
    .chat-message .content {
        display: flex;
        flex-direction: row;
        align-items: flex-start;
    }
    .chat-message .avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        margin-right: 1rem;
    }
    .chat-message .message {
        flex: 1;
    }
</style>
""", unsafe_allow_html=True)

# Title and description
st.title("🤖 Llama 3.3 Chat Bot")
st.markdown("""
This is a chat interface powered by the Llama 3.3 model. Type your message below and press Enter to chat!
""")

# Display chat messages
for message in st.session_state.messages:
    with st.container():
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user">
                <div class="content">
                    <div class="avatar">👤</div>
                    <div class="message">{message["content"]}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message bot">
                <div class="content">
                    <div class="avatar">🤖</div>
                    <div class="message">{message["content"]}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# Create a form for input
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Type your message here...", key="user_input")
    submit_button = st.form_submit_button("Send")

    if submit_button and user_input.strip():
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_input})
        
        try:
            # Get response from the model
            response = client.chat.completions.create(
                model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
                messages=st.session_state.messages,
                max_tokens=1024,
                temperature=0.7,
            )
            
            # Add bot response to chat history
            bot_response = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": bot_response})
            
            # Rerun to update the chat display
            st.rerun()
            
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info("Please try again.")

# Add a clear chat button
if st.button("Clear Chat"):
    st.session_state.messages = []
    st.rerun() 