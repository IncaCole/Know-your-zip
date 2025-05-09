import streamlit as st
from together import Together
import os
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import re
from src.zip_validator import ZIPValidator
from education import EducationAPI
from emergency_services import EmergencyServicesAPI
from healthcare import HealthcareAPI
from infrastructure import BusStopsAPI, LibrariesAPI, ParksAPI
import time
from typing import Dict, Any, List, Optional

# Initialize the Together client with your API key
TOGETHER_API_KEY = "tgp_v1_iDEzFWxeK_DmiYCbTRjWy89gRflopp-1jHGRYZGI1o0"
client = Together(api_key=TOGETHER_API_KEY)

# Set page config
st.set_page_config(
    page_title="Miami-Dade County AI Assistant",
    page_icon="🌴",
    layout="wide"
)

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "location_data" not in st.session_state:
    st.session_state.location_data = None
if "debug_info" not in st.session_state:
    st.session_state.debug_info = []

# Initialize APIs and validator
@st.cache_resource
def get_apis():
    return {
        'Education': EducationAPI(),
        'Emergency': EmergencyServicesAPI(),
        'Healthcare': HealthcareAPI(),
        'Infrastructure': {
            'Bus Stops': BusStopsAPI(),
            'Libraries': LibrariesAPI(),
            'Parks': ParksAPI()
        }
    }

@st.cache_resource
def get_zip_validator():
    return ZIPValidator()

apis = get_apis()
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
st.title("🌴 Miami-Dade County AI Assistant")
st.markdown("""
This AI assistant can help you learn about Miami-Dade County locations, find nearby points of interest, and answer questions about education, emergency services, healthcare, and infrastructure.
""")

# Create two columns for input and chat
col1, col2 = st.columns([1, 2])

with col1:
    # Location input section
    st.subheader("📍 Location Information")
    location_input = st.text_input("Enter your address or ZIP code")
    
    # Category selection
    st.subheader("Select Categories to Display")
    
    # Education facilities
    st.write("Education")
    show_public_schools = st.checkbox("Public Schools", value=True)
    show_private_schools = st.checkbox("Private Schools", value=True)
    show_charter_schools = st.checkbox("Charter Schools", value=True)
    
    # Emergency services
    st.write("Emergency Services")
    show_police = st.checkbox("Police Stations", value=True)
    show_fire = st.checkbox("Fire Stations", value=True)
    
    # Healthcare facilities
    st.write("Healthcare")
    show_hospitals = st.checkbox("Hospitals", value=True)
    show_mental_health = st.checkbox("Mental Health Centers", value=True)
    show_clinics = st.checkbox("Free-Standing Clinics", value=True)
    
    # Infrastructure
    st.write("Infrastructure")
    show_bus_stops = st.checkbox("Bus Stops", value=True)
    show_libraries = st.checkbox("Libraries", value=True)
    show_parks = st.checkbox("Parks", value=True)
    
    # Search radius
    radius = st.slider("Search radius (miles)", 1.0, 20.0, 5.0)

    # Debug mode
    show_debug = st.checkbox("Show Debug Info", value=False)

    if st.button("Find Nearby Locations"):
        # Clear previous debug info
        st.session_state.debug_info = []
        
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
                geolocator = Nominatim(user_agent="miami_explorer")
                try:
                    location = geolocator.geocode(location_input, timeout=10)
                    if location:
                        coordinates = (location.latitude, location.longitude)
                    else:
                        st.error("Could not find coordinates for the provided location")
                        st.stop()
                except Exception as e:
                    st.error(f"Error geocoding address: {str(e)}")
                    st.stop()
            
            # Store location data in session state
            st.session_state.location_data = {
                'coordinates': coordinates,
                'categories': {
                    'education': {
                        'public_schools': show_public_schools,
                        'private_schools': show_private_schools,
                        'charter_schools': show_charter_schools
                    },
                    'emergency': {
                        'police': show_police,
                        'fire': show_fire
                    },
                    'healthcare': {
                        'hospitals': show_hospitals,
                        'mental_health': show_mental_health,
                        'clinics': show_clinics
                    },
                    'infrastructure': {
                        'bus_stops': show_bus_stops,
                        'libraries': show_libraries,
                        'parks': show_parks
                    }
                },
                'radius': radius
            }
            
            # Get nearby locations
            all_locations = []
            
            # Education facilities
            if show_public_schools or show_private_schools or show_charter_schools:
                education_api = apis['Education']
                nearby_zips = zip_validator.get_nearby_zips(location_input, radius)
                
                for zip_code in nearby_zips:
                    if show_public_schools:
                        schools = education_api.get_schools_by_zip(zip_code, 'public')
                        if schools.get('success'):
                            all_locations.extend(schools['data']['schools'])
                    
                    if show_private_schools:
                        schools = education_api.get_schools_by_zip(zip_code, 'private')
                        if schools.get('success'):
                            all_locations.extend(schools['data']['schools'])
                    
                    if show_charter_schools:
                        schools = education_api.get_schools_by_zip(zip_code, 'charter')
                        if schools.get('success'):
                            all_locations.extend(schools['data']['schools'])
            
            # Emergency services
            if show_police or show_fire:
                emergency_api = apis['Emergency']
                
                if show_police:
                    police_stations = emergency_api.get_police_stations()
                    if police_stations and 'features' in police_stations:
                        all_locations.extend(police_stations['features'])
                
                if show_fire:
                    fire_stations = emergency_api.get_fire_stations()
                    if fire_stations and 'features' in fire_stations:
                        all_locations.extend(fire_stations['features'])
            
            # Healthcare facilities
            if show_hospitals or show_mental_health or show_clinics:
                healthcare_api = apis['Healthcare']
                
                if show_hospitals:
                    hospitals = healthcare_api.get_hospitals()
                    if hospitals and 'features' in hospitals:
                        all_locations.extend(hospitals['features'])
                
                if show_mental_health:
                    mental_health_centers = healthcare_api.get_mental_health_centers()
                    if mental_health_centers and 'features' in mental_health_centers:
                        all_locations.extend(mental_health_centers['features'])
                
                if show_clinics:
                    clinics = healthcare_api.get_free_standing_clinics()
                    if clinics and 'features' in clinics:
                        all_locations.extend(clinics['features'])
            
            # Infrastructure
            if show_bus_stops or show_libraries or show_parks:
                if show_bus_stops:
                    bus_stops = apis['Infrastructure']['Bus Stops'].get_all_stops()
                    if bus_stops and 'features' in bus_stops:
                        all_locations.extend(bus_stops['features'])
                
                if show_libraries:
                    libraries = apis['Infrastructure']['Libraries'].get_all_libraries()
                    if libraries and 'features' in libraries:
                        all_locations.extend(libraries['features'])
                
                if show_parks:
                    parks = apis['Infrastructure']['Parks'].get_all_parks()
                    if parks and 'features' in parks:
                        all_locations.extend(parks['features'])
            
            # Add a system message with location data
            location_summary = f"Location found at coordinates {coordinates}. Found {len(all_locations)} nearby points of interest within {radius} miles."
            st.session_state.messages.append({
                "role": "system",
                "content": location_summary
            })
            
            # Rerun to update the chat display
            st.rerun()

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
                    context += f"Searching for various facilities within {st.session_state.location_data['radius']} miles. "
                    
                    # Add category information
                    categories = st.session_state.location_data['categories']
                    if any(categories['education'].values()):
                        context += "Education facilities (public, private, charter schools) are available. "
                    if any(categories['emergency'].values()):
                        context += "Emergency services (police, fire stations) are available. "
                    if any(categories['healthcare'].values()):
                        context += "Healthcare facilities (hospitals, mental health centers, clinics) are available. "
                    if any(categories['infrastructure'].values()):
                        context += "Infrastructure (bus stops, libraries, parks) is available. "
                
                # Get response from the model
                response = client.chat.completions.create(
                    model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
                    messages=[
                        {"role": "system", "content": f"You are a helpful AI assistant that knows about Miami-Dade County and its facilities. {context}"},
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