import requests
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import streamlit as st
import json
import os
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

# API endpoints for Miami-Dade County Open Data
API_ENDPOINTS = {
    'hospitals': 'https://opendata.arcgis.com/datasets/MDC::hospitals.geojson',
    'zoning': 'https://opendata.arcgis.com/api/v3/datasets/69bda17d8d1f48e58268103aebf86546_0/downloads/data?format=geojson&spatialRefId=4326',
    'schools': 'https://gisweb.miamidade.gov/arcgis/rest/services/MD_SchoolBoardBuffer/MapServer/1/query?where=1=1&outFields=*&f=geojson',
    'parks': 'https://services.arcgis.com/8Pc9XBTAsYuxx9Ny/arcgis/rest/services/Parks/FeatureServer/0/query?where=1%3D1&outFields=*&returnGeometry=true&f=geojson'
}

def fetch_data(endpoint):
    try:
        response = requests.get(endpoint)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data from {endpoint}: {str(e)}")
        return None

def get_coordinates(address):
    geolocator = Nominatim(user_agent="location_finder")
    location = geolocator.geocode(address)
    if location:
        return (location.latitude, location.longitude)
    return None

def calculate_distances(user_location, locations_df):
    distances = []
    for _, row in locations_df.iterrows():
        try:
            # Extract coordinates from geometry if available
            if 'geometry' in row and row['geometry']:
                coords = row['geometry']['coordinates']
                location_coords = (coords[1], coords[0])  # GeoJSON uses [longitude, latitude]
            else:
                location_coords = (row.get('latitude'), row.get('longitude'))
            
            if all(coord is not None for coord in location_coords):
                distance = geodesic(user_location, location_coords).miles
                distances.append(distance)
            else:
                distances.append(None)
        except (KeyError, ValueError, TypeError):
            distances.append(None)
    return distances

def main():
    st.title("Miami-Dade County Location Finder")
    
    # User input
    address = st.text_input("Enter your address or zip code:")
    
    if address:
        user_location = get_coordinates(address)
        if user_location:
            st.success(f"Location found: {user_location}")
            
            # Fetch and process data
            for category, endpoint in API_ENDPOINTS.items():
                st.subheader(f"Nearby {category.replace('_', ' ').title()}")
                data = fetch_data(endpoint)
                
                if data and 'features' in data:
                    # Create DataFrame with both properties and geometry
                    features_with_geometry = []
                    for feature in data['features']:
                        properties = feature.get('properties', {})
                        properties['geometry'] = feature.get('geometry')
                        features_with_geometry.append(properties)
                    
                    df = pd.DataFrame(features_with_geometry)
                    
                    # Calculate distances
                    df['distance_miles'] = calculate_distances(user_location, df)
                    
                    # Sort by distance
                    df = df.sort_values('distance_miles')
                    
                    # Display results
                    display_df = df.drop('geometry', axis=1, errors='ignore')  # Remove geometry column for display
                    st.dataframe(display_df.head(5))
                else:
                    st.warning(f"No {category} data available")
        else:
            st.error("Could not find location. Please try a different address or zip code.")

if __name__ == "__main__":
    main() 