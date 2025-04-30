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
from src.logger import logger

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
    """Fetch data from API with retry mechanism"""
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to fetch data from {endpoint} (attempt {attempt + 1}/{max_retries})")
            response = requests.get(endpoint)
            response.raise_for_status()
            logger.info(f"Successfully fetched data from {endpoint}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.warning(f"Failed to fetch data from {endpoint}: {str(e)}")
            if attempt < max_retries - 1:
                logger.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                logger.error(f"All {max_retries} attempts failed for {endpoint}")
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

def get_nearby_locations(user_location: tuple, category: str, radius_miles: float = 5.0) -> pd.DataFrame:
    """
    Get nearby locations for a specific category within a given radius.
    
    Args:
        user_location: Tuple of (latitude, longitude)
        category: Type of location (hospitals, schools, etc.)
        radius_miles: Search radius in miles
        
    Returns:
        DataFrame containing nearby locations
    """
    try:
        # Fetch data from API
        data = fetch_data_with_retry(API_ENDPOINTS[category])
        if data is None:
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
            
            # Filter by radius
            df = df[df['distance_miles'] <= radius_miles]
            
            # Sort by distance
            df = df.sort_values('distance_miles')
            
            return df
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Error getting nearby {category}: {str(e)}")
        return pd.DataFrame()

def display_nearby_locations(df: pd.DataFrame, category: str, current_zip: str = None):
    """
    Display nearby locations in a formatted way.
    
    Args:
        df: DataFrame containing location data
        category: Type of location
        current_zip: Current ZIP code (if available)
    """
    if df.empty:
        st.info(f"No {category} found nearby.")
        return
        
    for _, row in df.iterrows():
        # Create a card for each location
        st.markdown(f"""
        <div style='background-color: #ffffff; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.1);'>
            <h4 style='color: #0d6efd; margin-bottom: 0.5rem;'>{row.get('name', 'Unknown')}</h4>
            <p style='margin-bottom: 0.5rem;'><strong>Address:</strong> {row.get('address', 'N/A')}</p>
            {f"<p style='margin-bottom: 0.5rem;'><strong>Phone:</strong> {row.get('phone', 'N/A')}</p>" if 'phone' in row else ''}
            <p style='margin-bottom: 0.5rem;'><strong>Distance:</strong> {row['distance_miles']:.1f} miles</p>
            {f"<p style='color: #ff0000;'>OUT OF YOUR ZIPCODE BUT NEARBY</p>" if current_zip and row.get('zip_code') != current_zip else ''}
        </div>
        """, unsafe_allow_html=True)

def get_nearby_zip_codes(zip_code: str, radius_miles: float = 5.0) -> list:
    """
    Get nearby ZIP codes within a given radius.
    
    Args:
        zip_code: Current ZIP code
        radius_miles: Search radius in miles
        
    Returns:
        List of nearby ZIP codes
    """
    # This is a placeholder - you would need to implement actual ZIP code distance calculation
    # using a ZIP code database or API
    return []

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