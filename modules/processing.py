"""
modules/processing.py
----------------------
Core signal-processing routines: flatten, BLS periodogram, phase-fold.
Pure functions — no Streamlit imports, easy to unit-test.
"""

from __future__ import annotations

import numpy as np


def preprocess(lc, window_length: int = 901, sigma: float = 5.0):
    """
    Clean and flatten a TESS light curve.

    Steps:
      1. Remove NaN cadences.
      2. Flatten long-term stellar variability with a Savitzky-Golay filter.
      3. Remove outlier cadences (sigma-clipping).

    Parameters
    ----------
    lc            : lightkurve.LightCurve
    window_length : SG filter window (must be odd; longer = less aggressive).
    sigma         : Outlier rejection threshold in standard deviations.

    Returns
    -------
    Cleaned, normalised LightCurve.
    """
    if window_length % 2 == 0:
        window_length += 1  # enforce odd

    return (
        lc.remove_nans()
          .flatten(window_length=window_length)
          .remove_outliers(sigma_upper=sigma)
    )


def run_bls(
    lc,
    period_min: float = 0.5,
    period_max: float = 15.0,
    n_periods: int = 10_000,
    duration_min: float = 0.05,
    duration_max: float = 0.20,
    n_durations: int = 10,
):
    """
    Compute a Box Least Squares (BLS) periodogram on a cleaned light curve.

    Parameters
    ----------
    lc            : Preprocessed lightkurve.LightCurve.
    period_min    : Minimum trial period in days.
    period_max    : Maximum trial period in days.
    n_periods     : Number of trial periods (resolution).
    duration_min  : Min transit duration as fraction of a day.
    duration_max  : Max transit duration as fraction of a day.
    n_durations   : Number of trial durations.

    Returns
    -------
    Tuple: (periodogram, best_period, best_t0, best_depth)
    """
    periods   = np.linspace(period_min, period_max, n_periods)
    durations = np.linspace(duration_min, duration_max, n_durations)

    bls = lc.to_periodogram(
        method="bls",
        period=periods,
        duration=durations,
    )

    best_period = bls.period_at_max_power
    best_t0     = bls.transit_time_at_max_power
    best_depth  = bls.depth_at_max_power

    return bls, best_period, best_t0, best_depth


def phase_fold(lc, period, t0):
    """
    Phase-fold the light curve at the best-fit period and epoch.

    Returns a FoldedLightCurve centred at phase 0 (mid-transit),
    with phase normalised to [-0.5, 0.5].
    """
    return lc.fold(period=period, epoch_time=t0, normalize_phase=True)


def estimate_planet_radius(transit_depth_ppm: float, star_radius_rsun: float = 1.0) -> float:
    """
    Rough estimate of planet radius from transit depth.

    R_p / R_star = sqrt(depth)
    Assumes circular, edge-on orbit and no limb-darkening correction.

    Parameters
    ----------
    transit_depth_ppm : Transit depth in parts per million.
    star_radius_rsun  : Host star radius in solar radii (default 1.0).

    Returns
    -------
    Planet radius in Earth radii (R⊕).
    """
    RSUN_TO_REARTH = 109.076  # 1 R_sun = 109.076 R_earth
    depth_frac = transit_depth_ppm / 1e6
    rp_rstar   = np.sqrt(max(depth_frac, 0.0))
    return rp_rstar * star_radius_rsun * RSUN_TO_REARTH


def mask_transits(lc, period, t0, duration_days: float = 0.1):
    """
    Mask out detected transit windows to search for secondary signals.

    Returns a LightCurve with transit cadences removed.
    """
    return lc.create_transit_mask(
        period=period,
        transit_time=t0,
        duration=duration_days,
    )
