import streamlit as st
import pandas as pd
import api_list_new
import re
from src.zip_validator import ZIPValidator

st.set_page_config(page_title="Location Finder", layout="wide")

st.title("📍 Location Finder")
st.write("Enter your address or ZIP code to find nearby locations in Miami-Dade County")

# Initialize ZIP validator
@st.cache_resource
def get_zip_validator():
    return ZIPValidator()

zip_validator = get_zip_validator()

# Single search input
location_input = st.text_input("Enter your address or ZIP code")

# Location categories
categories = ['public_schools', 'police_stations']
selected_category = st.selectbox("Select location type", categories)

# Search radius
radius = st.slider("Search radius (miles)", 1.0, 20.0, 13.38)

if st.button("Find Nearby Locations"):
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
                # Show valid ZIP codes in an expander
                with st.expander("Show valid Miami-Dade County ZIP codes"):
                    valid_zips = sorted(list(zip_validator.get_all_zip_codes()))
                    # Display ZIP codes in a grid
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
            # Get nearby locations
            locations_df = api_list_new.get_nearby_locations(coordinates, selected_category, radius)
            
            if not locations_df.empty:
                # Display the data in a formatted table
                st.subheader(f"Nearby {selected_category.replace('_', ' ').title()}")
                
                try:
                    # Create display dataframe with selected columns
                    display_df = pd.DataFrame()
                    
                    # Common columns for all location types
                    display_df['Name'] = locations_df['NAME']
                    display_df['Address'] = locations_df['ADDRESS']
                    display_df['City'] = locations_df['CITY']
                    display_df['ZIP'] = locations_df['ZIPCODE']
                    display_df['Distance (miles)'] = locations_df['distance_miles'].round(2)
                    
                    # Type-specific columns and formatting
                    if selected_category == 'public_schools':
                        if 'GRADES' in locations_df.columns:
                            display_df['Grades'] = locations_df['GRADES']
                        if 'ENROLLMNT' in locations_df.columns:
                            display_df['Enrollment'] = locations_df['ENROLLMNT']
                        if 'CAPACITY' in locations_df.columns:
                            display_df['Capacity'] = locations_df['CAPACITY']
                    elif selected_category == 'police_stations':
                        # Add any police station specific columns here
                        display_df['Station Type'] = 'Police Station'
                    
                    # Sort by distance
                    display_df = display_df.sort_values('Distance (miles)')
                    
                    # Display the formatted table
                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        hide_index=True
                    )
                    
                    # Show total count and radius
                    st.write(f"Found {len(display_df)} locations within {radius} miles")
                    
                    # Add expandable sections for additional information
                    with st.expander("Show Additional Information"):
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.write("Search Location:")
                            st.write(f"Coordinates: {coordinates}")
                            if zip_match:
                                st.write(f"ZIP Code: {location_input} (Miami-Dade County)")
                                # Show nearby ZIP codes
                                nearby_zips = zip_validator.get_nearby_zips(location_input, radius)
                                if nearby_zips:
                                    st.write(f"Nearby ZIP Codes ({len(nearby_zips)}):")
                                    st.write(", ".join(sorted(nearby_zips)))
                        with col2:
                            st.write("Results Summary:")
                            st.write(f"Closest: {display_df.iloc[0]['Name']} ({display_df.iloc[0]['Distance (miles)']} miles)")
                            st.write(f"Furthest: {display_df.iloc[-1]['Name']} ({display_df.iloc[-1]['Distance (miles)']} miles)")
                        with col3:
                            st.write("Location Type:")
                            if selected_category == 'public_schools':
                                if 'CAPACITY' in locations_df.columns and 'ENROLLMNT' in locations_df.columns:
                                    total_capacity = locations_df['CAPACITY'].sum()
                                    total_enrollment = locations_df['ENROLLMNT'].sum()
                                    st.write(f"Total Capacity: {total_capacity:,}")
                                    st.write(f"Total Enrollment: {total_enrollment:,}")
                                    st.write(f"Utilization: {(total_enrollment/total_capacity*100):.1f}%")
                            elif selected_category == 'police_stations':
                                st.write(f"Total Stations: {len(display_df)}")
                                st.write(f"Average Distance: {display_df['Distance (miles)'].mean():.1f} miles")
                    
                    # Display raw data option
                    if st.checkbox("Show raw data"):
                        st.write("Raw Data Columns:", locations_df.columns.tolist())
                        st.dataframe(locations_df)
                        
                except Exception as e:
                    st.error(f"Error processing data: {str(e)}")
                    st.write("Raw data structure:")
                    st.write(locations_df.dtypes)
                    st.write("Raw data:")
                    st.dataframe(locations_df)
            else:
                st.info(f"No {selected_category.replace('_', ' ')} found within {radius} miles")
        else:
            st.error("Could not find coordinates for the provided location") 