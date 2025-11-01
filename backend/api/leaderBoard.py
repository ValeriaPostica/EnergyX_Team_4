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

# Points calculation functions

def calculate_tariff_points(previous_cost: float, estimated_cost: float) -> int:
    """points = round((Previous Cost - Estimated Current Cost) / 10)"""
    try:
        points = round((previous_cost - estimated_cost) / 10)
        return int(points)
    except Exception as e:
        print(f"Error calculating tariff points: {e}")
        return 0

def calculate_smart_house_points(
    energy_usage: float,
    previous_energy_usage: float,
    thermostat: bool,
    air_conditioner: bool,
    lights: bool,
    energy_saving_mode: bool
) -> int:
    points = 0
    # Base rule: 3 kW is normal
    if previous_energy_usage >= 3 and energy_usage < 3:
        points += 20
    elif previous_energy_usage < 3 and energy_usage >= 3:
        points -= 20


    # Device rules
    for device in [thermostat, air_conditioner, lights]:
        if device:
            points -= 10   # device ON → minus points
        else:
            points += 10   # device OFF → plus points

    # Energy saving mode rule
    if energy_saving_mode:
        points += 10
    else:
        points -= 10

    return points

# Leaderboard functions

def update_user_points(user: str, points: int):
    """Update the points for a given user."""
    if user in leaderboard:
        leaderboard[user] += points
    else:
        leaderboard[user] = 0
    return leaderboard[user]

def get_leaderboard():
    """Return the leaderboard sorted by points in descending order."""
    sorted_leaderboard = sorted(leaderboard.items(), key=lambda item: item[1], reverse=True)
    return [{"user": user, "points": points} for user, points in sorted_leaderboard]
