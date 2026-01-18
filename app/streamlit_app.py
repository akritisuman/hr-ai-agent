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
import json
import logging
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import base64



logger = logging.getLogger(__name__)

def img_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def get_ey_logo_path() -> Optional[str]:
    """
    Get the EY logo path based on current theme
    
    Returns:
        Path to EY logo file, or None if no logo is available
    """
    current_theme = st.session_state.get("theme", "dark")
    
    if current_theme == "dark":
        dark_logo = "assets/ey_logo_dark.png"
        if os.path.exists(dark_logo):
            return dark_logo
    else:
        light_logo = "assets/ey_logo_light.png"
        if os.path.exists(light_logo):
            return light_logo
    
    generic_logo = "assets/ey_logo.png"
    if os.path.exists(generic_logo):
        return generic_logo
    return None


# Page configuration - MUST be first Streamlit command
st.set_page_config(
    page_title="HR AI Agent - Talent Intelligence Platform",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
/* FIX: Force header height parity between dark & light */
header[data-testid="stHeader"] {
    height: 64px !important;
    padding-top: 0 !important;
    margin-top: 0 !important;
}
</style>
""", unsafe_allow_html=True)


# Load environment variables
load_dotenv()

# ============================================
# AUTHENTICATION STATE INITIALIZATION
# ============================================
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "page" not in st.session_state:
    st.session_state.page = "login"

# Initialize theme in session state (must be before CSS injection)
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# Centralized theme configuration
THEME_CONFIG = {
    "dark": {
        "app_bg": "linear-gradient(135deg, #0f1419 0%, #1a1f2e 50%, #0f1419 100%)",
        "sidebar_bg": "linear-gradient(180deg, #1a1f2e 0%, #0f1419 100%)",
        "text_primary": "#e8eaed",
        "text_secondary": "#9aa0a6",
        "text_muted": "#9aa0a6",
        "input_bg": "#1e293b",
        "input_border": "#3d4043",
        "input_text": "#e8eaed",
        "card_bg": "linear-gradient(135deg, #1e293b 0%, #0f172a 100%)",
        "card_border": "#334155",
        "expander_header_bg": "#1e293b",
        "expander_content_bg": "#0f172a",
        "info_bg": "#1e293b",
        "success_bg": "#1e293b",
        "warning_bg": "#1e293b",
        "error_bg": "#1e293b",
        "dataframe_bg": "#1e293b",
        "dataframe_text": "#e0e0e0",
        "radio_bg": "#1e293b",
        "radio_border": "#334155",
        "uploader_bg": "#1e293b",
        "uploader_border": "#3d4043",
        "multiselect_bg": "#1e293b",
        "multiselect_border": "#3d4043",
        "multiselect_text": "#e8eaed",
        "accent": "#0a66c2",
        "accent_hover": "#004182",
        "accent_light": "#3b82f6",
        "score_high": "#10b981",
        "score_medium": "#f59e0b",
        "score_low": "#ef4444",
        "border": "#3d4043",
        "icon_color": "#9aa0a6",
        "surface": "#1e293b",
        "background": "#0f1419",
        "button_disabled_bg": "#3d4043",
        "button_disabled_text": "#9aa0a6",
        "tooltip_bg": "#1e293b",
        "tooltip_text": "#e8eaed",
    },
    "light": {
        "app_bg": "#FFFFFF",
        "sidebar_bg": "#F1F5F9",
        "text_primary": "#111827",
        "text_secondary": "#4B5563",
        "text_muted": "#6B7280",
        "input_bg": "#FFFFFF",
        "input_border": "#D1D5DB",
        "input_text": "#111827",
        "card_bg": "#FFFFFF",
        "card_border": "#D1D5DB",
        "expander_header_bg": "#FFFFFF",
        "expander_content_bg": "#FFFFFF",
        "info_bg": "#FFFFFF",
        "success_bg": "#FFFFFF",
        "warning_bg": "#FFFFFF",
        "error_bg": "#FFFFFF",
        "dataframe_bg": "#FFFFFF",
        "dataframe_text": "#111827",
        "radio_bg": "#FFFFFF",
        "radio_border": "#D1D5DB",
        "uploader_bg": "#FFFFFF",
        "uploader_border": "#D1D5DB",
        "multiselect_bg": "#FFFFFF",
        "multiselect_border": "#D1D5DB",
        "multiselect_text": "#111827",
        "accent": "#2563EB",
        "accent_hover": "#1d4ed8",
        "accent_light": "#3b82f6",
        "score_high": "#10b981",
        "score_medium": "#f59e0b",
        "score_low": "#ef4444",
        "border": "#D1D5DB",
        "icon_color": "#4B5563",
        "surface": "#F9FAFB",
        "background": "#FFFFFF",
        "button_disabled_bg": "#E5E7EB",
        "button_disabled_text": "#6B7280",
        "tooltip_bg": "#111827",
        "tooltip_text": "#FFFFFF",
    }
}

def get_theme() -> dict:
    """Get current theme configuration"""
    theme = st.session_state.get("theme", "dark")
    return THEME_CONFIG.get(theme, THEME_CONFIG["dark"])

def get_theme_css(theme: str) -> str:
    """
    Get CSS based on selected theme
    Uses centralized THEME_CONFIG for consistent colors
    
    Args:
        theme: "dark" or "light"
        
    Returns:
        CSS string for the selected theme
    """
    colors = THEME_CONFIG.get(theme, THEME_CONFIG["dark"])
    
    return f"""
<style>
    /* Import professional font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    /* Main background */
    .stApp {{
        background: {colors["app_bg"]};
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }}

    /* Streamlit top header bar */
    header[data-testid="stHeader"] {{
        background-color: {colors["app_bg"]} !important;
        box-shadow: none !important;
        border-bottom: 1px solid {colors["border"]} !important;
    }}

    /* ==================================================
    BASEWEB SELECT & MULTISELECT
    ================================================== */

    /* Select / Multiselect main input */
    div[data-baseweb="select"] {{
        background-color: {colors["input_bg"]} !important;
        color: {colors["input_text"]} !important;
        border: 1px solid {colors["input_border"]} !important;
    }}

    /* Ensure text inside select is correct */
    div[data-baseweb="select"] *,
    div[data-baseweb="select"] > div,
    div[data-baseweb="select"] > div > div {{
        color: {colors["input_text"]} !important;
        background-color: {colors["input_bg"]} !important;
    }}

    /* Dropdown popup container */
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    div[data-baseweb="popover"] [role="listbox"] {{
        background-color: {colors["input_bg"]} !important;
        border: 1px solid {colors["input_border"]} !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08) !important;
    }}
    
    /* Dropdown container inner elements */
    div[data-baseweb="popover"] > div *,
    div[data-baseweb="popover"] [role="listbox"] > * {{
        background-color: {colors["input_bg"]} !important;
    }}

    /* Dropdown options */
    div[data-baseweb="popover"] li,
    div[data-baseweb="popover"] [role="option"],
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] [role="listbox"],
    div[data-baseweb="popover"] [role="listbox"] li {{
        background-color: {colors["input_bg"]} !important;
        color: {colors["input_text"]} !important;
    }}
    
    /* Dropdown option text content - comprehensive override */
    div[data-baseweb="popover"] li *,
    div[data-baseweb="popover"] [role="option"] *,
    div[data-baseweb="popover"] [role="listbox"] *,
    div[data-baseweb="popover"] [role="listbox"] li *,
    div[data-baseweb="popover"] li span,
    div[data-baseweb="popover"] [role="option"] span,
    div[data-baseweb="popover"] li div,
    div[data-baseweb="popover"] [role="option"] div {{
        color: {colors["input_text"]} !important;
        background-color: transparent !important;
    }}

    /* Hover state */
    div[data-baseweb="popover"] li:hover,
    div[data-baseweb="popover"] [role="option"]:hover,
    div[data-baseweb="popover"] [role="listbox"] li:hover {{
        background-color: {colors["surface"]} !important;
        color: {colors["text_primary"]} !important;
    }}
    
    /* Hover state text content */
    div[data-baseweb="popover"] li:hover *,
    div[data-baseweb="popover"] [role="option"]:hover *,
    div[data-baseweb="popover"] [role="listbox"] li:hover * {{
        color: {colors["text_primary"]} !important;
    }}

    /* Selected option */
    div[data-baseweb="popover"] [aria-selected="true"],
    div[data-baseweb="popover"] [aria-selected="true"] *,
    div[data-baseweb="popover"] li[aria-selected="true"],
    div[data-baseweb="popover"] li[aria-selected="true"] *,
    div[data-baseweb="popover"] [role="option"][aria-selected="true"],
    div[data-baseweb="popover"] [role="option"][aria-selected="true"] * {{
        background-color: {colors["accent"]} !important;
        color: white !important;
    }}

    /* Dropdown arrow */
    div[data-baseweb="select"] svg {{
        fill: {colors["icon_color"]} !important;
        color: {colors["icon_color"]} !important;
    }}

    /* Multiselect text input */
    .stMultiSelect input {{
        background-color: {colors["input_bg"]} !important;
        color: {colors["input_text"]} !important;
    }}
    
    /* Multiselect container and inner elements */
    .stMultiSelect [data-baseweb="select"] > div,
    .stMultiSelect [data-baseweb="select"] > div > div,
    .stMultiSelect [data-baseweb="select"] > div > div > div {{
        background-color: {colors["multiselect_bg"]} !important;
        color: {colors["multiselect_text"]} !important;
    }}




    /* Sidebar styling */
    [data-testid="stSidebar"] {{
        background: {colors["sidebar_bg"]};
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }}
    
    /* Headers - professional styling */
    h1, h2, h3 {{
        color: {colors["text_primary"]} !important;
        font-weight: 600;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        letter-spacing: -0.02em;
    }}
    
    /* Body text */
    p, div, span {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        color: {colors["text_primary"]};
    }}
    
    /* Labels - ensure visibility in both themes */
    label,
    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] p {{
        color: {colors["text_primary"]} !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }}
    
        /* Placeholder text */
        input::placeholder,
        textarea::placeholder,
        div[data-baseweb="select"] input::placeholder {{
            color: {colors["text_muted"]} !important;
            opacity: 1 !important;
        }}
        
        /* BaseWeb select placeholder */
        div[data-baseweb="select"] [placeholder],
        .stMultiSelect input::placeholder {{
            color: {colors["text_muted"]} !important;
            opacity: 1 !important;
        }}
    
    /* Text areas - professional styling */
    .stTextArea > div > div > textarea {{
        background-color: {colors["input_bg"]};
        color: {colors["input_text"]};
        border: 1px solid {colors["input_border"]};
        border-radius: 6px;
        padding: 12px;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-size: 0.95rem;
    }}
    
    .stTextArea > div > div > textarea:focus {{
        border-color: {colors["accent"]};
        box-shadow: 0 0 0 2px rgba(10, 102, 194, 0.15);
        outline: none;
    }}
    
    /* Text inputs - professional styling */
    .stTextInput > div > div > input {{
        background-color: {colors["input_bg"]};
        color: {colors["input_text"]};
        border: 1px solid {colors["input_border"]};
        border-radius: 6px;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-size: 0.95rem;
    }}
    
    .stTextInput > div > div > input:focus {{
        border-color: {colors["accent"]};
        box-shadow: 0 0 0 2px rgba(10, 102, 194, 0.15);
        outline: none;
    }}
    
    /* Select boxes - professional styling */
    .stSelectbox > div > div > select {{
        background-color: {colors["input_bg"]} !important;
        color: {colors["input_text"]} !important;
        border: 1px solid {colors["input_border"]} !important;
        border-radius: 6px;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-size: 0.95rem;
    }}
    
    /* Selectbox dropdown arrow - theme-aware */
    .stSelectbox svg,
    .stSelectbox [data-baseweb="select"] svg {{
        fill: {colors["icon_color"]} !important;
        color: {colors["icon_color"]} !important;
        opacity: 1 !important;
    }}
    
    /* Selectbox label and text */
    .stSelectbox label,
    .stSelectbox [data-baseweb="select"] {{
        color: {colors["text_primary"]} !important;
    }}
    
    /* Selectbox selected value */
    .stSelectbox [data-baseweb="select"] > div,
    .stSelectbox [data-baseweb="select"] > div > div {{
        color: {colors["input_text"]} !important;
        background-color: {colors["input_bg"]} !important;
    }}
    
    /* Selectbox selected value text */
    .stSelectbox [data-baseweb="select"] > div *,
    .stSelectbox [data-baseweb="select"] > div > div * {{
        color: {colors["input_text"]} !important;
    }}
    
    /* Premium Buttons - LinkedIn/Workday style */
    .stButton > button {{
        background: {colors["accent"]} !important;
        color: white !important;
        border: none;
        border-radius: 6px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(10, 102, 194, 0.2);
    }}
    
    /* Ensure button text and inner elements are white */
    .stButton > button *,
    .stButton > button span,
    .stButton > button div {{
        color: white !important;
        background-color: transparent !important;
    }}
    
    .stButton > button:hover {{
        background: {colors["accent_hover"]} !important;
        color: white !important;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(10, 102, 194, 0.3);
    }}
    
    .stButton > button:hover * {{
        color: white !important;
        background-color: transparent !important;
    }}
    
    .stButton > button:disabled {{
        background: {colors["button_disabled_bg"]} !important;
        color: {colors["button_disabled_text"]} !important;
        cursor: not-allowed;
        transform: none;
        box-shadow: none;
    }}
    
    .stButton > button:disabled * {{
        color: {colors["button_disabled_text"]} !important;
        background-color: transparent !important;
    }}
    
    /* Metrics - professional styling */
    [data-testid="stMetricValue"] {{
        color: {colors["accent"]} !important;
        font-size: 2rem;
        font-weight: 600;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        background-color: transparent !important;
    }}
    
    [data-testid="stMetricLabel"] {{
        color: {colors["text_secondary"]} !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-size: 0.9rem;
        background-color: transparent !important;
    }}
    
    /* Expanders - professional styling */
    .streamlit-expanderHeader {{
        background-color: {colors["expander_header_bg"]} !important;
        color: {colors["text_primary"]} !important;
        border-radius: 6px;
        padding: 1rem;
        border: 1px solid {colors["input_border"]} !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-weight: 500;
    }}
    
    /* Expander header nested elements - transparent background, inherit text */
    .streamlit-expanderHeader *,
    .streamlit-expanderHeader > *,
    .streamlit-expanderHeader div,
    .streamlit-expanderHeader span,
    .streamlit-expanderHeader p,
    .streamlit-expanderHeader label {{
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: {colors["text_primary"]} !important;
    }}
    
    /* Dark expander headers - white text */
    .streamlit-expanderHeader[style*="background"][style*="#0f"],
    .streamlit-expanderHeader[style*="background"][style*="#1a"],
    .streamlit-expanderHeader[style*="background"][style*="#1e"],
    .streamlit-expanderHeader[style*="background-color"][style*="#0f"],
    .streamlit-expanderHeader[style*="background-color"][style*="#1a"],
    .streamlit-expanderHeader[style*="background-color"][style*="#1e"] {{
        color: white !important;
    }}
    
    .streamlit-expanderHeader[style*="background"][style*="#0f"] *,
    .streamlit-expanderHeader[style*="background"][style*="#1a"] *,
    .streamlit-expanderHeader[style*="background"][style*="#1e"] *,
    .streamlit-expanderHeader[style*="background-color"][style*="#0f"] *,
    .streamlit-expanderHeader[style*="background-color"][style*="#1a"] *,
    .streamlit-expanderHeader[style*="background-color"][style*="#1e"] * {{
        color: white !important;
        background-color: transparent !important;
    }}
    
    /* Expander arrow/chevron - theme-aware */
    .streamlit-expanderHeader svg,
    .streamlit-expanderHeader [data-testid="stExpanderToggleIcon"],
    [data-testid="stExpanderToggleIcon"] {{
        fill: {colors["icon_color"]} !important;
        color: {colors["icon_color"]} !important;
        opacity: 1 !important;
        stroke: {colors["icon_color"]} !important;
    }}
    
    .streamlit-expanderContent {{
        background-color: {colors["expander_content_bg"]} !important;
        border-radius: 0 0 6px 6px;
        padding: 1.5rem;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        line-height: 1.6;
        color: {colors["text_primary"]} !important;
    }}
    
    /* ALL nested elements in expander content - transparent background */
    .streamlit-expanderContent *,
    .streamlit-expanderContent > *,
    .streamlit-expanderContent div,
    .streamlit-expanderContent span,
    .streamlit-expanderContent p,
    .streamlit-expanderContent label {{
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: {colors["text_primary"]} !important;
    }}
    
    /* Exclude actual inputs and buttons - they need their own styling */
    .streamlit-expanderContent input[type="text"],
    .streamlit-expanderContent input[type="number"],
    .streamlit-expanderContent textarea,
    .streamlit-expanderContent button,
    .streamlit-expanderContent [data-testid="stButton"] > button,
    .streamlit-expanderContent [data-testid="stDownloadButton"] > button {{
        background-color: {colors["input_bg"]} !important;
    }}
    
    /* Sidebar expander arrows */
    [data-testid="stSidebar"] .streamlit-expanderHeader svg {{
        fill: {colors["icon_color"]} !important;
        color: {colors["icon_color"]} !important;
        opacity: 1 !important;
    }}
    
    /* Info boxes - professional styling - FLAT like button */
    .stInfo {{
        background-color: {colors["info_bg"]} !important;
        border: 1px solid {colors["card_border"]} !important;
        border-left: 3px solid {colors["accent"]} !important;
        border-radius: 6px;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        color: {colors["text_primary"]} !important;
    }}
    
    /* ALL nested elements - transparent background, inherit text color */
    .stInfo *,
    .stInfo > *,
    .stInfo div,
    .stInfo span,
    .stInfo p,
    .stInfo label {{
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: {colors["text_primary"]} !important;
    }}
    
    /* Exclude actual inputs and buttons - they need their own styling */
    .stInfo input[type="text"],
    .stInfo input[type="number"],
    .stInfo textarea,
    .stInfo button,
    .stInfo [data-testid="stButton"] > button,
    .stInfo [data-testid="stDownloadButton"] > button {{
        background-color: {colors["input_bg"]} !important;
    }}
    
    .stSuccess {{
        background-color: {colors["success_bg"]} !important;
        border: 1px solid {colors["card_border"]} !important;
        border-left: 3px solid #0d7377 !important;
        border-radius: 6px;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        color: {colors["text_primary"]} !important;
    }}
    
    /* ALL nested elements - transparent background, inherit text color */
    .stSuccess *,
    .stSuccess > *,
    .stSuccess div,
    .stSuccess span,
    .stSuccess p,
    .stSuccess label {{
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: {colors["text_primary"]} !important;
    }}
    
    /* Exclude actual inputs and buttons - they need their own styling */
    .stSuccess input[type="text"],
    .stSuccess input[type="number"],
    .stSuccess textarea,
    .stSuccess button,
    .stSuccess [data-testid="stButton"] > button,
    .stSuccess [data-testid="stDownloadButton"] > button {{
        background-color: {colors["input_bg"]} !important;
    }}
    
    .stWarning {{
        background-color: {colors["warning_bg"]} !important;
        border: 1px solid {colors["card_border"]} !important;
        border-left: 3px solid #f59e0b !important;
        border-radius: 6px;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        color: {colors["text_primary"]} !important;
    }}
    
    /* ALL nested elements - transparent background, inherit text color */
    .stWarning *,
    .stWarning > *,
    .stWarning div,
    .stWarning span,
    .stWarning p,
    .stWarning label {{
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: {colors["text_primary"]} !important;
    }}
    
    /* Exclude actual inputs and buttons - they need their own styling */
    .stWarning input[type="text"],
    .stWarning input[type="number"],
    .stWarning textarea,
    .stWarning button,
    .stWarning [data-testid="stButton"] > button,
    .stWarning [data-testid="stDownloadButton"] > button {{
        background-color: {colors["input_bg"]} !important;
    }}
    
    .stError {{
        background-color: {colors["error_bg"]} !important;
        border: 1px solid {colors["card_border"]} !important;
        border-left: 3px solid #d93025 !important;
        border-radius: 6px;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        color: {colors["text_primary"]} !important;
    }}
    
    /* ALL nested elements - transparent background, inherit text color */
    .stError *,
    .stError > *,
    .stError div,
    .stError span,
    .stError p,
    .stError label {{
        background-color: transparent !important;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        color: {colors["text_primary"]} !important;
    }}
    
    /* Exclude actual inputs and buttons - they need their own styling */
    .stError input[type="text"],
    .stError input[type="number"],
    .stError textarea,
    .stError button,
    .stError [data-testid="stButton"] > button,
    .stError [data-testid="stDownloadButton"] > button {{
        background-color: {colors["input_bg"]} !important;
    }}
    
    /* Dataframes */
    .dataframe,
    .dataframe *,
    .dataframe th,
    .dataframe td,
    .dataframe thead,
    .dataframe tbody {{
        background-color: {colors["dataframe_bg"]} !important;
        color: {colors["dataframe_text"]} !important;
    }}
    
    /* File uploader - professional styling */
    [data-testid="stFileUploader"] {{
        background-color: {colors["uploader_bg"]} !important;
        border-radius: 6px;
        padding: 1rem;
        border: 2px dashed {colors["uploader_border"]} !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }}
    
    /* File uploader inner section */
    [data-testid="stFileUploader"] section,
    [data-testid="stFileUploader"] > div,
    [data-testid="stFileUploader"] > div > div,
    [data-testid="stFileUploader"] section *,
    [data-testid="stFileUploader"] > div * {{
        background-color: {colors["uploader_bg"]} !important;
        color: {colors["text_primary"]} !important;
    }}
    
    /* Progress bar */
    .stProgress > div > div > div {{
        background-color: {colors["accent_light"]};
    }}
    
    /* Main content area */
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
    }}
    
    /* Custom card styling */
    .enterprise-card {{
        background: {colors["card_bg"]} !important;
        border: 1px solid {colors["card_border"]} !important;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        color: {colors["text_primary"]} !important;
    }}
    
    /* Text inside enterprise cards - no background override */
    .enterprise-card p,
    .enterprise-card div:not([class*="st"]):not([data-testid]),
    .enterprise-card span:not([class*="st"]):not([data-testid]) {{
        color: {colors["text_primary"]} !important;
        background-color: transparent !important;
    }}
    
    /* Exclude inputs and buttons from background inheritance */
    .enterprise-card input,
    .enterprise-card button,
    .enterprise-card [data-testid="stButton"],
    .enterprise-card [data-testid="stDownloadButton"],
    .enterprise-card [data-testid="stNumberInput"] {{
        background-color: {colors["input_bg"]} !important;
    }}
    
    /* Score badges */
    .score-high {{
        color: {colors["score_high"]};
        font-weight: 700;
        font-size: 1.2rem;
    }}
    
    .score-medium {{
        color: {colors["score_medium"]};
        font-weight: 700;
        font-size: 1.2rem;
    }}
    
    .score-low {{
        color: {colors["score_low"]};
        font-weight: 700;
        font-size: 1.2rem;
    }}

    
    /* Multiselect - professional styling to match theme */
    .stMultiSelect > div > div {{
        background-color: {colors["multiselect_bg"]} !important;
        border: 1px solid {colors["multiselect_border"]} !important;
        border-radius: 6px;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }}
    
    /* Multiselect tags container */
    .stMultiSelect [data-baseweb="select"] > div,
    .stMultiSelect [data-baseweb="select"] > div > div {{
        background-color: {colors["multiselect_bg"]} !important;
        color: {colors["multiselect_text"]} !important;
    }}
    
    /* Multiselect dropdown arrow - theme-aware */
    .stMultiSelect svg,
    .stMultiSelect [data-baseweb="select"] svg {{
        fill: {colors["icon_color"]} !important;
        color: {colors["icon_color"]} !important;
        opacity: 1 !important;
    }}
    
    /* Multiselect label */
    .stMultiSelect label {{
        color: {colors["text_primary"]} !important;
    }}
    
    /* Selected items (tags/chips) - dark background with white text */
    .stMultiSelect [data-baseweb="tag"],
    .stMultiSelect [data-baseweb="tag"] * {{
        background-color: #111827 !important;
        color: white !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 4px 8px !important;
        font-size: 0.875rem !important;
        font-weight: 500 !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }}
    
    .stMultiSelect [data-baseweb="tag"]:hover {{
        background-color: #1f2937 !important;
    }}
    
    /* Remove button (X) in tags */
    .stMultiSelect [data-baseweb="tag"] [role="button"],
    .stMultiSelect [data-baseweb="tag"] button,
    .stMultiSelect [data-baseweb="tag"] svg {{
        color: white !important;
        fill: white !important;
        opacity: 0.9 !important;
    }}
    
    .stMultiSelect [data-baseweb="tag"] [role="button"]:hover,
    .stMultiSelect [data-baseweb="tag"] button:hover {{
        opacity: 1 !important;
        background-color: rgba(255, 255, 255, 0.2) !important;
        border-radius: 3px !important;
    }}
    
    /* Alternative selectors for multiselect tags */
    .stMultiSelect span[data-testid="stMarkdownContainer"] span,
    .stMultiSelect div[style*="background"] {{
        background-color: #111827 !important;
        color: white !important;
    }}
    
    /* Target any chip-like elements in multiselect */
    .stMultiSelect > div > div > div > div[style*="rgb"] {{
        background-color: #111827 !important;
        color: white !important;
    }}
    
    /* Ensure no white backgrounds inside chips */
    .stMultiSelect [data-baseweb="tag"] span,
    .stMultiSelect [data-baseweb="tag"] div,
    .stMultiSelect [data-baseweb="tag"] > * {{
        background-color: transparent !important;
        color: white !important;
    }}
    
    /* Multiselect dropdown */
    .stMultiSelect [data-baseweb="select"] {{
        background-color: {colors["multiselect_bg"]} !important;
        color: {colors["multiselect_text"]} !important;
        border: 1px solid {colors["multiselect_border"]} !important;
        border-radius: 6px !important;
    }}
    
    /* Multiselect input */
    .stMultiSelect input {{
        background-color: {colors["multiselect_bg"]} !important;
        color: {colors["multiselect_text"]} !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
    }}
    
    
    /* Style for selected option chips/tags - dark background with white text */
    div[data-baseweb="select"] [data-baseweb="tag"],
    div[data-baseweb="select"] span[style*="background-color: rgb"],
    .stMultiSelect div[style*="background-color: rgb(255"] {{
        background-color: #111827 !important;
        color: white !important;
        border-color: #111827 !important;
    }}
    
    /* Ensure chip inner elements have no white backgrounds */
    div[data-baseweb="select"] [data-baseweb="tag"] *,
    div[data-baseweb="select"] [data-baseweb="tag"] span,
    div[data-baseweb="select"] [data-baseweb="tag"] div {{
        background-color: transparent !important;
        color: white !important;
    }}

    /* ============================================
       DROPDOWN OPTIONS MENU
       ============================================ */
    
    /* Selectbox dropdown menu/popover */
    div[data-baseweb="popover"] {{
        background-color: {colors["input_bg"]} !important;
        border: 1px solid {colors["input_border"]} !important;
        border-radius: 6px !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1) !important;
    }}
    
    /* Dropdown option items */
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] li,
    div[data-baseweb="popover"] [role="option"] {{
        background-color: {colors["input_bg"]} !important;
        color: {colors["input_text"]} !important;
    }}
    
    /* Dropdown option hover state */
    div[data-baseweb="popover"] [role="option"]:hover,
    div[data-baseweb="popover"] li:hover,
    div[data-baseweb="popover"] [role="listbox"] li:hover {{
        background-color: {colors["surface"]} !important;
        color: {colors["text_primary"]} !important;
    }}
    
    /* Dropdown option hover state text */
    div[data-baseweb="popover"] [role="option"]:hover *,
    div[data-baseweb="popover"] li:hover *,
    div[data-baseweb="popover"] [role="listbox"] li:hover * {{
        color: {colors["text_primary"]} !important;
    }}
    
    /* Dropdown option selected state */
    div[data-baseweb="popover"] [role="option"][aria-selected="true"],
    div[data-baseweb="popover"] li[aria-selected="true"],
    div[data-baseweb="popover"] [role="listbox"] li[aria-selected="true"],
    div[data-baseweb="popover"] [role="option"][aria-selected="true"] *,
    div[data-baseweb="popover"] li[aria-selected="true"] *,
    div[data-baseweb="popover"] [role="listbox"] li[aria-selected="true"] * {{
        background-color: {colors["accent"]} !important;
        color: white !important;
    }}
    
    /* Multiselect dropdown menu */
    .stMultiSelect div[data-baseweb="popover"],
    .stMultiSelect div[data-baseweb="popover"] ul,
    .stMultiSelect div[data-baseweb="popover"] li {{
        background-color: {colors["input_bg"]} !important;
        color: {colors["input_text"]} !important;
        border: 1px solid {colors["input_border"]} !important;
    }}
    
    /* Multiselect option hover */
    .stMultiSelect div[data-baseweb="popover"] [role="option"]:hover {{
        background-color: {colors["surface"]} !important;
        color: {colors["text_primary"]} !important;
    }}
    
    /* Multiselect option selected/checked */
    .stMultiSelect div[data-baseweb="popover"] [role="option"][aria-selected="true"],
    .stMultiSelect div[data-baseweb="popover"] [role="option"][aria-selected="true"] * {{
        background-color: {colors["accent"]} !important;
        color: white !important;
    }}
    
    section[data-testid="stSidebar"] {{
    background-color: #f1f5f9 !important;
    border-right: 1px solid #e5e7eb !important;
    box-shadow: 4px 0 12px rgba(0, 0, 0, 0.06) !important;
   }}

    
    /* Sidebar text */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {{
        color: {colors["text_primary"]} !important;
    }}
    
    /* Sidebar expander content */
    [data-testid="stSidebar"] .streamlit-expanderContent {{
        background-color: {colors["expander_content_bg"]} !important;
        color: {colors["text_primary"]} !important;
    }}
    
    /* ============================================
       ADDITIONAL FIXES
       ============================================ */
    
    /* Result sections and cards - ensure readable text in light mode */
    [data-testid="stVerticalBlock"],
    [data-testid="stHorizontalBlock"],
    [data-testid="stMarkdownContainer"],
    [class*="result"],
    [class*="candidate"],
    [class*="ranking"] {{
        background-color: {colors["app_bg"]} !important;
        color: {colors["text_primary"]} !important;
    }}
    
    [data-testid="stVerticalBlock"] *,
    [data-testid="stHorizontalBlock"] *,
    [data-testid="stMarkdownContainer"] * {{
        color: {colors["text_primary"]} !important;
    }}
    
    /* Download buttons and action buttons */
    [data-testid="stDownloadButton"] > button,
    [data-testid="stDownloadButton"] > button *,
    a[download],
    a[href*="download"] {{
        background-color: {colors["accent"]} !important;
        color: white !important;
    }}
    
    /* Number input */
    .stNumberInput > div > div > input {{
        background-color: {colors["input_bg"]} !important;
        color: {colors["input_text"]} !important;
        border: 1px solid {colors["input_border"]} !important;
    }}
    
    /* Number input label - ensure visibility */
    .stNumberInput label,
    .stNumberInput [data-testid="stWidgetLabel"],
    .stNumberInput [data-testid="stWidgetLabel"] * {{
        color: {colors["text_primary"]} !important;
        background-color: transparent !important;
        background: transparent !important;
    }}
    
    /* Number input container - remove white boxes */
    .stNumberInput > div,
    .stNumberInput > div > div {{
        background-color: transparent !important;
        background: transparent !important;
    }}
    
    /* Number input on dark backgrounds - white text */
    [style*="background"][style*="#0f"] .stNumberInput label,
    [style*="background"][style*="#1a"] .stNumberInput label,
    [style*="background"][style*="#1e"] .stNumberInput label,
    [style*="background-color"][style*="#0f"] .stNumberInput label,
    [style*="background-color"][style*="#1a"] .stNumberInput label,
    [style*="background-color"][style*="#1e"] .stNumberInput label {{
        color: white !important;
    }}
    
    /* File uploader text */
    [data-testid="stFileUploader"] label,
    [data-testid="stFileUploader"] p,
    [data-testid="stFileUploader"] span,
    [data-testid="stFileUploader"] div,
    [data-testid="stFileUploader"] button,
    [data-testid="stFileUploader"] button * {{
        color: {colors["text_primary"]} !important;
        background-color: transparent !important;
    }}
    
    /* File uploader helper text */
    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] [class*="caption"] {{
        color: {colors["text_secondary"]} !important;
    }}
    
    /* Result sections and cards - ensure readable text in light mode */
    [data-testid="stVerticalBlock"],
    [data-testid="stHorizontalBlock"],
    [data-testid="stMarkdownContainer"],
    [class*="result"],
    [class*="candidate"],
    [class*="ranking"] {{
        background-color: {colors["app_bg"]} !important;
        color: {colors["text_primary"]} !important;
    }}
    
    [data-testid="stVerticalBlock"] *,
    [data-testid="stHorizontalBlock"] *,
    [data-testid="stMarkdownContainer"] * {{
        color: {colors["text_primary"]} !important;
    }}
    
    /* ============================================
       TOOLTIP STYLING (GLOBAL FIX)
       ============================================ */
    
    /* BaseWeb tooltip container - comprehensive selectors */
    div[data-baseweb="tooltip"],
    [data-baseweb="tooltip"],
    [data-baseweb="popover"][role="tooltip"],
    div[role="tooltip"],
    [role="tooltip"] {{
        background-color: {colors["tooltip_bg"]} !important;
        color: {colors["tooltip_text"]} !important;
        border: 1px solid {colors["border"]} !important;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2) !important;
    }}
    
    /* Tooltip text content - all nested elements */
    div[data-baseweb="tooltip"] *,
    [data-baseweb="tooltip"] *,
    [data-baseweb="popover"][role="tooltip"] *,
    div[role="tooltip"] *,
    [role="tooltip"] *,
    div[data-baseweb="tooltip"] span,
    [data-baseweb="tooltip"] span,
    [data-baseweb="popover"][role="tooltip"] span,
    div[role="tooltip"] span,
    [role="tooltip"] span,
    div[data-baseweb="tooltip"] p,
    [data-baseweb="tooltip"] p,
    [data-baseweb="popover"][role="tooltip"] p,
    div[role="tooltip"] p,
    [role="tooltip"] p {{
        color: {colors["tooltip_text"]} !important;
        background-color: transparent !important;
    }}
    
    /* Streamlit-specific tooltip selectors */
    [data-testid="stTooltip"],
    [data-testid="stTooltip"] *,
    [data-testid="stTooltip"] span,
    [data-testid="stTooltip"] p {{
        color: {colors["tooltip_text"]} !important;
        background-color: {colors["tooltip_bg"]} !important;
    }}
    
    /* Tooltip arrow/pointer styling */
    div[data-baseweb="tooltip"]::before,
    [data-baseweb="tooltip"]::before,
    [data-baseweb="popover"][role="tooltip"]::before,
    div[role="tooltip"]::before,
    [role="tooltip"]::before {{
        border-color: {colors["border"]} transparent transparent transparent !important;
    }}
    
    /* Alternative tooltip selectors for BaseWeb classes */
    [class*="tooltip"],
    [class*="Tooltip"],
    [class*="Popover"][role="tooltip"] {{
        background-color: {colors["tooltip_bg"]} !important;
        color: {colors["tooltip_text"]} !important;
    }}
    
    [class*="tooltip"] *,
    [class*="Tooltip"] *,
    [class*="Popover"][role="tooltip"] * {{
        color: {colors["text_primary"]} !important;
    }}
    
    /* Ensure tooltip has high z-index and is visible */
    div[data-baseweb="tooltip"],
    [data-baseweb="tooltip"],
    [role="tooltip"] {{
        z-index: 9999 !important;
        opacity: 1 !important;
    }}
    
    /* Success toast animation - professional and subtle */
    .stSuccess {{
        animation: slideInDown 0.3s ease-out;
        position: relative;
        z-index: 999;
    }}
    
    @keyframes slideInDown {{
        from {{
            transform: translateY(-20px);
            opacity: 0;
        }}
        to {{
            transform: translateY(0);
            opacity: 1;
        }}
    }}
    
    {'''
    /* ============================================
       LIGHT MODE ONLY FIXES
       ============================================ */
    
    /* TASK 1: Fix 'Other Ranked Candidates' header bar (Light Mode Only) */
    /* Target the container with toggle button */
    [data-testid="stVerticalBlock"]:has(button[key*="toggle_other_candidates"]),
    [data-testid="stHorizontalBlock"]:has(button[key*="toggle_other_candidates"]) {
        background-color: #F9FAFB !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 6px;
        padding: 1rem;
    }
    
    [data-testid="stVerticalBlock"]:has(button[key*="toggle_other_candidates"]) *,
    [data-testid="stHorizontalBlock"]:has(button[key*="toggle_other_candidates"]) *,
    [data-testid="stVerticalBlock"]:has(button[key*="toggle_other_candidates"]) h3,
    [data-testid="stHorizontalBlock"]:has(button[key*="toggle_other_candidates"]) h3 {
        color: #111827 !important;
    }
    
    /* Icons in Other Ranked Candidates section */
    button[key*="toggle_other_candidates"] svg,
    [data-testid="stVerticalBlock"]:has(button[key*="toggle_other_candidates"]) svg,
    [data-testid="stHorizontalBlock"]:has(button[key*="toggle_other_candidates"]) svg {
        fill: #374151 !important;
        color: #374151 !important;
        stroke: #374151 !important;
    }
    
    /* TASK 2: Fix Matched Skills / Missing Skills boxes (Light Mode Only) */
    /* Outlined cards for st.info and st.warning in results section */
    [data-testid="stExpander"] .stInfo,
    [data-testid="stExpander"] .stWarning {
        background-color: #FFFFFF !important;
        border-radius: 6px;
        padding: 1rem;
        color: #111827 !important;
    }
    
    [data-testid="stExpander"] .stInfo {
        border: 1px solid #2563EB !important;
        border-left: 1px solid #2563EB !important;
    }
    
    [data-testid="stExpander"] .stWarning {
        border: 1px solid #F59E0B !important;
        border-left: 1px solid #F59E0B !important;
    }
    
    [data-testid="stExpander"] .stInfo *,
    [data-testid="stExpander"] .stWarning * {
        background-color: transparent !important;
        color: #111827 !important;
    }
    
    
    
    /* TASK 4: Fix Candidate expander headers (Light Mode Only) */
    /* Candidate result expander headers - light background */
    /* Target expanders that contain candidate info (not sidebar expanders) */
    [data-testid="stExpander"]:not([data-testid="stSidebar"] [data-testid="stExpander"]) .streamlit-expanderHeader {
        background-color: #FFFFFF !important;
        border: 1px solid #E5E7EB !important;
        color: #111827 !important;
        border-radius: 6px;
        padding: 1rem;
        font-weight: 600;
    }
    
    [data-testid="stExpander"]:not([data-testid="stSidebar"] [data-testid="stExpander"]) .streamlit-expanderHeader * {
        background-color: transparent !important;
        color: #111827 !important;
    }
    
    /* Candidate expander chevron icon */
    [data-testid="stExpander"]:not([data-testid="stSidebar"] [data-testid="stExpander"]) .streamlit-expanderHeader svg,
    [data-testid="stExpander"]:not([data-testid="stSidebar"] [data-testid="stExpander"]) [data-testid="stExpanderToggleIcon"] {
        fill: #374151 !important;
        color: #374151 !important;
        stroke: #374151 !important;
    }

    /* Fix light mode icon (sun) */
section[data-testid="stSidebar"] img {
    background: transparent !important;
    border-radius: 8px !important;
}

    ''' if theme == "light" else ""}
</style>
"""


# Apply theme-based CSS
current_css = get_theme_css(st.session_state.theme)
st.markdown(current_css, unsafe_allow_html=True)


if st.session_state.theme == "light":
    st.markdown("""
    <style>

    /* ===============================
       1. SIDEBAR OPEN / CLOSE ARROW
       =============================== */

    /* OPEN sidebar button (>>) */
    button[data-testid="collapsedControl"] {
        background: #ffffff !important;
        border: none !important;
        box-shadow: none !important;
    }

    

    /* CLOSE sidebar button (<<) */
    button[data-testid="stSidebarCollapseButton"] svg,
    button[data-testid="stSidebarCollapseButton"] svg path {
        fill: #111827 !important;
        stroke: #111827 !important;
        opacity: 1 !important;
    }

    /* ===============================
       2. OTHER RANKED CANDIDATES TABLE
       =============================== */

    /* Table wrapper */
    [data-testid="stDataFrame"] {
        background-color: #ffffff !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 8px !important;
    }

    /* Header */
    [data-testid="stDataFrame"] thead th {
        background-color: #f9fafb !important;
        color: #111827 !important;
        border-bottom: 1px solid #e5e7eb !important;
    }

    /* Rows */
    [data-testid="stDataFrame"] tbody td {
        background-color: #ffffff !important;
        color: #111827 !important;
        border-bottom: 1px solid #e5e7eb !important;
    }

    /* Kill dark BaseWeb layers */
    [data-testid="stDataFrame"] * {
        background-color: transparent !important;
        color: #111827 !important;
    }

    /* Hover */
    [data-testid="stDataFrame"] tbody tr:hover td {
        background-color: #f3f4f6 !important;
    }

    



/* =========================================
   LIGHT MODE – DATAFRAME FULLSCREEN (MODAL)
   ========================================= */

/* Fullscreen modal background */
[data-baseweb="modal"] {
    background-color: rgba(255, 255, 255, 0.98) !important;
}

/* Modal content wrapper */
[data-baseweb="modal"] [data-testid="stDataFrame"] {
    background-color: #ffffff !important;
    border-radius: 8px !important;
}

/* Table header in fullscreen */
[data-baseweb="modal"] thead tr th {
    background-color: #f9fafb !important;
    color: #111827 !important;
    border-bottom: 1px solid #e5e7eb !important;
}

/* Table rows in fullscreen */
[data-baseweb="modal"] tbody tr td {
    background-color: #ffffff !important;
    color: #111827 !important;
    border-bottom: 1px solid #e5e7eb !important;
}

/* Remove dark base layers */
[data-baseweb="modal"] * {
    background-color: transparent !important;
    color: #111827 !important;
}

/* Hover effect */
[data-baseweb="modal"] tbody tr:hover td {
    background-color: #f3f4f6 !important;
}

/* =========================================
   LIGHT MODE – SIDEBAR TOGGLE ARROW VISIBILITY
   ========================================= */

/* Sidebar toggle button container */
button[data-testid="collapsedControl"] {
    background-color: #ffffff !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 8px !important;
}

/* Arrow icon (OPEN sidebar >>) */
button[data-testid="collapsedControl"] svg {
    fill: #111827 !important;      /* dark icon */
    color: #111827 !important;
    opacity: 1 !important;
}

/* Hover state */
button[data-testid="collapsedControl"]:hover {
    background-color: #f9fafb !important;
}



/* =========================================
   LIGHT MODE – SIDEBAR OPEN (>>) BUTTON FIX
   ========================================= */

/* Floating sidebar open button */
button[data-testid="collapsedControl"] {
    background-color: #ffffff !important;
    border: 1px solid #d1d5db !important;
    border-radius: 8px !important;
    box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08) !important;
    opacity: 1 !important;
}

/* Arrow icon inside the button */
button[data-testid="collapsedControl"] svg {
    fill: #111827 !important;
    stroke: #111827 !important;
    color: #111827 !important;
    opacity: 1 !important;
}

/* Hover state */
button[data-testid="collapsedControl"]:hover {
    background-color: #f9fafb !important;
}


/* =========================================
   LIGHT MODE – SIDEBAR VISUAL SEPARATION
   ========================================= */

/* Sidebar background */
section[data-testid="stSidebar"] {
    background-color: #f8fafc !important;   /* slightly off-white */
    border-right: 1px solid #e5e7eb !important;
}

/* Inner sidebar content */
section[data-testid="stSidebar"] > div {
    background-color: #f8fafc !important;
}

/* Add subtle depth so it doesn't merge */
section[data-testid="stSidebar"] {
    box-shadow: 2px 0 6px rgba(0, 0, 0, 0.04) !important;
}

/* Sidebar text */
section[data-testid="stSidebar"] * {
    color: #111827 !important;
}

/* Sidebar buttons/cards */
section[data-testid="stSidebar"] button,
section[data-testid="stSidebar"] [role="button"] {
    background-color: #ffffff !important;
    border: 1px solid #e5e7eb !important;
}


    /* ===============================
       FIX EXPANDER HEADER – LIGHT MODE
       =============================== */

    [data-testid="stExpander"] summary {
        background-color: #ffffff !important;
        color: #111827 !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 6px !important;
        padding: 12px 16px !important;
        font-weight: 600 !important;
    }

    /* Remove dark inner bars */
    [data-testid="stExpander"] summary * {
        background: transparent !important;
        color: #111827 !important;
    }

    /* Arrow icon */
    [data-testid="stExpander"] svg {
        fill: #374151 !important;
        color: #374151 !important;
    }

    /* Hover */
    [data-testid="stExpander"] summary:hover {
        background-color: #f9fafb !important;
    }

    /* ===============================
       FIX OTHER RANKED CANDIDATES TABLE
       =============================== */

    section[data-testid="stDataFrame"] {
        background-color: #ffffff !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 8px !important;
    }

    section[data-testid="stDataFrame"] * {
        color: #111827 !important;
        background-color: transparent !important;
    }


    /* ========= SIDEBAR BACKGROUND ========= */
    section[data-testid="stSidebar"] {
        background-color: #f8fafc !important;
        border-right: 1px solid #e5e7eb !important;
        box-shadow: 2px 0 6px rgba(0,0,0,0.05) !important;
    }

  
# =====================================================
# LIGHT MODE – FIX ALL INFO / WARNING INNER WHITE BOXES
# =====================================================


    /* ================================
       BASE ALERT CONTAINERS
       ================================ */
    .stAlert {
        border-radius: 8px !important;
        box-shadow: none !important;
    }

    /* Selected / Matched Skills (Info) */
    .stAlert.stInfo {
        background-color: #dbeafe !important;  /* light blue */
        border: none !important;
    }

    /* Missing Skills (Warning) */
    .stAlert.stWarning {
        background-color: #fef3c7 !important;  /* light yellow */
        border: 1px solid #f59e0b !important;
    }

     /* =========================================
       4. TEXT CURSOR / CARET VISIBILITY
       ========================================= */
    
    /* Text input caret */
    .stTextInput input,
    .stTextInput input[type="text"],
    .stTextInput input[type="password"],
    .stTextArea textarea {
        caret-color: #000000 !important;
    }
    
    /* Number input caret */
    .stNumberInput input,
    .stNumberInput input[type="number"] {
        caret-color: #000000 !important;
    }
    
    /* Chat input caret (if exists) */
    .stChatInput input,
    .stChatInput textarea {
        caret-color: #000000 !important;
    }
    
    /* Expander content inputs */
    [data-testid="stExpander"] .stTextInput input,
    [data-testid="stExpander"] .stTextArea textarea {
        caret-color: #000000 !important;
    }

    

    /* ================================
       REMOVE ALL INNER WHITE LAYERS
       ================================ */
    .stAlert > div,
    .stAlert > div > div,
    .stAlert > div > div > div,
    .stAlert .stMarkdown,
    .stAlert .stMarkdownContainer {
        background-color: transparent !important;
        padding: 0 !important;
        margin: 0 !important;
        box-shadow: none !important;
    }

    /* ================================
       TEXT VISIBILITY
       ================================ */
    .stAlert p,
    .stAlert span,
    .stAlert div {
        background: transparent !important;
        color: #111827 !important;
    }

   

    /* =====================================================
       LIGHT MODE FIXES REMOVE DARK BASEWEB LAYERS
       ===================================================== */
    
    /* Candidate expander headers (normal + hover) */
    [data-testid="stExpander"] .streamlit-expanderHeader {
        background-color: #ffffff !important;
        color: #111827 !important;
        border: 1px solid #e5e7eb !important;
        border-radius: 6px !important;
    }

    [data-testid="stExpander"] .streamlit-expanderHeader > div {
        background-color: transparent !important;
    }

    [data-testid="stExpander"] .streamlit-expanderHeader * {
    background: transparent !important;
    color: #111827 !important;
    }

    /* Number input box */
    .stNumberInput input {
        background-color: #ffffff !important;
        color: #111827 !important;
        border: 1px solid #d1d5db !important;
    }

    /* Number input + / - buttons */
    .stNumberInput button,
    .stNumberInput button * {
        background-color: transparent !important;
        color: #374151 !important;
    }

    /* “Showing additional candidates…” info text */
    [data-testid="stMarkdownContainer"] p {
        background-color: transparent !important;
        color: #111827 !important;
    }

    /* Remove any remaining dark containers */
    [data-testid="stVerticalBlock"],
    [data-testid="stHorizontalBlock"] {
        background-color: transparent !important;
    }
     
    /* =====================================================
   LIGHT MODE – FORCE REMOVE DARK BASEWEB CONTAINERS
   ===================================================== */

/* 1️⃣ Candidate expander outer header */
[data-testid="stExpander"] .streamlit-expanderHeader {
    background-color: #ffffff !important;
    border: 1px solid #e5e7eb !important;
    color: #111827 !important;
}

/* 2️⃣ REMOVE inner dark BaseWeb bar */
[data-testid="stExpander"] .streamlit-expanderHeader > div,
[data-testid="stExpander"] .streamlit-expanderHeader > div > div {
    background-color: transparent !important;
}

/* 3️⃣ Text inside expander header */
[data-testid="stExpander"] .streamlit-expanderHeader *,
[data-testid="stExpander"] .streamlit-expanderHeader span {
    color: #111827 !important;
    background: transparent !important;
}

/* 4️⃣ Fix hover (prevent dark return) */
[data-testid="stExpander"] .streamlit-expanderHeader:hover {
    background-color: #f9fafb !important;
}

/* 5️⃣ “Showing additional candidates…” text block */
[data-testid="stMarkdownContainer"] {
    background-color: transparent !important;
}

[data-testid="stMarkdownContainer"] * {
    color: #111827 !important;
}

/* 6️⃣ Remove any leftover dark ranking containers */
[class*="ranking"],
[class*="candidate"],
[data-testid="stVerticalBlock"] > div {
    background-color: transparent !important;
}

/* =====================================================
   LIGHT MODE – FORCE OVERRIDE INLINE DARK BACKGROUNDS
   ===================================================== */

/* Candidate expander header – FORCE white */
[data-testid="stExpander"] .streamlit-expanderHeader,
[data-testid="stExpander"] .streamlit-expanderHeader[style],
[data-testid="stExpander"] .streamlit-expanderHeader > div[style] {
    background-color: #ffffff !important;
    color: #111827 !important;
    border: 1px solid #e5e7eb !important;
}

/* Kill ALL inline dark backgrounds inside header */
[data-testid="stExpander"] .streamlit-expanderHeader *[style*="background"] {
    background-color: transparent !important;
}

/* Text inside header */
[data-testid="stExpander"] .streamlit-expanderHeader *,
[data-testid="stExpander"] .streamlit-expanderHeader span {
    color: #111827 !important;
}

/* Prevent hover from being the only fix */
[data-testid="stExpander"] .streamlit-expanderHeader:hover,
[data-testid="stExpander"] .streamlit-expanderHeader:hover * {
    background-color: #ffffff !important;
    color: #111827 !important;
}

/* Other Ranked Candidates header block */
[data-testid="stVerticalBlock"] h3,
[data-testid="stVerticalBlock"] h3 + div {
    background-color: transparent !important;
    color: #111827 !important;
}

/* =====================================================
   FINAL FIX – BASEWEB EXPANDER BUTTON (BLACK BAR)
   ===================================================== */

/* Expander toggle button itself */
button[data-testid="stExpanderToggle"] {
    background-color: #f9fafb !important;
    color: #111827 !important;
    border: 1px solid #e5e7eb !important;
    border-radius: 6px !important;
}

/* Inner BaseWeb container inside the button */
button[data-testid="stExpanderToggle"] > div,
button[data-testid="stExpanderToggle"] div[style] {
    background-color: transparent !important;
}

/* Text inside expander button */
button[data-testid="stExpanderToggle"] span,
button[data-testid="stExpanderToggle"] p,
button[data-testid="stExpanderToggle"] div {
    color: #111827 !important;
    background: transparent !important;
}

/* Prevent hover-only behavior */
button[data-testid="stExpanderToggle"]:hover {
    background-color: #f3f4f6 !important;
}

/* Chevron icon */
button[data-testid="stExpanderToggle"] svg {
    color: #374151 !important;
    fill: #374151 !important;
}

.safe-expander summary {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    padding: 12px 16px;
    font-weight: 600;
    color: #111827;
    cursor: pointer;
    list-style: none;
}

/* Arrow for safe expander */
.safe-expander summary {
    position: relative;
    padding-left: 28px;
}

/* Arrow icon */
.safe-expander summary::before {
    content: "▸";
    position: absolute;
    left: 10px;
    top: 50%;
    transform: translateY(-50%);
    font-size: 14px;
    color: #374151;
    transition: transform 0.2s ease;
}

/* Rotate arrow when open */
.safe-expander details[open] summary::before {
    transform: translateY(-50%) rotate(90deg);
}


.safe-expander summary::-webkit-details-marker {
    display: none;
}

.safe-expander details {
    margin-bottom: 1rem;
}

.safe-expander details[open] summary {
    background: #f9fafb;
}

    </style>
    """, unsafe_allow_html=True) 


# ============================================
# AUTHENTICATION PAGE FUNCTIONS
# ============================================

def get_auth_theme_css() -> str:
    """Get CSS for authentication pages matching main app theme"""
    colors = THEME_CONFIG.get(st.session_state.get("theme", "dark"), THEME_CONFIG["dark"])
    
    return f"""
    <style>
        /* Import professional font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        
        /* Main background */
        .stApp {{
            background: {colors["app_bg"]};
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }}

        /* Headers */
        h1, h2, h3 {{
            color: {colors["text_primary"]} !important;
            font-weight: 600;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }}
        
        /* Body text */
        p, div, span {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            color: {colors["text_primary"]};
        }}
        
        /* Labels */
        label {{
            color: {colors["text_primary"]} !important;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }}
        
        /* Text inputs */
        .stTextInput > div > div > input {{
            background-color: {colors["input_bg"]};
            color: {colors["input_text"]};
            border: 1px solid {colors["input_border"]};
            border-radius: 6px;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }}
        
        /* Buttons */
        .stButton > button {{
            background: {colors["accent"]} !important;
            color: white !important;
            border: none;
            border-radius: 6px;
            padding: 0.75rem 2rem;
            font-weight: 600;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }}
        
        .stButton > button:hover {{
            background: {colors["accent_hover"]} !important;
        }}
    </style>
    """


def login_page():
    """Login page"""
    # Render global header with logos
    render_global_header()
    
    # Hide sidebar completely
    st.markdown(
        '''
        <style>
            [data-testid="stSidebar"] { display: none; }
            [data-testid="stSidebarNav"] { display: none; }
        </style>
        ''',
        unsafe_allow_html=True
    )
    
    # Apply auth theme CSS
    auth_css = get_auth_theme_css()
    st.markdown(auth_css, unsafe_allow_html=True)
    
    # Centered layout
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>HR AI Agent</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #9aa0a6;'>Enterprise Talent Intelligence Platform</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        with st.form("login_form"):
            st.markdown("### Sign In")
            
            email = st.text_input("Email", placeholder="your.email@company.com")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                login_button = st.form_submit_button("Login", use_container_width=True, type="primary")
            with col_btn2:
                forgot_button = st.form_submit_button("Forgot Password?", use_container_width=True)
            
            if forgot_button:
                st.session_state.page = "forgot"
                st.rerun()
            
            if login_button:
                if not email or not password:
                    st.error("Please enter both email and password")
                else:
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/auth/login",
                            json={"email": email, "password": password},
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            if not response.text or not response.text.strip():
                                st.error("Login failed. Empty response from server.")
                            else:
                                try:
                                    data = response.json()
                                    if data.get("success"):
                                        # Clear any query params (e.g., reset token)
                                        try:
                                            st.query_params.clear()
                                        except Exception:
                                            pass
                                        st.session_state.authenticated = True
                                        st.session_state.user_email = data.get("user_email", email)
                                        st.session_state.page = "main"
                                        st.session_state.reset_completed = False  # Clear reset flag
                                        st.rerun()
                                    else:
                                        st.error("Invalid email or password")
                                except Exception:
                                    st.error("Login failed. Invalid server response.")
                        else:
                            st.error("Invalid email or password")
                    except requests.exceptions.ConnectionError:
                        st.error("Cannot connect to server. Please ensure the backend is running.")
                    except requests.exceptions.Timeout:
                        st.error("Request timed out. Please try again.")
                    except Exception:
                        st.error("Invalid email or password")
        
        st.markdown("---")
        st.markdown("<p style='text-align: center;'>Don't have an account?</p>", unsafe_allow_html=True)
        if st.button("Create Account", use_container_width=True):
            st.session_state.page = "signup"
            st.rerun()


def signup_page():
    """Signup page"""
    # Render global header with logos
    render_global_header()
    
    # Hide sidebar completely (but allow page navigation to show)
    st.markdown(
        '''
        <style>
            [data-testid="stSidebar"] { display: none; }
        </style>
        ''',
        unsafe_allow_html=True
    )
    
    # Apply auth theme CSS
    auth_css = get_auth_theme_css()
    st.markdown(auth_css, unsafe_allow_html=True)
    
    # Centered layout
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>Create Account</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #9aa0a6;'>Join HR AI Agent Platform</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        with st.form("signup_form"):
            st.markdown("### Register")
            
            col_name1, col_name2 = st.columns(2)
            with col_name1:
                first_name = st.text_input("First Name", placeholder="John")
            with col_name2:
                last_name = st.text_input("Last Name", placeholder="Doe")
            
            email = st.text_input("Email", placeholder="your.email@company.com")
            password = st.text_input("Password", type="password", placeholder="At least 6 characters")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
            
            create_button = st.form_submit_button("Create Account", use_container_width=True, type="primary")
            
            if create_button:
                if not first_name or not last_name or not email:
                    st.error("All fields are required")
                elif password != confirm_password:
                    st.error("Passwords do not match")
                elif not password or len(password) < 6:
                    st.error("Password must be at least 6 characters long")
                else:
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/auth/signup",
                            json={
                                "first_name": first_name,
                                "last_name": last_name,
                                "email": email,
                                "password": password
                            },
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            if not response.text or not response.text.strip():
                                st.success("Account created successfully. Please login.")
                                st.session_state.page = "login"
                                time.sleep(1)
                                st.rerun()
                            else:
                                try:
                                    data = response.json()
                                    if data.get("success"):
                                        st.success("Account created successfully! Redirecting to login...")
                                        st.session_state.page = "login"
                                        time.sleep(1)
                                        st.rerun()
                                    else:
                                        st.error("Account creation failed. Email may already exist.")
                                except Exception:
                                    st.success("Account created successfully. Please login.")
                                    st.session_state.page = "login"
                                    time.sleep(1)
                                    st.rerun()
                        else:
                            st.error("Account creation failed. Email may already exist.")
                    except requests.exceptions.ConnectionError:
                        st.error("Cannot connect to server. Please ensure the backend is running.")
                    except requests.exceptions.Timeout:
                        st.error("Request timed out. Please try again.")
                    except Exception:
                        st.error("Account creation failed. Please try again.")
        
        st.markdown("---")
        st.markdown("<p style='text-align: center;'>Already have an account?</p>", unsafe_allow_html=True)
        if st.button("Log in", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()


def forgot_password_page():
    """Forgot password page"""
    # Render global header with logos
    render_global_header()
    
    # Hide sidebar completely (but allow page navigation to show)
    st.markdown(
        '''
        <style>
            [data-testid="stSidebar"] { display: none; }
        </style>
        ''',
        unsafe_allow_html=True
    )
    
    # Apply auth theme CSS
    auth_css = get_auth_theme_css()
    st.markdown(auth_css, unsafe_allow_html=True)
    
    # Centered layout
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>Forgot Password</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #9aa0a6;'>Enter your email to receive a reset link</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        with st.form("forgot_password_form"):
            st.markdown("### Request Password Reset")
            
            email = st.text_input("Email", placeholder="your.email@company.com")
            
            send_button = st.form_submit_button("Send Reset Link", use_container_width=True, type="primary")
            
            if send_button:
                if not email:
                    st.error("Please enter your email")
                else:
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/auth/forgot-password",
                            json={"email": email},
                            timeout=10
                        )
                        
                        # Always show success message for security
                        st.success("If the email exists, a password reset link has been sent.")
                    except requests.exceptions.ConnectionError:
                        st.error("Cannot connect to server. Please ensure the backend is running.")
                    except requests.exceptions.Timeout:
                        st.error("Request timed out. Please try again.")
                    except Exception:
                        st.success("If the email exists, a password reset link has been sent.")
        
        st.markdown("---")
        if st.button("Back to Login", use_container_width=True):
            st.session_state.page = "login"
            st.rerun()


def reset_password_page(token: str):
    """Reset password page - accessed via token in URL"""
    # Render global header with logos
    render_global_header()
    
    # Hide sidebar completely
    st.markdown(
        '''
        <style>
            [data-testid="stSidebar"] { display: none; }
            [data-testid="stSidebarNav"] { display: none; }
        </style>
        ''',
        unsafe_allow_html=True
    )
    
    # Apply auth theme CSS
    auth_css = get_auth_theme_css()
    st.markdown(auth_css, unsafe_allow_html=True)
    
    # Validate token format first
    if not token or len(token) < 10:
        st.error("Invalid or expired reset link")
        st.markdown("---")
        if st.button("Back to Login", use_container_width=True, key="back_to_login_invalid_token"):
            try:
                st.query_params.clear()
            except Exception:
                pass
            st.session_state.page = "login"
            st.rerun()
        return
    
    # Centered layout
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("<h1 style='text-align: center;'>Reset Password</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #9aa0a6;'>Enter your new password</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        # Token is present and valid format - show reset form
        # Backend will validate token validity and expiry on submit
        with st.form("reset_password_form"):
            st.markdown("### Set New Password")
            
            new_password = st.text_input("New Password", type="password", placeholder="At least 6 characters")
            confirm_password = st.text_input("Confirm New Password", type="password", placeholder="Re-enter password")
            
            reset_button = st.form_submit_button("Reset Password", use_container_width=True, type="primary")
            
            if reset_button:
                # Frontend validation
                if not new_password or len(new_password) < 6:
                    st.error("Password must be at least 6 characters long")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    # Call backend API to validate token and reset password
                    try:
                        response = requests.post(
                            f"{API_BASE_URL}/auth/reset-password",
                            json={"token": token, "new_password": new_password},
                            timeout=10
                        )
                        
                        if response.status_code == 200:
                            # Success - clear query params and redirect to login page
                            try:
                                st.query_params.clear()
                            except Exception:
                                pass
                            st.session_state.authenticated = False
                            st.session_state.page = "login"
                            st.session_state.reset_completed = True
                            st.success("Your password has been reset successfully. Redirecting to login...")
                            st.rerun()
                        else:
                            # Token is invalid or expired - show error and redirect to login
                            try:
                                error_data = response.json()
                                error_msg = error_data.get("detail", "Invalid or expired reset link")
                            except Exception:
                                error_msg = "Invalid or expired reset link"
                            st.error(error_msg)
                            st.markdown("---")
                            if st.button("Back to Login", use_container_width=True, key="back_to_login_after_error"):
                                try:
                                    st.query_params.clear()
                                except Exception:
                                    pass
                                st.session_state.page = "login"
                                st.rerun()
                                
                    except requests.exceptions.ConnectionError:
                        st.error("Cannot connect to server. Please ensure the backend is running.")
                    except requests.exceptions.Timeout:
                        st.error("Request timed out. Please try again.")
                    except Exception:
                        st.error("Invalid or expired reset link")
                        st.markdown("---")
                        if st.button("Back to Login", use_container_width=True, key="back_to_login_after_exception"):
                            try:
                                st.query_params.clear()
                            except Exception:
                                pass
                            st.session_state.page = "login"
                            st.rerun()
        
        st.markdown("---")
        if st.button("Back to Login", use_container_width=True, key="back_to_login_reset"):
            try:
                st.query_params.clear()
            except Exception:
                pass
            st.session_state.page = "login"
            st.rerun()

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
    if "theme" not in st.session_state:
        st.session_state.theme = "dark"  # Default theme

def render_global_header():
    """Render global header with SIEI and EY logos - call this on ALL pages"""

    # Logo paths
    siei_logo_path = "assets/siei_logo.png"
    SIEI_LOGO = Path(siei_logo_path)
    
    # Top header bar with left and right branding (ABOVE main title)
    col_left, col_center, col_right = st.columns([3, 4, 3])
    
    with col_left:

        
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
                        theme_colors = get_theme()
                        input_bg = theme_colors["input_bg"]
                        accent = theme_colors["accent"]
                        st.markdown(f'<div style="height:52px;width:52px;background:{input_bg};border-radius:4px;display:flex;align-items:center;justify-content:center;color:{accent};font-size:10px;font-weight:bold;">SIEI</div>', unsafe_allow_html=True)
        with logo_text_col2:
            theme_colors = get_theme()
            accent = theme_colors["accent"]
            text_muted = theme_colors["text_muted"]
            st.markdown(f"""
        <div style="
            font-size: 1.1rem;
            font-weight: 600;
            color: {accent};
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            line-height: 1.1;
            margin-top: 6px;
            margin-left: -16px;
        ">SIEI</div>

        <div style="
            font-size: 0.75rem;
            color: {text_muted};
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            margin-top: 2px;
            white-space: nowrap;
            margin-left: -16px;
        ">Snow IT Expert Institute</div>
    """, unsafe_allow_html=True)
    
    with col_right:

        

        # Right: EY Branding - Logo image using Base64 + HTML (theme-aware)
        ey_logo_path = get_ey_logo_path()
        
        if ey_logo_path and os.path.exists(ey_logo_path):
            ey_base64 = img_to_base64(ey_logo_path)
            st.markdown(
                f"""
                <div style="
                    display:flex;
                    justify-content:flex-end;
                    align-items:flex-start;
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
            # Do nothing if logo not found (NO BOX)
            st.markdown("")


def display_header():
    """Display enterprise header with institute and company branding (for main page)"""
    render_global_header()
    
    # Main title at center - moved slightly upward
    theme_colors = get_theme()
    text_primary = theme_colors["text_primary"]
    text_secondary = theme_colors["text_secondary"]
    st.markdown(f"""
        <div style="text-align: center; padding: 1rem 0 1.5rem 0;">
            <h1 style="color: {text_primary}; font-size: 2.5rem; margin-bottom: 0.5rem; font-weight: 600; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; letter-spacing: -0.02em;">
                HR AI Agent
            </h1>
            <p style="color: {text_secondary}; font-size: 1.1rem; margin-top: 0; font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;">
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
    # Validate all required fields are provided
    if not job_title or not job_title.strip():
        st.error("❌ Job Title is required. Please fill in all required fields (marked with *).")
        return ""
    
    if not experience or not experience.strip():
        st.error("❌ Experience is required. Please fill in all required fields (marked with *).")
        return ""
    
    if not domain or not domain.strip():
        st.error("❌ Domain is required. Please fill in all required fields (marked with *).")
        return ""
    
    if not seniority or not seniority.strip():
        st.error("❌ Seniority Level is required. Please fill in all required fields (marked with *).")
        return ""
    
    if not location or not location.strip():
        st.error("❌ Location is required. Please fill in all required fields (marked with *).")
        return ""
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        st.error("OpenAI API key not found. Please configure OPENAI_API_KEY in environment.")
        return ""
    
    client = OpenAI(api_key=openai_api_key)
    
    # Prepare skills text - use empty string if not provided
    skills_text = key_skills.strip() if key_skills else ""
    
    # Build skills note for prompt (avoid nested f-strings)
    skills_note = f"Note: Must include these key skills: {skills_text}" if skills_text else ""
    skills_rule = f"9. Required Skills must include: {skills_text}" if skills_text else ""
    
    prompt = f"""Generate a professional, enterprise-grade Job Description using the following STRICT STRUCTURE.

The output MUST start with a header section in this exact order:

Job Title: {job_title}
Location: {location}

After the header, include the following sections in order:

Role Summary (2-3 concise paragraphs)

Roles & Responsibilities (bullet points)

Required Skills (bullet points)
{skills_note}

Preferred Skills (bullet points)

Experience & Education Requirements

STRICT RULES (DO NOT VIOLATE):

1. Use the values exactly as provided by the user
2. Do NOT repeat Job Title or Location inside Role Summary
3. Do NOT use placeholders like "Please insert location", "TBD", "Not specified", or similar
4. Do NOT invent or modify experience or location
5. If location is "Remote", show exactly: Location: Remote
6. Experience must be stated exactly as: {experience}
7. Domain must be stated exactly as: {domain}
8. Seniority Level must be stated exactly as: {seniority}
{skills_rule}

Output format:
Plain text only
No markdown
No emojis
No code blocks

Generate the complete job description now following this exact structure:"""

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
        # Validate inputs before processing
        if not jd_text or not jd_text.strip():
            st.error("Please provide a Job Description.")
            return None
        
        if not uploaded_files or len(uploaded_files) == 0:
            st.error("Please upload at least one CV file.")
            return None
        
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
        
        # Validate response is not empty before parsing JSON
        if not response.text or not response.text.strip():
            st.error("Received empty response from server. Please try again.")
            return None
        
        # Parse JSON response with error handling
        try:
            return response.json()
        except ValueError as e:
            st.error(f"Failed to parse server response: {str(e)}")
            logger.error(f"JSON parse error. Response text: {response.text[:500]}")
            return None
    
    except requests.exceptions.RequestException as e:
        st.error(f"Error processing request: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                # Validate response has content before parsing
                if e.response.text and e.response.text.strip():
                    error_detail = e.response.json()
                    st.error(f"Details: {error_detail.get('detail', 'Unknown error')}")
                else:
                    st.error(f"Status Code: {e.response.status_code}")
            except (ValueError, json.JSONDecodeError):
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
        raw_score = candidate["match_score"]
        displayed_score = scale_score(raw_score)
        score_class = (
            "score-high" if displayed_score >= 70
            else "score-medium" if displayed_score >= 50
            else "score-low"
        )
        
        with st.expander(
            f"#{idx} {candidate['candidate_name']} - Match Score: {displayed_score:.1f}%",
            expanded=True
        ):

            # Overall score
            st.markdown(
                f'<p class="{score_class}">Overall Match Score: {displayed_score:.1f}%</p>',
                unsafe_allow_html=True
            )

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
    # ============================================
    # RESET PASSWORD TOKEN CHECK (HIGHEST PRIORITY)
    # ============================================
    # Check for reset token at the VERY TOP, before any page routing
    # This must execute BEFORE page state logic to prevent blank pages
    try:
        token = st.query_params.get("token", "")
    except (AttributeError, Exception):
        token = ""
    
    # If user is logged in, never show reset password page - redirect to main
    if st.session_state.get("authenticated", False):
        if token:
            # Clear token from URL if user is already logged in
            try:
                st.query_params.clear()
            except Exception:
                pass
        # Continue to main page routing below
    
    # Case: Reset link with token (from email) - user must NOT be authenticated
    elif token:
        # Validate token and render reset password page
        reset_password_page(token)
        st.stop()  # Stop execution to prevent further routing


    
    # ============================================
    # AUTHENTICATION ROUTING
    # ============================================
    # Clear reset_completed flag if it was set
    if st.session_state.get("reset_completed", False):
        st.session_state.reset_completed = False
    
    # If not authenticated, show auth pages
    if not st.session_state.authenticated:
        # Route to appropriate auth page
        if st.session_state.page == "signup":
            signup_page()
            return
        elif st.session_state.page == "forgot":
            forgot_password_page()
            return
        else:
            # Default to login
            login_page()
            return
    
    # If authenticated but page is not main, set to main
    if st.session_state.page != "main":
        st.session_state.page = "main"
    
    # Sidebar visibility (already handled by CSS above)
    
    # Main HR AI Agent UI
    initialize_session()
    display_header()
    
    # Sidebar - HR-friendly content only (collapsible)
    with st.sidebar:
        # Theme toggle
        theme_col1, theme_col2 = st.columns([1, 3])
        with theme_col1:
            theme_icon = "🌙" if st.session_state.theme == "dark" else "☀️"
            if st.button(theme_icon, key="theme_toggle", help=f"Switch to {'Light' if st.session_state.theme == 'dark' else 'Dark'} mode", use_container_width=True):
                # Toggle theme without resetting other session state
                st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
                # Rerun to apply new theme CSS - session state persists automatically
                st.rerun()
        with theme_col2:
            theme_colors = get_theme()
            text_secondary = theme_colors["text_secondary"]
            theme_label = "Dark Mode" if st.session_state.theme == "dark" else "Light Mode"
            st.markdown(f"<div style='margin-top:8px; color: {text_secondary}; font-size: 0.85rem;'>{theme_label}</div>", unsafe_allow_html=True)
        
        st.markdown("---")
        
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
        
        st.markdown("---")
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            st.session_state.clear()
            st.session_state.page = "login"
            st.session_state.authenticated = False
            st.rerun()
    
    # Job Description Input Mode Selection
    st.markdown('<div class="jd-mode-section">', unsafe_allow_html=True)
    st.markdown("### 📝 Job Description")
    jd_mode = st.radio(
        "How would you like to provide the Job Description?",
        ["Manual", "AI Generated"],
        horizontal=True,
        key="jd_mode_selector"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
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

            # Checkbox for select all
            select_all = st.checkbox(
                "Select all recommended skills",
                key="select_all_skills"
            )

            
            # Determine selected values
            if select_all:
                selected_recommended = recommended_skills
            else:
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
            # Validate required fields before generation
            if not job_title or not job_title.strip():
                st.error("❌ Please fill in all required fields (marked with *). Job Title is required.")
            elif not experience or not experience.strip():
                st.error("❌ Please fill in all required fields (marked with *). Experience is required.")
            elif not domain or not domain.strip():
                st.error("❌ Please fill in all required fields (marked with *). Domain is required.")
            elif not seniority or not seniority.strip():
                st.error("❌ Please fill in all required fields (marked with *). Seniority Level is required.")
            elif not location or not location.strip():
                st.error("❌ Please fill in all required fields (marked with *). Location is required.")
            else:
                with st.spinner("Generating professional job description..."):
                    generated_jd = generate_job_description(
                        job_title=job_title.strip(),
                        experience=experience.strip(),
                        domain=domain.strip(),
                        seniority=seniority.strip(),
                        location=location.strip(),
                        key_skills=key_skills.strip() if key_skills else ""
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


