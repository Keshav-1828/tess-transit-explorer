"""
tests/test_processing.py
--------------------------
Unit tests for processing.py using a synthetic injected-transit light curve.
No internet required — all tests use fabricated data.
"""

import pytest
import numpy as np
import lightkurve as lk
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from modules.processing import preprocess, run_bls, phase_fold, estimate_planet_radius


# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_synthetic_lc(
    n_points: int = 20_000,
    baseline_days: float = 27.0,
    period_days: float = 3.5,
    depth: float = 0.01,
    duration_days: float = 0.1,
    noise_ppm: float = 100.0,
    seed: int = 42,
) -> lk.LightCurve:
    """
    Create a synthetic TESS-like light curve with injected box transits.

    Parameters
    ----------
    n_points      : Number of cadences.
    baseline_days : Total duration in days (1 TESS sector ≈ 27 days).
    period_days   : Injected orbital period.
    depth         : Transit depth (fractional flux decrement).
    duration_days : Transit duration in days.
    noise_ppm     : White noise amplitude in ppm.
    seed          : RNG seed for reproducibility.
    """
    rng  = np.random.default_rng(seed)
    time = np.linspace(0.0, baseline_days, n_points)
    flux = np.ones(n_points, dtype=float)

    # Inject transits at every multiple of period_days
    for t0 in np.arange(period_days, baseline_days, period_days):
        in_transit = np.abs(time - t0) < duration_days / 2
        flux[in_transit] -= depth

    # Add white noise
    flux += rng.normal(0.0, noise_ppm * 1e-6, size=n_points)

    return lk.LightCurve(time=time, flux=flux)


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestPreprocess:
    def test_no_nans_after_preprocess(self):
        """Preprocessed light curve must contain no NaN flux values."""
        lc = make_synthetic_lc()
        clean = preprocess(lc)
        assert not np.any(np.isnan(clean.flux.value)), "NaN values remain after preprocess"

    def test_flux_normalised(self):
        """Flattened flux should be close to 1.0 out of transit."""
        lc    = make_synthetic_lc()
        clean = preprocess(lc)
        median = np.nanmedian(clean.flux.value)
        assert abs(median - 1.0) < 0.01, f"Median flux {median:.4f} not close to 1.0"

    def test_even_window_becomes_odd(self):
        """preprocess must handle an even window_length without raising."""
        lc = make_synthetic_lc()
        preprocess(lc, window_length=900)   # should auto-increment to 901

    def test_output_shorter_than_input(self):
        """Outlier removal may shorten the array; output must be <= input length."""
        lc    = make_synthetic_lc()
        clean = preprocess(lc)
        assert len(clean) <= len(lc)


class TestBLS:
    def test_recovers_injected_period(self):
        """BLS must recover the injected period within 0.1 days."""
        injected_period = 3.5
        lc    = make_synthetic_lc(period_days=injected_period)
        _, best_period, _, _ = run_bls(
            lc, period_min=1.0, period_max=10.0, n_periods=5_000
        )
        assert abs(best_period.value - injected_period) < 0.1, (
            f"BLS recovered period {best_period.value:.4f} d, "
            f"expected {injected_period:.4f} d"
        )

    def test_bls_returns_four_values(self):
        """run_bls must return a 4-tuple."""
        lc    = make_synthetic_lc()
        clean = preprocess(lc)
        result = run_bls(clean, period_min=1.0, period_max=10.0, n_periods=1_000)
        assert len(result) == 4

    def test_best_depth_positive(self):
        """Detected transit depth must be positive."""
        lc    = make_synthetic_lc()
        clean = preprocess(lc)
        _, _, _, best_depth = run_bls(clean, period_min=1.0, period_max=10.0, n_periods=1_000)
        assert best_depth.value >= 0.0


class TestPhaseFold:
    def test_fold_preserves_length(self):
        """Phase-folded LC must have the same number of cadences as input."""
        lc     = make_synthetic_lc()
        clean  = preprocess(lc)
        folded = phase_fold(clean, period=3.5, t0=1.0)
        assert len(folded) == len(clean)

    def test_fold_phase_range(self):
        """Phase values must span [-0.5, 0.5]."""
        lc     = make_synthetic_lc()
        clean  = preprocess(lc)
        folded = phase_fold(clean, period=3.5, t0=1.0)
        phases = folded.phase.value
        assert phases.min() >= -0.5 - 1e-6
        assert phases.max() <=  0.5 + 1e-6


class TestPlanetRadius:
    def test_earth_analogue(self):
        """Earth around Sun: depth ≈ 84 ppm → radius ≈ 1.0 R⊕."""
        rp = estimate_planet_radius(84.0, star_radius_rsun=1.0)
        assert 0.8 < rp < 1.2, f"Expected ~1.0 R⊕, got {rp:.3f}"

    def test_zero_depth(self):
        """Zero depth must return zero planet radius without crashing."""
        rp = estimate_planet_radius(0.0)
        assert rp == 0.0

    def test_scales_with_host_star(self):
        """Planet radius should scale linearly with host star radius."""
        rp1 = estimate_planet_radius(1000.0, star_radius_rsun=1.0)
        rp2 = estimate_planet_radius(1000.0, star_radius_rsun=2.0)
        assert abs(rp2 / rp1 - 2.0) < 0.01
