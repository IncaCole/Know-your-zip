import streamlit as st
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set page config - MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Miami-Dade County Explorer",
    page_icon="🌴",
    layout="wide"
)

# Custom CSS for better navigation, layout and logo
st.markdown("""
<style>
    /* Global background color */
    .stApp {
        background-color: #C2EAE7;
    }
    
    /* Make sure content areas match the background */
    .main .block-container {
        background-color: #C2EAE7;
    }

    /* Ensure sidebar also matches */
    .css-1d391kg {
        background-color: #C2EAE7;
    }

    .stButton > button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #f0f2f6;
    }
    .stButton > button:hover {
        background-color: #4CAF50;
        color: white;
    }
    .stButton > button[data-selected="true"] {
        background-color: #4CAF50;
        color: white;
    }
    div[data-testid="stVerticalBlock"] > div:has(div.stButton) {
        background-color: white;
        padding: 1em;
        border-radius: 5px;
    }
    .title-container {
        display: flex;
        align-items: center;
        gap: 2em;
        margin: 1em 0;
    }
    .title-text {
        margin: 0;
        font-family: "Source Sans Pro", sans-serif;
        font-size: 3.5rem;
        font-weight: bold;
        line-height: 1.2;
    }
    /* Dark mode adjustments */
    [data-theme="dark"] .title-text {
        color: #ffffff;
    }
    [data-theme="light"] .title-text {
        color: rgb(49, 51, 63);
    }
    /* Logo container styling */
    .logo-container {
        background: white;
        padding: 15px;
        border-radius: 12px;
        min-width: 200px;
        display: flex;
        justify-content: center;
    }
    [data-theme="dark"] .logo-container {
        background: white;  /* Keep white background in dark mode for logo visibility */
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state for navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Dashboard'

# Initialize map-related session state variables
if 'map_center' not in st.session_state:
    st.session_state.map_center = [25.7617, -80.1918]  # Miami-Dade County center coordinates
if 'zoom_level' not in st.session_state:
    st.session_state.zoom_level = 10
if 'markers' not in st.session_state:
    st.session_state.markers = []
if 'debug_info' not in st.session_state:
    st.session_state.debug_info = []

# Initialize chat-related session state variables
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'location_data' not in st.session_state:
    st.session_state.location_data = None

# Title with logo
title_col1, title_col2 = st.columns([1, 3])  # Adjusted ratio for bigger logo
with title_col1:
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    st.image("assets/miami-logo-zip.png", width=180)  # Increased logo size
    st.markdown('</div>', unsafe_allow_html=True)
with title_col2:
    st.markdown('<p class="title-text">Miami-Dade County Explorer</p>', unsafe_allow_html=True)

# Create three columns for navigation buttons
col1, col2, col3 = st.columns(3)

# Navigation buttons with active state
with col1:
    if st.button("📊 Dashboard", key="dash_btn", 
                 help="View county-wide analytics and insights",
                 use_container_width=True):
        st.session_state.current_page = 'Dashboard'
with col2:
    if st.button("🗺️ Map Explorer", key="map_btn", 
                 help="Explore locations on interactive map",
                 use_container_width=True):
        st.session_state.current_page = 'Map'
with col3:
    if st.button("🤖 AI Assistant", key="bot_btn", 
                 help="Chat with AI about county information",
                 use_container_width=True):
        st.session_state.current_page = 'Bot'

# Horizontal line for visual separation
st.markdown("---")

# Import required modules based on current page
if st.session_state.current_page == 'Dashboard':
    # Modify dashboard imports to avoid page_config
    import dashboard
    # Remove page config from dashboard.py execution
    if hasattr(dashboard, 'main'):
        dashboard.main()
    else:
        # Run dashboard code without page config
        from dashboard import get_apis, get_zip_validator
        apis = get_apis()
        zip_validator = get_zip_validator()
        # Rest of dashboard functionality
        
elif st.session_state.current_page == 'Map':
    # Modify map imports to avoid page_config
    import map4
    # Remove page config from map4.py execution
    if hasattr(map4, 'main'):
        map4.main()
    else:
        # Run map code without page config
        from map4 import get_apis as get_map_apis
        apis = get_map_apis()
        # Rest of map functionality
        
elif st.session_state.current_page == 'Bot':
    # Modify bot imports to avoid page_config
    import bot4
    # Remove page config from bot4.py execution
    if hasattr(bot4, 'main'):
        bot4.main()
    else:
        # Run bot code without page config
        from bot4 import get_apis as get_bot_apis
        apis = get_bot_apis()
        # Rest of bot functionality

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Miami-Dade County Explorer | Created with Streamlit</p>
</div>
""", unsafe_allow_html=True) 