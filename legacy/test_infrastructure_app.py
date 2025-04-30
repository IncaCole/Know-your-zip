import streamlit as st
import pandas as pd
from infrastructure import BusRoutesAPI, BusStopsAPI, LibrariesAPI, ParksAPI
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import re
from src.zip_validator import ZIPValidator

st.set_page_config(page_title="Miami-Dade Infrastructure Finder", layout="wide")

st.title("🏢 Miami-Dade Infrastructure Finder")
st.write("Enter your address or ZIP code to find nearby infrastructure in Miami-Dade County")

# Initialize APIs
@st.cache_resource
def get_apis():
    return {
        'Bus Routes': BusRoutesAPI(),
        'Bus Stops': BusStopsAPI(),
        'Libraries': LibrariesAPI(),
        'Parks': ParksAPI()
    }

# Initialize ZIP validator
@st.cache_resource
def get_zip_validator():
    return ZIPValidator()

apis = get_apis()
zip_validator = get_zip_validator()

# Single search input
location_input = st.text_input("Enter your address or ZIP code")

# Infrastructure categories
categories = list(apis.keys())
selected_category = st.selectbox("Select infrastructure type", categories)

# Search radius
radius = st.slider("Search radius (miles)", 1.0, 20.0, 5.0)

def get_coordinates(address: str):
    """Get coordinates for an address using Nominatim"""
    geolocator = Nominatim(user_agent="infrastructure_finder")
    try:
        location = geolocator.geocode(address, timeout=10)
        if location:
            return (location.latitude, location.longitude)
        return None
    except Exception as e:
        st.error(f"Error geocoding address: {str(e)}")
        return None

def calculate_distances(user_location: tuple, locations_data: dict) -> pd.DataFrame:
    """Calculate distances between user location and infrastructure locations"""
    distances = []
    features = []
    
    for feature in locations_data.get('features', []):
        try:
            if 'geometry' in feature and feature['geometry']:
                coords = feature['geometry']['coordinates']
                location_coords = (coords[1], coords[0])  # GeoJSON uses [longitude, latitude]
                
                if all(coord is not None for coord in location_coords):
                    distance = geodesic(user_location, location_coords).miles
                    feature['properties']['distance_miles'] = distance
                    features.append(feature['properties'])
        except Exception as e:
            st.warning(f"Error calculating distance for a location: {str(e)}")
    
    return pd.DataFrame(features)

if st.button("Find Nearby Infrastructure"):
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
            api = apis[selected_category]
            try:
                data = api.get_all_routes() if selected_category == 'Bus Routes' else \
                       api.get_all_stops() if selected_category == 'Bus Stops' else \
                       api.get_all_libraries() if selected_category == 'Libraries' else \
                       api.get_all_parks()
                
                if data:
                    # Calculate distances and create DataFrame
                    df = calculate_distances(coordinates, data)
                    
                    # Filter by radius
                    df = df[df['distance_miles'] <= radius]
                    
                    if not df.empty:
                        # Sort by distance
                        df = df.sort_values('distance_miles')
                        
                        # Display the data
                        st.subheader(f"Nearby {selected_category}")
                        
                        # Create display dataframe with selected columns
                        display_df = pd.DataFrame()
                        
                        # Add common columns
                        for col in df.columns:
                            if col != 'distance_miles':
                                display_df[col] = df[col]
                        display_df['Distance (miles)'] = df['distance_miles'].round(2)
                        
                        # Display the formatted table
                        st.dataframe(
                            display_df,
                            use_container_width=True,
                            hide_index=True
                        )
                        
                        # Show total count and radius
                        st.write(f"Found {len(display_df)} locations within {radius} miles")
                        
                        # Add expandable sections for additional information
                        with st.expander("Show Additional Information"):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write("Search Location:")
                                st.write(f"Coordinates: {coordinates}")
                                if zip_match:
                                    st.write(f"ZIP Code: {location_input} (Miami-Dade County)")
                            with col2:
                                st.write("Results Summary:")
                                st.write(f"Closest: {display_df.iloc[0].get('NAME', 'Unknown')} ({display_df.iloc[0]['Distance (miles)']} miles)")
                                st.write(f"Furthest: {display_df.iloc[-1].get('NAME', 'Unknown')} ({display_df.iloc[-1]['Distance (miles)']} miles)")
                        
                        # Display raw data option
                        if st.checkbox("Show raw data"):
                            st.write("Raw Data Columns:", df.columns.tolist())
                            st.dataframe(df)
                    else:
                        st.info(f"No {selected_category} found within {radius} miles")
                else:
                    st.error(f"Could not fetch {selected_category} data")
            except Exception as e:
                st.error(f"Error fetching {selected_category} data: {str(e)}")
        else:
            st.error("Could not find coordinates for the provided location") 