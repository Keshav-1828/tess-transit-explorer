# 🔭 TESS Transit Explorer

> An interactive web app to detect and visualise exoplanet transits in NASA TESS data.

[![CI](https://github.com/YOUR_USERNAME/tess-transit-explorer/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/tess-transit-explorer/actions)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red?logo=streamlit)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Data: NASA MAST](https://img.shields.io/badge/Data-NASA%20MAST-blue)](https://mast.stsci.edu)

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔍 **Target Search** | Search any star by name or TIC ID |
| 📡 **Live MAST Data** | Fetches TESS light curves directly from NASA MAST |
| 🧹 **Preprocessing** | Savitzky-Golay flattening + sigma-clipping outlier removal |
| 📉 **BLS Periodogram** | Box Least Squares transit detection with configurable period grid |
| 🌑 **Phase Fold** | Interactive phase-folded transit profile with binned median |
| 📊 **Catalog Trends** | Population stats from the NASA Exoplanet Archive |
| 🌙 **Dark Mode UI** | Astronomy-optimised dark theme throughout |

---

## 🚀 Quick Start

### Local installation

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/tess-transit-explorer.git
cd tess-transit-explorer

# 2. Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Launch the app
streamlit run app.py
```

The app opens automatically at `http://localhost:8501`.

### Try it instantly — Streamlit Community Cloud

1. Fork this repo (make it **public**)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub → select this repo → set **Main file: `app.py`**
4. Click **Deploy** — done in ~2 minutes, no server needed!

---

## 🗂️ Project Structure

```
tess-transit-explorer/
│
├── .streamlit/
│   └── config.toml              # Dark astronomy theme
│
├── modules/
│   ├── mast_api.py              # lightkurve → MAST data fetch (cached)
│   ├── processing.py            # Flatten, BLS periodogram, phase-fold
│   └── plotting.py              # Plotly interactive figure builders
│
├── pages/
│   ├── 1_🔭_Transit_Explorer.py # Main interactive transit search page
│   ├── 2_📊_Catalog_Trends.py   # Exoplanet population statistics
│   └── 3_ℹ️_About.py            # Mission background & app docs
│
├── data/
│   └── famous_targets.csv       # Pre-seeded famous TESS targets
│
├── tests/
│   ├── test_processing.py       # Unit tests for BLS/fold (no network)
│   └── test_mast_api.py         # Mock-based tests for data layer
│
├── .github/workflows/ci.yml     # GitHub Actions CI (test + lint)
├── app.py                       # Entry point / landing page
├── requirements.txt
└── README.md
```

---

## 🧪 Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest tests/ -v

# With coverage report
pytest tests/ -v --cov=modules --cov-report=term-missing
```

Expected output:
```
tests/test_processing.py::TestPreprocess::test_no_nans_after_preprocess   PASSED
tests/test_processing.py::TestPreprocess::test_flux_normalised             PASSED
tests/test_processing.py::TestBLS::test_recovers_injected_period           PASSED
tests/test_processing.py::TestPhaseFold::test_fold_preserves_length        PASSED
tests/test_processing.py::TestPlanetRadius::test_earth_analogue            PASSED
...
```

---

## 🎯 Example: Pi Mensae (TIC 261136679)

Pi Mensae hosts two known planets, including **Pi Men c** — a Super-Earth
discovered by TESS with an orbital period of **~6.27 days**. Enter
`"Pi Mensae"` in the Transit Explorer to see BLS recover this period.

| BLS Output | Expected |
|---|---|
| Best period | ~6.27 days |
| Transit depth | ~700–900 ppm |
| Estimated planet radius | ~2.0 R⊕ |

---

## 📡 Data Sources

| Source | Used For |
|---|---|
| [NASA MAST](https://mast.stsci.edu) | TESS light curve downloads via `lightkurve` |
| [NASA Exoplanet Archive](https://exoplanetarchive.ipac.caltech.edu) | Confirmed planet catalog (Catalog Trends page) |
| [lightkurve](https://docs.lightkurve.org) | Python interface to MAST + BLS analysis |
| [astroquery](https://astroquery.readthedocs.io) | Programmatic archive queries |

---

## 🤝 Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit -m "Add my feature"`
4. Push and open a Pull Request

Please add or update tests in `tests/` for any new processing logic.

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgements

- **NASA / MIT TESS Mission** for making exoplanet data publicly available
- **lightkurve** development team at the Space Telescope Science Institute
- **Streamlit** for the interactive web framework
