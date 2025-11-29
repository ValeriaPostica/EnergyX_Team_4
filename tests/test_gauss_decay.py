import os
import sys

# Ensure backend/api is importable
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
API_DIR = os.path.join(ROOT, 'backend', 'api')
if API_DIR not in sys.path:
    sys.path.append(API_DIR)

from gauss_tarrif import gaussian  # type: ignore


def test_gaussian_decays_with_distance():
    mean = 12
    sigma = 2.5
    near = gaussian(mean + sigma, mean, sigma)
    far = gaussian(mean + 3 * sigma, mean, sigma)
    assert far < near
