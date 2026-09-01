import streamlit as st
import pandas as pd
from pathlib import Path

# Paths Configuration
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "processed" / "uber_cleaned.csv"
ASSETS_PATH = BASE_DIR / "uber_dataset" / "Images"

# Page Configuration
PAGE_CONFIG = {
    "page_title": "Uber Executive Mobility Analytics",
    "page_icon": "🚘",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
}

# Theme Colors
THEME_COLORS = {
    "primary": "#FACC15",       # Bright Yellow
    "background": "#0E1117",    # Dark Charcoal
    "card_bg": "#1A1D24",       # Container Slate
    "text_primary": "#FFFFFF",  # Pure White
    "text_secondary": "#94A3B8",  # Muted Slate
    "accent_red": "#EF4444",    # Warning Red
    "accent_green": "#10B981",  # Positive Green
}


def apply_custom_css():
    """Injects aggressive CSS overrides to completely eliminate metric text truncation."""
    st.markdown(
        f"""
        <style>
        /* Global Background */
        .stApp {{
            background-color: {THEME_COLORS['background']};
            color: {THEME_COLORS['text_primary']};
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        
        /* Metric Card Container */
        div[data-testid="stMetric"] {{
            background-color: {THEME_COLORS['card_bg']} !important;
            border: 1px solid rgba(250, 204, 21, 0.2) !important;
            border-radius: 8px !important;
            padding: 8px 12px !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3) !important;
            min-height: 85px !important;
            display: flex !important;
            flex-direction: column !important;
            justify-content: center !important;
        }}

        /* Strict Override for Metric Value (No '...') */
        div[data-testid="stMetricValue"] > div {{
            color: {THEME_COLORS['primary']} !important;
            font-weight: 700 !important;
            font-size: 1.15rem !important;
            line-height: 1.25 !important;
            overflow: visible !important;
            text-overflow: clip !important;
            white-space: normal !important;
            word-break: break-word !important;
        }}

        /* Metric Label */
        div[data-testid="stMetricLabel"] > div {{
            color: {THEME_COLORS['text_secondary']} !important;
            font-size: 0.72rem !important;
            font-weight: 600 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.4px !important;
            overflow: visible !important;
            white-space: normal !important;
        }}

        /* Metric Delta */
        div[data-testid="stMetricDelta"] {{
            font-size: 0.70rem !important;
        }}

        /* Sidebar Styling */
        section[data-testid="stSidebar"] {{
            background-color: #12151A !important;
            border-right: 1px solid rgba(250, 204, 21, 0.15) !important;
        }}
        
        /* Main Body Padding */
        .block-container {{
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data
def load_data():
    """Loads and caches processed Uber dataset."""
    df = pd.read_csv(DATA_PATH)
    return df
