import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ----------------------------
# BASE DIR (DEPLOYMENT SAFE)
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(page_title="Health Insights", layout="wide")

# ----------------------------
# COLOR PALETTE
# ----------------------------
COLOR_PALETTE = ["#00bf63", "#db4a2b", "#fcfaf4"]

# ----------------------------
# DARK THEME
# ----------------------------
st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        font-family: 'Open Sauce', sans-serif;
        color: #fcfaf4;
        background-color: #000000 !important;
    }

    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stHeader"],
    [data-testid="stSidebar"],
    [data-testid="stToolbar"],
    .block-container {
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
# TITLE
# ----------------------------
st.title("Health Overview")

# ----------------------------
# BANNER IMAGE (DEPLOYMENT SAFE FIX)
# ----------------------------
col1, col2, col3 = st.columns([0.5, 3, 0.5])

with col2:
    banner_path = os.path.join("pages", "banner.png")

    if os.path.exists(banner_path):
        st.image(banner_path, width=700)
    else:
        st.error(f"Missing banner image: {banner_path}")

# ----------------------------
# LOAD DATA (FIXED PATH)
# ----------------------------
DATA_PATH = os.path.join(BASE_DIR, "dataset.csv")
df = pd.read_csv(DATA_PATH)

# safe numeric conversion
if "chronic_condition_status" in df.columns:
    df["chronic_condition_status"] = pd.to_numeric(df["chronic_condition_status"], errors="coerce").fillna(0)

# ----------------------------
# SIDEBAR FILTERS
# ----------------------------
st.sidebar.header("Filters")

def safe_unique(col):
    return df[col].dropna().unique() if col in df.columns else []

school = st.sidebar.multiselect("School", safe_unique("school"))
school_code = st.sidebar.multiselect("School Code", safe_unique("school_code"))
age = st.sidebar.multiselect("Age", safe_unique("age"))
sex = st.sidebar.multiselect("Sex", safe_unique("sex"))
academic_level = st.sidebar.multiselect("Academic Level", safe_unique("academic_level"))
ses_level = st.sidebar.multiselect("SES Level", safe_unique("ses_level"))

filtered_df = df.copy()

def apply_filter(col, values):
    global filtered_df
    if values and col in filtered_df.columns:
        filtered_df = filtered_df[filtered_df[col].isin(values)]

apply_filter("school", school)
apply_filter("school_code", school_code)
apply_filter("age", age)
apply_filter("sex", sex)
apply_filter("academic_level", academic_level)
apply_filter("ses_level", ses_level)

# ----------------------------
# 1. CHRONIC CONDITION %
# ----------------------------
st.subheader("Chronic Condition Overview")

if "chronic_condition_status" in filtered_df.columns:
    total_students = len(filtered_df)
    chronic_yes = filtered_df["chronic_condition_status"].sum()

    chronic_percent = (chronic_yes / total_students * 100) if total_students > 0 else 0

    st.metric(
        "Students with Chronic Condition",
        f"{chronic_percent:.2f}%"
    )

# ----------------------------
# 2. HEIGHT & WEIGHT
# ----------------------------
st.subheader("Physical Measurements")

col1, col2 = st.columns(2)

avg_height = filtered_df["height_in"].mean() if "height_in" in filtered_df else 0
avg_weight = filtered_df["body_weight_lb"].mean() if "body_weight_lb" in filtered_df else 0

col1.metric("Avg Height (inches)", f"{avg_height:.2f}")
col2.metric("Avg Weight (lbs)", f"{avg_weight:.2f}")

# ----------------------------
# 3. BMI DISTRIBUTION
# ----------------------------
st.subheader("BMI Category Distribution")

if "BMI_category" in filtered_df.columns:
    bmi_counts = filtered_df["BMI_category"].value_counts().reset_index()
    bmi_counts.columns = ["Category", "Count"]

    if not bmi_counts.empty:
        fig = px.bar(
            bmi_counts,
            x="Category",
            y="Count",
            color="Category",
            color_discrete_sequence=COLOR_PALETTE
        )

        fig.update_layout(
            paper_bgcolor="#000000",
            plot_bgcolor="#000000",
            font=dict(color="#fcfaf4")
        )

        st.plotly_chart(fig, use_container_width=True)
