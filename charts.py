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
    Creates and returns a histogram showing the distribution of schools across ZIP codes,
    styled to look like realistic stacks of books
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
        category_orders={'Total_Schools': sorted(df['Total_Schools'].unique())},
        text_auto=True
    )
    
    # Update traces to look like stacks of books
    fig.update_traces(
        marker=dict(
            color='#D4B08C',  # Base book color (light brown)
            pattern=dict(
                shape="-",  # Horizontal lines to represent individual books
                fillmode="overlay",
                size=4,  # Size of the pattern (representing book thickness)
                solidity=0.9,
                fgcolor="rgba(139, 69, 19, 0.5)"  # Darker brown for book edges
            )
        ),
        textposition='inside',
        textfont=dict(size=14, color='#2F1810'),  # Dark brown text
        insidetextanchor='middle'
    )
    
    # Update layout for better appearance
    fig.update_layout(
        bargap=0.2,  # Increased gap between bars
        xaxis_title='Number of Schools per ZIP',
        yaxis_title='Number of ZIPs',
        showlegend=False,
        yaxis_range=[0, 40],
        title={
            'text': 'School Distribution',
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': {'size': 24}
        },
        plot_bgcolor='rgba(253, 245, 230, 0.5)',  # Old lace color for background
        paper_bgcolor='white'
    )
    
    # Add multiple border effects to create book edges
    fig.update_traces(
        marker_line_color='#8B4513',  # Saddle brown for edges
        marker_line_width=2,  # Thicker border for more defined books
        # Add a second pattern layer for more texture
        marker=dict(
            color='#D4B08C',  # Base color
            pattern=dict(
                shape="-",  # Horizontal lines
                fillmode="overlay",
                size=4,
                solidity=0.9,
                fgcolor="rgba(139, 69, 19, 0.5)"  # Darker brown
            ),
            line=dict(  # Add subtle vertical lines for book spines
                color="rgba(139, 69, 19, 0.3)",
                width=1
            )
        )
    )
    
    # Add subtle shadow effect
    fig.update_layout(
        shapes=[
            dict(
                type="rect",
                xref="paper",
                yref="paper",
                x0=0,
                y0=0,
                x1=1,
                y1=0.1,
                fillcolor="rgba(0,0,0,0.1)",
                layer="below",
                line_width=0,
            )
        ]
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