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
import time
from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API endpoints for Miami-Dade County Open Data
API_ENDPOINTS = {
    'hospitals': 'https://opendata.arcgis.com/datasets/MDC::hospitals.geojson',
    'zoning': 'https://opendata.arcgis.com/api/v3/datasets/69bda17d8d1f48e58268103aebf86546_0/downloads/data?format=geojson&spatialRefId=4326',
    'schools': 'https://gisweb.miamidade.gov/arcgis/rest/services/MD_SchoolBoardBuffer/MapServer/1/query?where=1=1&outFields=*&f=geojson',
    'parks': 'https://services.arcgis.com/8Pc9XBTAsYuxx9Ny/arcgis/rest/services/Parks/FeatureServer/0/query?where=1%3D1&outFields=*&returnGeometry=true&f=geojson'
}

# Fallback data for each category
FALLBACK_DATA = {
    'hospitals': {
        'features': [
            {
                'properties': {
                    'name': 'Jackson Memorial Hospital',
                    'address': '1611 NW 12th Ave, Miami, FL 33136',
                    'phone': '(305) 585-1111'
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [-80.2103, 25.7907]
                }
            }
        ]
    },
    'schools': {
        'features': [
            {
                'properties': {
                    'name': 'Miami Senior High School',
                    'address': '2450 SW 1st St, Miami, FL 33135',
                    'phone': '(305) 649-9900'
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [-80.2156, 25.7644]
                }
            }
        ]
    },
    'parks': {
        'features': [
            {
                'properties': {
                    'name': 'Bayfront Park',
                    'address': '301 N Biscayne Blvd, Miami, FL 33132'
                },
                'geometry': {
                    'type': 'Point',
                    'coordinates': [-80.1877, 25.7743]
                }
            }
        ]
    },
    'zoning': {
        'features': [
            {
                'properties': {
                    'name': 'Downtown Miami',
                    'zoning_code': 'T6-8-O'
                },
                'geometry': {
                    'type': 'Polygon',
                    'coordinates': [[[-80.1937, 25.7743], [-80.1937, 25.7743]]]
                }
            }
        ]
    }
}

def fetch_data_with_retry(endpoint: str, max_retries: int = 3, retry_delay: int = 2) -> Optional[Dict[str, Any]]:
    """
    Fetch data from an API endpoint with retry logic.
    
    Args:
        endpoint: The API endpoint URL
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
        
    Returns:
        JSON response data or None if all retries fail
    """
    for attempt in range(max_retries):
        try:
            response = requests.get(endpoint, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt + 1} failed for {endpoint}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
            else:
                logger.error(f"All retry attempts failed for {endpoint}")
                return None

def get_coordinates(address: str) -> Optional[tuple]:
    """
    Get coordinates for an address with error handling.
    
    Args:
        address: The address to geocode
        
    Returns:
        Tuple of (latitude, longitude) or None if geocoding fails
    """
    geolocator = Nominatim(user_agent="location_finder")
    try:
        location = geolocator.geocode(address, timeout=10)
        if location:
            return (location.latitude, location.longitude)
        logger.warning(f"Could not find coordinates for address: {address}")
        return None
    except Exception as e:
        logger.error(f"Error geocoding address {address}: {str(e)}")
        return None

def calculate_distances(user_location: tuple, locations_df: pd.DataFrame) -> list:
    """
    Calculate distances between user location and locations in DataFrame.
    
    Args:
        user_location: Tuple of (latitude, longitude)
        locations_df: DataFrame containing location data
        
    Returns:
        List of distances in miles
    """
    distances = []
    for _, row in locations_df.iterrows():
        try:
            if 'geometry' in row and row['geometry']:
                coords = row['geometry']['coordinates']
                location_coords = (coords[1], coords[0])
            else:
                location_coords = (row.get('latitude'), row.get('longitude'))
            
            if all(coord is not None for coord in location_coords):
                distance = geodesic(user_location, location_coords).miles
                distances.append(distance)
            else:
                distances.append(None)
        except Exception as e:
            logger.error(f"Error calculating distance: {str(e)}")
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
                
                # Try to fetch data with retries
                data = fetch_data_with_retry(endpoint)
                
                # If API call fails, use fallback data
                if data is None:
                    st.warning(f"Could not fetch {category} data. Using fallback data.")
                    data = FALLBACK_DATA[category]
                
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
                    display_df = df.drop('geometry', axis=1, errors='ignore')
                    st.dataframe(display_df.head(5))
                else:
                    st.error(f"No {category} data available")
        else:
            st.error("Could not find location. Please try a different address or zip code.")

if __name__ == "__main__":
    main() 