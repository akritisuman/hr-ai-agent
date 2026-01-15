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
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv()

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
        "sidebar_bg": "#FFFFFF",
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
    
    # Light-mode-only global fix for white boxes inside colored containers
    light_mode_global_fix = ""
    if theme == "light":
        light_mode_global_fix = f"""
    /* ============================================
       GLOBAL FIX: Remove white boxes inside colored containers (Light Mode Only)
       Rule-based approach: All informational containers get flat styling
       ============================================ */
    
    /* Target ALL informational/message containers - comprehensive list */
    .stInfo,
    .stSuccess,
    .stWarning,
    .stError,
    [data-testid="stMarkdownContainer"],
    [data-testid="stVerticalBlock"],
    [data-testid="stHorizontalBlock"],
    [class*="result"],
    [class*="candidate"],
    [class*="ranking"],
    [class*="summary"],
    [class*="skill"],
    [class*="matched"],
    [class*="missing"],
    [class*="metric"],
    [class*="score"],
    .enterprise-card,
    .streamlit-expanderHeader,
    .streamlit-expanderContent {{
        /* Container itself keeps its background - no change */
    }}
    
    /* ALL nested elements in informational containers - FORCE transparent */
    .stInfo *,
    .stInfo > *,
    .stInfo div,
    .stInfo span,
    .stInfo p,
    .stInfo label,
    .stSuccess *,
    .stSuccess > *,
    .stSuccess div,
    .stSuccess span,
    .stSuccess p,
    .stSuccess label,
    .stWarning *,
    .stWarning > *,
    .stWarning div,
    .stWarning span,
    .stWarning p,
    .stWarning label,
    .stError *,
    .stError > *,
    .stError div,
    .stError span,
    .stError p,
    .stError label,
    [data-testid="stMarkdownContainer"] *,
    [data-testid="stMarkdownContainer"] > *,
    [data-testid="stMarkdownContainer"] div,
    [data-testid="stMarkdownContainer"] span,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stVerticalBlock"] *,
    [data-testid="stHorizontalBlock"] *,
    [class*="result"] *,
    [class*="candidate"] *,
    [class*="ranking"] *,
    [class*="summary"] *,
    [class*="skill"] *,
    [class*="matched"] *,
    [class*="missing"] *,
    .enterprise-card *,
    .enterprise-card > *,
    .enterprise-card div,
    .enterprise-card span,
    .enterprise-card p,
    .enterprise-card label,
    .streamlit-expanderHeader *,
    .streamlit-expanderHeader > *,
    .streamlit-expanderHeader div,
    .streamlit-expanderHeader span,
    .streamlit-expanderHeader p,
    .streamlit-expanderHeader label,
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
        -webkit-box-shadow: none !important;
    }}
    
    /* EXCLUDE: JD Type radio selector - must keep active background for selected state */
    .stRadio [role="radiogroup"][aria-orientation="horizontal"],
    .stRadio [role="radiogroup"][aria-orientation="horizontal"] *,
    .stRadio [role="radiogroup"][aria-orientation="horizontal"] > *,
    .stRadio [role="radiogroup"][aria-orientation="horizontal"] div,
    .stRadio [role="radiogroup"][aria-orientation="horizontal"] span,
    .stRadio [role="radiogroup"][aria-orientation="horizontal"] label,
    .stRadio [role="radiogroup"][aria-orientation="horizontal"] input[type="radio"],
    .stRadio [role="radiogroup"][aria-orientation="horizontal"] input[type="radio"]:checked + label {{
        background-color: revert !important;
        background: revert !important;
        border: revert !important;
        box-shadow: revert !important;
        -webkit-box-shadow: revert !important;
    }}
    
    /* EXCLUDE: Streamlit input components - they MUST keep their input styling */
    .stInfo .stTextInput,
    .stInfo .stTextInput *,
    .stInfo .stTextArea,
    .stInfo .stTextArea *,
    .stInfo .stSelectbox,
    .stInfo .stSelectbox *,
    .stInfo .stMultiSelect,
    .stInfo .stMultiSelect *,
    .stInfo .stNumberInput,
    .stInfo .stNumberInput *,
    .stInfo [data-testid="stFileUploader"],
    .stInfo [data-testid="stFileUploader"] *,
    .stSuccess .stTextInput,
    .stSuccess .stTextInput *,
    .stSuccess .stTextArea,
    .stSuccess .stTextArea *,
    .stSuccess .stSelectbox,
    .stSuccess .stSelectbox *,
    .stSuccess .stMultiSelect,
    .stSuccess .stMultiSelect *,
    .stSuccess .stNumberInput,
    .stSuccess .stNumberInput *,
    .stSuccess [data-testid="stFileUploader"],
    .stSuccess [data-testid="stFileUploader"] *,
    .stWarning .stTextInput,
    .stWarning .stTextInput *,
    .stWarning .stTextArea,
    .stWarning .stTextArea *,
    .stWarning .stSelectbox,
    .stWarning .stSelectbox *,
    .stWarning .stMultiSelect,
    .stWarning .stMultiSelect *,
    .stWarning .stNumberInput,
    .stWarning .stNumberInput *,
    .stWarning [data-testid="stFileUploader"],
    .stWarning [data-testid="stFileUploader"] *,
    .stError .stTextInput,
    .stError .stTextInput *,
    .stError .stTextArea,
    .stError .stTextArea *,
    .stError .stSelectbox,
    .stError .stSelectbox *,
    .stError .stMultiSelect,
    .stError .stMultiSelect *,
    .stError .stNumberInput,
    .stError .stNumberInput *,
    .stError [data-testid="stFileUploader"],
    .stError [data-testid="stFileUploader"] *,
    [data-testid="stMarkdownContainer"] .stTextInput,
    [data-testid="stMarkdownContainer"] .stTextInput *,
    [data-testid="stMarkdownContainer"] .stTextArea,
    [data-testid="stMarkdownContainer"] .stTextArea *,
    [data-testid="stMarkdownContainer"] .stSelectbox,
    [data-testid="stMarkdownContainer"] .stSelectbox *,
    [data-testid="stMarkdownContainer"] .stMultiSelect,
    [data-testid="stMarkdownContainer"] .stMultiSelect *,
    [data-testid="stMarkdownContainer"] .stNumberInput,
    [data-testid="stMarkdownContainer"] .stNumberInput *,
    [data-testid="stMarkdownContainer"] [data-testid="stFileUploader"],
    [data-testid="stMarkdownContainer"] [data-testid="stFileUploader"] *,
    .enterprise-card .stTextInput,
    .enterprise-card .stTextInput *,
    .enterprise-card .stTextArea,
    .enterprise-card .stTextArea *,
    .enterprise-card .stSelectbox,
    .enterprise-card .stSelectbox *,
    .enterprise-card .stMultiSelect,
    .enterprise-card .stMultiSelect *,
    .enterprise-card .stNumberInput,
    .enterprise-card .stNumberInput *,
    .enterprise-card [data-testid="stFileUploader"],
    .enterprise-card [data-testid="stFileUploader"] *,
    .streamlit-expanderContent .stTextInput,
    .streamlit-expanderContent .stTextInput *,
    .streamlit-expanderContent .stTextArea,
    .streamlit-expanderContent .stTextArea *,
    .streamlit-expanderContent .stSelectbox,
    .streamlit-expanderContent .stSelectbox *,
    .streamlit-expanderContent .stMultiSelect,
    .streamlit-expanderContent .stMultiSelect *,
    .streamlit-expanderContent .stNumberInput,
    .streamlit-expanderContent .stNumberInput *,
    .streamlit-expanderContent [data-testid="stFileUploader"],
    .streamlit-expanderContent [data-testid="stFileUploader"] * {{
        background-color: {colors["input_bg"]} !important;
        border: 1px solid {colors["input_border"]} !important;
    }}
    
    /* EXCLUDE: Buttons - they have their own styling */
    .stInfo [data-testid="stButton"] > button,
    .stSuccess [data-testid="stButton"] > button,
    .stWarning [data-testid="stButton"] > button,
    .stError [data-testid="stButton"] > button,
    [data-testid="stMarkdownContainer"] [data-testid="stButton"] > button,
    [class*="result"] [data-testid="stButton"] > button,
    .enterprise-card [data-testid="stButton"] > button,
    .streamlit-expanderContent [data-testid="stButton"] > button,
    .stInfo [data-testid="stDownloadButton"] > button,
    .stSuccess [data-testid="stDownloadButton"] > button,
    .stWarning [data-testid="stDownloadButton"] > button,
    .stError [data-testid="stDownloadButton"] > button,
    [data-testid="stMarkdownContainer"] [data-testid="stDownloadButton"] > button,
    [class*="result"] [data-testid="stDownloadButton"] > button,
    .enterprise-card [data-testid="stDownloadButton"] > button,
    .streamlit-expanderContent [data-testid="stDownloadButton"] > button {{
        background-color: {colors["accent"]} !important;
    }}
    
    /* Dark backgrounds - white text for readability */
    [style*="background"][style*="#0f"],
    [style*="background"][style*="#1a"],
    [style*="background"][style*="#1e"],
    [style*="background-color"][style*="#0f"],
    [style*="background-color"][style*="#1a"],
    [style*="background-color"][style*="#1e"],
    [style*="background: #0f"],
    [style*="background: #1a"],
    [style*="background: #1e"],
    [style*="background-color: #0f"],
    [style*="background-color: #1a"],
    [style*="background-color: #1e"] {{
        color: white !important;
    }}
    
    [style*="background"][style*="#0f"] *,
    [style*="background"][style*="#1a"] *,
    [style*="background"][style*="#1e"] *,
    [style*="background-color"][style*="#0f"] *,
    [style*="background-color"][style*="#1a"] *,
    [style*="background-color"][style*="#1e"] *,
    [style*="background: #0f"] *,
    [style*="background: #1a"] *,
    [style*="background: #1e"] *,
    [style*="background-color: #0f"] *,
    [style*="background-color: #1a"] *,
    [style*="background-color: #1e"] * {{
        color: white !important;
        background-color: transparent !important;
    }}
    """
    
    # Light-mode-only fixes for dark sections with invisible text
    light_mode_dark_section_fixes = ""
    if theme == "light":
        light_mode_dark_section_fixes = f"""
    /* ============================================
       LIGHT MODE: Fix text visibility in dark sections
       (ONLY text color, NO background changes)
       ============================================ */
    
    /* Dark/black result cards and sections - white text only */
    [style*="background"][style*="#0f"],
    [style*="background"][style*="#1a"],
    [style*="background"][style*="#1e"],
    [style*="background"][style*="rgb(15"],
    [style*="background"][style*="rgb(26"],
    [style*="background"][style*="rgb(30"],
    [style*="background-color"][style*="#0f"],
    [style*="background-color"][style*="#1a"],
    [style*="background-color"][style*="#1e"],
    [style*="background-color"][style*="rgb(15"],
    [style*="background-color"][style*="rgb(26"],
    [style*="background-color"][style*="rgb(30"],
    [style*="background: #0f"],
    [style*="background: #1a"],
    [style*="background: #1e"],
    [style*="background-color: #0f"],
    [style*="background-color: #1a"],
    [style*="background-color: #1e"] {{
        color: white !important;
    }}
    
    [style*="background"][style*="#0f"] *,
    [style*="background"][style*="#1a"] *,
    [style*="background"][style*="#1e"] *,
    [style*="background-color"][style*="#0f"] *,
    [style*="background-color"][style*="#1a"] *,
    [style*="background-color"][style*="#1e"] * {{
        color: white !important;
    }}
    
    /* Expandable candidate sections with dark backgrounds */
    .streamlit-expanderHeader[style*="background"][style*="#0f"],
    .streamlit-expanderHeader[style*="background"][style*="#1a"],
    .streamlit-expanderHeader[style*="background"][style*="#1e"],
    .streamlit-expanderContent[style*="background"][style*="#0f"],
    .streamlit-expanderContent[style*="background"][style*="#1a"],
    .streamlit-expanderContent[style*="background"][style*="#1e"] {{
        color: white !important;
    }}
    
    .streamlit-expanderHeader[style*="background"][style*="#0f"] *,
    .streamlit-expanderHeader[style*="background"][style*="#1a"] *,
    .streamlit-expanderHeader[style*="background"][style*="#1e"] *,
    .streamlit-expanderContent[style*="background"][style*="#0f"] *,
    .streamlit-expanderContent[style*="background"][style*="#1a"] *,
    .streamlit-expanderContent[style*="background"][style*="#1e"] * {{
        color: white !important;
    }}
    
    /* Score containers with dark backgrounds */
    [class*="score"][style*="background"][style*="#0f"],
    [class*="score"][style*="background"][style*="#1a"],
    [class*="score"][style*="background"][style*="#1e"],
    p[class*="score"][style*="background"][style*="#0f"],
    p[class*="score"][style*="background"][style*="#1a"],
    p[class*="score"][style*="background"][style*="#1e"] {{
        color: white !important;
    }}
    
    [class*="score"][style*="background"][style*="#0f"] *,
    [class*="score"][style*="background"][style*="#1a"] *,
    [class*="score"][style*="background"][style*="#1e"] * {{
        color: white !important;
    }}
    
    /* Selection sliders and controls with dark backgrounds */
    .stSlider [style*="background"][style*="#0f"],
    .stSlider [style*="background"][style*="#1a"],
    .stSlider [style*="background"][style*="#1e"] {{
        color: white !important;
    }}
    
    .stSlider [style*="background"][style*="#0f"] *,
    .stSlider [style*="background"][style*="#1a"] *,
    .stSlider [style*="background"][style*="#1e"] * {{
        color: white !important;
    }}
    
    /* Buttons with dark backgrounds - text only */
    .stButton > button[style*="background"][style*="#0f"],
    .stButton > button[style*="background"][style*="#1a"],
    .stButton > button[style*="background"][style*="#1e"],
    [data-testid="stDownloadButton"] > button[style*="background"][style*="#0f"],
    [data-testid="stDownloadButton"] > button[style*="background"][style*="#1a"],
    [data-testid="stDownloadButton"] > button[style*="background"][style*="#1e"] {{
        color: white !important;
    }}
    
    .stButton > button[style*="background"][style*="#0f"] *,
    .stButton > button[style*="background"][style*="#1a"] *,
    .stButton > button[style*="background"][style*="#1e"] * {{
        color: white !important;
    }}
    
    /* Selected Skills display - no white background, only text fix if needed */
    [class*="skill"][style*="background"][style*="#0f"],
    [class*="skill"][style*="background"][style*="#1a"],
    [class*="skill"][style*="background"][style*="#1e"] {{
        color: white !important;
    }}
    
    [class*="skill"][style*="background"][style*="#0f"] *,
    [class*="skill"][style*="background"][style*="#1a"] *,
    [class*="skill"][style*="background"][style*="#1e"] * {{
        color: white !important;
    }}
    """
    
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
    
    /* Radio buttons - base container */
    .stRadio > div {{
        background-color: {colors["radio_bg"]} !important;
        padding: 0.35rem;
        border-radius: 9999px;
        border: 1px solid {colors["radio_border"]} !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }}

    /* Horizontal JD Type radio group as segmented control */
    .stRadio [role="radiogroup"][aria-orientation="horizontal"] {{
        display: inline-flex !important;
        gap: 0;
        border-radius: 9999px;
        overflow: hidden;
    }}
    
    /* Radio button options container */
    .stRadio > div > div,
    .stRadio > div > div > div,
    .stRadio [role="radiogroup"][aria-orientation="horizontal"] > div {{
        background-color: transparent !important;
        border: none !important;
    }}
    
    /* Radio button option items (segments) - base styling */
    .stRadio [role="radiogroup"][aria-orientation="horizontal"] label {{
        color: {colors["text_primary"]} !important;
        background-color: transparent !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        font-weight: 400;
        padding: 0.4rem 1rem;
        padding-left: 0.4rem;
        border-radius: 9999px;
        transition: all 0.2s ease;
        cursor: pointer;
        display: inline-flex;
        align-items: center;
        justify-content: flex-start;
        white-space: nowrap;
        min-width: fit-content;
    }}
    
    /* Radio button option hover state - only for unselected */
    .stRadio [role="radiogroup"][aria-orientation="horizontal"] input[type="radio"]:not(:checked) + label:hover {{
        background-color: {colors["surface"]} !important;
        opacity: 1;
    }}
    
    /* Selected option should not change on hover */
    .stRadio [role="radiogroup"][aria-orientation="horizontal"] input[type="radio"]:checked + label:hover {{
        background-color: {colors["accent"]} !important;
        color: white !important;
    }}
    
    /* Show and style radio dots - clearly visible in Light Mode */
    .stRadio [role="radiogroup"][aria-orientation="horizontal"] input[type="radio"] {{
        position: relative !important;
        opacity: 1 !important;
        width: 18px !important;
        height: 18px !important;
        margin: 0 0.5rem 0 0 !important;
        padding: 0 !important;
        cursor: pointer;
        accent-color: {colors["accent"]} !important;
        -webkit-appearance: radio;
        appearance: radio;
    }}
    
    /* Radio dot - checked state - clearly visible colored dot */
    .stRadio [role="radiogroup"][aria-orientation="horizontal"] input[type="radio"]:checked {{
        accent-color: {colors["accent"]} !important;
        border-color: {colors["accent"]} !important;
    }}
    
    /* Ensure radio dot is visible with accent color */
    .stRadio [role="radiogroup"][aria-orientation="horizontal"] input[type="radio"]:checked::before {{
        content: "";
        display: block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background-color: {colors["accent"]} !important;
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
    }}
    
    /* Selected segment state - VERY CLEAR in Light Mode */
    .stRadio [role="radiogroup"][aria-orientation="horizontal"] input[type="radio"]:checked + label,
    .stRadio [role="radiogroup"][aria-orientation="horizontal"] input[type="radio"]:checked ~ label,
    .stRadio [role="radiogroup"][aria-orientation="horizontal"] label[for*="jd_mode"]:has(+ input[type="radio"]:checked),
    .stRadio [role="radiogroup"][aria-orientation="horizontal"] > div > div:has(input[type="radio"]:checked) label {{
        background-color: {colors["accent"]} !important;
        color: white !important;
        font-weight: 700 !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1) !important;
    }}
    
    /* Unselected segments - clearly inactive */
    .stRadio [role="radiogroup"][aria-orientation="horizontal"] input[type="radio"]:not(:checked) + label,
    .stRadio [role="radiogroup"][aria-orientation="horizontal"] input[type="radio"]:not(:checked) ~ label,
    .stRadio [role="radiogroup"][aria-orientation="horizontal"] > div > div:not(:has(input[type="radio"]:checked)) label {{
        background-color: transparent !important;
        color: {colors["text_secondary"]} !important;
        font-weight: 400 !important;
        opacity: 0.7;
    }}
    
    /* Ensure selected state is always visible - additional selectors */
    .stRadio [role="radiogroup"][aria-orientation="horizontal"] input[type="radio"][checked] + label,
    .stRadio [role="radiogroup"][aria-orientation="horizontal"] [aria-checked="true"] + label {{
        background-color: {colors["accent"]} !important;
        color: white !important;
        font-weight: 700 !important;
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
    
    /* ============================================
       SIDEBAR ICONS AND ARROWS
       ============================================ */
    
    /* Sidebar icons */
    [data-testid="stSidebar"] svg,
    [data-testid="stSidebar"] [class*="icon"],
    [data-testid="stSidebar"] [class*="arrow"],
    [data-testid="stSidebar"] .streamlit-expanderHeader svg,
    [data-testid="stSidebar"] [data-testid="stExpanderToggleIcon"] {{
        fill: {colors["icon_color"]} !important;
        color: {colors["icon_color"]} !important;
        opacity: 1 !important;
        stroke: {colors["icon_color"]} !important;
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
    
    /* Radio button labels - consolidated with main radio styling above */
    
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
    
    {light_mode_global_fix}
    
    {light_mode_dark_section_fixes}
</style>
"""


# Apply theme-based CSS
current_css = get_theme_css(st.session_state.theme)
st.markdown(current_css, unsafe_allow_html=True)

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


def display_header():
    """Display enterprise header with institute and company branding"""
    # Logo paths
    siei_logo_path = "assets/siei_logo.png"
    SIEI_LOGO = Path(siei_logo_path)
    
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
            # Do nothing if logo not found (NO BOX)
            st.markdown("")
    
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
Experience Required: {experience}
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
