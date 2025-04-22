import streamlit as st
import pandas as pd
from api_list import API_ENDPOINTS, fetch_data_with_retry

def main():
    st.title("API Data Test Viewer")
    st.write("This app displays data from various Miami-Dade County APIs in a table format.")

    # Create a sidebar for category selection
    category = st.sidebar.selectbox(
        "Select Data Category",
        list(API_ENDPOINTS.keys())
    )

    # Fetch data for the selected category
    data = fetch_data_with_retry(API_ENDPOINTS[category])
    
    if data and 'features' in data:
        # Convert features to a DataFrame
        features = []
        for feature in data['features']:
            properties = feature.get('properties', {})
            features.append(properties)
        
        df = pd.DataFrame(features)
        
        # Display the data
        st.subheader(f"{category.title()} Data")
        st.dataframe(df, use_container_width=True)
        
        # Show some basic statistics
        st.subheader("Data Statistics")
        st.write(f"Total records: {len(df)}")
        st.write("Column information:")
        st.write(df.dtypes)
        
    else:
        st.error(f"Failed to fetch data for {category}")

if __name__ == "__main__":
    main() 