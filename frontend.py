import streamlit as st
import requests

# Configuration
API_URL = "http://127.0.0.1:8003"

# Page config for wide layout and dark theme
st.set_page_config(
    page_title="MPRI Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark theme (eye-catching: cyan accents, rounded buttons, clean typography)
st.markdown("""
<style>
    /* Dark background */
    .stApp {
        background-color: #0f1419;
        color: #e5e7eb;
    }
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0e1117;
    }
    /* Metrics: Cyan for value, white for label */
    .stMetric > label {
        color: #ffffff !important;
        font-size: 14px;
    }
    .stMetric > .stMetricValue {
        color: #00d4ff !important;
        font-size: 24px;
    }
    /* Inputs: White labels, dark backgrounds */
    .stTextArea > label, .stFileUploader > label {
        color: #ffffff !important;
    }
    .stTextArea textarea, .stFileUploader {
        background-color: #1f2937 !important;
        color: #e5e7eb !important;
        border-radius: 8px;
    }
    /* Buttons: Dark with cyan hover */
    .stButton > button {
        background-color: #1f2937 !important;
        color: #ffffff !important;
        border-radius: 12px;
        border: none;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #00d4ff !important;
        color: #0f1419 !important;
        transform: scale(1.02);
    }
    /* Headers: Cyan for main, white for sub */
    h1 {
        color: #00d4ff !important;
        font-size: 2.5em;
        text-align: center;
        margin-bottom: 0.5em;
    }
    h2 {
        color: #ffffff !important;
        font-size: 1.8em;
        border-bottom: 2px solid #00d4ff;
        padding-bottom: 0.5em;
    }
    /* Expanders and containers */
    .stExpander {
        background-color: #1f2937;
        border-radius: 10px;
        border: 1px solid #374151;
    }
    /* Footer */
    .main-footer {
        background-color: #0e1117;
        color: #9ca3af;
        text-align: center;
        padding: 1em;
        font-size: 12px;
    }
    /* Success messages */
    .stSuccess {
        background-color: #1f2937;
        border-radius: 8px;
        border-left: 4px solid #00d4ff;
    }
    /* Candidate card styling */
    .candidate-card {
        background-color: #1f2937;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #374151;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions
def get_score_emoji(score):
    if score >= 80:
        return "🌟"
    elif score >= 70:
        return "✅" 
    elif score >= 60:
        return "⚠️"
    else:
        return "❌"

# Sidebar Navigation (clean and aligned)
st.sidebar.title("🚀 MPRI Controls")
st.sidebar.markdown("---")
selected_page = st.sidebar.selectbox(
    "Navigate:",
    ["📄 Analyze Resume", "👥 Shortlisted Candidates", "📋 All Candidates"],
    index=0
)
st.sidebar.markdown("---")
st.sidebar.info("**Dark Mode Active** | Eye-catching & Simple")
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 MPRI Weights")
st.sidebar.markdown("""
- **Surface Fit**: 55%
- **Depth Fit**: 30%  
- **Growth Potential**: 10%
- **Cultural Fit**: 5%
""")

# Main content based on selection
if selected_page == "📄 Analyze Resume":
    # Header with icon
    st.markdown("<h1>📄 Resume Analyzer</h1>", unsafe_allow_html=True)
    
    # Two-column layout for upload and input (perfect alignment)
    col1, col2 = st.columns([1, 3], gap="medium")
    
    with col1:
        st.subheader("Upload PDF")
        uploaded_file = st.file_uploader(
            "Choose a resume file",
            type="pdf",
            help="Upload your PDF resume here."
        )
    
    with col2:
        st.subheader("Job Description")
        job_desc = st.text_area(
            "Enter details",
            height=200,
            placeholder="e.g., Seeking Python developer with SQL skills, teamwork values...",
            help="Describe the role requirements."
        )
    
    # Analyze button (centered, full-width)
    if st.button("🔍 Run MPRI Analysis", use_container_width=True):
        if uploaded_file and job_desc:
            with st.spinner("🔄 Processing with AI..."):
                try:
                    # Real API integration
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                    data = {"job_desc": job_desc}
                    response = requests.post(f"{API_URL}/upload", files=files, data=data)
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.success("✅ Analysis Complete!")
                        
                        # Metrics row (3 columns, eye-catching cyan values)
                        col_a, col_b, col_c = st.columns(3, gap="large")
                        with col_a:
                            st.metric("Surface Fit", f"{result['surface_fit']}%", f"{get_score_emoji(result['surface_fit'])}")
                        with col_b:
                            st.metric("Depth Fit", f"{result['depth_fit']}%", f"{get_score_emoji(result['depth_fit'])}")
                        with col_c:
                            st.metric("Final Score", f"{result['final_score']}/100", f"🎯 {result['status']}")
                        
                        # Additional metrics row
                        col_d, col_e = st.columns(2, gap="large")
                        with col_d:
                            st.metric("Growth Potential", f"{result['growth_potential']}%", f"{get_score_emoji(result['growth_potential'])}")
                        with col_e:
                            st.metric("Cultural Fit", f"{result['cultural_fit']}%", f"{get_score_emoji(result['cultural_fit'])}")
                        
                        # Radar chart section (centered image)
                        if 'radar_chart' in result:
                            st.markdown("<h2>📊 MPRI Radar Chart</h2>", unsafe_allow_html=True)
                            with st.container():
                                st.image(f"{API_URL}{result['radar_chart']}", 
                                        caption="Visual breakdown of scores",
                                        use_container_width=True)
                        
                        # Justification expander (clean, collapsible)
                        with st.expander("📝 Detailed Justification", expanded=True):
                            st.markdown(f"**Weights:** {result['weights']}")
                            st.markdown("---")
                            for line in result['justification']:
                                if line.strip():
                                    st.markdown(f"- {line}")
                    
                    else:
                        st.error(f"❌ Analysis failed: {response.status_code}")
                        
                except Exception as e:
                    st.error(f"❌ Connection error: {str(e)}")
        else:
            st.warning("⚠️ Please upload a PDF and enter a job description.")

elif selected_page == "👥 Shortlisted Candidates":
    # Header
    st.markdown("<h1>👥 Candidate Shortlist</h1>", unsafe_allow_html=True)
    
    # Input for job desc
    shortlist_desc = st.text_area(
        "Filter by Job Description",
        height=150,
        placeholder="Enter JD to fetch shortlist..."
    )
    
    # Fetch button
    if st.button("📋 Generate Shortlist", use_container_width=True):
        if shortlist_desc:
            with st.spinner("🔄 Fetching candidates..."):
                try:
                    response = requests.get(f"{API_URL}/shortlisted", params={"job_desc": shortlist_desc})
                    
                    if response.status_code == 200:
                        candidates = response.json()
                        st.success("✅ Shortlist Generated!")
                        
                        if candidates:
                            for candidate in candidates:
                                # Candidate card (using columns for alignment)
                                st.markdown(f"""
                                <div class="candidate-card">
                                    <h2>{candidate['name']}</h2>
                                </div>
                                """, unsafe_allow_html=True)
                                
                                col_left, col_right = st.columns([3, 1])
                                with col_left:
                                    st.metric("Overall Score", f"{candidate['final_score']}%")
                                    st.metric("Status", candidate['status'])
                                    
                                with col_right:
                                    st.markdown("### Quick View")
                                    if candidate['status'] == "Shortlist":
                                        st.success("✅ Proceed")
                                    else:
                                        st.warning("⚠️ Review")
                                
                                # Radar chart per candidate
                                if 'radar_chart' in candidate:
                                    st.markdown("### 📊 Radar Chart")
                                    with st.container():
                                        st.image(f"{API_URL}{candidate['radar_chart']}", 
                                                caption=f"MPRI scores for {candidate['name']}",
                                                use_container_width=True)
                                
                                # Justification
                                with st.expander(f"📝 Why {candidate['name']}?", expanded=False):
                                    for line in candidate.get('justification', []):
                                        if line.strip():
                                            st.write(f"- {line}")
                                
                                st.markdown("---")  # Divider for clean separation
                        else:
                            st.info("ℹ️ No shortlisted candidates found.")
                    
                    else:
                        st.error(f"❌ Failed to fetch shortlist: {response.status_code}")
                        
                except Exception as e:
                    st.error(f"❌ Connection error: {str(e)}")
        else:
            st.info("ℹ️ Enter a job description to generate the shortlist.")

elif selected_page == "📋 All Candidates":
    # Header
    st.markdown("<h1>📋 All Candidates</h1>", unsafe_allow_html=True)
    
    # Fetch button
    if st.button("📊 Load All Candidates", use_container_width=True):
        with st.spinner("🔄 Loading candidates..."):
            try:
                response = requests.get(f"{API_URL}/candidates")
                
                if response.status_code == 200:
                    candidates = response.json()
                    st.success(f"✅ Loaded {len(candidates)} candidates!")
                    
                    if candidates:
                        for candidate in candidates:
                            # Candidate card
                            st.markdown(f"""
                            <div class="candidate-card">
                                <h2>{candidate['name']}</h2>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Metrics in columns
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                st.metric("Surface Fit", f"{candidate['surface_fit']}%")
                            with col2:
                                st.metric("Depth Fit", f"{candidate['depth_fit']}%")
                            with col3:
                                st.metric("Growth Potential", f"{candidate['growth_potential']}%")
                            with col4:
                                st.metric("Cultural Fit", f"{candidate['cultural_fit']}%")
                            
                            # Final score and status
                            col_final1, col_final2 = st.columns(2)
                            with col_final1:
                                st.metric("🏆 Final Score", f"{candidate['final_score']}%")
                            with col_final2:
                                status_color = "#10B981" if candidate['status'] == "Shortlist" else "#F59E0B" if candidate['status'] == "On-hold" else "#EF4444"
                                st.markdown(f"<h3 style='color: {status_color};'>Status: {candidate['status']}</h3>", unsafe_allow_html=True)
                            
                            # Radar chart
                            if 'radar_chart' in candidate:
                                with st.container():
                                    st.image(f"{API_URL}{candidate['radar_chart']}", 
                                            caption=f"Analysis for {candidate['name']}",
                                            use_container_width=True)
                            
                            st.markdown("---")
                    else:
                        st.info("ℹ️ No candidates found in database.")
                
                else:
                    st.error(f"❌ Failed to load candidates: {response.status_code}")
                    
            except Exception as e:
                st.error(f"❌ Connection error: {str(e)}")

# Footer (centered, subtle)
st.markdown("---")
st.markdown(
    "<div class='main-footer'>"
    "<p style='text-align: center; color: #9ca3af; font-size: 14px;'>"
    "© 2025 Multi-Perspective Resume Intelligence | Powered by Streamlit & OpenAI"
    "</p></div>",
    unsafe_allow_html=True
)