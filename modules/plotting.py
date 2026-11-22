"""
modules/plotting.py
--------------------
Plotly figure builders for the Transit Explorer UI.
All figures use template="plotly_dark" to match the dark Streamlit theme.
"""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


_TEMPLATE = "plotly_dark"
_TESS_BLUE = "#6C8EBF"
_TRANSIT_RED = "#EF5350"


def plot_lightcurve(lc_raw, lc_flat=None, title: str = "TESS Light Curve") -> go.Figure:
    """
    Plot raw (and optionally flattened) TESS light curve as an interactive time series.

    Parameters
    ----------
    lc_raw  : Raw stitched LightCurve.
    lc_flat : Flattened LightCurve (optional overlay).
    title   : Figure title string.
    """
    fig = go.Figure()

    time_raw = lc_raw.time.value
    flux_raw = lc_raw.flux.value

    fig.add_trace(go.Scattergl(
        x=time_raw,
        y=flux_raw,
        mode="markers",
        marker=dict(size=2, color="rgba(108,142,191,0.4)"),
        name="Raw flux (PDCSAP)",
        hovertemplate="BJD: %{x:.4f}<br>Flux: %{y:.6f}<extra></extra>",
    ))

    if lc_flat is not None:
        fig.add_trace(go.Scattergl(
            x=lc_flat.time.value,
            y=lc_flat.flux.value,
            mode="markers",
            marker=dict(size=2, color=_TESS_BLUE),
            name="Flattened flux",
            hovertemplate="BJD: %{x:.4f}<br>Flux: %{y:.6f}<extra></extra>",
        ))

    fig.update_layout(
        template=_TEMPLATE,
        title=title,
        xaxis_title="Time [BTJD]",
        yaxis_title="Normalized Flux",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=420,
        margin=dict(l=60, r=20, t=50, b=50),
    )
    return fig


def plot_periodogram(bls, best_period=None, title: str = "BLS Periodogram") -> go.Figure:
    """
    Plot the BLS power spectrum with the best-fit period annotated.

    Parameters
    ----------
    bls         : lightkurve BoxLeastSquaresPeriodogram.
    best_period : Best period (Quantity), used for annotation.
    title       : Figure title.
    """
    periods = bls.period.value
    power   = bls.power.value

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=periods,
        y=power,
        mode="lines",
        line=dict(color=_TESS_BLUE, width=1),
        name="BLS power",
        hovertemplate="Period: %{x:.4f} d<br>Power: %{y:.4f}<extra></extra>",
    ))

    if best_period is not None:
        p_val = best_period.value
        fig.add_vline(
            x=p_val,
            line=dict(color=_TRANSIT_RED, width=2, dash="dash"),
            annotation_text=f"Best: {p_val:.4f} d",
            annotation_position="top right",
            annotation_font_color=_TRANSIT_RED,
        )

    fig.update_layout(
        template=_TEMPLATE,
        title=title,
        xaxis_title="Period [days]",
        yaxis_title="BLS Power",
        height=380,
        margin=dict(l=60, r=20, t=50, b=50),
    )
    return fig


def plot_phase_fold(
    folded_lc,
    best_period=None,
    best_depth=None,
    title: str = "Phase-Folded Transit",
) -> go.Figure:
    """
    Plot the phase-folded light curve to reveal the transit shape.

    Parameters
    ----------
    folded_lc   : FoldedLightCurve (output of lc.fold()).
    best_period : Best period Quantity, for subtitle annotation.
    best_depth  : Transit depth Quantity, for reference line.
    title       : Figure title.
    """
    phase = folded_lc.phase.value
    flux  = folded_lc.flux.value

    # Sort for a cleaner scatter
    sort_idx = np.argsort(phase)
    phase = phase[sort_idx]
    flux  = flux[sort_idx]

    fig = go.Figure()

    # Individual points
    fig.add_trace(go.Scattergl(
        x=phase,
        y=flux,
        mode="markers",
        marker=dict(size=2, color="rgba(108,142,191,0.5)"),
        name="Individual cadences",
        hovertemplate="Phase: %{x:.4f}<br>Flux: %{y:.6f}<extra></extra>",
    ))

    # Binned median overlay
    n_bins = 100
    bins   = np.linspace(phase.min(), phase.max(), n_bins + 1)
    bin_centres = 0.5 * (bins[:-1] + bins[1:])
    bin_medians = np.array([
        np.median(flux[(phase >= bins[i]) & (phase < bins[i + 1])])
        if np.any((phase >= bins[i]) & (phase < bins[i + 1]))
        else np.nan
        for i in range(n_bins)
    ])

    fig.add_trace(go.Scatter(
        x=bin_centres,
        y=bin_medians,
        mode="lines+markers",
        line=dict(color=_TRANSIT_RED, width=2),
        marker=dict(size=4, color=_TRANSIT_RED),
        name="Binned median",
        hovertemplate="Phase: %{x:.4f}<br>Median flux: %{y:.6f}<extra></extra>",
    ))

    subtitle = ""
    if best_period is not None:
        subtitle = f"  P = {best_period.value:.5f} days"

    fig.update_layout(
        template=_TEMPLATE,
        title=title + subtitle,
        xaxis_title="Orbital Phase",
        yaxis_title="Normalized Flux",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400,
        margin=dict(l=60, r=20, t=50, b=50),
    )

    # Zoom to ±0.3 around transit
    fig.update_xaxes(range=[-0.3, 0.3])

    return fig


def plot_tpf_pixels(tpf, frame: int = 0, title: str = "Target Pixel File") -> go.Figure:
    """
    Display a single frame of a Target Pixel File as a heatmap.
    Useful for checking centroid shifts (false positive test).
    """
    flux_frame = tpf.flux.value[frame]
    fig = go.Figure(go.Heatmap(
        z=flux_frame,
        colorscale="Viridis",
        colorbar=dict(title="e⁻/s"),
    ))
    fig.update_layout(
        template=_TEMPLATE,
        title=title,
        xaxis_title="Pixel column",
        yaxis_title="Pixel row",
        height=350,
        margin=dict(l=60, r=20, t=50, b=50),
    )
    return fig
