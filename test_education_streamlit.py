import streamlit as st
from education import EducationAPI
import pandas as pd

st.set_page_config(page_title="Education API Tester", layout="wide")

st.title("📚 Education API Test Interface")
st.write("Test various education API endpoints and see their responses")

# Initialize API
api = EducationAPI()

# Create tabs for different API tests
tab1, tab2, tab3, tab4 = st.tabs([
    "Schools by ZIP", 
    "School Search", 
    "Bus Stops",
    "School Ratings"
])

with tab1:
    st.header("Find Schools by ZIP Code")
    col1, col2 = st.columns(2)
    
    with col1:
        zip_code = st.text_input("Enter ZIP Code", value="33101")
        school_type = st.selectbox(
            "School Type",
            options=["all", "public", "private"],
            index=0
        )
        
        if st.button("Find Schools"):
            with st.spinner("Fetching schools..."):
                result = api.get_schools_by_zip(zip_code, school_type)
                
                if result['success']:
                    schools = result['data']['schools']
                    st.success(f"Found {len(schools)} schools")
                    
                    # Convert to DataFrame for better display
                    if schools:
                        df = pd.DataFrame(schools)
                        st.dataframe(
                            df,
                            column_config={
                                "NAME": "School Name",
                                "ADDRESS": "Address",
                                "ZIPCODE": "ZIP Code",
                                "school_type": "Type"
                            }
                        )
                    else:
                        st.info("No schools found in this ZIP code")
                else:
                    st.error(f"Error: {result['message']}")

with tab2:
    st.header("Search Schools by Name")
    col1, col2 = st.columns(2)
    
    with col1:
        school_name = st.text_input("Enter School Name")
        search_type = st.selectbox(
            "Search In",
            options=["all", "public", "private"],
            index=0,
            key="search_type"
        )
        
        if st.button("Search Schools"):
            with st.spinner("Searching schools..."):
                result = api.get_school_by_name(school_name, search_type)
                
                if result['success']:
                    schools = result['data']['schools']
                    st.success(f"Found {len(schools)} matching schools")
                    
                    if schools:
                        df = pd.DataFrame(schools)
                        st.dataframe(
                            df,
                            column_config={
                                "NAME": "School Name",
                                "ADDRESS": "Address",
                                "ZIPCODE": "ZIP Code",
                                "school_type": "Type"
                            }
                        )
                    else:
                        st.info("No schools found matching your search")
                else:
                    st.error(f"Error: {result['message']}")

with tab3:
    st.header("Bus Stops Information")
    search_by = st.radio("Search By", ["ZIP Code", "Route ID"])
    
    if search_by == "ZIP Code":
        zip_code = st.text_input("Enter ZIP Code", key="bus_zip")
        if st.button("Find Bus Stops"):
            with st.spinner("Fetching bus stops..."):
                result = api.get_bus_stops_by_zip(zip_code)
                
                if result['success']:
                    stops = result['data']['bus_stops']
                    st.success(f"Found {len(stops)} bus stops")
                    
                    if stops:
                        df = pd.DataFrame(stops)
                        st.dataframe(df)
                    else:
                        st.info("No bus stops found in this ZIP code")
                else:
                    st.error(f"Error: {result['message']}")
    else:
        route_id = st.text_input("Enter Route ID")
        if st.button("Find Route Stops"):
            with st.spinner("Fetching route stops..."):
                result = api.get_bus_stops_by_route(route_id)
                
                if result['success']:
                    stops = result['data']['bus_stops']
                    st.success(f"Found {len(stops)} stops on route {route_id}")
                    
                    if stops:
                        df = pd.DataFrame(stops)
                        st.dataframe(df)
                    else:
                        st.info(f"No stops found for route {route_id}")
                else:
                    st.error(f"Error: {result['message']}")

with tab4:
    st.header("School Ratings")
    school_id = st.text_input("Enter School ID")
    
    if st.button("Get Ratings"):
        with st.spinner("Fetching school ratings..."):
            result = api.get_school_ratings(school_id)
            
            if result['success']:
                ratings = result['data']['ratings']
                st.success("Successfully retrieved ratings")
                
                # Display ratings in a more readable format
                col1, col2 = st.columns(2)
                with col1:
                    for key, value in ratings.items():
                        st.metric(label=key, value=value)
            else:
                st.error(f"Error: {result['message']}")

# Add expander for API response inspection
with st.expander("🔍 API Response Inspector"):
    st.write("This section shows the raw API response for debugging")
    if 'result' in locals():
        st.json(result)
    else:
        st.info("Make an API call to see the response") 