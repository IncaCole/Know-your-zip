import streamlit as st
import streamlit.components.v1 as components
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
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f8f9fa;
        border-radius: 8px;
        gap: 1px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e9ecef;
        transform: translateY(-2px);
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #ffffff;
        color: #0d6efd;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* Card styling */
    .card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: transform 0.3s ease;
    }
    
    .card:hover {
        transform: translateY(-5px);
    }
    
    /* Button styling */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        font-weight: 600;
        background-color: #0d6efd;
        color: white;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #0b5ed7;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Input field styling */
    .stTextInput>div>div>input {
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    
    /* Metric styling */
    .stMetric {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    </style>
""", unsafe_allow_html=True)

# Create tabs with icons
tab1, tab2, tab3 = st.tabs(["🏠 Home", "ℹ️ About", "📞 Contact"])

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
                    st.success(f"Searching for ZIP code: {search_input}")
                    
                    # What's Nearby section
                    st.markdown("""
                    <div style='margin-top: 2rem;'>
                        <h2 style='color: #0d6efd;'>📍 What's Nearby</h2>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Create tabs for different categories
                    nearby_tabs = st.tabs(["🏥 Hospitals", "🏫 Schools", "👮 Police Stations", "🌳 Parks", "⚠️ Flood Hazards"])
                    
                    with nearby_tabs[0]:  # Hospitals
                        st.markdown("""
                        <div style='background-color: #f8f9fa; padding: 1.5rem; border-radius: 12px;'>
                            <h3 style='color: #0d6efd;'>Hospitals in ZIP Code {}</h3>
                        </div>
                        """.format(search_input), unsafe_allow_html=True)
                        user_location = get_coordinates(search_input)
                        if user_location:
                            hospitals_df = get_nearby_locations(user_location, 'hospitals')
                            display_nearby_locations(hospitals_df, 'hospitals', search_input)
                        
                    with nearby_tabs[1]:  # Schools
                        st.markdown("""
                        <div style='background-color: #f8f9fa; padding: 1.5rem; border-radius: 12px;'>
                            <h3 style='color: #0d6efd;'>Public Schools in ZIP Code {}</h3>
                        </div>
                        """.format(search_input), unsafe_allow_html=True)
                        if user_location:
                            schools_df = get_nearby_locations(user_location, 'schools')
                            display_nearby_locations(schools_df, 'schools', search_input)
                        
                    with nearby_tabs[2]:  # Police Stations
                        st.markdown("""
                        <div style='background-color: #f8f9fa; padding: 1.5rem; border-radius: 12px;'>
                            <h3 style='color: #0d6efd;'>Police Stations in ZIP Code {}</h3>
                        </div>
                        """.format(search_input), unsafe_allow_html=True)
                        if user_location:
                            police_df = get_nearby_locations(user_location, 'police_stations')
                            display_nearby_locations(police_df, 'police stations', search_input)
                        
                    with nearby_tabs[3]:  # Parks
                        st.markdown("""
                        <div style='background-color: #f8f9fa; padding: 1.5rem; border-radius: 12px;'>
                            <h3 style='color: #0d6efd;'>County Parks in ZIP Code {}</h3>
                        </div>
                        """.format(search_input), unsafe_allow_html=True)
                        if user_location:
                            parks_df = get_nearby_locations(user_location, 'parks')
                            display_nearby_locations(parks_df, 'parks', search_input)
                        
                    with nearby_tabs[4]:  # Flood Hazards
                        st.markdown("""
                        <div style='background-color: #f8f9fa; padding: 1.5rem; border-radius: 12px;'>
                            <h3 style='color: #0d6efd;'>Flood Hazards in ZIP Code {}</h3>
                        </div>
                        """.format(search_input), unsafe_allow_html=True)
                        if user_location:
                            flood_df = get_nearby_locations(user_location, 'flood_hazards')
                            display_nearby_locations(flood_df, 'flood hazards', search_input)
                        
                    # Nearby ZIP codes section
                    st.markdown("""
                    <div style='margin-top: 2rem;'>
                        <h3 style='color: #0d6efd;'>Nearby ZIP Codes</h3>
                        <p style='color: #ff0000;'>OUT OF YOUR ZIPCODE BUT NEARBY:</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    nearby_zips = get_nearby_zip_codes(search_input)
                    if nearby_zips:
                        st.markdown("""
                        <div style='display: flex; flex-wrap: wrap; gap: 0.5rem;'>
                        """, unsafe_allow_html=True)
                        for zip_code in nearby_zips:
                            st.markdown(f"""
                            <div style='background-color: #f8f9fa; padding: 0.5rem 1rem; border-radius: 4px;'>
                                {zip_code}
                            </div>
                            """, unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.info("No nearby ZIP codes found.")
                else:
                    st.error("Please enter a valid 5-digit ZIP code")
            else:
                st.success(f"Searching for address: {search_input}")
                # Similar structure for full address search
                # ... (will add this in next edit)
        elif search_button and not search_input:
            st.warning("Please enter a search term before clicking SEARCH")
            
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

with tab3:
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
            st.success("Thank you for your message! We'll get back to you soon.")
    
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
