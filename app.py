"""
TESS Transit Explorer — Entry Point / Landing Page
"""

import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(
    page_title="TESS Transit Explorer",
    page_icon="🔭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Hero Header ──────────────────────────────────────────────────────────────
st.title("🔭 TESS Transit Explorer")
st.markdown(
    """
    NASA's **Transiting Exoplanet Survey Satellite (TESS)** surveys the brightest
    ~200,000 stars for telltale dips in brightness — **planetary transits** — caused
    by worlds passing in front of their host star.

    This app lets you fetch live TESS light curves from the
    [MAST archive](https://mast.stsci.edu), detect periodic transit signals via the
    **Box Least Squares (BLS)** periodogram, and visualise the phase-folded transit
    profile — all interactively in your browser.
    """,
    unsafe_allow_html=False,
)

st.divider()

# ── Mission Stats ─────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("🌟 Stars Observed",    "~500 million")
col2.metric("🪐 Planet Candidates", "8 000+")
col3.metric("✅ Confirmed Planets", "1 000+")
col4.metric("📡 TESS Sectors",      "96 (ongoing)")

st.divider()

# ── Quick-Start Targets ───────────────────────────────────────────────────────
st.subheader("⚡ Quick-Start: Famous TESS Targets")
data_path = Path(__file__).parent / "data" / "famous_targets.csv"
if data_path.exists():
    df = pd.read_csv(data_path)
    df.index = df.index + 1
    st.dataframe(
        df.rename(columns={
            "name": "Star / System",
            "tic_id": "TIC ID",
            "description": "Why It's Famous",
            "known_period_days": "Known Period (days)",
        }),
        use_container_width=True,
        hide_index=False,
    )
    st.caption("Copy any TIC ID into the **Transit Explorer** page to get started!")

st.divider()

# ── How It Works ─────────────────────────────────────────────────────────────
st.subheader("🧭 How It Works")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(
        "### 1️⃣ Fetch\n"
        "Enter a star name or TIC ID. The app downloads its TESS light curve(s) "
        "directly from the NASA MAST archive using `lightkurve`."
    )
with c2:
    st.markdown(
        "### 2️⃣ Detect\n"
        "The **BLS periodogram** scans a grid of trial periods to find the strongest "
        "periodic dip — your candidate planet's orbital period."
    )
with c3:
    st.markdown(
        "### 3️⃣ Visualise\n"
        "Phase-fold the light curve at the best period to reveal the transit shape, "
        "depth, and duration. Estimate the planet's radius from the depth!"
    )

st.divider()
st.caption(
    "Data: [NASA MAST](https://mast.stsci.edu) · "
    "[NASA Exoplanet Archive](https://exoplanetarchive.ipac.caltech.edu) · "
    "Built with [lightkurve](https://docs.lightkurve.org) & [Streamlit](https://streamlit.io)"
)
