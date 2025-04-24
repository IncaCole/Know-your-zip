import streamlit as st
import folium
from streamlit_folium import st_folium
from geo_data import GeoDataAPI
import json

# Configure the page
st.set_page_config(page_title="Miami-Dade Geographic Data Explorer", layout="wide")

# Initialize the GeoDataAPI
@st.cache_resource
def get_geo_api():
    return GeoDataAPI()

geo_api = get_geo_api()

# Set up the main title
st.title("🗺️ Miami-Dade Geographic Data Explorer")
st.write("Explore flood zones, evacuation routes, and bus routes in Miami-Dade County")

# Create two columns for controls and map
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Data Layers")
    
    # Layer toggles
    show_flood_zones = st.checkbox("Show Flood Zones", value=True)
    show_evacuation_routes = st.checkbox("Show Evacuation Routes", value=True)
    show_bus_routes = st.checkbox("Show Bus Routes", value=True)
    
    # Color settings
    flood_zone_color = 'blue'
    evacuation_route_color = 'red'
    bus_route_color = 'green'

# Initialize map center to Miami-Dade County
miami_center = [25.7617, -80.1918]

with col2:
    # Create base map
    m = folium.Map(location=miami_center, zoom_start=10)
    
    try:
        if show_flood_zones:
            with st.spinner("Loading flood zones..."):
                flood_zones = geo_api.get_flood_zones()
                folium.GeoJson(
                    flood_zones,
                    name='Flood Zones',
                    style_function=lambda x: {
                        'fillColor': flood_zone_color,
                        'color': flood_zone_color,
                        'weight': 1,
                        'fillOpacity': 0.3
                    },
                    tooltip=folium.GeoJsonTooltip(
                        fields=['ZONESUBTY', 'FZONE', 'ELEV'],
                        aliases=['Zone Subtype:', 'Flood Zone:', 'Elevation:'],
                        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
                    )
                ).add_to(m)
        
        if show_evacuation_routes:
            with st.spinner("Loading evacuation routes..."):
                evacuation_routes = geo_api.get_evacuation_routes()
                folium.GeoJson(
                    evacuation_routes,
                    name='Evacuation Routes',
                    style_function=lambda x: {
                        'color': evacuation_route_color,
                        'weight': 3,
                        'opacity': 0.8
                    },
                    tooltip=folium.GeoJsonTooltip(
                        fields=['SN', 'CREATEDBY'],
                        aliases=['Serial Number:', 'Created By:'],
                        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
                    )
                ).add_to(m)
        
        if show_bus_routes:
            with st.spinner("Loading bus routes..."):
                bus_routes = geo_api.get_bus_routes()
                folium.GeoJson(
                    bus_routes,
                    name='Bus Routes',
                    style_function=lambda x: {
                        'color': bus_route_color,
                        'weight': 2,
                        'opacity': 0.7
                    },
                    tooltip=folium.GeoJsonTooltip(
                        fields=['LINEABBR', 'LINENAME', 'RTNAME'],
                        aliases=['Line:', 'Line Name:', 'Route Name:'],
                        style=("background-color: white; color: #333333; font-family: arial; font-size: 12px; padding: 10px;")
                    )
                ).add_to(m)
        
        # Add layer control
        folium.LayerControl().add_to(m)
        
        # Display the map
        map_data = st_folium(
            m,
            width=800,
            height=600,
            key="main_map"
        )
        
    except Exception as e:
        st.error(f"Error loading map data: {str(e)}")
        st.write("Please check if the API endpoints are accessible and returning valid GeoJSON data.")

# Add a debug section
with st.expander("Debug Information"):
    st.write("API Base URL:", geo_api.base_url)
    st.write("Flood Zones URL:", geo_api.flood_zones_url)
    st.write("Evacuation Routes URL:", geo_api.evacuation_routes_url)
    st.write("Bus Routes URL:", geo_api.bus_routes_url) 