# Points Calculator for the Leadervoard implemetation

def calculate_tariff_points(previous_cost: float, estimated_cost: float) -> int:
    try:
        points = round((previous_cost -estimated_cost) /10)
        return int(points)
    except Exception as e:
        print(f"Error calculating tariff points: {e}")
        return 0
    
def calculate_smart_house_points(
        energy_usage: float,
        thermostat: bool,
        air_conditioner: bool,
        lights: bool,
        energy_saving_mode: bool
) ->int:
    points = 0
    if energy_usage < 3:
        points += 20
    elif energy_usage > 3:
        points -= 20

    # Logic for devices
    for device in [thermostat, air_conditioner, lights]:
        if device:
            points += 10
        else:
            points -= 10

    # Energy saving mode
    if energy_saving_mode:
        points += 10
    else:
        points -= 10

    return points
    

