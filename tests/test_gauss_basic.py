import os
import sys

# Ensure backend/api is importable
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
API_DIR = os.path.join(ROOT, 'backend', 'api')
if API_DIR not in sys.path:
    sys.path.append(API_DIR)

from gauss_tarrif import gaussian, precompute_gaussian_peak  # type: ignore


def test_gaussian_at_mean_is_one():
    assert gaussian(10, 10, sigma=2) == 1.0


def test_precompute_has_24_positive_hours():
    vals = precompute_gaussian_peak()
    assert isinstance(vals, list)
    assert len(vals) == 24
    assert all(v > 0 for v in vals)
