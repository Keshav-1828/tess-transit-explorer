"""
modules/mast_api.py
--------------------
Thin wrapper around lightkurve for fetching TESS data from MAST.
All heavy I/O is wrapped in @st.cache_data to avoid re-downloading.
"""

from __future__ import annotations

import streamlit as st
import lightkurve as lk


@st.cache_data(show_spinner="📡 Fetching light curve from MAST archive…")
def search_and_download(
    target: str,
    sector: int | None = None,
    cadence: str = "2min",
) -> tuple:
    """
    Search MAST for TESS light curves and download all available sectors.

    Parameters
    ----------
    target  : Star name (e.g. "Pi Mensae") or "TIC <id>" string.
    sector  : Specific TESS sector number, or None for all sectors.
    cadence : "2min" (short cadence) or "fast" (20-sec).

    Returns
    -------
    (lc, sectors) where lc is a stitched LightCurve and sectors is a list
    of sector numbers that were found.  Returns (None, []) if no data.
    """
    result = lk.search_lightcurve(
        target, mission="TESS", sector=sector, cadence=cadence
    )
    if len(result) == 0:
        return None, []

    sectors = list(result.table["sector"].data)
    lc_col = result.download_all(flux_column="pdcsap_flux")
    if lc_col is None:
        return None, sectors

    lc = lc_col.stitch()
    return lc, sectors


@st.cache_data(show_spinner="📐 Loading Target Pixel File…")
def load_tpf(target: str, sector: int):
    """
    Download a Target Pixel File for a given target and sector.
    Returns the TPF object or None if not found.
    """
    result = lk.search_targetpixelfile(
        target, mission="TESS", sector=sector
    )
    if len(result) == 0:
        return None
    return result[0].download()


def available_cadences(target: str) -> list[str]:
    """Return a list of available cadences for a target on MAST."""
    cadences = []
    for c in ("2min", "fast"):
        r = lk.search_lightcurve(target, mission="TESS", cadence=c)
        if len(r) > 0:
            cadences.append(c)
    return cadences or ["2min"]
