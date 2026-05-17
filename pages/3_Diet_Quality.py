import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ----------------------------
# BASE DIRECTORY (DEPLOYMENT FIX)
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(page_title="Diet Quality", layout="wide")

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

    .stApp,
    [data-testid="stAppViewContainer"],
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
# TITLE
# ----------------------------
st.title("Diet Quality")

# ----------------------------
# BANNER IMAGE (FIXED + DEPLOYMENT SAFE)
# ----------------------------
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
df = pd.read_csv(os.path.join(BASE_DIR, "dataset.csv"))

# ----------------------------
# SIDEBAR FILTERS
# ----------------------------
st.sidebar.header("Filters")

school = st.sidebar.multiselect("School", df["school"].dropna().unique())
school_code = st.sidebar.multiselect("School Code", df["school_code"].dropna().unique())
age = st.sidebar.multiselect("Age", df["age"].dropna().unique())
sex = st.sidebar.multiselect("Sex", df["sex"].dropna().unique())
academic_level = st.sidebar.multiselect("Academic Level", df["academic_level"].dropna().unique())
ses_level = st.sidebar.multiselect("SES Level", df["ses_level"].dropna().unique())
bmi_category = st.sidebar.multiselect("BMI Category", df["BMI_category"].dropna().unique())

# ----------------------------
# FILTER DATA
# ----------------------------
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
apply_filter("BMI_category", bmi_category)

# ----------------------------
# TREEMAP FUNCTION
# ----------------------------
def make_tree(cols):

    cols = [c for c in cols if c in filtered_df.columns]

    label_map = {
        "Cooking Method - Cooked (Dry)": "Cooked (Dry)",
        "Cooking Method - Cooked (Wet)": "Cooked (Wet)",
        "Cooking Method - Fried": "Fried",
        "Cooking Method - Other / Mixed": "Other / Mixed",
        "Cooking Method - Processed / Industrial": "Processed / Industrial",
        "Cooking Method - Raw / Salad": "Raw / Salad",

        "Energy Density - Balanced": "Balanced",
        "Energy Density - High energy, balanced": "High energy, balanced",
        "Energy Density - High energy, low nutrient": "High energy, low nutrient",
        "Energy Density - Low energy, high nutrient": "Low energy, high nutrient",
        "Energy Density - Low energy, low nutrient": "Low energy, low nutrient",

        "Food Group - Animal Protein & Processed Protein": "Animal Protein",
        "Food Group - Cereals & Grains": "Cereals",
        "Food Group - Dairy & Fats": "Dairy & Fats",
        "Food Group - Fruits": "Fruits",
        "Food Group - Sugary / Snack / Dessert / Beverage / Condiment": "Sugary/Snack",
        "Food Group - Vegetables & Plant-based": "Vegetables",

        "NOVA Category - Minimally processed": "Minimally processed",
        "NOVA Category - Processed": "Processed",
        "NOVA Category - Processed culinary ingredient": "Processed ingredient",
        "NOVA Category - Ultra-processed": "Ultra-processed",

        "Traditional vs Modern - Mixed / Fusion": "Fusion",
        "Traditional vs Modern - Modern": "Modern",
        "Traditional vs Modern - Traditional": "Traditional"
    }

    green = "#00bf63"
    red = "#db4a2b"
    gray = "#888888"

    desirable = {
        "Cooked (Dry)", "Cooked (Wet)", "Raw / Salad",
        "Balanced", "Low energy, high nutrient",
        "Cereals", "Fruits", "Vegetables",
        "Minimally processed", "Traditional"
    }

    undesirable = {
        "Fried", "Processed / Industrial",
        "High energy, low nutrient",
        "Sugary/Snack",
        "Ultra-processed", "Processed"
    }

    data = filtered_df[cols].sum().reset_index()
    data.columns = ["Category", "Value"]

    data["Category"] = data["Category"].map(label_map).fillna(data["Category"])

    def color(cat):
        if cat in desirable:
            return green
        elif cat in undesirable:
            return red
        return gray

    data["Color"] = data["Category"].apply(color)

    fig = px.treemap(
        data,
        path=["Category"],
        values="Value",
        color="Category",
        color_discrete_map=dict(zip(data["Category"], data["Color"]))
    )

    fig.update_traces(
        texttemplate="<b>%{label}</b><br>%{percentRoot:.1%}",
        textfont=dict(size=20, color="black"),
        hovertemplate="<b>%{label}</b><br>Value: %{value}<br>%{percentRoot:.1%}<extra></extra>"
    )

    fig.update_layout(
        paper_bgcolor="#000000",
        plot_bgcolor="#000000",
        font=dict(color="#fcfaf4"),
        margin=dict(t=10, l=0, r=0, b=0)
    )

    st.plotly_chart(fig, use_container_width=True)

# ----------------------------
# TREEMAPS
# ----------------------------
st.subheader("Cooking Methods")
make_tree([
    "Cooking Method - Cooked (Dry)",
    "Cooking Method - Cooked (Wet)",
    "Cooking Method - Fried",
    "Cooking Method - Other / Mixed",
    "Cooking Method - Processed / Industrial",
    "Cooking Method - Raw / Salad"
])

st.subheader("Energy Density")
make_tree([
    "Energy Density - Balanced",
    "Energy Density - High energy, balanced",
    "Energy Density - High energy, low nutrient",
    "Energy Density - Low energy, high nutrient",
    "Energy Density - Low energy, low nutrient"
])

st.subheader("Food Groups")
make_tree([
    "Food Group - Animal Protein & Processed Protein",
    "Food Group - Cereals & Grains",
    "Food Group - Dairy & Fats",
    "Food Group - Fruits",
    "Food Group - Sugary / Snack / Dessert / Beverage / Condiment",
    "Food Group - Vegetables & Plant-based"
])

st.subheader("NOVA Categories")
make_tree([
    "NOVA Category - Minimally processed",
    "NOVA Category - Processed",
    "NOVA Category - Processed culinary ingredient",
    "NOVA Category - Ultra-processed"
])

st.subheader("Traditional vs Modern")
make_tree([
    "Traditional vs Modern - Mixed / Fusion",
    "Traditional vs Modern - Modern",
    "Traditional vs Modern - Traditional"
])