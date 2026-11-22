"""
pages/2_📊_Catalog_Trends.py
------------------------------
Population-level exoplanet statistics from the NASA Exoplanet Archive.
Requires internet — data is cached for 24 hours.
"""

import sys
from pathlib import Path
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

st.set_page_config(page_title="Catalog Trends · TESS", page_icon="📊", layout="wide")
st.title("📊 Exoplanet Catalog Trends")
st.markdown(
    "Population-level statistics for **confirmed transiting exoplanets** "
    "from the [NASA Exoplanet Archive](https://exoplanetarchive.ipac.caltech.edu)."
)


@st.cache_data(ttl=86_400, show_spinner="🌌 Querying NASA Exoplanet Archive…")
def load_confirmed_planets() -> pd.DataFrame:
    """Load confirmed transiting planet parameters from NASA Exoplanet Archive."""
    try:
        from astroquery.ipac.nexsci.nasa_exoplanet_archive import NasaExoplanetArchive
        result = NasaExoplanetArchive.query_criteria(
            table="pscomppars",
            select="pl_name,hostname,discoverymethod,pl_orbper,pl_rade,pl_masse,st_teff,disc_year,disc_facility",
            where="discoverymethod like 'Transit%'",
        )
        return result.to_pandas()
    except Exception as e:
        st.warning(f"Could not reach NASA Exoplanet Archive: {e}")
        return pd.DataFrame()


df = load_confirmed_planets()

if df.empty:
    st.error("No data loaded. Check your internet connection and try again.")
    st.stop()

# Clean up
df = df.dropna(subset=["pl_orbper", "pl_rade"])
df["disc_year"] = pd.to_numeric(df["disc_year"], errors="coerce")
df["st_teff"]   = pd.to_numeric(df["st_teff"],   errors="coerce")

st.success(f"✅ Loaded {len(df):,} confirmed transiting planets.")

# ── KPIs ──────────────────────────────────────────────────────────────────────
k1, k2, k3, k4 = st.columns(4)
k1.metric("Total Planets",      f"{len(df):,}")
k2.metric("Multi-planet Systems", f"{df['hostname'].duplicated(keep=False).sum():,}")
k3.metric("Median Period",      f"{df['pl_orbper'].median():.1f} days")
k4.metric("Median Radius",      f"{df['pl_rade'].median():.2f} R⊕")

st.divider()

# ── Plots ─────────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    st.subheader("Planet Radius vs. Orbital Period")
    fig = px.scatter(
        df,
        x="pl_orbper",
        y="pl_rade",
        color="st_teff",
        color_continuous_scale="Plasma",
        labels={
            "pl_orbper": "Orbital Period (days)",
            "pl_rade":   "Planet Radius (R⊕)",
            "st_teff":   "Host Star Teff (K)",
        },
        hover_name="pl_name",
        log_x=True,
        opacity=0.6,
        template="plotly_dark",
    )
    fig.update_traces(marker=dict(size=4))
    fig.update_layout(height=420)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "The **radius gap** (~1.5–2.0 R⊕) separates super-Earths from sub-Neptunes — "
        "likely caused by photoevaporation."
    )

with col2:
    st.subheader("Planet Radius Distribution")
    fig2 = go.Figure()
    fig2.add_trace(go.Histogram(
        x=df["pl_rade"],
        nbinsx=60,
        marker_color="#6C8EBF",
        name="All planets",
    ))
    fig2.update_layout(
        template="plotly_dark",
        xaxis_title="Planet Radius (R⊕)",
        yaxis_title="Count",
        height=420,
        xaxis=dict(range=[0, 25]),
    )
    # Annotate the radius gap
    fig2.add_vrect(x0=1.5, x1=2.0, fillcolor="#EF5350", opacity=0.15,
                   annotation_text="Radius gap", annotation_position="top left")
    st.plotly_chart(fig2, use_container_width=True)

st.divider()
col3, col4 = st.columns(2)

with col3:
    st.subheader("Discoveries Per Year")
    year_counts = df["disc_year"].dropna().astype(int).value_counts().sort_index()
    fig3 = go.Figure(go.Bar(
        x=year_counts.index,
        y=year_counts.values,
        marker_color="#6C8EBF",
    ))
    fig3.update_layout(
        template="plotly_dark",
        xaxis_title="Discovery Year",
        yaxis_title="New Planets Confirmed",
        height=380,
    )
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("Top Discovery Facilities")
    fac_counts = df["disc_facility"].value_counts().head(10)
    fig4 = go.Figure(go.Bar(
        x=fac_counts.values[::-1],
        y=fac_counts.index[::-1],
        orientation="h",
        marker_color="#6C8EBF",
    ))
    fig4.update_layout(
        template="plotly_dark",
        xaxis_title="Confirmed Planets",
        height=380,
        margin=dict(l=200),
    )
    st.plotly_chart(fig4, use_container_width=True)

st.divider()
with st.expander("📋 Raw Data Table"):
    st.dataframe(
        df[["pl_name", "hostname", "pl_orbper", "pl_rade", "pl_masse", "st_teff", "disc_year"]]
        .rename(columns={
            "pl_name":   "Planet",
            "hostname":  "Host Star",
            "pl_orbper": "Period (days)",
            "pl_rade":   "Radius (R⊕)",
            "pl_masse":  "Mass (M⊕)",
            "st_teff":   "Host Teff (K)",
            "disc_year": "Year",
        })
        .sort_values("Period (days)"),
        use_container_width=True,
        hide_index=True,
    )
