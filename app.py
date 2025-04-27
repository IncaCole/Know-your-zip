import streamlit as st
import sys
import os

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set page config - MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Miami-Dade County Explorer",
    page_icon="��",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better navigation, layout and logo
st.markdown("""
<style>
    /* Global text color adjustments for dark mode */
    [data-theme="dark"] {
        color: #FFFFFF;
    }

    [data-theme="dark"] .stButton > button {
        color: #2A3A40;
        background-color: #f0f2f6;
    }

    [data-theme="dark"] .stButton > button:hover {
        color: white;
        background-color: #4CAF50;
    }

    [data-theme="dark"] div[data-testid="stVerticalBlock"] > div:has(div.stButton) {
        background-color: rgba(255, 255, 255, 0.1);
    }

    /* Dark mode text adjustments */
    [data-theme="dark"] .title-text {
        color: #FFFFFF;
    }

    [data-theme="dark"] .stMarkdown {
        color: #FFFFFF;
    }

    [data-theme="dark"] .stTextInput input {
        color: #FFFFFF;
        background-color: rgba(255, 255, 255, 0.1);
    }

    [data-theme="dark"] .stTextInput label {
        color: #FFFFFF;
    }

    [data-theme="dark"] .stCheckbox label {
        color: #FFFFFF !important;
    }

    [data-theme="dark"] .stSlider label {
        color: #FFFFFF;
    }

    [data-theme="dark"] .stSubheader {
        color: #FFFFFF;
    }

    [data-theme="dark"] p {
        color: #FFFFFF;
    }

    /* Global background color */
    .stApp {
        background-color: transparent;
    }
    
    /* Make sure content areas match the background */
    .main .block-container {
        background-color: transparent;
        padding-top: 1rem;
        padding-right: 1rem;
        padding-left: 1rem;
        padding-bottom: 1rem;
    }

    /* Ensure sidebar also matches */
    .css-1d391kg {
        background-color: transparent;
    }

    /* Responsive button styling */
    .stButton > button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #f0f2f6;
        margin: 0.2rem 0;
        padding: 0.5rem;
        white-space: normal;
        word-wrap: break-word;
    }
    
    .stButton > button:hover {
        background-color: #4CAF50;
        color: white;
    }
    
    .stButton > button[data-selected="true"] {
        background-color: #4CAF50;
        color: white;
    }

    /* Responsive container for buttons */
    div[data-testid="stVerticalBlock"] > div:has(div.stButton) {
        background-color: white;
        padding: 0.5rem;
        border-radius: 5px;
        margin: 0.2rem 0;
    }

    /* Responsive title container */
    .title-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1rem;
        margin: 0.5rem 0;
        padding: 0.5rem;
    }

    /* Responsive title text */
    .title-text {
        margin: 0;
        font-family: "Source Sans Pro", sans-serif;
        font-size: calc(2rem + 2vw);
        font-weight: bold;
        line-height: 1.2;
        text-align: center;
        color: #2A3A40;
    }

    .title-text-line {
        display: block;
    }

    /* Light mode specific colors */
    [data-theme="light"] .title-text {
        color: #2A3A40;
    }

    /* Responsive logo container */
    .logo-container {
        background: white;
        padding: 0.8rem;
        border-radius: 12px;
        width: min(200px, 80%);
        margin: 0 auto;
        display: flex;
        justify-content: center;
    }

    [data-theme="dark"] .logo-container {
        background: white;
    }

    /* Make columns more responsive */
    div[data-testid="column"] {
        padding: 0.5rem !important;
    }

    /* Responsive text inputs */
    .stTextInput input {
        width: 100%;
    }

    /* Adjust spacing for mobile */
    @media (max-width: 640px) {
        .main .block-container {
            padding: 0.5rem;
        }

        .title-text {
            font-size: calc(1.5rem + 1.5vw);
        }

        .logo-container {
            width: 60%;
            padding: 0.5rem;
        }

        div[data-testid="column"] {
            padding: 0.3rem !important;
        }

        .stButton > button {
            height: auto;
            min-height: 3em;
            font-size: 0.9rem;
        }
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
title_col1, title_col2 = st.columns([1, 2])  # Adjusted ratio for better mobile display
with title_col1:
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    st.image("assets/miami-logo-zip.png", use_column_width=True)  # Make image responsive
    st.markdown('</div>', unsafe_allow_html=True)
with title_col2:
    st.markdown('<div class="title-text"><span class="title-text-line">Miami-Dade</span><span class="title-text-line">County Explorer</span></div>', unsafe_allow_html=True)

# Create three columns for navigation buttons with adjusted ratios
col1, col2, col3 = st.columns([1, 1, 1])  # Equal width columns for better mobile display

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