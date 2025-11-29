import os
import sys

# Ensure backend/api is importable
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
API_DIR = os.path.join(ROOT, 'backend', 'api')
if API_DIR not in sys.path:
    sys.path.append(API_DIR)

import leaderBoard as lb  # type: ignore


def test_update_user_points_new_user_is_set():
    pass


def test_get_leaderboard_sorted_descending():
    board = lb.get_leaderboard()
    points = [entry["points"] for entry in board]
    assert points == sorted(points, reverse=True)
