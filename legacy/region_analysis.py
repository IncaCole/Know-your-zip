import streamlit as st
from infrastructure import ParksAPI
from typing import Dict, Any, Tuple

def categorize_location(lat: float, lon: float) -> str:
    """
    Categorize a location into one of Miami-Dade's regions based on coordinates.
    
    Approximate boundaries:
    - Northeast: North of 25.8500°N and East of -80.2000°W
    - Southeast: South of 25.8500°N and East of -80.2000°W
    - Southwest: South of 25.8500°N and West of -80.2000°W
    - Northwest: North of 25.8500°N and West of -80.2000°W
    """
    if lat >= 25.8500:  # North
        if lon >= -80.2000:  # East
            return "Northeast"
        else:
            return "Northwest"
    else:  # South
        if lon >= -80.2000:  # East
            return "Southeast"
        else:
            return "Southwest"

def analyze_parks_distribution():
    """Analyze the distribution of parks across Miami-Dade County regions."""
    
    # Initialize the Parks API
    parks_api = ParksAPI()
    
    # Get all parks
    parks_data = parks_api.get_all_parks()
    
    # Initialize counters for each region
    region_counts = {
        "Northeast": 0,
        "Southeast": 0,
        "Southwest": 0,
        "Northwest": 0
    }
    
    # Initialize lists to store parks in each region
    region_parks = {
        "Northeast": [],
        "Southeast": [],
        "Southwest": [],
        "Northwest": []
    }
    
    if parks_data and 'features' in parks_data:
        for park in parks_data['features']:
            if 'geometry' in park and park['geometry']:
                coords = park['geometry']['coordinates']
                # GeoJSON uses [longitude, latitude] order
                lon, lat = coords[0], coords[1]
                region = categorize_location(lat, lon)
                region_counts[region] += 1
                region_parks[region].append(park['properties'].get('NAME', 'Unnamed Park'))
    
    return region_counts, region_parks

if __name__ == "__main__":
    st.title("Miami-Dade County Parks Distribution Analysis")
    
    counts, parks = analyze_parks_distribution()
    
    # Display the counts
    st.header("Parks Distribution by Region")
    for region, count in counts.items():
        st.metric(f"{region} Region", count)
    
    # Display detailed park lists
    st.header("Detailed Park Lists by Region")
    for region, park_list in parks.items():
        with st.expander(f"{region} Region Parks"):
            for park in sorted(park_list):
                st.write(f"- {park}") 