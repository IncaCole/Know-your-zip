import streamlit as st
import sys
import os

# Add the current directory to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(current_dir)

# Set page config - MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="Miami-Dade County Explorer (Test)",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state for navigation
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Dashboard'

# Title
st.title("Miami-Dade County Explorer (Test)")

# Create three columns for navigation buttons
col1, col2, col3 = st.columns([1, 1, 1])

# Navigation buttons
with col1:
    if st.button("📊 Dashboard", key="dash_btn", help="View county-wide analytics and insights"):
        st.session_state.current_page = 'Dashboard'
with col2:
    if st.button("🗺️ Map Explorer", key="map_btn", help="Explore locations on interactive map"):
        st.session_state.current_page = 'Map'
with col3:
    if st.button("🤖 AI Assistant", key="bot_btn", help="Chat with AI about county information"):
        st.session_state.current_page = 'Bot'

# Display current page
st.write(f"Current page: {st.session_state.current_page}")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <p>Miami-Dade County Explorer (Test) | Created with Streamlit</p>
</div>
""", unsafe_allow_html=True) 