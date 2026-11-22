"""
tests/test_mast_api.py
-----------------------
Unit tests for mast_api.py using unittest.mock to avoid real network calls.
"""

import sys
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch
import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent))

# Import module so that unittest.mock.patch can resolve attributes on it
import modules.mast_api


class TestSearchAndDownload(unittest.TestCase):
    """Test search_and_download with mocked lightkurve calls."""

    def _make_mock_lc(self):
        """Return a minimal mock LightCurve object."""
        lc = MagicMock()
        lc.__len__ = MagicMock(return_value=1000)
        return lc

    def _make_mock_collection(self, lc):
        col = MagicMock()
        col.stitch.return_value = lc
        return col

    def _make_mock_result(self, n_results: int = 3):
        result = MagicMock()
        result.__len__ = MagicMock(return_value=n_results)
        result.table = {"sector": list(range(1, n_results + 1))}
        return result

    @patch("modules.mast_api.lk.search_lightcurve")
    @patch("modules.mast_api.st.cache_data", lambda **kw: (lambda f: f))
    def test_returns_none_when_no_results(self, mock_search):
        """Should return (None, []) when MAST finds nothing."""
        mock_result = MagicMock()
        mock_result.__len__ = MagicMock(return_value=0)
        mock_search.return_value = mock_result

        # Import after patching
        from modules import mast_api
        # Bypass cache for testing
        lc, sectors = mast_api.search_and_download.__wrapped__("TIC 999999999")
        self.assertIsNone(lc)
        self.assertEqual(sectors, [])

    def test_available_cadences_returns_list(self):
        """available_cadences must always return a non-empty list."""
        with patch("modules.mast_api.lk.search_lightcurve") as mock_search:
            mock_res = MagicMock()
            mock_res.__len__ = MagicMock(return_value=1)
            mock_search.return_value = mock_res

            from modules.mast_api import available_cadences
            cadences = available_cadences("Pi Mensae")
            self.assertIsInstance(cadences, list)
            self.assertGreater(len(cadences), 0)


class TestProcessingIntegration(unittest.TestCase):
    """Quick integration smoke-tests for processing helpers."""

    def setUp(self):
        import lightkurve as lk
        time = np.linspace(0, 27, 5000)
        flux = np.ones(5000) + np.random.normal(0, 1e-4, 5000)
        self.lc = lk.LightCurve(time=time, flux=flux)

    def test_preprocess_smoke(self):
        from modules.processing import preprocess
        clean = preprocess(self.lc, window_length=201)
        self.assertGreater(len(clean), 0)

    def test_estimate_planet_radius_smoke(self):
        from modules.processing import estimate_planet_radius
        rp = estimate_planet_radius(500.0)
        self.assertGreater(rp, 0)


if __name__ == "__main__":
    unittest.main()
