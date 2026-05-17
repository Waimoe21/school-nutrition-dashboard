import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ----------------------------
# BASE PATH (DEPLOYMENT SAFE)
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(page_title="Socioeconomics Overview", layout="wide")

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
    html, body, [class*="css"]  {
        font-family: 'Open Sauce', sans-serif;
        color: #fcfaf4;
        background-color: #000000 !important;
    }

    .stApp, [data-testid="stAppViewContainer"],
    [data-testid="stHeader"], [data-testid="stSidebar"],
    [data-testid="stToolbar"], .block-container {
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
# TITLE + BANNER (DEPLOYMENT SAFE FIX)
# ----------------------------
st.title("Socioeconomics Overview")

col1, col2, col3 = st.columns([0.5, 3, 0.5])

with col2:
    banner_path = os.path.join("pages", "banner.png")

    if os.path.exists(banner_path):
        st.image(banner_path, use_container_width=True)
    else:
        st.error(f"Missing banner image: {banner_path}")
# ----------------------------
# LOAD DATA (FIXED PATH)
# ----------------------------
DATA_PATH = os.path.join(BASE_DIR, "dataset.csv")
df = pd.read_csv(DATA_PATH)

# ----------------------------
# LABELS
# ----------------------------
edu_labels = {
    1: "Primary School",
    2: "Middle School",
    3: "High School",
    4: "Undergraduate",
    5: "Post Graduate"
}

occ_labels = {
    0: "Unemployed / No Income",
    1: "Low-Skill / Manual Labor",
    2: "Skilled / Technical",
    3: "Skilled / Small Business / Stable Income",
    4: "High SES / Professional / Leadership"
}

fin_labels = {
    1: "Very Difficult",
    2: "Unstable",
    3: "Stable",
    4: "Comfortable"
}

save_labels = {
    1: "No Savings",
    2: "Fairly Prepared",
    3: "Properly Prepared"
}

income_labels = {
    1: "Less than 2 lakhs",
    2: "2–5 lakhs",
    3: "5–8 lakhs",
    4: "8–10 lakhs",
    5: "More than 10 lakhs"
}

# ----------------------------
# SIDEBAR FILTERS
# ----------------------------
st.sidebar.header("Filters")

school = st.sidebar.multiselect("School", df["school"].dropna().unique())
school_code = st.sidebar.multiselect("School Code", df["school_code"].dropna().unique())
age = st.sidebar.multiselect("Age", df["age"].dropna().unique())
sex = st.sidebar.multiselect("Sex", df["sex"].dropna().unique())
academic_level = st.sidebar.multiselect("Academic Level", df["academic_level"].dropna().unique())

filtered_df = df.copy()

def apply_filter(col, values):
    global filtered_df
    if values:
        filtered_df = filtered_df[filtered_df[col].isin(values)]

apply_filter("school", school)
apply_filter("school_code", school_code)
apply_filter("age", age)
apply_filter("sex", sex)
apply_filter("academic_level", academic_level)

# ----------------------------
# PLOT STYLE HELPER (REDUCES REPETITION)
# ----------------------------
def style_fig(fig):
    fig.update_layout(
        paper_bgcolor="#000000",
        plot_bgcolor="#000000",
        font=dict(color="#fcfaf4")
    )
    return fig

# ----------------------------
# 1. EDUCATION
# ----------------------------
st.subheader("Guardian Education Distribution")

edu_series = pd.concat([
    filtered_df["guardian1_edu"],
    filtered_df["guardian2_edu"]
])

edu_counts = edu_series.value_counts().reset_index()
edu_counts.columns = ["Level", "Count"]
edu_counts["Level"] = edu_counts["Level"].map(edu_labels)

fig = px.bar(
    edu_counts,
    x="Level",
    y="Count",
    color="Level",
    color_discrete_sequence=COLOR_PALETTE
)

st.plotly_chart(style_fig(fig), use_container_width=True)

# ----------------------------
# 2. OCCUPATION
# ----------------------------
st.subheader("Guardian Occupation Distribution")

occ_series = pd.concat([
    filtered_df["guardian1_occ_cat"],
    filtered_df["guardian2_occ_cat"]
])

occ_counts = occ_series.value_counts().reset_index()
occ_counts.columns = ["Occupation", "Count"]
occ_counts["Occupation"] = occ_counts["Occupation"].map(occ_labels)

fig = px.bar(
    occ_counts,
    x="Occupation",
    y="Count",
    color="Occupation",
    color_discrete_sequence=COLOR_PALETTE
)

st.plotly_chart(style_fig(fig), use_container_width=True)

# ----------------------------
# 3. FAMILY SIZE
# ----------------------------
st.subheader("Average Family Size")

st.metric("Average Family Size", f"{filtered_df['family_size'].mean():.2f}")

# ----------------------------
# 4. DISEASE
# ----------------------------
st.subheader("Household Health Condition")

disease_percent = (filtered_df["diseased_member"].sum() / len(filtered_df)) * 100
st.metric("Households with Diseased Member", f"{disease_percent:.2f}%")

# ----------------------------
# 5. HUNGER
# ----------------------------
st.subheader("Food Insecurity (Last 6 Months)")

hunger_percent = (filtered_df["hunger_6m"].sum() / len(filtered_df)) * 100
st.metric("Experienced Hunger", f"{hunger_percent:.2f}%")

# ----------------------------
# 6. FINANCIAL SECURITY
# ----------------------------
st.subheader("Financial Security Perception")

fin_counts = filtered_df["financial_security"].value_counts().reset_index()
fin_counts.columns = ["Level", "Count"]
fin_counts["Level"] = fin_counts["Level"].map(fin_labels)

fig = px.bar(
    fin_counts,
    x="Level",
    y="Count",
    color="Level",
    color_discrete_sequence=COLOR_PALETTE
)

st.plotly_chart(style_fig(fig), use_container_width=True)

# ----------------------------
# 7. SAVINGS
# ----------------------------
st.subheader("Emergency Savings Preparedness")

save_counts = filtered_df["emergency_savings"].value_counts().reset_index()
save_counts.columns = ["Level", "Count"]
save_counts["Level"] = save_counts["Level"].map(save_labels)

fig = px.bar(
    save_counts,
    x="Level",
    y="Count",
    color="Level",
    color_discrete_sequence=COLOR_PALETTE
)

st.plotly_chart(style_fig(fig), use_container_width=True)

# ----------------------------
# 8. INCOME
# ----------------------------
st.subheader("Household Income Level")

income_counts = filtered_df["income_level"].value_counts().reset_index()
income_counts.columns = ["Level", "Count"]
income_counts["Level"] = income_counts["Level"].map(income_labels)

fig = px.bar(
    income_counts,
    x="Level",
    y="Count",
    color="Level",
    color_discrete_sequence=COLOR_PALETTE
)

st.plotly_chart(style_fig(fig), use_container_width=True)

# ----------------------------
# 9. SES
# ----------------------------
st.subheader("SES Level Distribution")

ses_counts = filtered_df["ses_level"].value_counts().reset_index()
ses_counts.columns = ["SES Level", "Count"]

fig = px.bar(
    ses_counts,
    x="SES Level",
    y="Count",
    color="SES Level",
    color_discrete_sequence=COLOR_PALETTE
)

st.plotly_chart(style_fig(fig), use_container_width=True)