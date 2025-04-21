import streamlit as st
import streamlit.components.v1 as components
import folium
from folium import plugins
from api_list import get_coordinates, get_nearby_locations, display_nearby_locations, get_nearby_zip_codes

# Set page configuration
st.set_page_config(
    page_title="Know Your Zip",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for enhanced styling
st.markdown("""
    <style>
    /* Main container styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        background-color: #f8fafc;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #e6f0ff;
        border-radius: 8px;
        gap: 1px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
        color: #1a56db;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #d0e1ff;
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #1a56db;
        color: white;
        box-shadow: 0 2px 4px rgba(26, 86, 219, 0.2);
    }
    
    /* Card styling */
    .card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 4px 6px rgba(26, 86, 219, 0.1);
        transition: transform 0.3s ease;
        border: 1px solid #e6f0ff;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(26, 86, 219, 0.15);
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        font-weight: 600;
        background-color: #1a56db;
        color: white;
        transition: all 0.3s ease;
        border: none;
    }
    
    .stButton>button:hover {
        background-color: #1649c0;
        box-shadow: 0 4px 6px rgba(26, 86, 219, 0.2);
    }
    
    /* Input field styling */
    .stTextInput>div>div>input {
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: 1px solid #e6f0ff;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #1a56db;
        box-shadow: 0 0 0 2px rgba(26, 86, 219, 0.1);
    }
    
    /* Metric styling */
    .stMetric {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(26, 86, 219, 0.1);
        border: 1px solid #e6f0ff;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5ff;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #1a56db;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #1649c0;
    }

    /* Loading spinner */
    .loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem;
    }

    .globe-spinner {
        width: 50px;
        height: 50px;
        border: 3px solid #e6f0ff;
        border-top: 3px solid #1a56db;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .loading-text {
        margin-top: 1rem;
        color: #1a56db;
        font-weight: 600;
    }

    /* Expander styling */
    .streamlit-expanderHeader {
        background-color: #e6f0ff;
        border-radius: 8px;
        padding: 1rem;
        color: #1a56db;
        font-weight: 600;
    }

    .streamlit-expanderContent {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 1rem;
        border: 1px solid #e6f0ff;
    }

    /* Mobile Responsive Design */
    @media screen and (max-width: 768px) {
        /* Main container adjustments */
        .main .block-container {
            padding: 1rem;
        }
        
        /* Tab adjustments */
        .stTabs [data-baseweb="tab-list"] {
            gap: 0.5rem;
            margin-bottom: 1rem;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 40px;
            padding: 5px 10px;
            font-size: 0.9rem;
        }
        
        /* Card adjustments */
        .card {
            padding: 1rem;
        }
        
        /* Metric adjustments */
        .stMetric {
            padding: 1rem;
        }
        
        /* Button adjustments */
        .stButton>button {
            height: 2.5em;
            font-size: 0.9rem;
        }
        
        /* Input field adjustments */
        .stTextInput>div>div>input {
            padding: 0.4rem 0.8rem;
            font-size: 0.9rem;
        }
        
        /* Loading spinner adjustments */
        .loading-container {
            padding: 1rem;
        }
        
        .globe-spinner {
            width: 40px;
            height: 40px;
        }
    }
    
    /* Small mobile devices */
    @media screen and (max-width: 480px) {
        .stTabs [data-baseweb="tab"] {
            height: 35px;
            padding: 3px 8px;
            font-size: 0.8rem;
        }
        
        .card {
            padding: 0.8rem;
        }
        
        .stMetric {
            padding: 0.8rem;
        }
    }
    </style>
""", unsafe_allow_html=True)

def show_loading_spinner():
    """Display a loading spinner with a globe animation"""
    st.markdown("""
    <div class="loading-container">
        <div class="globe-spinner"></div>
        <div class="loading-text">Loading...</div>
    </div>
    """, unsafe_allow_html=True)

def create_stats_dashboard(hospitals_df, schools_df, police_df, parks_df, zip_code):
    """Create a visually appealing statistics dashboard"""
    # Create a container for the dashboard
    st.markdown("""
    <div style='background-color: #ffffff; padding: 2rem; border-radius: 16px; box-shadow: 0 4px 6px rgba(26, 86, 219, 0.1); margin-bottom: 2rem; border: 1px solid #e6f0ff;'>
        <h2 style='color: #1a56db; text-align: center; margin-bottom: 2rem;'>📍 Area Statistics for ZIP Code {}</h2>
    """.format(zip_code), unsafe_allow_html=True)
    
    # Create 4 columns for the metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🏥 Hospitals",
            value=len(hospitals_df) if not hospitals_df.empty else 0,
            help="Number of hospitals within 5 miles"
        )
    
    with col2:
        st.metric(
            label="🏫 Schools",
            value=len(schools_df) if not schools_df.empty else 0,
            help="Number of public schools within 5 miles"
        )
    
    with col3:
        st.metric(
            label="👮 Police Stations",
            value=len(police_df) if not police_df.empty else 0,
            help="Number of police stations within 5 miles"
        )
    
    with col4:
        st.metric(
            label="🌳 Parks",
            value=len(parks_df) if not parks_df.empty else 0,
            help="Number of parks within 5 miles"
        )
    
    # Add expandable sections for detailed information
    st.markdown("""
    <div style='margin-top: 2rem;'>
        <h3 style='color: #1a56db;'>Detailed Information</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Hospitals section
    with st.expander("🏥 Hospitals Details", expanded=False):
        if not hospitals_df.empty:
            for _, row in hospitals_df.iterrows():
                st.markdown(f"""
                <div style='background-color: #f8fafc; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border: 1px solid #e6f0ff;'>
                    <h4 style='color: #1a56db; margin-bottom: 0.5rem;'>{row.get('name', 'Unknown Hospital')}</h4>
                    <p style='margin-bottom: 0.5rem; color: #1e40af;'><strong>Address:</strong> {row.get('address', 'N/A')}</p>
                    {f"<p style='margin-bottom: 0.5rem; color: #1e40af;'><strong>Phone:</strong> {row.get('phone', 'N/A')}</p>" if 'phone' in row else ''}
                    <p style='margin-bottom: 0.5rem; color: #1e40af;'><strong>Distance:</strong> {row['distance_miles']:.1f} miles</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No hospitals found in the area.")
    
    # Schools section
    with st.expander("🏫 Schools Details", expanded=False):
        if not schools_df.empty:
            for _, row in schools_df.iterrows():
                st.markdown(f"""
                <div style='background-color: #f8fafc; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border: 1px solid #e6f0ff;'>
                    <h4 style='color: #1a56db; margin-bottom: 0.5rem;'>{row.get('name', 'Unknown School')}</h4>
                    <p style='margin-bottom: 0.5rem; color: #1e40af;'><strong>Address:</strong> {row.get('address', 'N/A')}</p>
                    {f"<p style='margin-bottom: 0.5rem; color: #1e40af;'><strong>Phone:</strong> {row.get('phone', 'N/A')}</p>" if 'phone' in row else ''}
                    <p style='margin-bottom: 0.5rem; color: #1e40af;'><strong>Distance:</strong> {row['distance_miles']:.1f} miles</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No schools found in the area.")
    
    # Police Stations section
    with st.expander("👮 Police Stations Details", expanded=False):
        if not police_df.empty:
            for _, row in police_df.iterrows():
                st.markdown(f"""
                <div style='background-color: #f8fafc; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border: 1px solid #e6f0ff;'>
                    <h4 style='color: #1a56db; margin-bottom: 0.5rem;'>{row.get('name', 'Unknown Police Station')}</h4>
                    <p style='margin-bottom: 0.5rem; color: #1e40af;'><strong>Address:</strong> {row.get('address', 'N/A')}</p>
                    {f"<p style='margin-bottom: 0.5rem; color: #1e40af;'><strong>Phone:</strong> {row.get('phone', 'N/A')}</p>" if 'phone' in row else ''}
                    <p style='margin-bottom: 0.5rem; color: #1e40af;'><strong>Distance:</strong> {row['distance_miles']:.1f} miles</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No police stations found in the area.")
    
    # Parks section
    with st.expander("🌳 Parks Details", expanded=False):
        if not parks_df.empty:
            for _, row in parks_df.iterrows():
                st.markdown(f"""
                <div style='background-color: #f8fafc; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; border: 1px solid #e6f0ff;'>
                    <h4 style='color: #1a56db; margin-bottom: 0.5rem;'>{row.get('name', 'Unknown Park')}</h4>
                    <p style='margin-bottom: 0.5rem; color: #1e40af;'><strong>Address:</strong> {row.get('address', 'N/A')}</p>
                    <p style='margin-bottom: 0.5rem; color: #1e40af;'><strong>Distance:</strong> {row['distance_miles']:.1f} miles</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No parks found in the area.")
    
    # Close the dashboard container
    st.markdown("</div>", unsafe_allow_html=True)

def create_interactive_map(user_location, search_input, hospitals_df, schools_df, police_df, parks_df, is_zip_code):
    """Create an interactive map with markers for the location and nearby points of interest"""
    # Create a map centered at the user's location
    m = folium.Map(
        location=[user_location['lat'], user_location['lng']],
        zoom_start=12,
        tiles='OpenStreetMap'
    )
    
    # Add the main location marker
    if is_zip_code:
        # For ZIP codes, create a shaded area
        folium.Circle(
            location=[user_location['lat'], user_location['lng']],
            radius=5000,  # 5km radius
            color='#1a56db',
            fill=True,
            fill_color='#1a56db',
            fill_opacity=0.2,
            popup=f'ZIP Code: {search_input}'
        ).add_to(m)
    else:
        # For exact addresses, add a red marker
        folium.Marker(
            location=[user_location['lat'], user_location['lng']],
            popup=f'Address: {search_input}',
            icon=folium.Icon(color='red', icon='info-sign')
        ).add_to(m)
    
    # Add markers for hospitals
    if not hospitals_df.empty:
        for _, row in hospitals_df.iterrows():
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=f"Hospital: {row['name']}",
                icon=folium.Icon(color='blue', icon='plus-sign', prefix='fa')
            ).add_to(m)
    
    # Add markers for schools
    if not schools_df.empty:
        for _, row in schools_df.iterrows():
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=f"School: {row['name']}",
                icon=folium.Icon(color='green', icon='book', prefix='fa')
            ).add_to(m)
    
    # Add markers for police stations
    if not police_df.empty:
        for _, row in police_df.iterrows():
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=f"Police Station: {row['name']}",
                icon=folium.Icon(color='black', icon='shield', prefix='fa')
            ).add_to(m)
    
    # Add markers for parks
    if not parks_df.empty:
        for _, row in parks_df.iterrows():
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=f"Park: {row['name']}",
                icon=folium.Icon(color='lightgreen', icon='tree-conifer', prefix='fa')
            ).add_to(m)
    
    # Add a layer control to toggle different markers
    folium.LayerControl().add_to(m)
    
    # Convert the map to HTML
    map_html = m._repr_html_()
    
    # Display the map in Streamlit
    components.html(map_html, height=600)

def show_toast(message, type="success"):
    """Display a toast notification with custom styling"""
    if type == "success":
        st.toast(message, icon="✅")
    elif type == "error":
        st.toast(message, icon="❌")
    elif type == "info":
        st.toast(message, icon="ℹ️")
    elif type == "warning":
        st.toast(message, icon="⚠️")

def test_mobile_responsive_layout():
    """Test the mobile responsive layout with different screen sizes"""
    st.markdown("""
    <div class="card">
        <h2 style='color: #1a56db; text-align: center;'>📱 Mobile Responsive Layout Test</h2>
        <p style='text-align: center; color: #6c757d;'>Test how the layout adapts to different screen sizes</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Test different layout components
    st.markdown("### 1. Column Layout Test")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Test Metric 1", "123", "+10%")
    with col2:
        st.metric("Test Metric 2", "456", "-5%")
    with col3:
        st.metric("Test Metric 3", "789", "0%")
    
    st.markdown("### 2. Input Fields Test")
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Test Input 1", placeholder="Type something...")
    with col2:
        st.text_input("Test Input 2", placeholder="Type something...")
    
    st.markdown("### 3. Button Test")
    st.button("Test Button", use_container_width=True)
    
    st.markdown("### 4. Card Layout Test")
    st.markdown("""
    <div class="card">
        <h3>Test Card</h3>
        <p>This is a test card to check responsive behavior.</p>
        <p>On mobile devices, the padding and margins should adjust automatically.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 5. Loading Spinner Test")
    show_loading_spinner()
    
    st.markdown("### 6. Tab Navigation Test")
    tab1, tab2, tab3 = st.tabs(["Tab 1", "Tab 2", "Tab 3"])
    with tab1:
        st.write("Content for Tab 1")
    with tab2:
        st.write("Content for Tab 2")
    with tab3:
        st.write("Content for Tab 3")

# Create tabs with icons
tab1, tab2, tab3, tab4 = st.tabs(["🏠 Home", "🗺️ Map", "ℹ️ About", "📞 Contact"])

with tab1:
    # Hero section
    st.markdown("""
    <div style='text-align: center; margin-bottom: 3rem;'>
        <h1 style='color: #0d6efd; font-size: 3rem; margin-bottom: 1rem;'>Welcome to Know Your Zip! 🗺️</h1>
        <p style='font-size: 1.2rem; color: #6c757d;'>
            Your one-stop destination for ZIP code information and insights
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Add mobile responsive test section
    test_mobile_responsive_layout()
    
    # Main content in a card
    st.markdown('<div class="card">', unsafe_allow_html=True)
    
    # Create two columns for the search section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🔍 Quick Search")
        search_type = st.radio(
            "Search by:",
            ["ZIP Code", "Full Address"],
            horizontal=True,
            key="search_type"
        )
        
        if search_type == "ZIP Code":
            search_input = st.text_input(
                "Enter a ZIP code:",
                max_chars=5,
                key="zip_search",
                placeholder="e.g., 90210"
            )
        else:
            search_input = st.text_input(
                "Enter a full address:",
                key="address_search",
                placeholder="e.g., 123 Main St, City, State"
            )
            
        # Add search button
        search_button = st.button("SEARCH", type="primary", use_container_width=True)
        
        if search_button and search_input:
            if search_type == "ZIP Code":
                if search_input.isdigit() and len(search_input) == 5:
                    show_toast(f"Searching for ZIP code: {search_input}", "info")
                    
                    # Show loading spinner while fetching data
                    with st.spinner("Loading data..."):
                        show_loading_spinner()
                        user_location = get_coordinates(search_input)
                    
                    if user_location:
                        show_toast("Location found successfully!", "success")
                        # Fetch all data first
                        with st.spinner("Loading statistics..."):
                            hospitals_df = get_nearby_locations(user_location, 'hospitals')
                            schools_df = get_nearby_locations(user_location, 'schools')
                            police_df = get_nearby_locations(user_location, 'police_stations')
                            parks_df = get_nearby_locations(user_location, 'parks')
                        
                        # Store the data in session state for the Map tab
                        st.session_state.user_location = user_location
                        st.session_state.search_input = search_input
                        st.session_state.hospitals_df = hospitals_df
                        st.session_state.schools_df = schools_df
                        st.session_state.police_df = police_df
                        st.session_state.parks_df = parks_df
                        st.session_state.is_zip_code = True
                        
                        # Display the statistics dashboard
                        create_stats_dashboard(hospitals_df, schools_df, police_df, parks_df, search_input)
                        
                        # Switch to the Map tab
                        st.experimental_set_query_params(tab="Map")
                    else:
                        show_toast("Could not find location. Please try again.", "error")
                else:
                    show_toast("Please enter a valid 5-digit ZIP code", "error")
            else:
                show_toast(f"Searching for address: {search_input}", "info")
                # Similar structure for full address search
                # ... (will add this in next edit)
        elif search_button and not search_input:
            show_toast("Please enter a search term before clicking SEARCH", "warning")
            
    with col2:
        st.subheader("📊 Quick Stats")
        col_metric1, col_metric2 = st.columns(2)
        with col_metric1:
            st.metric(label="Total ZIP Codes", value="41,692", delta="+2.3%")
        with col_metric2:
            st.metric(label="States Covered", value="50", delta="+1")
    
    # Map section
    st.subheader("📍 Interactive Map")
    st.markdown("""
    <div style='background-color: #f8f9fa; padding: 2rem; border-radius: 12px; text-align: center;'>
        <p style='color: #6c757d;'>Interactive map will be displayed here</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    # Map tab content
    st.markdown("""
    <div style='text-align: center; margin-bottom: 2rem;'>
        <h1 style='color: #0d6efd;'>Interactive Map 🗺️</h1>
        <p style='color: #6c757d;'>Explore the location and nearby points of interest</p>
    </div>
    """, unsafe_allow_html=True)
    
    if 'user_location' in st.session_state:
        create_interactive_map(
            st.session_state.user_location,
            st.session_state.search_input,
            st.session_state.hospitals_df,
            st.session_state.schools_df,
            st.session_state.police_df,
            st.session_state.parks_df,
            st.session_state.is_zip_code
        )
    else:
        st.info("Please search for a location in the Home tab to view the map.")

with tab3:
    # About page content
    st.markdown("""
    <div class="card">
        <h1 style='color: #0d6efd; margin-bottom: 2rem;'>About Know Your Zip</h1>
        
        <div style='background-color: #f8f9fa; padding: 2rem; border-radius: 12px; margin-bottom: 2rem;'>
            <h3 style='color: #0d6efd;'>Our Mission</h3>
            <p style='color: #495057;'>To provide comprehensive and accurate ZIP code information to help users make informed decisions.</p>
        </div>
        
        <h3 style='color: #0d6efd; margin-bottom: 1rem;'>Key Features</h3>
        <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;'>
            <div style='background-color: #f8f9fa; padding: 1.5rem; border-radius: 8px;'>
                <h4 style='color: #0d6efd;'>📊 Detailed Analytics</h4>
                <p style='color: #495057;'>Comprehensive ZIP code statistics and trends</p>
            </div>
            <div style='background-color: #f8f9fa; padding: 1.5rem; border-radius: 8px;'>
                <h4 style='color: #0d6efd;'>🗺️ Interactive Maps</h4>
                <p style='color: #495057;'>Visual representation of ZIP code data</p>
            </div>
            <div style='background-color: #f8f9fa; padding: 1.5rem; border-radius: 8px;'>
                <h4 style='color: #0d6efd;'>📈 Historical Data</h4>
                <p style='color: #495057;'>Track changes and trends over time</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with tab4:
    # Contact page content
    st.markdown("""
    <div class="card">
        <h1 style='color: #0d6efd; margin-bottom: 2rem;'>Contact Us</h1>
        
        <div style='background-color: #f8f9fa; padding: 2rem; border-radius: 12px; margin-bottom: 2rem;'>
            <h3 style='color: #0d6efd;'>Get in Touch</h3>
            <p style='color: #495057;'>We'd love to hear from you! Fill out the form below to reach out to our team.</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Contact form
    with st.form("contact_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Name", placeholder="Your name")
        with col2:
            email = st.text_input("Email", placeholder="your.email@example.com")
        message = st.text_area("Message", placeholder="Your message here...", height=150)
        submitted = st.form_submit_button("Send Message")
        if submitted:
            if name and email and message:
                show_toast("Thank you for your message! We'll get back to you soon.", "success")
            else:
                show_toast("Please fill in all fields", "warning")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Footer
st.markdown("""
<div style='text-align: center; margin-top: 3rem; padding: 2rem; background-color: #f8f9fa; border-radius: 12px;'>
    <p style='color: #6c757d; margin-bottom: 0.5rem;'>© 2024 Know Your Zip. All rights reserved.</p>
    <div style='display: flex; justify-content: center; gap: 1rem;'>
        <a href='#' style='color: #0d6efd; text-decoration: none;'>Privacy Policy</a>
        <span style='color: #6c757d;'>|</span>
        <a href='#' style='color: #0d6efd; text-decoration: none;'>Terms of Service</a>
        <span style='color: #6c757d;'>|</span>
        <a href='#' style='color: #0d6efd; text-decoration: none;'>Contact Support</a>
    </div>
</div>
""", unsafe_allow_html=True) 
