import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ----------------------------
# BASE DIRECTORY (DEPLOYMENT FIX)
# ----------------------------
BASE_DIR = os.path.dirname(__file__)

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(page_title="Behavioral Patterns", layout="wide")

# ----------------------------
# COLOR PALETTE
# ----------------------------
COLOR_PALETTE = ["#db4a2b", "#00bf63", "#fcfaf4"]

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
st.title("Behavioral Patterns")

# ----------------------------
# BANNER IMAGE (FIXED PATH)
# ----------------------------
col1, col2, col3 = st.columns([0.5, 3, 0.5])

with col2:
    st.image(
        os.path.join(BASE_DIR, "DESIGNING.png"),
        use_container_width=True
    )

# ----------------------------
# LOAD DATA (FIXED PATH)
# ----------------------------
df = pd.read_csv(os.path.join(BASE_DIR, "dataset.csv"))

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
bmi = st.sidebar.multiselect("BMI Category", safe_unique("BMI_category"))
ses = st.sidebar.multiselect("SES Level", safe_unique("ses_level"))

filtered_df = df.copy()

def apply_filter(col, values):
    global filtered_df
    if values and col in filtered_df.columns:
        filtered_df = filtered_df[filtered_df[col].isin(values)]

apply_filter("school", school)
apply_filter("school_code", school_code)
apply_filter("age", age)
apply_filter("sex", sex)
apply_filter("BMI_category", bmi)
apply_filter("ses_level", ses)

# ----------------------------
# 1. ALLOWANCE OVERVIEW
# ----------------------------
st.subheader("Allowance Overview")

avg_received = filtered_df["allowance_received_amt_mmk"].mean() if "allowance_received_amt_mmk" in filtered_df else 0
avg_spent = filtered_df["allowance_expenditure_amt_mmk"].mean() if "allowance_expenditure_amt_mmk" in filtered_df else 0

col1, col2 = st.columns(2)
col1.metric("Avg Allowance Received (MMK)", f"{avg_received:,.0f}")
col2.metric("Avg Allowance Expenditure (MMK)", f"{avg_spent:,.0f}")

# ----------------------------
# 2. LUNCH PROCUREMENT
# ----------------------------
st.subheader("Lunch Procurement Source")

if "lunch_procurement_source" in filtered_df.columns:
    lunch_counts = filtered_df["lunch_procurement_source"].value_counts().reset_index()
    lunch_counts.columns = ["Source", "Count"]

    fig = px.bar(
        lunch_counts,
        x="Source",
        y="Count",
        color="Source",
        color_discrete_sequence=COLOR_PALETTE
    )

    fig.update_layout(
        paper_bgcolor="#000000",
        plot_bgcolor="#000000",
        font=dict(color="#fcfaf4")
    )

    st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# 3. MEAL SKIPPING
# ----------------------------
st.subheader("Average Meal Skipping Frequency")

def safe_mean(col):
    return filtered_df[col].mean() if col in filtered_df.columns else 0

skip_df = pd.DataFrame({
    "Meal": ["Breakfast", "Lunch", "Dinner"],
    "Average Skips": [
        safe_mean("breakfast_skipping_freq"),
        safe_mean("lunch_skipping_freq"),
        safe_mean("dinner_skipping_freq")
    ]
})

fig = px.bar(
    skip_df,
    x="Meal",
    y="Average Skips",
    color="Meal",
    color_discrete_sequence=COLOR_PALETTE
)

fig.update_layout(
    paper_bgcolor="#000000",
    plot_bgcolor="#000000",
    font=dict(color="#fcfaf4")
)

st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# 4. TOTAL SKIPPING
# ----------------------------
st.subheader("Total Meal Skipping Frequency")

if all(col in filtered_df.columns for col in ["breakfast_skipping_freq", "lunch_skipping_freq", "dinner_skipping_freq"]):
    filtered_df["total_skip"] = (
        filtered_df["breakfast_skipping_freq"] +
        filtered_df["lunch_skipping_freq"] +
        filtered_df["dinner_skipping_freq"]
    )

    st.metric("Average Total Skips per Week", f"{filtered_df['total_skip'].mean():.2f}")

# ----------------------------
# 5. CANTEEN PREF TOP 5
# ----------------------------
st.subheader("Top 5 Canteen Food Preferences")

score = {}

def add_scores(series, weight):
    for item in series.dropna().astype(str):
        score[item] = score.get(item, 0) + weight

if "canteen_pref_rank1" in filtered_df:
    add_scores(filtered_df["canteen_pref_rank1"], 3)
if "canteen_pref_rank2" in filtered_df:
    add_scores(filtered_df["canteen_pref_rank2"], 2)
if "canteen_pref_rank3" in filtered_df:
    add_scores(filtered_df["canteen_pref_rank3"], 1)

top5 = pd.DataFrame(score.items(), columns=["Food", "Score"]).sort_values("Score", ascending=False).head(5)

if not top5.empty:
    fig = px.bar(
        top5,
        x="Food",
        y="Score",
        color="Food",
        color_discrete_sequence=COLOR_PALETTE
    )

    fig.update_layout(
        paper_bgcolor="#000000",
        plot_bgcolor="#000000",
        font=dict(color="#fcfaf4")
    )

    st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# 6. CUISINE TOP 3
# ----------------------------
st.subheader("Cuisine Preferences")

def top3_bar(col, title):
    if col not in filtered_df.columns:
        return

    counts = filtered_df[col].value_counts().head(3).reset_index()
    counts.columns = ["Item", "Count"]

    fig = px.bar(
        counts,
        x="Item",
        y="Count",
        color="Item",
        color_discrete_sequence=COLOR_PALETTE
    )

    fig.update_layout(
        paper_bgcolor="#000000",
        plot_bgcolor="#000000",
        font=dict(color="#fcfaf4")
    )

    st.markdown(title)
    st.plotly_chart(fig, use_container_width=True)

top3_bar("pref_local_cuisine", "Local Cuisine Preference")
top3_bar("pref_foreign_cuisine", "Foreign Cuisine Preference")

# ----------------------------
# 7. PIE CHART
# ----------------------------
st.subheader("Cuisine Type Preference")

if "cuisine_type_preference" in filtered_df.columns:
    pie_df = filtered_df["cuisine_type_preference"].value_counts(dropna=False).reset_index()
    pie_df.columns = ["Type", "Count"]

    label_map = {
        "M": "Myanmar Cuisine",
        "F": "Transnational Cuisine"
    }

    pie_df["Type"] = pie_df["Type"].map(label_map).fillna("Other")

    fig = px.pie(
        pie_df,
        names="Type",
        values="Count",
        hole=0.4,
        color_discrete_sequence=COLOR_PALETTE
    )

    fig.update_traces(
        textinfo="percent+label",
        marker=dict(line=dict(color="#000000", width=2))
    )

    fig.update_layout(
        paper_bgcolor="#000000",
        font=dict(color="#fcfaf4")
    )

    st.plotly_chart(fig, use_container_width=True)