from sqlalchemy import create_engine, text

# Stored users scores in memory for demonstration purposes
leaderboard = {
}

# Database connection 
DATABASE_URL = "postgresql://postgres:11111@localhost:5433/postgres"
engine = create_engine(DATABASE_URL)

# Global state tracking (simple dictionaries)
previous_energy_usage = {}
previous_temperature = {}
energy_thresholds_crossed = {}

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
    username: str,
    energy_usage: float,
    temperature: float,
    motion: bool,
    energy_saving_mode: bool
) -> int:
    """Calculate points based on smart house metrics"""
    points = 0
    
    # Initialize user state if first time
    if username not in previous_energy_usage:
        previous_energy_usage[username] = energy_usage
        previous_temperature[username] = temperature
        energy_thresholds_crossed[username] = set()
        return 0
    
    prev_energy = previous_energy_usage[username]
    prev_temp = previous_temperature[username]
    
    # Your existing smart house points calculation logic here
    # Base rule: 3 kW is normal
    if prev_energy >= 3 and energy_usage < 3:
        points += 20
    elif prev_energy < 3 and energy_usage >= 3:
        points -= 20

    # Device rules (simplified)
    device_states = [temperature < 20, temperature > 25, motion]  # thermostat, AC, lights
    for device_on in device_states:
        points += -10 if device_on else 10

    # Energy saving mode rule
    points += 10 if energy_saving_mode else -10
    
    # Update previous states
    previous_energy_usage[username] = energy_usage
    previous_temperature[username] = temperature
    
    return points

def update_user_points(username: str, points: int):
    """Update the points for a given user in the database."""
    try:
        with engine.connect() as conn:
            # First get user_id from users table
            user_result = conn.execute(
                text("SELECT id FROM users WHERE username = :username"),
                {"username": username}
            )
            user = user_result.fetchone()
            
            if not user:
                print(f"User {username} not found in users table")
                return 0
                
            user_id = user[0]
            
            # Check if user exists in leaderboard
            result = conn.execute(
                text("SELECT points FROM leaderboard WHERE user_id = :user_id"),
                {"user_id": user_id}
            )
            existing = result.fetchone()
            
            if existing:
                # Update existing points
                new_points = existing[0] + points
                conn.execute(
                    text("UPDATE leaderboard SET points = :points, last_updated = CURRENT_TIMESTAMP WHERE user_id = :user_id"),
                    {"points": new_points, "user_id": user_id}
                )
            else:
                # Insert new user
                new_points = points
                conn.execute(
                    text("INSERT INTO leaderboard (user_id, points) VALUES (:user_id, :points)"),
                    {"user_id": user_id, "points": new_points}
                )
            conn.commit()
            return new_points
    except Exception as e:
        print(f"Error updating leaderboard: {e}")
        return 0
    

def get_leaderboard():
    """Return the leaderboard sorted by points in descending order."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT username, points 
                FROM v_leaderboard 
                ORDER BY points DESC
            """))
            leaderboard_data = result.fetchall()
            return [{"username": user[0], "points": user[1]} for user in leaderboard_data]
    except Exception as e:
        print(f"Error fetching leaderboard from v_leaderboard: {e}")
        return []