# Stored users scores in memory for demonstration purposes

leaderboard = {
    "Maria Ionescu": 150,
    "Ion Georgescu": 140,
    "Ioana Vasilescu": 135,
    "Elena Radu": 120,
    "Gabriel Marinescu": 115,
    "Ana Dumitrescu": 100,
    "Vlad Mihăilescu": 95,
    "Cristina Dobre": 90,
}

def update_user_points(user_name: str, points: int):
    """Update the points for a given user."""
    if user_name in leaderboard:
        leaderboard[user_name] += points
    else:
        leaderboard[user_name] = 0
    return leaderboard[user_name]

def get_leaderboard():
    """Return the leaderboard sorted by points in descending order."""
    sorted_leaderboard = sorted(leaderboard.items(), key=lambda item: item[1], reverse=True)
    return [{"user": user, "points": points} for user, points in sorted_leaderboard]
