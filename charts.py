"""
# Charts module for Miami-Dade County Explorer
# This file will contain chart generation functions for the dashboard
""" 

import streamlit as st
import plotly.express as px
import pandas as pd
from education import EducationAPI
from src.zip_validator import ZIPValidator

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
        title='Distribution of Schools Across Miami-Dade ZIP Codes',
        labels={'Total_Schools': 'Number of Schools', 'count': 'Number of ZIP Codes'},
        color_discrete_sequence=['#1f77b4']  # Use a nice blue color
    )
    
    # Update layout for better appearance
    fig.update_layout(
        bargap=0.1,
        xaxis_title='Number of Schools per ZIP Code',
        yaxis_title='Number of ZIP Codes',
        showlegend=False
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