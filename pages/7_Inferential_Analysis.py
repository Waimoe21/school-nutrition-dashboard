import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import statsmodels.api as sm
from scipy.stats import pearsonr
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import os

# =========================================================
# BASE PATH (DEPLOYMENT SAFE)
# =========================================================
BASE_DIR = os.path.dirname(__file__)

dataset_path = os.path.join(BASE_DIR, "dataset.csv")

# FIXED BANNER PATH
banner_path = os.path.join("pages", "banner.png")

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Inferential Analysis",
    layout="wide"
)

# =========================================================
# GLOBAL STYLE
# =========================================================
st.markdown(
    """
    <style>
    html, body, [class*="css"] {
        background-color: #000000;
        color: #fcfaf4;
        font-family: 'Open Sauce', sans-serif;
    }

    .stApp {
        background-color: #000000;
    }

    section[data-testid="stSidebar"] {
        background-color: #000000;
    }

    h1, h2, h3, h4, h5, h6, p, label, div {
        color: #fcfaf4 !important;
    }

    .block-container {
        padding-top: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# COLOR SYSTEM
# =========================================================
NEG_COLOR = "#db4a2b"
NEU_COLOR = "#111111"
NEU_COLOR2 = "#FFFFFF"
POS_COLOR = "#00bf63"

# =========================================================
# LOAD DATA
# =========================================================
df = pd.read_csv(dataset_path)

# =========================================================
# TITLE + BANNER (FIXED)
# =========================================================
st.title("Inferential Analysis")

col1, col2, col3 = st.columns([0.5, 3, 0.5])

with col2:
    if os.path.exists(banner_path):
        st.image(banner_path, width=700)
    else:
        st.error(f"Missing banner image: {banner_path}")
# =========================================================
# VARIABLES
# =========================================================
columns = [
    "BMI_percentile",
    "food_knowledge_percent",
    "ses_score",
    "nova_score",
    "food_group_score",
    "energy_density_score",
    "nutrient_score",
    "age",
    "allowance_received_amt_mmk",
    "allowance_expenditure_amt_mmk",
    "breakfast_skipping_freq",
    "lunch_skipping_freq",
    "dinner_skipping_freq"
]

corr_df = df[columns].replace([np.inf, -np.inf], np.nan).dropna()

# =========================================================
# CORRELATION + P VALUES
# =========================================================
corr_matrix = corr_df.corr()

p_matrix = pd.DataFrame(np.ones((len(columns), len(columns))),
                        columns=columns, index=columns)

for i in range(len(columns)):
    for j in range(i + 1, len(columns)):
        c1, c2 = columns[i], columns[j]
        temp = corr_df[[c1, c2]].dropna()
        r, p = pearsonr(temp[c1], temp[c2])
        p_matrix.loc[c1, c2] = p
        p_matrix.loc[c2, c1] = p

# =========================================================
# HEATMAP ANNOTATIONS
# =========================================================
annotation_text = []

for i in range(len(columns)):
    row = []
    for j in range(len(columns)):
        r = corr_matrix.iloc[i, j]
        p = p_matrix.iloc[i, j]

        text = f"{r:.2f}"
        if i != j and p < 0.05 and abs(r) >= 0.15:
            text += " ★"
        row.append(text)
    annotation_text.append(row)

# =========================================================
# CORRELATION HEATMAP
# =========================================================
st.subheader("Correlation Matrix")

fig = go.Figure()

fig.add_trace(
    go.Heatmap(
        z=corr_matrix.values,
        x=columns,
        y=columns,
        text=annotation_text,
        texttemplate="%{text}",
        textfont=dict(size=12, color="#fcfaf4"),
        zmin=-1,
        zmax=1,
        colorscale=[
            [0.0, NEG_COLOR],
            [0.5, NEU_COLOR],
            [1.0, POS_COLOR]
        ],
        colorbar=dict(
            title="r",
            tickfont=dict(color="#fcfaf4")
        ),
        hovertemplate="<b>%{x}</b> ↔ <b>%{y}</b><br>r=%{z:.3f}<extra></extra>"
    )
)

fig.update_layout(
    paper_bgcolor="black",
    plot_bgcolor="black",
    font=dict(color="#fcfaf4"),
    height=800
)

fig.update_xaxes(tickangle=45, showgrid=False)
fig.update_yaxes(showgrid=False)

st.plotly_chart(fig, use_container_width=True)

st.caption("★ p < 0.05 and |r| ≥ 0.15")

# =========================================================
# REGRESSION
# =========================================================
st.markdown("---")
st.title("Multiple Regression Analysis")

target = st.selectbox(
    "Select Target Variable",
    ["BMI_percentile", "food_knowledge_percent", "nutrient_score"]
)

predictors = [c for c in columns if c != target]

reg_df = df[[target] + predictors].replace([np.inf, -np.inf], np.nan).dropna()

X = sm.add_constant(reg_df[predictors])
y = reg_df[target]

model = sm.OLS(y, X).fit()

st.text(model.summary())

coef_df = pd.DataFrame({
    "Variable": model.params.index,
    "Coefficient": model.params.values,
    "p-value": model.pvalues.values
})

st.dataframe(coef_df, use_container_width=True)

col1, col2, col3 = st.columns(3)
col1.metric("R²", f"{model.rsquared:.3f}")
col2.metric("Adj R²", f"{model.rsquared_adj:.3f}")
col3.metric("F-stat", f"{model.fvalue:.2f}")

reg_df["Predicted"] = model.predict(X)

st.subheader("Actual vs Predicted")
st.scatter_chart(reg_df[[target, "Predicted"]])

# =========================================================
# CLUSTERING
# =========================================================
st.markdown("---")
st.title("Clustering Analysis")

cluster_cols = [
    "allowance_received_amt_mmk",
    "allowance_expenditure_amt_mmk",
    "breakfast_skipping_freq",
    "lunch_skipping_freq",
    "dinner_skipping_freq",
    "nova_score",
    "food_group_score",
    "energy_density_score"
]

cluster_df = df[cluster_cols].replace([np.inf, -np.inf], np.nan).dropna()

scaler = StandardScaler()
X_scaled = scaler.fit_transform(cluster_df)

k = st.slider("Number of clusters", 2, 6, 3)

kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
cluster_df["Cluster"] = kmeans.fit_predict(X_scaled)

if k == 3:
    cluster_df["Cluster"] = cluster_df["Cluster"].replace({0: 2, 2: 0})

st.dataframe(cluster_df.groupby("Cluster").mean(), use_container_width=True)

# =========================================================
# PCA
# =========================================================
pca = PCA(n_components=2)
components = pca.fit_transform(X_scaled)

cluster_df["PCA1"] = components[:, 0]
cluster_df["PCA2"] = components[:, 1]

# =========================================================
# CLUSTER VISUAL
# =========================================================
fig = go.Figure()

colors = {
    0: NEG_COLOR,
    1: NEU_COLOR2,
    2: POS_COLOR
}

for c in sorted(cluster_df["Cluster"].unique()):
    sub = cluster_df[cluster_df["Cluster"] == c]

    fig.add_trace(
        go.Scatter(
            x=sub["PCA1"],
            y=sub["PCA2"],
            mode="markers",
            name=f"Cluster {c}",
            marker=dict(color=colors.get(c, "#888888"), size=8)
        )
    )

fig.update_layout(
    paper_bgcolor="black",
    plot_bgcolor="black",
    font=dict(color="#fcfaf4"),
    height=600
)

fig.update_xaxes(showgrid=False)
fig.update_yaxes(showgrid=False)

st.plotly_chart(fig, use_container_width=True)

with st.expander("Clustered Dataset"):
    st.dataframe(cluster_df, use_container_width=True)
