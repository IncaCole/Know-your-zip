import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from src.data_loader import DataLoader
from src.chatbot import Chatbot
from src.zip_validator import ZipValidator
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize components
data_loader = DataLoader()
zip_validator = ZipValidator()
chatbot = Chatbot(api_key=os.getenv("TOGETHER_API_KEY"))

# Page config
st.set_page_config(
    page_title="Know Your ZIP",
    page_icon="📍",
    layout="wide"
)

# Sidebar
st.sidebar.title("Know Your ZIP")
zip_code = st.sidebar.text_input("Enter ZIP Code", max_chars=5)

# Main content
if zip_code:
    if not zip_validator.is_valid_zip(zip_code):
        st.error("Please enter a valid ZIP code")
    else:
        # Create tabs
        tab1, tab2, tab3 = st.tabs(["Dashboard", "Map View", "AI Assistant"])
        
        with tab1:
            st.header("Dashboard")
            
            # Load and display data
            try:
                # Load various datasets
                schools_df = data_loader.load_zip_dataframe(f"data/schools_{zip_code}.csv")
                hospitals_df = data_loader.load_zip_dataframe(f"data/hospitals_{zip_code}.csv")
                parks_df = data_loader.load_zip_dataframe(f"data/parks_{zip_code}.csv")
                
                # Display summary statistics
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Schools", len(schools_df))
                with col2:
                    st.metric("Hospitals", len(hospitals_df))
                with col3:
                    st.metric("Parks", len(parks_df))
                
                # Display detailed tables
                st.subheader("Nearby Schools")
                st.dataframe(schools_df)
                
                st.subheader("Nearby Hospitals")
                st.dataframe(hospitals_df)
                
                st.subheader("Nearby Parks")
                st.dataframe(parks_df)
                
            except Exception as e:
                st.error(f"Error loading data: {str(e)}")
        
        with tab2:
            st.header("Map View")
            
            try:
                # Create a map centered on the ZIP code
                m = folium.Map(location=[0, 0], zoom_start=13)
                
                # Add markers for each location type
                if not schools_df.empty:
                    for _, row in schools_df.iterrows():
                        folium.Marker(
                            [row['latitude'], row['longitude']],
                            popup=row['name'],
                            icon=folium.Icon(color='blue', icon='graduation-cap')
                        ).add_to(m)
                
                if not hospitals_df.empty:
                    for _, row in hospitals_df.iterrows():
                        folium.Marker(
                            [row['latitude'], row['longitude']],
                            popup=row['name'],
                            icon=folium.Icon(color='red', icon='hospital')
                        ).add_to(m)
                
                if not parks_df.empty:
                    for _, row in parks_df.iterrows():
                        folium.Marker(
                            [row['latitude'], row['longitude']],
                            popup=row['name'],
                            icon=folium.Icon(color='green', icon='tree')
                        ).add_to(m)
                
                # Display the map
                folium_static(m)
                
            except Exception as e:
                st.error(f"Error displaying map: {str(e)}")
        
        with tab3:
            st.header("AI Assistant")
            
            # Initialize chat history
            if "messages" not in st.session_state:
                st.session_state.messages = []
            
            # Display chat history
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            
            # Chat input
            if prompt := st.chat_input("Ask about your area"):
                # Add user message to chat history
                st.session_state.messages.append({"role": "user", "content": prompt})
                
                # Display user message
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                # Generate response
                with st.chat_message("assistant"):
                    response = chatbot.generate_answer(prompt)
                    if response:
                        st.markdown(response)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    else:
                        st.error("Sorry, I couldn't generate a response. Please try again.")
else:
    st.info("Please enter a ZIP code in the sidebar to begin.") 