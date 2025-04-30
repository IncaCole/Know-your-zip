import streamlit as st
import pandas as pd
from api_list import API_ENDPOINTS as OLD_API_ENDPOINTS, fetch_data_with_retry as old_fetch_data
from api_list_new import API_ENDPOINTS as NEW_API_ENDPOINTS, fetch_data_with_retry as new_fetch_data

def main():
    st.title("API Data Comparison Viewer")
    st.write("This app compares data from both the old and new API endpoints.")

    # Create a sidebar for category selection
    old_categories = list(OLD_API_ENDPOINTS.keys())
    new_categories = list(NEW_API_ENDPOINTS.keys())
    
    st.sidebar.header("Select Data Category")
    category = st.sidebar.selectbox(
        "Category",
        list(set(old_categories + new_categories))
    )

    # Create two columns for side-by-side comparison
    col1, col2 = st.columns(2)

    # Fetch and display data from old API
    with col1:
        st.subheader("Old API Data")
        if category in OLD_API_ENDPOINTS:
            data = old_fetch_data(OLD_API_ENDPOINTS[category])
            if data and 'features' in data:
                features = []
                for feature in data['features']:
                    properties = feature.get('properties', {})
                    features.append(properties)
                
                df_old = pd.DataFrame(features)
                st.dataframe(df_old, use_container_width=True)
                st.write(f"Total records: {len(df_old)}")
                st.write("Column information:")
                st.write(df_old.dtypes)
            else:
                st.error(f"Failed to fetch data from old API for {category}")
        else:
            st.info(f"Category {category} not available in old API")

    # Fetch and display data from new API
    with col2:
        st.subheader("New API Data")
        if category in NEW_API_ENDPOINTS:
            data = new_fetch_data(NEW_API_ENDPOINTS[category])
            if data and 'features' in data:
                features = []
                for feature in data['features']:
                    properties = feature.get('properties', {})
                    features.append(properties)
                
                df_new = pd.DataFrame(features)
                st.dataframe(df_new, use_container_width=True)
                st.write(f"Total records: {len(df_new)}")
                st.write("Column information:")
                st.write(df_new.dtypes)
            else:
                st.error(f"Failed to fetch data from new API for {category}")
        else:
            st.info(f"Category {category} not available in new API")

    # Add comparison metrics
    if category in OLD_API_ENDPOINTS and category in NEW_API_ENDPOINTS:
        st.subheader("Comparison Metrics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Old API Records", len(df_old) if 'df_old' in locals() else 0)
        with col2:
            st.metric("New API Records", len(df_new) if 'df_new' in locals() else 0)
        with col3:
            if 'df_old' in locals() and 'df_new' in locals():
                diff = len(df_new) - len(df_old)
                st.metric("Difference", diff, delta=f"{diff:+d}")

if __name__ == "__main__":
    main() 