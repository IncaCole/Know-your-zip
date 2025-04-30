import streamlit as st
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import re
from src.zip_validator import ZIPValidator
import requests
import time
from typing import Optional, Dict, Any

st.set_page_config(page_title="Education Facility Finder", layout="wide")

st.title("🎓 Education Facility Finder")
st.write("Enter your address or ZIP code to find nearby schools and education facilities in Miami-Dade County")

# API endpoints
EDUCATION_API_ENDPOINTS = {
    'public_schools': 'https://services.arcgis.com/8Pc9XBTAsYuxx9Ny/arcgis/rest/services/SchoolSite_gdb/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson',
    'private_schools': 'https://services.arcgis.com/8Pc9XBTAsYuxx9Ny/arcgis/rest/services/PrivateSchool_gdb/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson',
    'charter_schools': 'https://services.arcgis.com/8Pc9XBTAsYuxx9Ny/arcgis/rest/services/CharterSchool_gdb/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson',
    'bus_stops': 'https://services.arcgis.com/8Pc9XBTAsYuxx9Ny/arcgis/rest/services/MDCPSBusStop_gdb/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson'
}

# Initialize ZIP validator
@st.cache_resource
def get_zip_validator():
    return ZIPValidator()

zip_validator = get_zip_validator()

# Single search input
location_input = st.text_input("Enter your address or ZIP code")

# Education facility types
facility_types = ['Public Schools', 'Private Schools', 'Charter Schools', 'School Bus Stops']
selected_type = st.selectbox("Select facility type", facility_types)

# Search radius
radius = st.slider("Search radius (miles)", 1.0, 20.0, 5.0)

def fetch_data_with_retry(endpoint: str, max_retries: int = 3, retry_delay: int = 2) -> Optional[Dict[str, Any]]:
    """Fetch data from API with retry mechanism"""
    for attempt in range(max_retries):
        try:
            response = requests.get(endpoint)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                return None

def get_coordinates(address: str):
    """Get coordinates for an address using Nominatim"""
    geolocator = Nominatim(user_agent="education_finder")
    try:
        location = geolocator.geocode(address, timeout=10)
        if location:
            return (location.latitude, location.longitude)
        return None
    except Exception as e:
        st.error(f"Error geocoding address: {str(e)}")
        return None

def calculate_distances(user_location: tuple, facilities_data: dict) -> pd.DataFrame:
    """Calculate distances between user location and education facilities"""
    facilities = []
    
    for feature in facilities_data.get('features', []):
        try:
            if 'geometry' in feature and feature['geometry']:
                coords = feature['geometry']['coordinates']
                location_coords = (coords[1], coords[0])  # GeoJSON uses [longitude, latitude]
                
                if all(coord is not None for coord in location_coords):
                    distance = geodesic(user_location, location_coords).miles
                    feature['properties']['distance_miles'] = distance
                    facilities.append(feature['properties'])
        except Exception as e:
            st.warning(f"Error calculating distance for a facility: {str(e)}")
    
    return pd.DataFrame(facilities)

if st.button("Find Nearby Education Facilities"):
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
            coordinates = get_coordinates(location_input)
        
        if coordinates:
            # Get data from selected API
            try:
                if selected_type == 'Public Schools':
                    data = fetch_data_with_retry(EDUCATION_API_ENDPOINTS['public_schools'])
                elif selected_type == 'Private Schools':
                    data = fetch_data_with_retry(EDUCATION_API_ENDPOINTS['private_schools'])
                elif selected_type == 'Charter Schools':
                    data = fetch_data_with_retry(EDUCATION_API_ENDPOINTS['charter_schools'])
                else:  # School Bus Stops
                    data = fetch_data_with_retry(EDUCATION_API_ENDPOINTS['bus_stops'])
                
                if data:
                    # Calculate distances and create DataFrame
                    df = calculate_distances(coordinates, data)
                    
                    # Filter by radius
                    df = df[df['distance_miles'] <= radius]
                    
                    if not df.empty:
                        # Sort by distance
                        df = df.sort_values('distance_miles')
                        
                        # Display the data
                        st.subheader(f"Nearby {selected_type}")
                        
                        # Create display dataframe with selected columns
                        display_df = pd.DataFrame()
                        
                        # Add common columns
                        display_df['Name'] = df['NAME']
                        display_df['Address'] = df['ADDRESS']
                        display_df['City'] = df['CITY']
                        display_df['ZIP'] = df['ZIPCODE']
                        display_df['Distance (miles)'] = df['distance_miles'].round(2)
                        
                        # Add type-specific columns
                        if selected_type in ['Public Schools', 'Private Schools', 'Charter Schools']:
                            if 'GRADE' in df.columns:
                                display_df['Grades'] = df['GRADE']
                            if 'ENROLLMNT' in df.columns:
                                display_df['Enrollment'] = df['ENROLLMNT']
                            if 'CAPACITY' in df.columns:
                                display_df['Capacity'] = df['CAPACITY']
                        
                        # Display the formatted table
                        st.dataframe(
                            display_df,
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        # Show total count and radius
                        st.write(f"Found {len(display_df)} facilities within {radius} miles")
                        
                        # Add expandable sections for additional information
                        with st.expander("Show Additional Information"):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.write("Search Location:")
                                st.write(f"Coordinates: {coordinates}")
                                if zip_match:
                                    st.write(f"ZIP Code: {location_input} (Miami-Dade County)")
                                    # Show nearby ZIP codes
                                    nearby_zips = zip_validator.get_nearby_zips(location_input, radius)
                                    if nearby_zips:
                                        st.write(f"Nearby ZIP Codes ({len(nearby_zips)}):")
                                        st.write(", ".join(sorted(nearby_zips)))
                            with col2:
                                st.write("Results Summary:")
                                st.write(f"Closest: {display_df.iloc[0]['Name']} ({display_df.iloc[0]['Distance (miles)']} miles)")
                                st.write(f"Furthest: {display_df.iloc[-1]['Name']} ({display_df.iloc[-1]['Distance (miles)']} miles)")
                            with col3:
                                st.write("Facility Statistics:")
                                if selected_type in ['Public Schools', 'Private Schools', 'Charter Schools']:
                                    if 'CAPACITY' in df.columns and 'ENROLLMNT' in df.columns:
                                        total_capacity = df['CAPACITY'].sum()
                                        total_enrollment = df['ENROLLMNT'].sum()
                                        st.write(f"Total Capacity: {total_capacity:,}")
                                        st.write(f"Total Enrollment: {total_enrollment:,}")
                                        if total_capacity > 0:
                                            st.write(f"Utilization: {(total_enrollment/total_capacity*100):.1f}%")
                        
                        # Display raw data option
                        if st.checkbox("Show raw data"):
                            st.write("Raw Data Columns:", df.columns.tolist())
                            st.dataframe(df)
                    else:
                        st.info(f"No {selected_type} found within {radius} miles")
                else:
                    st.error(f"Could not fetch {selected_type} data")
            except Exception as e:
                st.error(f"Error fetching {selected_type} data: {str(e)}")
                st.write("Debug info:")
                st.write("Data:", data)
        else:
            st.error("Could not find coordinates for the provided location") 