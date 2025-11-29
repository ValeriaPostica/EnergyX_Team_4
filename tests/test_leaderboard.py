import os
import sys

# Ensure backend/api is importable
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
API_DIR = os.path.join(ROOT, 'backend', 'api')
if API_DIR not in sys.path:
    sys.path.append(API_DIR)

import leaderBoard as lb  # type: ignore


def test_update_user_points_new_user_is_set():
    user = "_pytest_user_"
    before = lb.leaderboard.get(user)
    new_total = lb.update_user_points(user, 5)
    assert new_total == 5
    # cleanup not required; leaderboard is in-memory for tests only


def test_get_leaderboard_sorted_descending():
    board = lb.get_leaderboard()
    points = [entry["points"] for entry in board]
    assert points == sorted(points, reverse=True)
