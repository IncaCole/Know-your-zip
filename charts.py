"""
# Charts module for Miami-Dade County Explorer
# This file will contain chart generation functions for the dashboard
""" 

import streamlit as st
import plotly.express as px
import pandas as pd
from education import EducationAPI
from src.zip_validator import ZIPValidator
from emergency_services import EmergencyServicesAPI
from geopy.distance import geodesic
from infrastructure import ParksAPI, BusStopsAPI

@st.cache_data
def get_schools_by_zip():
    """
    Fetches all schools from each ZIP code and returns a DataFrame with school counts
    """
    education_api = EducationAPI()
    zip_validator = ZIPValidator()
    
    # Get all valid Miami-Dade ZIP codes
    zip_codes = zip_validator.get_all_zip_codes()
    
    # Initialize dictionary to store school counts
    school_counts = {
        'ZIP_Code': [],
        'Total_Schools': [],
        'Public_Schools': [],
        'Private_Schools': [],
        'Charter_Schools': []
    }
    
    # Fetch schools for each ZIP code
    for zip_code in zip_codes:
        public_schools = education_api.get_schools_by_zip(zip_code, 'public')
        private_schools = education_api.get_schools_by_zip(zip_code, 'private')
        charter_schools = education_api.get_schools_by_zip(zip_code, 'charter')
        
        # Count schools if data exists and is successful
        public_count = len(public_schools.get('data', {}).get('schools', [])) if public_schools and public_schools.get('success') else 0
        private_count = len(private_schools.get('data', {}).get('schools', [])) if private_schools and private_schools.get('success') else 0
        charter_count = len(charter_schools.get('data', {}).get('schools', [])) if charter_schools and charter_schools.get('success') else 0
        
        # Add to counts dictionary
        school_counts['ZIP_Code'].append(zip_code)
        school_counts['Public_Schools'].append(public_count)
        school_counts['Private_Schools'].append(private_count)
        school_counts['Charter_Schools'].append(charter_count)
        school_counts['Total_Schools'].append(public_count + private_count + charter_count)
    
    return pd.DataFrame(school_counts)

def plot_schools_histogram():
    """
    Creates and returns a histogram showing the distribution of schools across ZIP codes
    """
    # Get the school counts data
    df = get_schools_by_zip()
    
    # Create histogram using plotly express
    fig = px.histogram(
        df,
        x='Total_Schools',
        nbins=6,
        title='School Distribution',
        labels={'Total_Schools': 'Number of Schools', 'count': 'Number of ZIPs'},
        category_orders={'Total_Schools': sorted(df['Total_Schools'].unique())},  # Sort bins by value
        text_auto=True  # Enable automatic text display
    )
    
    # Update layout for better appearance
    fig.update_layout(
        bargap=0.1,
        xaxis_title='Number of Schools per ZIP',
        yaxis_title='Number of ZIPs',
        showlegend=False,
        yaxis_range=[0, 40],  # Set y-axis range from 0 to 40
        title={
            'text': 'School Distribution',
            'y': 0.95,  # Adjust title position
            'x': 0.5,   # Center title
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 24}  # Make title larger
        }
    )
    
    # Update text position to be inside the bars
    fig.update_traces(
        textposition='inside',
        textfont=dict(size=14, color='white'),  # Make text white and larger
        insidetextanchor='middle'  # Center text in bars
    )
    
    return fig

def plot_schools_by_type():
    """
    Creates and returns a stacked bar chart showing the breakdown of school types by ZIP code
    """
    # Get the school counts data
    df = get_schools_by_zip()
    
    # Create stacked bar chart
    fig = px.bar(
        df,
        x='ZIP_Code',
        y=['Public_Schools', 'Private_Schools', 'Charter_Schools'],
        title='School Types by ZIP Code',
        labels={
            'ZIP_Code': 'ZIP Code',
            'value': 'Number of Schools',
            'variable': 'School Type'
        },
        color_discrete_map={
            'Public_Schools': '#1f77b4',
            'Private_Schools': '#ff7f0e',
            'Charter_Schools': '#2ca02c'
        }
    )
    
    # Update layout for better appearance
    fig.update_layout(
        xaxis_title='ZIP Code',
        yaxis_title='Number of Schools',
        barmode='stack',
        showlegend=True
    )
    
    return fig

@st.cache_data
def plot_fire_station_proximity_pie():
    """
    Creates and returns a pie chart showing the distribution of ZIP codes
    based on their proximity to the nearest fire station.
    """
    # Initialize APIs
    emergency_api = EmergencyServicesAPI()
    zip_validator = ZIPValidator()
    
    # Get all ZIP codes and fire stations
    zip_codes = zip_validator.get_all_zip_codes()
    fire_stations = emergency_api.get_fire_stations()
    
    # Initialize distance categories with new ranges
    distance_categories = {
        '0-1 mile': 0,
        '2-3 miles': 0,
        '4-5 miles': 0,
        '6+ miles': 0
    }
    
    # Calculate distances for each ZIP code
    for zip_code in zip_codes:
        zip_coords = zip_validator.get_zip_coordinates(zip_code)
        if not zip_coords:
            continue
            
        # Find nearest fire station
        min_distance = float('inf')
        for station in fire_stations.get('features', []):
            if 'geometry' in station and station['geometry']:
                coords = station['geometry']['coordinates']
                station_coords = (coords[1], coords[0])  # Convert to (lat, lon)
                distance = geodesic(zip_coords, station_coords).miles
                min_distance = min(min_distance, distance)
        
        # Categorize the ZIP code based on new distance ranges
        if min_distance <= 1:
            distance_categories['0-1 mile'] += 1
        elif min_distance <= 3:
            distance_categories['2-3 miles'] += 1
        elif min_distance <= 5:
            distance_categories['4-5 miles'] += 1
        else:
            distance_categories['6+ miles'] += 1
    
    # Create DataFrame for the pie chart
    df = pd.DataFrame({
        'Distance': list(distance_categories.keys()),
        'ZIP Codes': list(distance_categories.values())
    })
    
    # Sort DataFrame by ZIP code count to assign colors based on segment size
    df = df.sort_values('ZIP Codes', ascending=False)  # Changed to descending order
    
    # Create custom color sequence from light red (larger values) to darker red (smaller values)
    colors = ['#FFD9D9',    # Light red for largest (slightly darker than before)
             '#FFB3B3',     # Medium-light red
             '#FF8080',     # Medium red
             '#FF4D4D']     # Darker red for smallest
    
    # Create pie chart
    fig = px.pie(
        df,
        values='ZIP Codes',
        names='Distance',
        title='Fire Station Coverage',
        color_discrete_sequence=colors,  # Use our custom color sequence
        hole=0.3  # Create a donut chart for better visualization
    )
    
    # Update layout for better appearance
    fig.update_layout(
        title={
            'text': 'Fire Station Coverage',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 24}
        },
        legend_title_text='Distance to Nearest Fire Station',
        annotations=[
            dict(
                text=f'<b>Total ZIP:<br>{sum(distance_categories.values())}</b>',
                x=0.5,
                y=0.5,
                font=dict(
                    size=14,
                    color='black',
                    family='Arial Black'
                ),
                showarrow=False,
                align='center'
            )
        ]
    )
    
    return fig 

@st.cache_data
def plot_zip_park_density_treemap():
    """
    Creates a treemap visualization showing ZIP code sizes with park density indicated by color
    """
    # Initialize APIs
    zip_validator = ZIPValidator()
    parks_api = ParksAPI()
    
    # Get all ZIP codes and their areas
    zip_codes = zip_validator.get_all_zip_codes()
    
    # Get all parks
    parks_data = parks_api.get_all_parks()
    
    # Initialize data structure
    zip_data = {
        'ZIP_Code': [],
        'Area': [],  # Area in square miles
        'Park_Count': [],
        'Parks_per_SqMile': []
    }
    
    # Calculate park counts and densities for each ZIP
    for zip_code in zip_codes:
        # Get ZIP code area (approximate using bounding box for now)
        zip_area = zip_validator.get_zip_area(zip_code)
        
        # Count parks in this ZIP
        park_count = 0
        if parks_data and 'features' in parks_data:
            for park in parks_data['features']:
                if 'geometry' in park and park['geometry']:
                    coords = park['geometry']['coordinates']
                    # Check if park is in this ZIP code
                    if zip_validator.is_point_in_zip(coords[1], coords[0], zip_code):
                        park_count += 1
        
        # Add to data structure
        zip_data['ZIP_Code'].append(zip_code)
        zip_data['Area'].append(zip_area)
        zip_data['Park_Count'].append(park_count)
        zip_data['Parks_per_SqMile'].append(park_count / zip_area if zip_area > 0 else 0)
    
    # Create DataFrame
    df = pd.DataFrame(zip_data)
    
    # Create treemap
    fig = px.treemap(
        df,
        path=[px.Constant("Miami-Dade"), 'ZIP_Code'],
        values='Area',
        color='Park_Count',
        color_continuous_scale='Greens',  # Restore green color scale
        title='Park Locations and Density',
        custom_data=['Park_Count']
    )
    
    # Update layout and hover template
    fig.update_traces(
        hovertemplate="""
        ZIP Code: %{label}<br>
        Parks: %{customdata[0]}<br>
        Area: %{value:.1f} sq mi<br>
        <extra></extra>
        """,
        textinfo="label",
        texttemplate="<b>%{label}</b>"
    )
    
    fig.update_layout(
        title={
            'text': 'Park Locations and Density',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 24}
        },
        height=450,
        margin=dict(l=0, r=0, t=50, b=0),
        showlegend=False  # Keep the color scale legend hidden
    )
    
    return fig 

@st.cache_data(show_spinner=False, ttl=3600)  # Cache for 1 hour
def plot_bus_stop_distance_heatmap(zip_validator):
    """
    Creates a heat map showing the average distance to the nearest bus stop for each ZIP code
    
    Args:
        zip_validator: An instance of ZIPValidator to use for ZIP code operations
    """
    # Initialize APIs
    bus_stops_api = BusStopsAPI()
    
    # Get all ZIP codes and bus stops
    zip_codes = zip_validator.get_all_zip_codes()
    bus_stops = bus_stops_api.get_all_stops()
    
    # Initialize data structure
    zip_data = {
        'ZIP_Code': [],
        'Avg_Distance': []  # Average distance to nearest bus stop in miles
    }
    
    # Calculate average distances for each ZIP code
    for zip_code in zip_codes:
        zip_coords = zip_validator.get_zip_coordinates(zip_code)
        if not zip_coords:
            continue
            
        # Find distances to all bus stops
        distances = []
        for stop in bus_stops.get('features', []):
            if 'geometry' in stop and stop['geometry']:
                coords = stop['geometry']['coordinates']
                stop_coords = (coords[1], coords[0])  # Convert to (lat, lon)
                distance = geodesic(zip_coords, stop_coords).miles
                distances.append(distance)
        
        # Calculate average distance if we found any bus stops
        if distances:
            avg_distance = sum(distances) / len(distances)
            zip_data['ZIP_Code'].append(zip_code)
            zip_data['Avg_Distance'].append(avg_distance)
    
    # Create DataFrame
    df = pd.DataFrame(zip_data)
    
    # Get GeoJSON data
    geojson_data = zip_validator.get_zip_geojson()
    
    # Create heat map
    fig = px.choropleth(
        df,
        geojson=geojson_data,
        locations='ZIP_Code',
        color='Avg_Distance',
        color_continuous_scale='Brwnyl',  # Brown to yellow color scale
        title='Average Distance to Nearest Bus Stop by ZIP Code',
        labels={'Avg_Distance': 'Average Distance (miles)'}
    )
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'Average Distance to Nearest Bus Stop by ZIP Code',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 24}
        },
        height=450,
        margin=dict(l=0, r=0, t=50, b=0),
        geo=dict(
            scope='usa',
            projection_scale=20,  # Zoom level
            center=dict(lat=25.55, lon=-80.5),  # Center of the map
            showland=True,
            landcolor='rgb(243, 243, 243)',
            showcoastlines=True,
            coastlinecolor='rgb(80, 80, 80)',
            showframe=False
        )
    )
    
    return fig 