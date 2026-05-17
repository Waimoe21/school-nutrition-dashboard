import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import unicodedata
import altair as alt
import os
import importlib.util

# ----------------------------
# BASE DIRECTORY
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(
    page_title="School Nutrition Dashboard",
    layout="wide"
)

# ----------------------------
# GLOBAL DARK THEME
# ----------------------------
st.markdown(
    """
    <style>
    html, body, [class*="css"]  {
        font-family: 'Open Sauce', sans-serif;
        color: #fcfaf4;
        background-color: #000000 !important;
    }

    .stApp, [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    .block-container {
        background-color: #000000 !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #000000 !important;
    }

    .block-container {
        padding-top: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ----------------------------
# SIDEBAR MENU
# ----------------------------
st.sidebar.title("Menu")

page = st.sidebar.radio(
    "Navigate",
    [
        "Home",
        "Overview",
        "Nutrition Insights",
        "Diet Quality",
        "Behavioral Patterns",
        "Socioeconomics Overview",
        "Health",
        "Inferential Analysis"
    ]
)

# ----------------------------
# PAGE LOADER
# ----------------------------
def run_page(path):
    full_path = os.path.join(BASE_DIR, path)

    spec = importlib.util.spec_from_file_location("page_module", full_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

# ----------------------------
# IMAGE PATHS (FIXED)
# ----------------------------
BANNER_PATH = os.path.join(BASE_DIR, "pages", "banner.png")
POSTER_PATH = os.path.join(BASE_DIR, "pages", "poster.jpg")

# ----------------------------
# HOME PAGE
# ----------------------------
if page == "Home":
    st.title("School Nutrition Dashboard")

    col1, col2, col3 = st.columns([0.5, 3, 0.5])

    with col2:
        # Banner image
        if os.path.exists(BANNER_PATH):
            st.image(BANNER_PATH, width=700)

        # Poster image (optional second visual)
        if os.path.exists(POSTER_PATH):
            st.image(POSTER_PATH, width=1200)

# ----------------------------
# PAGE ROUTING
# ----------------------------
elif page == "Overview":
    run_page("pages/1_Overview.py")

elif page == "Nutrition Insights":
    run_page("pages/2_Nutrition_Insights.py")

elif page == "Diet Quality":
    run_page("pages/3_Diet_Quality.py")

elif page == "Behavioral Patterns":
    run_page("pages/4_Behavioral_Patterns.py")

elif page == "Health":
    run_page("pages/5_Health.py")

elif page == "Socioeconomics Overview":
    run_page("pages/6_Socioeconomics_Overview.py")

elif page == "Inferential Analysis":
    run_page("pages/7_Inferential_Analysis.py")
