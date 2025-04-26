import streamlit as st
import pandas as pd
import api_list_new
import re
from src.zip_validator import ZIPValidator
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster

# Configure the page
st.set_page_config(page_title="Miami County Map Viewer", layout="wide")

# Add custom CSS for popup styling
st.markdown("""
<style>
    .folium-popup-content {
        color: #000000 !important;
        background-color: #ffffff !important;
    }
    .folium-popup-content-wrapper {
        background-color: #ffffff !important;
    }
    [data-theme="dark"] .folium-popup-content {
        color: #ffffff !important;
        background-color: #1e1e1e !important;
    }
    [data-theme="dark"] .folium-popup-content-wrapper {
        background-color: #1e1e1e !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state variables
if 'map_center' not in st.session_state:
    st.session_state.map_center = [25.7617, -80.1918]  # Miami coordinates
if 'zoom_level' not in st.session_state:
    st.session_state.zoom_level = 10
if 'markers' not in st.session_state:
    st.session_state.markers = []
if 'last_location' not in st.session_state:
    st.session_state.last_location = None

def convert_to_latlong(center):
    """Convert center format between Streamlit-Folium and Folium."""
    if isinstance(center, dict) and 'lat' in center and 'lng' in center:
        return [center['lat'], center['lng']]
    return center

st.title("🗺️ Miami County Map Viewer")
st.write("Enter your address or ZIP code to see your location and nearby points of interest in Miami-Dade County")

# Initialize ZIP validator
@st.cache_resource
def get_zip_validator():
    return ZIPValidator()

zip_validator = get_zip_validator()

# Create two columns for input and map
col1, col2 = st.columns([1, 2])

with col1:
    # Location input
    location_input = st.text_input("Enter your address or ZIP code")
    
    # Location categories
    categories = ['public_schools', 'police_stations']
    selected_categories = st.multiselect(
        "Select location types to display",
        categories,
        default=['public_schools', 'police_stations']
    )
    
    # Search radius
    radius = st.slider("Search radius (miles)", 1.0, 20.0, 13.38)

    if st.button("Find Locations"):
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
                coordinates = api_list_new.get_coordinates(location_input)
            
            if coordinates:
                # Update map center and zoom
                st.session_state.map_center = list(coordinates)  # Convert to list
                st.session_state.zoom_level = 12
                st.session_state.last_location = location_input
                
                # Clear previous markers
                st.session_state.markers = []
                
                # Add user location marker
                st.session_state.markers.append({
                    'location': list(coordinates),  # Convert to list
                    'popup': "Your Location",
                    'icon': 'red'
                })
                
                # Get and display locations for each selected category
                all_locations = []
                for category in selected_categories:
                    locations_df = api_list_new.get_nearby_locations(coordinates, category, radius)
                    
                    if not locations_df.empty:
                        for _, row in locations_df.iterrows():
                            if 'geometry' in row and row['geometry']:
                                coords = row['geometry']['coordinates']
                                location_coords = [coords[1], coords[0]]
                                
                                popup_text = f"""
                                <b>{row.get('NAME', 'Unknown')}</b><br>
                                Address: {row.get('ADDRESS', 'N/A')}<br>
                                City: {row.get('CITY', 'N/A')}<br>
                                ZIP: {row.get('ZIPCODE', 'N/A')}<br>
                                Distance: {row['distance_miles']:.2f} miles
                                """
                                
                                if category == 'public_schools':
                                    if 'GRADES' in row:
                                        popup_text += f"<br>Grades: {row['GRADES']}"
                                    if 'ENROLLMNT' in row:
                                        popup_text += f"<br>Enrollment: {row['ENROLLMNT']}"
                                
                                icon_color = 'blue' if category == 'public_schools' else 'green'
                                
                                st.session_state.markers.append({
                                    'location': location_coords,
                                    'popup': popup_text,
                                    'icon': icon_color
                                })
                                
                                all_locations.append(row)
                
                # Store locations for summary
                if all_locations:
                    summary_df = pd.DataFrame(all_locations)
                    summary_df['Category'] = summary_df.apply(
                        lambda x: 'Public School' if 'GRADES' in x else 'Police Station', axis=1
                    )
                    
                    # Display summary statistics
                    st.write(f"Found {len(summary_df)} locations within {radius} miles")
                    
                    # Show category breakdown
                    category_counts = summary_df['Category'].value_counts()
                    st.write("Location Types:")
                    for category, count in category_counts.items():
                        st.write(f"- {category}: {count}")
                    
                    # Show closest locations
                    st.write("\nClosest Locations:")
                    closest_locations = summary_df.nsmallest(5, 'distance_miles')
                    for _, loc in closest_locations.iterrows():
                        st.write(f"- {loc.get('NAME', 'Unknown')} ({loc['distance_miles']:.2f} miles)")
            else:
                st.error("Could not find coordinates for the provided location")

# Display the map in col2
with col2:
    # Create the base map with converted center coordinates
    map_center = convert_to_latlong(st.session_state.map_center)
    m = folium.Map(location=map_center, zoom_start=st.session_state.zoom_level)
    
    # Add markers
    for marker in st.session_state.markers:
        folium.Marker(
            marker['location'],
            popup=folium.Popup(marker['popup'], max_width=300),
            icon=folium.Icon(color=marker['icon'], icon='info-sign')
        ).add_to(m)
    
    # Display the map with a key to maintain state
    map_data = st_folium(
        m,
        width=800,
        height=600,
        key="main_map"
    )
    
    # Update center and zoom if map is moved
    if map_data['center']:
        st.session_state.map_center = convert_to_latlong(map_data['center'])
    if map_data['zoom']:
        st.session_state.zoom_level = map_data['zoom'] 