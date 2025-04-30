import streamlit as st
from together import Together
import os
import api_list_new
from src.zip_validator import ZIPValidator
import re

# Initialize the Together client with your API key
TOGETHER_API_KEY = "tgp_v1_iDEzFWxeK_DmiYCbTRjWy89gRflopp-1jHGRYZGI1o0"
client = Together(api_key=TOGETHER_API_KEY)

# Set page config
st.set_page_config(
    page_title="South Florida AI Assistant",
    page_icon="🌴",
    layout="wide"
)

# Initialize session state for chat history and location data
if "messages" not in st.session_state:
    st.session_state.messages = []
if "location_data" not in st.session_state:
    st.session_state.location_data = None

# Initialize ZIP validator
@st.cache_resource
def get_zip_validator():
    return ZIPValidator()

zip_validator = get_zip_validator()

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
st.title("🌴 South Florida AI Assistant")
st.markdown("""
This AI assistant can help you learn about South Florida locations, find nearby points of interest, and answer questions about Miami-Dade County.
""")

# Create two columns for input and chat
col1, col2 = st.columns([1, 2])

with col1:
    # Location input section
    st.subheader("📍 Location Information")
    location_input = st.text_input("Enter your address or ZIP code")
    
    # Location categories
    categories = ['public_schools', 'police_stations']
    selected_categories = st.multiselect(
        "Select location types to display",
        categories,
        default=['public_schools', 'police_stations']
    )
    
    # Search radius
    radius = st.slider("Search radius (miles)", 1.0, 20.0, 13.38)

    if st.button("Find Locations"):
        if not location_input:
            st.error("Please enter an address or ZIP code")
        else:
            # Check if input is a ZIP code
            zip_match = re.match(r'^\d{5}$', location_input.strip())
            if zip_match:
                # Validate ZIP code
                is_valid, message, zip_info = zip_validator.validate_zip(location_input)
                if not is_valid:
                    st.error(message)
                    with st.expander("Show valid Miami-Dade County ZIP codes"):
                        valid_zips = sorted(list(zip_validator.get_all_zip_codes()))
                        cols = st.columns(5)
                        for i, zip_code in enumerate(valid_zips):
                            cols[i % 5].write(zip_code)
                    st.stop()
                
                # Get coordinates from ZIP code
                coordinates = zip_validator.get_zip_coordinates(location_input)
                if not coordinates:
                    st.error("Could not get coordinates for this ZIP code")
                    st.stop()
            else:
                # Get coordinates from address
                coordinates = api_list_new.get_coordinates(location_input)
            
            if coordinates:
                # Store location data in session state
                st.session_state.location_data = {
                    'coordinates': coordinates,
                    'categories': selected_categories,
                    'radius': radius
                }
                
                # Get nearby locations
                all_locations = []
                for category in selected_categories:
                    locations_df = api_list_new.get_nearby_locations(coordinates, category, radius)
                    if not locations_df.empty:
                        all_locations.extend(locations_df.to_dict('records'))
                
                # Add a system message with location data
                location_summary = f"Location found at coordinates {coordinates}. Found {len(all_locations)} nearby points of interest within {radius} miles."
                st.session_state.messages.append({
                    "role": "system",
                    "content": location_summary
                })
                
                # Rerun to update the chat display
                st.rerun()
            else:
                st.error("Could not find coordinates for the provided location")

# Display chat messages
with col2:
    st.subheader("💬 Chat with AI Assistant")
    
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
            elif message["role"] == "assistant":
                st.markdown(f"""
                <div class="chat-message bot">
                    <div class="content">
                        <div class="avatar">🤖</div>
                        <div class="message">{message["content"]}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:  # system message
                st.info(message["content"])

    # Create a form for input
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("Type your message here...", key="user_input")
        submit_button = st.form_submit_button("Send")

        if submit_button and user_input.strip():
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            try:
                # Prepare context for the AI
                context = ""
                if st.session_state.location_data:
                    context = f"Current location: {st.session_state.location_data['coordinates']}. "
                    context += f"Searching for {', '.join(st.session_state.location_data['categories'])} within {st.session_state.location_data['radius']} miles."
                
                # Get response from the model
                response = client.chat.completions.create(
                    model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
                    messages=[
                        {"role": "system", "content": f"You are a helpful AI assistant that knows about South Florida and Miami-Dade County. {context}"},
                        *st.session_state.messages
                    ],
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
    st.session_state.location_data = None
    st.rerun() 