"""
# Charts module for Miami-Dade County Explorer
# This file will contain chart generation functions for the dashboard
""" 

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from education import EducationAPI
from src.zip_validator import ZIPValidator
from emergency_services import EmergencyServicesAPI
from geopy.distance import geodesic

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

def plot_county_regions():
    """
    Creates and returns a figure showing Miami-Dade County shape with region labels and park statistics
    """
    # Approximate coordinates for Miami-Dade County corners
    county_shape = [
        [25.97, -80.14],  # North point
        [25.97, -80.87],  # Northwest point
        [25.13, -80.87],  # Southwest point
        [25.13, -80.14],  # Southeast point
        [25.97, -80.14]   # Close the shape
    ]
    
    # Create the base figure
    fig = go.Figure()
    
    # Add the county outline
    fig.add_trace(go.Scattergeo(
        lon=[point[1] for point in county_shape],
        lat=[point[0] for point in county_shape],
        mode='lines',
        line=dict(width=2, color='#2F4538'),  # Dark muted green for outline
        fill='toself',
        fillcolor='rgba(144, 169, 144, 0.3)',  # Muted sage green with transparency
        name='Miami-Dade County'
    ))
    
    # Add region labels with park statistics
    region_labels = [
        dict(text="NE<br>118 parks (18%)", lat=25.85, lon=-80.20),  # Northeast
        dict(text="SE<br>77 parks (12%)", lat=25.25, lon=-80.20),   # Southeast
        dict(text="SW<br>452 parks (70%)", lat=25.25, lon=-80.75)   # Southwest
    ]
    
    for label in region_labels:
        fig.add_trace(go.Scattergeo(
            lon=[label['lon']],
            lat=[label['lat']],
            text=[label['text']],
            mode='text',
            textfont=dict(size=16, color='#2F4538', family='Arial Black'),  # Matching dark muted green for text
            name=label['text']
        ))
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'Miami-Dade County Regions - Park Distribution',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 24}
        },
        showlegend=False,
        geo=dict(
            scope='usa',
            projection_scale=20,  # Zoom level
            center=dict(lat=25.55, lon=-80.5),  # Center of the map
            showland=True,
            landcolor='rgb(243, 243, 243)',
            showcoastlines=True,
            coastlinecolor='rgb(80, 80, 80)',
            showframe=False
        ),
        height=600,
        margin=dict(l=0, r=0, t=50, b=0)
    )
    
    return fig 