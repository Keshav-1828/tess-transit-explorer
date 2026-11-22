"""
pages/3_ℹ️_About.py
---------------------
TESS mission background and app documentation.
"""

import streamlit as st

st.set_page_config(page_title="About TESS · Transit Explorer", page_icon="ℹ️", layout="wide")

st.title("ℹ️ About TESS & This App")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
## The Transiting Exoplanet Survey Satellite

**TESS** was launched on 18 April 2018 aboard a SpaceX Falcon 9. Its primary
mission is to perform an all-sky survey for transiting exoplanets orbiting
the nearest, brightest stars — perfect targets for follow-up characterisation
with the James Webb Space Telescope (JWST).

### How Transits Work

When a planet crosses in front of its host star (from our line of sight), it
blocks a small fraction of the starlight, causing a brief dip in brightness.
The depth of this dip tells us the **planet's radius** relative to the star:

$$
\\left(\\frac{R_p}{R_\\star}\\right)^2 = \\delta$$

where $\\delta$ is the transit depth. For Earth around the Sun, $\\delta \\approx 84$ ppm.

### TESS Observing Strategy

TESS divides the sky into 26 **sectors**, each observed for ~27 days using its
four wide-field cameras (each 24° × 24°). Stars near the ecliptic poles receive
continuous coverage for up to ~350 days.

### Data Products

| Product | Description |
|---|---|
| **PDCSAP flux** | Pre-search Data Conditioning SAP — systematic-corrected photometry |
| **SAP flux** | Simple Aperture Photometry — raw summed pixel flux |
| **Target Pixel File (TPF)** | Per-cadence postage-stamp pixel images |
| **Full Frame Images (FFI)** | Complete 24° × 24° snapshots at 10-min cadence |

### The Box Least Squares (BLS) Algorithm

BLS is the standard algorithm for detecting periodic transit signals in
photometric time series. It models the transit as a rectangular dip of
depth $\\delta$, duration $q$, and period $P$, then maximises the
signal-to-noise over a dense grid of $(P, q)$ pairs.

---

## App Architecture

```
tess-transit-explorer/
├── app.py                      ← Landing page
├── modules/
│   ├── mast_api.py             ← MAST / lightkurve download layer
│   ├── processing.py           ← Flatten, BLS, phase-fold
│   └── plotting.py             ← Plotly figure builders
└── pages/
    ├── 1_🔭_Transit_Explorer.py ← Interactive transit search
    ├── 2_📊_Catalog_Trends.py   ← Population statistics
    └── 3_ℹ️_About.py           ← This page
```

## Data Sources

- **[NASA MAST Archive](https://mast.stsci.edu)** — official repository for all TESS data
- **[NASA Exoplanet Archive](https://exoplanetarchive.ipac.caltech.edu)** — confirmed planet parameters
- **[lightkurve](https://docs.lightkurve.org)** — Python package for Kepler/TESS analysis
- **[astroquery](https://astroquery.readthedocs.io)** — Python interface to astronomical archives
    """)

with col2:
    st.markdown("### 🔗 Useful Links")
    st.markdown("""
- [TESS Mission Page](https://tess.mit.edu)
- [MAST Portal](https://mast.stsci.edu)
- [ExoFOP-TESS](https://exofop.ipac.caltech.edu/tess/)
- [lightkurve Docs](https://docs.lightkurve.org)
- [NASA Exoplanet Archive](https://exoplanetarchive.ipac.caltech.edu)
- [Planet Hunters TESS](https://www.zooniverse.org/projects/nora-dot-eisner/planet-hunters-tess)
    """)

    st.markdown("### 📦 Dependencies")
    st.code("""
lightkurve>=2.4.2
astropy>=6.1.0
astroquery>=0.4.7
plotly>=5.22.0
streamlit>=1.35.0
pandas>=2.2.0
numpy>=1.26.0
    """, language="text")

    st.markdown("### 📄 License")
    st.markdown("MIT License — free to use, modify, and share.")
