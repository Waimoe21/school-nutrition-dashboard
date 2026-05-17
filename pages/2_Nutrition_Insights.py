import pandas as pd
import streamlit as st
import altair as alt
import re
import os

# ----------------------------
# BASE DIRECTORY (DEPLOYMENT FIX)
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(
    page_title="Nutrition Dashboard",
    layout="wide"
)

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
st.title("Nutrition Insights")

# ----------------------------
# BANNER IMAGE (FIXED + DEPLOYMENT SAFE)
# ----------------------------
col1, col2, col3 = st.columns([0.5, 3, 0.5])

with col2:
    banner_path = os.path.join("pages", "banner.png")

    if os.path.exists(banner_path):
        st.image(banner_path, width=700)
    else:
        st.error(f"Missing banner image: {banner_path}")

st.markdown("<br>", unsafe_allow_html=True)

# ----------------------------
# LOAD DATA (FIXED PATH)
# ----------------------------
df = pd.read_csv(os.path.join(BASE_DIR, "dataset.csv"))

# ----------------------------
# NUTRIENT COLUMNS
# ----------------------------
nutrient_cols = [
    "energy_kcal_diff",
    "carb_g_diff",
    "protein_g_diff",
    "fat_g_diff",
    "saturated_fat_g_diff",
    "sugar_g_diff",
    "fiber_g_diff",
    "sodium_mg_diff",
    "iron_mg_diff",
    "folate_ug_diff",
    "calcium_mg_diff",
    "vitamin_a_ug_diff",
    "vitamin_c_mg_diff",
    "zinc_mg_diff",
    "potassium_mg_diff",
    "magnesium_mg_diff",
    "iodine_ug_diff",
    "cholesterol_mg_diff",
    "vitamin_b12_ug_diff",
    "vitamin_d_ug_diff",
    "vitamin_b6_mg_diff",
    "thiamin_b1_mg_diff",
    "caffeine_mg_diff"
]

# keep only valid columns (prevents crash if dataset differs)
nutrient_cols = [c for c in nutrient_cols if c in df.columns]

# ----------------------------
# CLEAN LABELS
# ----------------------------
def clean_label(text: str) -> str:
    text = text.replace("_diff", "")

    match = re.search(r"_(kcal|mg|ug|g)$", text)
    unit = ""

    if match:
        unit = match.group(1)
        text = text[: -(len(unit) + 1)]

    unit_map = {
        "g": "g",
        "mg": "mg",
        "ug": "µg",
        "kcal": "kcal"
    }

    text = text.replace("_", " ").title()

    if unit:
        return f"{text} ({unit_map[unit]})"

    return text

# ----------------------------
# SIDEBAR FILTER
# ----------------------------
st.sidebar.header("Filters")

filter_options = {
    "All": "All",
    "sex": "Sex",
    "school": "School",
    "BMI_category": "BMI Category",
    "academic_level": "Academic Level",
    "ses_level": "SES Level"
}

reverse_filter = {v: k for k, v in filter_options.items()}

selected_display = st.sidebar.selectbox(
    "Group by",
    list(filter_options.values())
)

group_by = reverse_filter[selected_display]

# ----------------------------
# FILTERING
# ----------------------------
if group_by == "All":
    filtered_df = df.copy()
    group_label = "All Students"

else:
    if group_by in df.columns:
        selected_value = st.sidebar.selectbox(
            f"Select {filter_options[group_by]}",
            sorted(df[group_by].dropna().unique())
        )

        filtered_df = df[df[group_by] == selected_value]
        group_label = f"{filter_options[group_by]}: {selected_value}"
    else:
        filtered_df = df.copy()
        group_label = "All Students"

# ----------------------------
# AVERAGES
# ----------------------------
avg_values = filtered_df[nutrient_cols].mean().reset_index()
avg_values.columns = ["nutrient", "average_difference"]
avg_values["nutrient"] = avg_values["nutrient"].apply(clean_label)

# ----------------------------
# TITLE
# ----------------------------
st.markdown(f"## Average Nutrient Difference — {group_label}")
st.markdown("---")

# ----------------------------
# BAR CHART (GREEN + RED ACCENTS)
# ----------------------------
bar = alt.Chart(avg_values).mark_bar(
    color="#00bf63"
).encode(
    y=alt.Y("nutrient:N", sort="-x", title="Nutrient"),
    x=alt.X("average_difference:Q", title="Average Difference"),
    tooltip=[
        alt.Tooltip("nutrient:N"),
        alt.Tooltip("average_difference:Q", format=".2f")
    ]
)

text = alt.Chart(avg_values).mark_text(
    align="left",
    baseline="middle",
    dx=5,
    color="#db4a2b"
).encode(
    y="nutrient:N",
    x="average_difference:Q",
    text=alt.Text("average_difference:Q", format=".2f")
)

chart = (bar + text).properties(
    height=700,
    background="#000000"
).configure_view(
    stroke=None
).configure_axis(
    grid=False,
    labelColor="#fcfaf4",
    titleColor="#fcfaf4",
    domainColor="#fcfaf4",
    tickColor="#fcfaf4"
).configure_title(
    color="#fcfaf4"
)

st.altair_chart(chart, use_container_width=True)
