import streamlit as st
import streamlit.components.v1 as components

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
        zip_code = st.text_input("Enter a ZIP code:", max_chars=5, key="zip_search")
        if zip_code:
            st.success(f"Searching for ZIP code: {zip_code}")
            
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