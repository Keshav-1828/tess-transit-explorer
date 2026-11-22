"""
pages/1_🔭_Transit_Explorer.py
-------------------------------
Main interactive page: search, download, process, and plot TESS transits.
"""

import sys
from pathlib import Path
import streamlit as st
import pandas as pd

# Allow imports from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.mast_api import search_and_download, load_tpf
from modules.processing import preprocess, run_bls, phase_fold, estimate_planet_radius
from modules.plotting import (
    plot_lightcurve,
    plot_periodogram,
    plot_phase_fold,
    plot_tpf_pixels,
)

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Transit Explorer · TESS", page_icon="🔭", layout="wide")
st.title("🔭 Transit Explorer")
st.markdown(
    "Search any star, fetch its TESS light curve from MAST, detect periodic "
    "transit signals, and visualise the phase-folded transit profile."
)

# ── Load famous targets for quick-pick ───────────────────────────────────────
data_path = Path(__file__).parent.parent / "data" / "famous_targets.csv"
famous_df = pd.read_csv(data_path) if data_path.exists() else pd.DataFrame()

# ── Sidebar: Input controls ───────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Controls")

    if not famous_df.empty:
        quick = st.selectbox(
            "Quick-pick a famous target",
            options=["— type your own —"] + list(famous_df["name"]),
        )
    else:
        quick = "— type your own —"

    default_target = (
        famous_df.loc[famous_df["name"] == quick, "name"].values[0]
        if quick != "— type your own —"
        else "Pi Mensae"
    )

    target = st.text_input(
        "Star name or TIC ID",
        value=default_target,
        help="Examples: 'Pi Mensae', 'TIC 261136679', 'TOI-700'",
    )

    sector_choice = st.selectbox(
        "TESS Sector",
        options=["All"] + list(range(1, 97)),
        help="'All' stitches every available sector together.",
    )
    sector = None if sector_choice == "All" else int(sector_choice)

    st.subheader("🧹 Preprocessing")
    window_length = st.slider(
        "Flatten window length (cadences)",
        min_value=51, max_value=2001, value=901, step=50,
        help="Savitzky-Golay filter window. Longer = less stellar variability removed.",
    )
    sigma = st.slider(
        "Outlier sigma threshold",
        min_value=2.0, max_value=10.0, value=5.0, step=0.5,
    )

    st.subheader("🔍 BLS Periodogram")
    period_range = st.slider(
        "Period search range (days)",
        min_value=0.1, max_value=30.0, value=(0.5, 15.0), step=0.1,
    )
    n_periods = st.select_slider(
        "Period grid resolution",
        options=[1_000, 5_000, 10_000, 20_000],
        value=10_000,
    )

    run_button = st.button("🚀 Fetch & Analyse", type="primary", use_container_width=True)

# ── Main panel ────────────────────────────────────────────────────────────────
if run_button or ("lc_flat" in st.session_state and st.session_state.get("last_target") == target):
    # ── 1. Download ──────────────────────────────────────────────────────────
    with st.spinner("Fetching data from MAST…"):
        lc_raw, sectors_found = search_and_download(target, sector=sector)

    if lc_raw is None:
        st.error(
            f"❌ No TESS 2-min light curves found for **{target}**.\n\n"
            "Try a different sector, check the TIC ID, or switch to a 'fast' cadence target."
        )
        st.stop()

    st.success(
        f"✅ Downloaded {len(lc_raw)} cadences across "
        f"{len(sectors_found)} sector(s): {sectors_found}"
    )

    # ── 2. Preprocess ────────────────────────────────────────────────────────
    with st.spinner("Preprocessing…"):
        lc_flat = preprocess(lc_raw, window_length=window_length, sigma=sigma)

    # ── 3. BLS ───────────────────────────────────────────────────────────────
    with st.spinner("Running BLS periodogram (may take 10–30 s)…"):
        bls, best_period, best_t0, best_depth = run_bls(
            lc_flat,
            period_min=period_range[0],
            period_max=period_range[1],
            n_periods=n_periods,
        )

    # ── 4. Phase fold ────────────────────────────────────────────────────────
    folded_lc = phase_fold(lc_flat, best_period, best_t0)

    # Cache for sidebar re-runs
    st.session_state["lc_flat"]     = lc_flat
    st.session_state["last_target"] = target

    # ── 5. Planet parameter card ─────────────────────────────────────────────
    depth_ppm   = float(best_depth.value) * 1e6 if best_depth is not None else 0.0
    rp_earth    = estimate_planet_radius(depth_ppm)

    st.subheader(f"🪐 Best Transit Signal for **{target}**")
    mc1, mc2, mc3, mc4 = st.columns(4)
    mc1.metric("Orbital Period",   f"{best_period.value:.4f} days")
    mc2.metric("Transit Epoch",    f"BTJD {best_t0.value:.3f}")
    mc3.metric("Transit Depth",    f"{depth_ppm:.0f} ppm")
    mc4.metric("Est. Planet Radius", f"{rp_earth:.2f} R⊕")

    st.caption(
        "⚠️ These are raw BLS estimates, not fitted parameters. "
        "Always inspect the phase-folded profile for false positives (V-shape = likely eclipsing binary)."
    )

    # ── 6. Tabs ──────────────────────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs(["📉 Light Curve", "📡 Periodogram", "🌑 Phase Fold"])

    with tab1:
        st.plotly_chart(
            plot_lightcurve(lc_raw, lc_flat, title=f"TESS Light Curve — {target}"),
            use_container_width=True,
        )
        st.caption(
            "Blue = raw PDCSAP flux | Teal = flattened flux after Savitzky-Golay filtering."
        )

    with tab2:
        st.plotly_chart(
            plot_periodogram(bls, best_period, title=f"BLS Periodogram — {target}"),
            use_container_width=True,
        )
        st.info(
            f"🏆 Peak power at **{best_period.value:.4f} days**. "
            "Harmonics (½×P, 2×P) can appear as secondary peaks — always check the phase fold."
        )

    with tab3:
        st.plotly_chart(
            plot_phase_fold(folded_lc, best_period, best_depth,
                            title=f"Phase-Folded Transit — {target}"),
            use_container_width=True,
        )
        st.markdown(
            "**U-shaped** flat-bottomed dip → likely planet ✅ &nbsp;|&nbsp; "
            "**V-shaped** dip → possible eclipsing binary ⚠️"
        )

else:
    st.info("👈 Enter a star name or TIC ID in the sidebar and click **Fetch & Analyse**.")

    # Show example targets
    if not famous_df.empty:
        st.subheader("💡 Suggested Targets")
        st.dataframe(
            famous_df[["name", "description", "known_period_days"]].rename(columns={
                "name": "Target",
                "description": "Why it's interesting",
                "known_period_days": "Known period (days)",
            }),
            use_container_width=True,
            hide_index=True,
        )
