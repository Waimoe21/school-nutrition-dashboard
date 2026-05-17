import pandas as pd
import folium
import streamlit as st
from streamlit_folium import st_folium
import unicodedata
import altair as alt
import os

# ----------------------------
# BASE DIRECTORY (DEPLOYMENT FIX)
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ----------------------------
# PAGE CONFIG
# ----------------------------
st.set_page_config(layout="wide")

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
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Overview")

# ----------------------------
# BANNER IMAGE (ROBUST STREAMLIT FIX)
# ----------------------------
col1, col2, col3 = st.columns([0.5, 3, 0.5])


# ----------------------------
# LOAD DATA (FIXED PATH)
# ----------------------------
df = pd.read_csv(os.path.join(BASE_DIR, "dataset.csv"))

# ----------------------------
# CLEAN TEXT
# ----------------------------
def clean_text(x):
    if pd.isna(x):
        return x
    x = str(x)
    x = unicodedata.normalize("NFC", x)
    x = x.strip()
    x = " ".join(x.split())
    return x

df["school"] = df["school"].apply(clean_text)

for col in ["BMI_category", "ses_level"]:
    if col in df.columns:
        df[col] = df[col].apply(clean_text)

# ----------------------------
# SIDEBAR FILTERS
# ----------------------------
st.sidebar.header("Filters")

selected_schools = st.sidebar.multiselect("School", df["school"].dropna().unique())

selected_sex = st.sidebar.multiselect(
    "Sex",
    df["sex"].dropna().unique(),
    default=df["sex"].dropna().unique()
)

selected_bmi = st.sidebar.multiselect(
    "BMI Category",
    df["BMI_category"].dropna().unique(),
    default=df["BMI_category"].dropna().unique()
)

selected_ses = st.sidebar.multiselect(
    "SES Level",
    df["ses_level"].dropna().unique(),
    default=df["ses_level"].dropna().unique()
)

# ----------------------------
# FILTER DATA
# ----------------------------
filtered_df = df[
    (df["sex"].isin(selected_sex)) &
    (df["BMI_category"].isin(selected_bmi)) &
    (df["ses_level"].isin(selected_ses))
]

if selected_schools:
    filtered_df = filtered_df[filtered_df["school"].isin(selected_schools)]

# ----------------------------
# METRICS
# ----------------------------
avg_nova = filtered_df["nova_score"].mean()
avg_food = filtered_df["food_group_score"].mean()
avg_energy = filtered_df["energy_density_score"].mean()
avg_nutrient = filtered_df["nutrient_score"].mean()

col1, col2, col3, col4, col5 = st.columns([1.2, 1, 1, 1, 1])

with col1:
    st.metric("Total Students", len(filtered_df))

with col2:
    st.metric("NOVA Score", f"{avg_nova:.1f}/100")

with col3:
    st.metric("Food Group Score", f"{avg_food:.1f}/100")

with col4:
    st.metric("Energy Density Score", f"{avg_energy:.1f}/100")

with col5:
    st.metric("Nutrient Score", f"{avg_nutrient:.1f}/100")

# ----------------------------
# CHART HELPERS
# ----------------------------
def horizontal_bar_chart(data, x, y, title):
    return (
        alt.Chart(data)
        .mark_bar(color="#00bf63")
        .encode(
            y=alt.Y(x, sort=None, axis=alt.Axis(labelColor="#fcfaf4", titleColor="#fcfaf4")),
            x=alt.X(y, axis=alt.Axis(labelColor="#fcfaf4", titleColor="#fcfaf4"))
        )
        .properties(height=250, title=alt.TitleParams(title, color="#fcfaf4"))
    )

def transparent_chart(chart):
    return (
        chart.configure_view(fill="#000000", stroke=None)
        .configure(background="#000000")
        .configure_axis(
            labelColor="#fcfaf4",
            titleColor="#fcfaf4",
            grid=False,
            domainColor="#fcfaf4",
            tickColor="#fcfaf4"
        )
        .configure_title(color="#fcfaf4")
    )

def plot_distribution(column):
    data = filtered_df[column].value_counts().reset_index()
    data.columns = ["category", "count"]
    return data

# ----------------------------
# DISTRIBUTIONS
# ----------------------------
filtered_df["age"] = filtered_df["age"].astype(str)
filtered_df["academic_level"] = filtered_df["academic_level"].astype(str)

age_order = sorted(filtered_df["age"].unique())
academic_order = sorted(filtered_df["academic_level"].unique())

col1, col2 = st.columns(2)

with col1:
    age_data = plot_distribution("age")
    st.altair_chart(
        transparent_chart(
            horizontal_bar_chart(age_data, "category", "count", "Age Distribution")
        ),
        use_container_width=True
    )

with col2:
    academic_data = plot_distribution("academic_level")
    st.altair_chart(
        transparent_chart(
            horizontal_bar_chart(academic_data, "category", "count", "Academic Level Distribution")
        ),
        use_container_width=True
    )

col3, col4, col5 = st.columns(3)

with col3:
    st.altair_chart(
        transparent_chart(
            horizontal_bar_chart(plot_distribution("sex"), "category", "count", "Sex Distribution")
        ),
        use_container_width=True
    )

with col4:
    st.altair_chart(
        transparent_chart(
            horizontal_bar_chart(plot_distribution("BMI_category"), "category", "count", "BMI Category")
        ),
        use_container_width=True
    )

with col5:
    st.altair_chart(
        transparent_chart(
            horizontal_bar_chart(plot_distribution("ses_level"), "category", "count", "SES Level")
        ),
        use_container_width=True
    )

# ----------------------------
# MAP
# ----------------------------
school_summary = (
    filtered_df.groupby(["school", "school_code", "latitude", "longitude", "sex"])
    .size()
    .reset_index(name="count")
)

school_pivot = school_summary.pivot_table(
    index=["school", "school_code", "latitude", "longitude"],
    columns="sex",
    values="count",
    fill_value=0
).reset_index()

if "M" not in school_pivot.columns:
    school_pivot["M"] = 0
if "F" not in school_pivot.columns:
    school_pivot["F"] = 0

if len(school_pivot) > 0:
    m = folium.Map(
        location=[school_pivot["latitude"].mean(), school_pivot["longitude"].mean()],
        zoom_start=12
    )
else:
    m = folium.Map(location=[20.0, 94.9], zoom_start=12)

for _, row in school_pivot.iterrows():
    total = int(row["M"]) + int(row["F"])

    folium.CircleMarker(
        location=[row["latitude"], row["longitude"]],
        radius=5,
        color="#00bf63",
        fill=True,
        fill_color="#00bf63",
        fill_opacity=0.9,
        tooltip=f"{row['school']} | Total: {total}",
        popup=folium.Popup(
            f"{row['school']}<br>Total: {total}<br>M: {row['M']}<br>F: {row['F']}",
            max_width=250
        )
    ).add_to(m)

st_folium(m, width=1800, height=550)
