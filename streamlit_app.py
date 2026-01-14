"""
Enterprise HR AI Agent - Streamlit Frontend
Professional HR dashboard for intelligent CV ranking
"""

import streamlit as st
import requests
import pandas as pd
from typing import List, Dict, Optional
import os
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import base64

def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="HR AI Agent - Talent Intelligence Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv()

# Enterprise Professional Theme CSS (LinkedIn/Workday Style)
ENTERPRISE_CSS = """
<style>
    /* Import professional font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Main background - professional dark theme */
    .stApp {
        background: linear-gradient(135deg, #0f1419 0%, #1a1f2e 50%, #0f1419 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f2e 0%, #0f1419 100%);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Headers - professional styling */
    h1, h2, h3 {
        color: #e8eaed !important;
        font-weight: 600;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        letter-spacing: -0.02em;
    }
    
    /* Body text */
    p, div, span, label {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Text areas - professional styling */
    .stTextArea > div > div > textarea {
        background-color: #1e293b;
        color: #e8eaed;
        border: 1px solid #3d4043;
        border-radius: 6px;
        padding: 12px;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-size: 0.95rem;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #0a66c2;
        box-shadow: 0 0 0 2px rgba(10, 102, 194, 0.15);
        outline: none;
    }
    
    /* Text inputs - professional styling */
    .stTextInput > div > div > input {
        background-color: #1e293b;
        color: #e8eaed;
        border: 1px solid #3d4043;
        border-radius: 6px;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-size: 0.95rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #0a66c2;
        box-shadow: 0 0 0 2px rgba(10, 102, 194, 0.15);
        outline: none;
    }
    
    /* Select boxes - professional styling */
    .stSelectbox > div > div > select {
        background-color: #1e293b;
        color: #e8eaed;
        border: 1px solid #3d4043;
        border-radius: 6px;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-size: 0.95rem;
    }
    
    /* Premium Buttons - LinkedIn/Workday style */
    .stButton > button {
        background: #0a66c2;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(10, 102, 194, 0.2);
    }
    
    .stButton > button:hover {
        background: #004182;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(10, 102, 194, 0.3);
    }
    
    .stButton > button:disabled {
        background: #3d3d3d;
        color: #8e8e8e;
        cursor: not-allowed;
        transform: none;
        box-shadow: none;
    }
    
    /* Metrics - professional styling */
    [data-testid="stMetricValue"] {
        color: #0a66c2 !important;
        font-size: 2rem;
        font-weight: 600;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    [data-testid="stMetricLabel"] {
        color: #9aa0a6 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-size: 0.9rem;
    }
    
    /* Expanders - professional styling */
    .streamlit-expanderHeader {
        background-color: #1e293b;
        color: #e8eaed;
        border-radius: 6px;
        padding: 1rem;
        border: 1px solid #3d4043;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-weight: 500;
    }
    
    .streamlit-expanderContent {
        background-color: #0f172a;
        border-radius: 0 0 6px 6px;
        padding: 1.5rem;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        line-height: 1.6;
    }
    
    /* Info boxes - professional styling */
    .stInfo {
        background-color: #1e293b;
        border-left: 3px solid #0a66c2;
        border-radius: 6px;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    .stSuccess {
        background-color: #1e293b;
        border-left: 3px solid #0d7377;
        border-radius: 6px;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    .stWarning {
        background-color: #1e293b;
        border-left: 3px solid #f59e0b;
        border-radius: 6px;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    .stError {
        background-color: #1e293b;
        border-left: 3px solid #d93025;
        border-radius: 6px;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Dataframes */
    .dataframe {
        background-color: #1e293b;
        color: #e0e0e0;
    }
    
    /* Radio buttons */
    .stRadio > div {
        background-color: #1e293b;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #334155;
    }
    
    /* File uploader - professional styling */
    [data-testid="stFileUploader"] {
        background-color: #1e293b;
        border-radius: 6px;
        padding: 1rem;
        border: 2px dashed #3d4043;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Progress bar */
    .stProgress > div > div > div {
        background-color: #3b82f6;
    }
    
    /* Main content area */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Custom card styling */
    .enterprise-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    /* Score badges */
    .score-high {
        color: #10b981;
        font-weight: 700;
        font-size: 1.2rem;
    }
    
    .score-medium {
        color: #f59e0b;
        font-weight: 700;
        font-size: 1.2rem;
    }
    
    .score-low {
        color: #ef4444;
        font-weight: 700;
        font-size: 1.2rem;
    }
    
    /* Multiselect - professional styling to match theme */
    .stMultiSelect > div > div {
        background-color: #1e293b;
        border: 1px solid #3d4043;
        border-radius: 6px;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }
    
    /* Selected items (tags/chips) - blue theme instead of red */
    .stMultiSelect [data-baseweb="tag"] {
        background-color: #0a66c2 !important;
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 4px 8px !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }
    
    .stMultiSelect [data-baseweb="tag"]:hover {
        background-color: #004182 !important;
    }
    
    /* Remove button (X) in tags */
    .stMultiSelect [data-baseweb="tag"] [role="button"],
    .stMultiSelect [data-baseweb="tag"] button {
        color: white !important;
        opacity: 0.9 !important;
    }
    
    .stMultiSelect [data-baseweb="tag"] [role="button"]:hover,
    .stMultiSelect [data-baseweb="tag"] button:hover {
        opacity: 1 !important;
        background-color: rgba(255, 255, 255, 0.2) !important;
        border-radius: 3px !important;
    }
    
    /* Alternative selectors for multiselect tags (Streamlit may use different structures) */
    .stMultiSelect span[data-testid="stMarkdownContainer"] span,
    .stMultiSelect div[style*="background"] {
        background-color: #0a66c2 !important;
        color: white !important;
    }
    
    /* Target any red/chip-like elements in multiselect */
    .stMultiSelect > div > div > div > div[style*="rgb"] {
        background-color: #0a66c2 !important;
        color: white !important;
    }
    
    /* Multiselect dropdown */
    .stMultiSelect [data-baseweb="select"] {
        background-color: #1e293b !important;
        color: #e8eaed !important;
        border: 1px solid #3d4043 !important;
        border-radius: 6px !important;
    }
    
    /* Multiselect input */
    .stMultiSelect input {
        background-color: #1e293b !important;
        color: #e8eaed !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }
    
    /* Override any red colors in multiselect */
    .stMultiSelect * {
        --primary-color: #0a66c2 !important;
    }
    
    /* Style for selected option chips/tags - comprehensive override */
    div[data-baseweb="select"] [data-baseweb="tag"],
    div[data-baseweb="select"] span[style*="background-color: rgb"],
    .stMultiSelect div[style*="background-color: rgb(255"] {
        background-color: #0a66c2 !important;
        color: white !important;
        border-color: #0a66c2 !important;
    }
    
    /* Success toast animation - professional and subtle */
    .stSuccess {
        animation: slideInDown 0.3s ease-out;
        position: relative;
        z-index: 999;
    }
    
    @keyframes slideInDown {
        from {
            transform: translateY(-20px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
</style>
"""

st.markdown(ENTERPRISE_CSS, unsafe_allow_html=True)

# API configuration (hardcoded, not exposed to users)
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")


def get_domain_skills(domain: str) -> List[str]:
    """
    Get recommended skills for a given domain
    
    Args:
        domain: Selected domain
        
    Returns:
        List of recommended skills for the domain
    """
    domain_skills_map = {
        "Data Science": [
            "Python", "SQL", "Statistics", "Probability", "Linear Algebra",
            "Pandas", "NumPy", "Scikit-learn", "Machine Learning", "Deep Learning",
            "Data Visualization", "Matplotlib", "Seaborn", "Jupyter", "R"
        ],
        "GenAI": [
            "LLMs", "Prompt Engineering", "LangChain", "Vector Databases", "RAG",
            "OpenAI APIs", "Pinecone", "Embeddings", "Transformers", "Hugging Face",
            "Fine-tuning", "Tokenization", "Semantic Search", "Chroma", "Weaviate"
        ],
        "Backend": [
            "Python", "Java", "REST APIs", "Microservices", "SQL", "NoSQL",
            "Docker", "Kubernetes", "FastAPI", "Flask", "Spring Boot", "Node.js",
            "PostgreSQL", "MongoDB", "Redis", "AWS", "GCP", "Azure"
        ],
        "AI Platform": [
            "MLOps", "Model Deployment", "CI/CD", "Monitoring", "AWS", "GCP",
            "Azure", "Airflow", "Kubeflow", "MLflow", "TensorFlow Serving",
            "Model Registry", "A/B Testing", "Feature Stores", "Data Pipelines"
        ],
        "HR Analytics": [
            "Python", "SQL", "Data Analysis", "Statistics", "Tableau", "Power BI",
            "Excel", "HRIS", "People Analytics", "Predictive Analytics",
            "Dashboard Design", "Reporting", "Workday", "SuccessFactors"
        ]
    }
    
    return domain_skills_map.get(domain, [])


def combine_skills(selected_skills: List[str], custom_skills_text: str) -> str:
    """
    Combine selected skills and custom skills, removing duplicates
    
    Args:
        selected_skills: List of skills from multi-select
        custom_skills_text: Comma-separated custom skills string
        
    Returns:
        Comma-separated string of all unique skills
    """
    # Parse custom skills
    custom_skills = []
    if custom_skills_text and custom_skills_text.strip():
        custom_skills = [skill.strip() for skill in custom_skills_text.split(",") if skill.strip()]
    
    # Combine and deduplicate (case-insensitive)
    all_skills = selected_skills + custom_skills
    seen = set()
    unique_skills = []
    
    for skill in all_skills:
        skill_lower = skill.lower()
        if skill_lower not in seen:
            seen.add(skill_lower)
            unique_skills.append(skill)
    
    return ", ".join(unique_skills)


def initialize_session():
    """Initialize session state variables"""
    if "session_id" not in st.session_state:
        st.session_state.session_id = None
    if "ranking_results" not in st.session_state:
        st.session_state.ranking_results = None
    if "processing" not in st.session_state:
        st.session_state.processing = False
    if "jd_mode" not in st.session_state:
        st.session_state.jd_mode = "Manual"
    if "generated_jd" not in st.session_state:
        st.session_state.generated_jd = ""
    if "top_k_display" not in st.session_state:
        st.session_state.top_k_display = 3  # Default to Top 3


def display_header():
    """Display enterprise header with institute and company branding"""
    # Logo paths
    siei_logo_path = "assets/siei_logo.png"
    ey_logo_path = "assets/ey_logo.png"  # Primary path
    ey_logo_path_alt = "assets/ey_logo.png"  # Alternative path
    SIEI_LOGO = Path(siei_logo_path)
    EY_LOGO = Path(ey_logo_path)
    
    # Top header bar with left and right branding (ABOVE main title)
    col_left, col_center, col_right = st.columns([3, 4, 3])
    
    with col_left:
        # Push the whole left block slightly down
        st.markdown("<div style='margin-top:16px;'></div>", unsafe_allow_html=True)
        # Left: SIEI Branding - Logo image MUST be visible
        logo_text_col1, logo_text_col2 = st.columns([0.9, 3.1], gap="small")
        with logo_text_col1:
            if SIEI_LOGO.exists():
                siei_base64 = img_to_base64(SIEI_LOGO)
                st.markdown(
                    f"""
                    <img src="data:image/png;base64,{siei_base64}"
                         style="
                            width:56px;
                            height:auto;
                            margin-right:-16px;
                            display:block;
                        "
                    />
                    """,
              unsafe_allow_html=True
            )
            else:
                # Fallback to st.image if Path doesn't work
                if os.path.exists(siei_logo_path):
                    st.image(siei_logo_path, width=52)
                else:
                    # Try alternative paths
                    alt_paths = [
                        "assets/siei_logo.jpg",
                        "assets/SIEI_logo.png",
                        "assets/SIEI_logo.jpg",
                        "siei_logo.png",
                        "siei_logo.jpg"
                    ]
                    logo_found = False
                    for alt_path in alt_paths:
                        if os.path.exists(alt_path):
                            st.image(alt_path, width=52)
                            logo_found = True
                            break
                    if not logo_found:
                        st.markdown('<div style="height:52px;width:52px;background:#1e293b;border-radius:4px;display:flex;align-items:center;justify-content:center;color:#0a66c2;font-size:10px;font-weight:bold;">SIEI</div>', unsafe_allow_html=True)
        with logo_text_col2:
            st.markdown("""
        <div style="
            font-size: 1.1rem;
            font-weight: 600;
            color: #0a66c2;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            line-height: 1.1;
            margin-top: 6px;
            margin-left: -16px;  /* ⬅️ pulls text closer to logo */
        ">SIEI</div>

        <div style="
            font-size: 0.75rem;
            color: #9aa0a6;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            margin-top: 2px;
            white-space: nowrap;
            margin-left: -16px;
        ">Snow IT Expert Institute</div>
    """, unsafe_allow_html=True)
    
    with col_right:
        # Right: EY Branding - Logo image using Base64 + HTML
        
        if EY_LOGO.exists():
            ey_base64 = img_to_base64(EY_LOGO)
            st.markdown(
                f"""
                <div style="
                    display:flex;
                    justify-content:flex-end;
                    align-items:flex-start;
                    margin-top:16px;
                    margin-right:-32px;
                ">
                    <img src="data:image/png;base64,{ey_base64}"
                         style="
                            width:64px;
                            height:auto;
                            display:block;
                            pointer-events:none;
                            user-select:none;
                        "
                    />
                </div>
                """,
                unsafe_allow_html=True
            )

        elif os.path.exists(ey_logo_path_alt):
            # Try alternative .png extension
            EY_LOGO_ALT = Path(ey_logo_path_alt)
            if EY_LOGO_ALT.exists():
                ey_base64 = img_to_base64(EY_LOGO_ALT)
                st.markdown(
                    f"""
                    <div style="
                        display:flex;
                        justify-content:flex-end;
                        align-items:flex-start;
                        margin-top:16px;
                        margin-right:-32px;
                    ">
                        <img src="data:image/png;base64,{ey_base64}"
                             style="
                                width:64px;
                                height:auto;
                                display:block;
                                pointer-events:none;
                                user-select:none;  
                            "
                        />
                    </div>
                    """,
                    unsafe_allow_html=True     
                )  
        else:
            # ❌ Do nothing if logo not found (NO BOX)
            st.markdown("")
    
    # Main title at center - moved slightly upward
    st.markdown("""
        <div style="text-align: center; padding: 1rem 0 1.5rem 0;">
            <h1 style="color: #0a66c2; font-size: 2.5rem; margin-bottom: 0.5rem; font-weight: 600; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; letter-spacing: -0.02em;">
                HR AI Agent
            </h1>
            <p style="color: #9aa0a6; font-size: 1.1rem; margin-top: 0; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">
                Enterprise Talent Intelligence Platform
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")


def generate_job_description(
    job_title: str,
    experience: str,
    domain: str,
    seniority: str,
    location: str,
    key_skills: str
) -> str:
    """
    Generate job description using OpenAI
    
    Args:
        job_title: Job title
        experience: Experience range
        domain: Domain/field
        seniority: Seniority level
        location: Location
        key_skills: Comma-separated key skills
        
    Returns:
        Generated job description text
    """
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        st.error("OpenAI API key not found. Please configure OPENAI_API_KEY in environment.")
        return ""
    
    client = OpenAI(api_key=openai_api_key)
    
    prompt = f"""Generate a professional, enterprise-grade job description for the following role.

Job Title: {job_title}
Experience Required: {experience} years
Domain: {domain}
Seniority Level: {seniority}
Location: {location}
Key Skills: {key_skills}

Requirements:
1. Use corporate, professional tone
2. Make it ATS-friendly (no emojis, no markdown)
3. Structure must include:
   - Role Summary (2-3 sentences)
   - Roles & Responsibilities (bullet points)
   - Required Skills (list)
   - Preferred Skills (list)
   - Experience & Education Requirements

Output format: Plain text only, no markdown, no emojis, no code blocks.
Use clear sections with headers in plain text format.

Generate the complete job description now:"""

    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",  # Using GPT-4 Turbo for JD generation
            messages=[
                {"role": "system", "content": "You are an expert HR professional who writes clear, professional, ATS-friendly job descriptions for enterprise companies. Always output plain text only, no markdown, no emojis."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        generated_text = response.choices[0].message.content.strip()
        
        # Clean up any markdown that might have been added
        if generated_text.startswith("```"):
            lines = generated_text.split("\n")
            generated_text = "\n".join(lines[1:-1]) if len(lines) > 2 else generated_text
        
        return generated_text
    
    except Exception as e:
        st.error(f"Error generating job description: {str(e)}")
        return ""


def rank_cvs(jd_text: str, uploaded_files: List) -> Dict:
    """
    Call API to rank CVs
    
    Args:
        jd_text: Job description text
        uploaded_files: List of uploaded files
        
    Returns:
        API response with ranking results
    """
    try:
        # Prepare files for upload
        files = []
        for uploaded_file in uploaded_files:
            files.append(
                ("files", (uploaded_file.name, uploaded_file.read(), uploaded_file.type))
            )
            uploaded_file.seek(0)  # Reset file pointer
        
        # Prepare form data - request all candidates for full ranking display
        data = {
            "job_description": jd_text,
            "top_n": 50  # Get all candidates to show full ranking
        }
        
        # Make API request
        response = requests.post(
            f"{API_BASE_URL}/rank-cvs",
            files=files,
            data=data,
            timeout=300  # 5 minute timeout for processing
        )
        
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        st.error(f"Error processing request: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                st.error(f"Details: {error_detail.get('detail', 'Unknown error')}")
            except:
                st.error(f"Status Code: {e.response.status_code}")
        return None


def display_results(results: Dict):
    """
    Display ranking results in enterprise format with dynamic Top-K selection
    Relative benchmark: Top candidate is scaled to 80%, all others scaled proportionally
    
    Args:
        results: Ranking results from API
    """
    if not results or "top_candidates" not in results:
        st.warning("No results to display")
        return
    
    all_candidates = results["top_candidates"]
    total_candidates = results.get("total_candidates", len(all_candidates))
    processing_time = results.get("processing_time_seconds", 0)
    session_id = results.get("session_id", "unknown")
    
    # Initialize top_k_display if not set
    if "top_k_display" not in st.session_state:
        st.session_state.top_k_display = 3
    
    # Ensure top_k_display is within valid range
    max_display = min(total_candidates, len(all_candidates))
    if st.session_state.top_k_display > max_display:
        st.session_state.top_k_display = max_display
    if st.session_state.top_k_display < 1:
        st.session_state.top_k_display = 1
    
    # RELATIVE BENCHMARK: Calculate scaling factor
    # Top candidate's raw score becomes 80% benchmark
    BENCHMARK_DISPLAY = 80.0
    if all_candidates:
        top_candidate_raw_score = all_candidates[0].get('match_score', 100.0)
    else:
        top_candidate_raw_score = 100.0  # Default fallback
    
    def scale_score(raw_score: float) -> float:
        """Scale score relative to top candidate (top = 80%)"""
        if top_candidate_raw_score > 0:
            return (raw_score / top_candidate_raw_score) * BENCHMARK_DISPLAY
        return raw_score
    
    # Display summary metrics
    st.markdown("### 📊 Analysis Summary")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Candidates", total_candidates)
    with col2:
        st.metric("Shortlisted", st.session_state.top_k_display)
    with col3:
        st.metric("Processing Time", f"{processing_time:.2f}s")
    
    st.markdown("---")
    
    # Top-K selection control
    st.markdown("### 🎯 Candidate Selection")
    col1, col2 = st.columns([2, 3])
    with col1:
        top_k = st.number_input(
            "Number of top candidates to display",
            min_value=1,
            max_value=max_display,
            value=st.session_state.top_k_display,
            step=1,
            help=f"Select how many top-ranked candidates you want to review (1 to {max_display})",
            key="top_k_input"
        )
        st.session_state.top_k_display = top_k
    with col2:
        st.markdown("")
        st.markdown("")
        st.caption(f"Showing top {top_k} candidates based on overall match score")
    
    st.markdown("---")
    
    # Separate top K candidates from remaining candidates
    top_k_candidates = all_candidates[:top_k]
    remaining_candidates = all_candidates[top_k:] if len(all_candidates) > top_k else []
    
    # Display Top K Shortlisted Candidates (prominently)
    if len(top_k_candidates) == 1:
        st.markdown("### ⭐ Top Shortlisted Candidate")
    else:
        st.markdown(f"### ⭐ Top {len(top_k_candidates)} Shortlisted Candidates")
    
    for idx, candidate in enumerate(top_k_candidates, 1):
        raw_score = candidate['match_score']
        displayed_score = scale_score(raw_score)
        score_class = "score-high" if displayed_score >= 70 else "score-medium" if displayed_score >= 50 else "score-low"
        
        with st.expander(
            f"#{idx} {candidate['candidate_name']} - Match Score: {displayed_score:.1f}%",
            expanded=True  # All top K candidates expanded by default
        ):
            # Overall score (displayed with relative scaling)
            st.markdown(f'<p class="{score_class}">Overall Match Score: {displayed_score:.1f}%</p>', unsafe_allow_html=True)
            
            # Detailed scores
            detailed_scores = candidate.get("detailed_scores", {})
            if detailed_scores:
                st.markdown("**Score Breakdown:**")
                score_cols = st.columns(5)
                with score_cols[0]:
                    st.metric("Skills", f"{detailed_scores.get('skill_match', 0):.0f}%")
                with score_cols[1]:
                    st.metric("Experience", f"{detailed_scores.get('experience', 0):.0f}%")
                with score_cols[2]:
                    st.metric("Tools/Tech", f"{detailed_scores.get('tool_tech', 0):.0f}%")
                with score_cols[3]:
                    st.metric("Seniority", f"{detailed_scores.get('seniority', 0):.0f}%")
                with score_cols[4]:
                    st.metric("Semantic", f"{detailed_scores.get('semantic', 0):.0f}%")
            
            # Matched skills
            matched_skills = candidate.get("matched_skills", [])
            if matched_skills:
                st.markdown("**✅ Matched Skills:**")
                skills_text = ", ".join(matched_skills[:10])
                if len(matched_skills) > 10:
                    skills_text += f" (+{len(matched_skills) - 10} more)"
                st.info(skills_text)
            
            # Missing skills
            missing_skills = candidate.get("missing_skills", [])
            if missing_skills:
                st.markdown("**⚠️ Missing Skills:**")
                missing_text = ", ".join(missing_skills[:10])
                if len(missing_skills) > 10:
                    missing_text += f" (+{len(missing_skills) - 10} more)"
                st.warning(missing_text)
            
            # Explanation
            explanation = candidate.get("explanation", "")
            if explanation:
                st.markdown("**📋 Analysis:**")
                st.write(explanation)
            
            # Download button
            file_path = candidate.get("file_path", "")
            if file_path:
                filename = Path(file_path).name
                download_url = f"{API_BASE_URL}/download-cv/{session_id}/{filename}"
                
                try:
                    response = requests.get(download_url, timeout=30)
                    if response.status_code == 200:
                        st.download_button(
                            label=f"📥 Download CV: {filename}",
                            data=response.content,
                            file_name=filename,
                            mime="application/octet-stream",
                            key=f"download_top_{idx}"
                        )
                    else:
                        st.warning(f"File not available: {filename}")
                except Exception as e:
                    st.warning(f"Could not download {filename}: {str(e)}")
    
    # Display remaining candidates in collapsible section
    if remaining_candidates:
        st.markdown("---")
        
        # Initialize session state for toggle
        if "show_other_candidates" not in st.session_state:
            st.session_state.show_other_candidates = False
        
        # Toggle button
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown("### 📋 Other Ranked Candidates")
        with col2:
            button_label = "Hide" if st.session_state.show_other_candidates else "View All"
            if st.button(button_label, key="toggle_other_candidates"):
                st.session_state.show_other_candidates = not st.session_state.show_other_candidates
        
        if st.session_state.show_other_candidates:
            if remaining_candidates:
                st.markdown(f"*Showing {len(remaining_candidates)} additional candidates ranked below the top {st.session_state.top_k_display}*")
            st.markdown("")
            
            # Create table for remaining candidates
            table_data = []
            start_rank = st.session_state.top_k_display + 1
            for idx, candidate in enumerate(remaining_candidates, start_rank):
                raw_score = candidate['match_score']
                displayed_score = scale_score(raw_score)
                table_data.append({
                    "Rank": idx,
                    "Candidate Name": candidate['candidate_name'],
                    "Match Score (%)": f"{displayed_score:.1f}",
                    "Matched Skills": len(candidate.get('matched_skills', [])),
                    "Missing Skills": len(candidate.get('missing_skills', [])),
                    "CV File": Path(candidate.get('file_path', '')).name
                })
            
            df = pd.DataFrame(table_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.markdown("")
            st.markdown("**View individual candidate details:**")
            
            # Optional details per candidate (no nested expanders - use individual expanders)
            start_rank = st.session_state.top_k_display + 1
            for idx, candidate in enumerate(remaining_candidates, start_rank):
                raw_score = candidate['match_score']
                displayed_score = scale_score(raw_score)
                with st.expander(f"Rank #{idx}: {candidate['candidate_name']} ({displayed_score:.1f}%)", expanded=False):
                    score = displayed_score
                    
                    # Brief summary
                    explanation = candidate.get("explanation", "")
                    if explanation:
                        st.markdown("**Summary:**")
                        st.write(explanation)
                    
                    # Quick stats
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Match Score", f"{score:.1f}%")
                        matched_count = len(candidate.get('matched_skills', []))
                        st.metric("Matched Skills", matched_count)
                    with col2:
                        missing_count = len(candidate.get('missing_skills', []))
                        st.metric("Missing Skills", missing_count)
                    
                    # Download button
                    file_path = candidate.get("file_path", "")
                    if file_path:
                        filename = Path(file_path).name
                        download_url = f"{API_BASE_URL}/download-cv/{session_id}/{filename}"
                        
                        try:
                            response = requests.get(download_url, timeout=30)
                            if response.status_code == 200:
                                st.download_button(
                                    label=f"📥 Download CV: {filename}",
                                    data=response.content,
                                    file_name=filename,
                                    mime="application/octet-stream",
                                    key=f"download_remaining_{idx}"
                                )
                            else:
                                st.warning(f"File not available: {filename}")
                        except Exception as e:
                            st.warning(f"Could not download {filename}: {str(e)}")


def main():
    """Main application function"""
    initialize_session()
    display_header()
    
    # Sidebar - HR-friendly content only (collapsible)
    with st.sidebar:
        # Collapsible "How to Use" section
        with st.expander("📋 How to Use", expanded=False):
            st.markdown("""
            1. **Choose JD Input Mode**: Manual entry or AI generation
            2. **Provide Job Description**: Either paste existing JD or generate one
            3. **Upload CV Files**: Select candidate resumes (PDF, DOC, DOCX)
            4. **Analyze & Rank**: Click to process and get top matches
            5. **Review Results**: See ranked candidates with detailed analysis
            6. **Download CVs**: Get shortlisted candidate resumes
            """)
        
        # Collapsible "About" section - properly formatted
        with st.expander("ℹ️ About", expanded=False):
            st.markdown("""
            HR AI Agent is an enterprise talent intelligence platform that helps recruiters make faster, data-driven hiring decisions.
            
            
            """)
            st.markdown("""
            • Extracts skills and requirements from job descriptions  
            • Analyzes candidate CVs using AI  
            • Scores candidates on multiple factors  
            • Provides transparent ranking explanations  
            """)
    
    # Job Description Input Mode Selection
    st.markdown("### 📝 Job Description")
    jd_mode = st.radio(
        "How would you like to provide the Job Description?",
        ["Manual", "AI Generated"],
        horizontal=True,
        key="jd_mode_selector"
    )
    
    st.session_state.jd_mode = jd_mode
    jd_text = ""
    
    if jd_mode == "Manual":
        # Manual JD input
        jd_text = st.text_area(
            "Enter Job Description",
            height=250,
            placeholder="Paste or type the complete job description here...\n\nInclude:\n- Role summary\n- Responsibilities\n- Required skills\n- Experience requirements\n- Education requirements",
            help="Paste the complete job description. The system will analyze this against candidate CVs.",
            key="manual_jd"
        )
    
    else:  # AI Generated
        st.markdown("#### Generate Job Description with AI")
        
        # JD Generation Form
        col1, col2 = st.columns(2)
        
        with col1:
            job_title = st.text_input("Job Title *", placeholder="e.g., Senior Data Scientist")
            experience = st.selectbox(
                "Experience Required *",
                ["0-2 years", "2-4 years", "4-7 years", "7+ years"]
            )
            domain = st.selectbox(
                "Domain *",
                ["GenAI", "Data Science", "Backend", "AI Platform", "HR Analytics"]
            )
        
        with col2:
            seniority = st.selectbox(
                "Seniority Level *",
                ["Junior", "Mid", "Senior", "Lead"]
            )
            location = st.text_input("Location *", placeholder="e.g., San Francisco, CA")
        
        # Skills section with domain-based suggestions and manual entry
        st.markdown("#### Key Skills")
        
        # Get recommended skills based on selected domain
        recommended_skills = get_domain_skills(domain)
        
        # Multi-select for recommended skills
        if recommended_skills:
            selected_recommended = st.multiselect(
                "Recommended Skills",
                options=recommended_skills,
                help=f"Select relevant skills for {domain} domain",
                key="recommended_skills_multiselect"
            )
        else:
            selected_recommended = []
        
        # Manual skill entry
        custom_skills_text = st.text_input(
            "Add Custom Skills (comma-separated)",
            placeholder="e.g., TensorFlow, PyTorch, Custom Framework",
            help="Add any additional skills not listed above, separated by commas",
            key="custom_skills_input"
        )
        
        # Combine and display final skills
        combined_skills = combine_skills(selected_recommended, custom_skills_text)
        
        # Show final combined skills (read-only display) - skills are optional
        if combined_skills:
            st.markdown("**Selected Skills:**")
            st.info(combined_skills)
            key_skills = combined_skills
        else:
            key_skills = ""  # Empty skills allowed - AI will infer from job title and domain
        
        # Generate button
        if st.button("✨ Generate Job Description", type="primary", use_container_width=True):
            with st.spinner("Generating professional job description..."):
                generated_jd = generate_job_description(
                    job_title=job_title,
                    experience=experience,
                    domain=domain,
                    seniority=seniority,
                    location=location,
                    key_skills=key_skills
                )
                
                if generated_jd:
                    st.session_state.generated_jd = generated_jd
                    st.success("Job description generated successfully!")
        
        # Display generated JD and allow editing
        if st.session_state.generated_jd:
            st.markdown("#### Generated Job Description")
            jd_text = st.text_area(
                "Review and edit the generated job description:",
                value=st.session_state.generated_jd,
                height=300,
                key="generated_jd_editor"
            )
        else:
            st.info("Fill in the form above and click 'Generate Job Description' to create a professional JD.")
    
    st.markdown("---")
    
    # CV Upload
    st.markdown("### 📄 Upload Candidate CVs")
    uploaded_files = st.file_uploader(
        "Select CV files (PDF, DOC, DOCX)",
        type=["pdf", "doc", "docx"],
        accept_multiple_files=True,
        help="Upload candidate resumes. Maximum 10 files per analysis."
    )
    
    # Maximum CV limit
    MAX_CVS_ALLOWED = 10
    
    # Validate CV count
    cv_count = len(uploaded_files) if uploaded_files else 0
    exceeds_max = cv_count > MAX_CVS_ALLOWED
    
    # Show warning if exceeds maximum (clean, professional message)
    if exceeds_max:
        st.warning("You can upload a maximum of 10 CVs at a time.")
    
    # Show uploaded files in expander (only if files uploaded)
    if uploaded_files and not exceeds_max:
        with st.expander("View Uploaded Files", expanded=False):
            for file in uploaded_files:
                st.write(f"📄 {file.name} ({file.size / 1024:.1f} KB)")
    
    st.markdown("---")
    
    # Validate inputs for button enablement
    has_jd = bool(jd_text.strip())
    has_valid_cvs = uploaded_files is not None and cv_count >= 1 and cv_count <= MAX_CVS_ALLOWED
    can_analyze = has_jd and has_valid_cvs
    
    # Analyze button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        analyze_button = st.button(
            "🚀 Analyze & Rank CVs",
            type="primary",
            use_container_width=True,
            disabled=not can_analyze
        )
    
    # Process ranking
    if analyze_button and can_analyze:
        if not has_jd:
            st.error("Job description is required")
        elif exceeds_max:
            st.error("Please upload a maximum of 10 CV files")
        elif cv_count < 1:
            st.error("Please upload at least 1 CV file")
        else:
            st.session_state.processing = True
            
            with st.spinner("Processing candidates... This may take a few minutes."):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Simulated progress
                for i in range(100):
                    time.sleep(0.05)
                    progress_bar.progress(i + 1)
                    if i < 20:
                        status_text.text("📥 Loading documents...")
                    elif i < 40:
                        status_text.text("🔍 Analyzing CVs...")
                    elif i < 70:
                        status_text.text("🤖 AI processing...")
                    elif i < 90:
                        status_text.text("📊 Ranking candidates...")
                    else:
                        status_text.text("✅ Finalizing results...")
                
                # Call API
                status_text.text("🌐 Processing request...")
                results = rank_cvs(jd_text, uploaded_files)
                
                progress_bar.empty()
                status_text.empty()
                
                if results:
                    st.session_state.ranking_results = results
                    st.session_state.session_id = results.get("session_id")
                    # Show clean success toast (auto-dismiss)
                    st.success("✅ CV analysis completed successfully!")
                else:
                    st.error("❌ Failed to process CVs. Please try again.")
            
            st.session_state.processing = False
    
    # Display results
    if st.session_state.ranking_results:
        st.markdown("---")
        display_results(st.session_state.ranking_results)
        
        # Cleanup button
        if st.session_state.session_id:
            if st.button("🗑️ Clear Session & Start New", use_container_width=True):
                # Cleanup session via API
                try:
                    requests.delete(f"{API_BASE_URL}/session/{st.session_state.session_id}")
                except:
                    pass
                
                st.session_state.session_id = None
                st.session_state.ranking_results = None
                st.session_state.generated_jd = ""
                st.rerun()


if __name__ == "__main__":
    main()
