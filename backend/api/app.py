from flask import Flask, jsonify
from flask import request
from flask_cors import CORS
from pydantic import BaseModel, ValidationError
from auth import auth_bp
import aiProvider
import aiCustomer
import os
import openai
from model.xlstm_runner import m_eval, m_eval_devices
#from leaderBoard import smart_house_calculator, update_user_points
from retrieve_data import get_location_color, get_series, general_info, regional_consumption, calc_timeseries_from_db, get_series_country, get_all_keys
# Commented our lines below and above use ai implementations
from gauss_tarrif import precompute_gaussian_peak
from simple_log_handler import simple_log, simple_log_clear
import json
from migrations import load_migrations
import hashlib

from auth import auth_bp
from auth import token_required
from leaderBoard import (
    calculate_tariff_points,
    #calculate_smart_house_points,
    update_user_points,
    get_leaderboard,
)

from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

IS_PROD = str(os.getenv("IS_PROD", "false")).lower() == "true"

if IS_PROD:
    load_migrations()

client = None

try:
    if OPENAI_API_KEY:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)
    else:
        print("Warning: OPENAI_API_KEY not set.")
except Exception as e:
    print(f"Warning: Could not initialize OpenAI client: {e}")
    
# Use relative paths for local development
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

app = Flask(__name__)
CORS(app)

app.register_blueprint(auth_bp, url_prefix='/auth')

# Optional prediction caching to keep outputs consistent across repeated calls
# even if the underlying time series updates in the database.
PREDICTION_CACHE_ENABLED = os.getenv("PREDICTION_CACHE", "1") != "0"
_prediction_cache = {}

def _cache_key(*parts):
    return ":".join(str(p) for p in parts)

def _series_digest(values):
    try:
        # Stable digest to debug if inputs change between requests
        b = (",".join(f"{float(v):.6f}" for v in values)).encode("utf-8")
        return hashlib.sha1(b).hexdigest()  # nosec - debugging only
    except Exception:
        return "na"

# Path to a simple plain-text log file. We'll truncate it at startup so it's empty when app runs.
SIMPLE_LOG_PATH = os.path.join(DATA_DIR, "simple_log.txt")
try:
    os.makedirs(os.path.dirname(SIMPLE_LOG_PATH), exist_ok=True)
    # Truncate the file at startup
    open(SIMPLE_LOG_PATH, "w", encoding="utf-8").close()
except Exception as e:
    print(f"Warning: could not create/truncate simple_log: {e}")

@app.route("/diff/<id>/<day>")
@token_required
def diffs(current_user, id, day):
    return get_series(id, day)

@app.route("/")
@app.route("/keys")
@token_required
def keys_route(current_user):
    return get_all_keys()

diffs = general_info()
@app.route("/general_info")
@token_required
def general_info_route(current_user):
    return jsonify(diffs)

values = precompute_gaussian_peak()
@app.route("/tariff")
@token_required
def tariff(current_user):
    return jsonify(values)

@app.route("/region/all")
@token_required
def get_regions(current_user):
    try:
        return calc_timeseries_from_db()
    except Exception as e:
        print(f"Error in /region/all: {e}")
        return jsonify({"error": str(e)}), 500

class OpenAiMessage(BaseModel):
    message: str

@app.route("/ai/chat", methods=['POST'])
@token_required
def chat_q(current_user):
    if client is None:
        return jsonify({"error": "OpenAI client not initialized"}), 500
    json_data = request.get_json()  # parse JSON body
    if not json_data or "message" not in json_data:
        return jsonify({"error": "Missing 'message' field"}), 400
    
    message = json_data["message"]
    try:
        return {"response": aiCustomer.get_ai_response(message)}
    except ValidationError:
        return jsonify({"error": "Invalid input format"}), 400
    except Exception as e:
        print(f"Error in /ai/chat : {e}")
        return jsonify({"error": "Something went wrong"}), 500


@app.route("/pred/<user_id>")
@token_required
def pred_user(current_user, user_id):
    series = get_series(user_id)
    try:
        # Ensure we return a proper JSON response (list of floats)
        predictions = m_eval(series=series, week=False)
        return jsonify(predictions)
    except ValueError:
        return jsonify({"error": "Invalid user ID"}), 400

@app.route("/pred/loc/<location_name>")
@token_required
def pred_location(current_user, location_name):
    """Get predictions for a specific location"""
    try:
        # Load regions index
        regions_index_path = os.path.join(BASE_DIR, "data", "model_data", "regions_index.json")
        with open(regions_index_path, "r", encoding="utf-8") as f:
            regions_data = json.load(f)
        
        regions_list = regions_data["regions"]
        
        # Find location index
        location_index = None
        for i, region in enumerate(regions_list):
            if region.lower() == location_name.lower():
                location_index = i
                break
        
        if location_index is None:
            return jsonify({
                "error": f"Location '{location_name}' not found",
                "available_locations": regions_list
            }), 400

        series = get_series_country(location_name)

        key = _cache_key("loc", location_name.lower(), "week", 0)
        if PREDICTION_CACHE_ENABLED and key in _prediction_cache:
            return jsonify(_prediction_cache[key])

        print(f"pred_location: {location_name} len={len(series)} sha1={_series_digest(series)}")

        # Get predictions using location index
        predictions = m_eval(series=series, week=False)
        if PREDICTION_CACHE_ENABLED:
            _prediction_cache[key] = predictions
        return jsonify(predictions)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/pred/loc/<location_name>/week")
@token_required
def pred_location_week(current_user, location_name):
    """Get predictions for a specific location"""
    try:
        # Load regions index
        regions_index_path = os.path.join(BASE_DIR, "data", "model_data", "regions_index.json")
        with open(regions_index_path, "r", encoding="utf-8") as f:
            regions_data = json.load(f)
        
        regions_list = regions_data["regions"]
        
        # Find location index
        location_index = None
        for i, region in enumerate(regions_list):
            if region.lower() == location_name.lower():
                location_index = i
                break
        
        if location_index is None:
            return jsonify({
                "error": f"Location '{location_name}' not found",
                "available_locations": regions_list
            }), 400

        series = get_series_country(location_name)

        key = _cache_key("loc", location_name.lower(), "week", 1)
        if PREDICTION_CACHE_ENABLED and key in _prediction_cache:
            return jsonify(_prediction_cache[key])

        print(f"pred_location_week: {location_name} len={len(series)} sha1={_series_digest(series)}")

        # Get predictions using location index
        predictions = m_eval(series=series, week=True)
        if PREDICTION_CACHE_ENABLED:
            _prediction_cache[key] = predictions
        return jsonify(predictions)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/pred/simulate/<user_id>/<schedule>")
@token_required
def pred_simulate(current_user, user_id, schedule):
    """Simulate device schedule for a user.

    The `schedule` path parameter may be a URL-encoded JSON array, e.g.
    %5B%5B%22thermostat%22%2C12%2C15%5D%2C...%5D. We attempt to decode JSON
    and normalize it to a list of (device, start, end) tuples expected by
    `m_eval_devices`.
    """
    try:
        # Try to parse schedule as JSON (frontend sends encoded JSON in the path)
        parsed_schedule = None
        try:
            parsed_schedule = json.loads(schedule)
        except Exception:
            # If parsing fails, leave as raw string (will be handled below)
            parsed_schedule = schedule

        # Normalize to list of (device, start, end) tuples
        normalized = []
        if isinstance(parsed_schedule, list):
            for item in parsed_schedule:
                if (isinstance(item, (list, tuple)) and len(item) >= 3):
                    try:
                        device = str(item[0])
                        start = int(item[1])
                        end = int(item[2])
                        normalized.append((device, start, end))
                    except Exception:
                        # Skip malformed entries
                        continue
        else:
            # If schedule wasn't JSON/list, return an error to the client
            return jsonify({"error": "Schedule must be a JSON array of [device, start, end]"}), 400

        if not normalized:
            return jsonify({"error": "Empty or invalid schedule provided"}), 400

        series = get_series(user_id)
        pred_series = m_eval_devices(series=series, schedule=normalized, week=False)
        return jsonify(pred_series)

    except ValueError:
        return jsonify({"error": "Invalid user ID"}), 400
    except Exception as e:
        # Return a JSON error instead of an HTML traceback
        return jsonify({"error": str(e)}), 500


location_data = {}
try:
    location_data = regional_consumption()
except Exception as e:
    print(f"Warning: Could not fetch regional consumption: {e}")
    location_data = {}

@app.route("/consumption")
@token_required
def get_location_consumption(current_user):
    #Get consumption data for a specific location
    try:
        return jsonify(location_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/color", methods=['POST']) #Why this is POST?, This feature is not compleate
@token_required
def give_color(current_user):
    try:
        # Parse posted JSON (optional); not required for current implementation.
        req_data = request.get_json(silent=True) or {}
        print("Received request data:", req_data)

        if not isinstance(location_data, dict) or not location_data:
            print("Error: Invalid or empty location_data")
            return jsonify({"error": "No location data available"}), 500

        return jsonify(get_location_color(location_data))

    except Exception as e:
        print("Unhandled /color error:", e)
        return jsonify({"error": str(e)}), 500

    
response = []
if client and location_data:
    try:
        response = aiProvider.get_ai_recommendations(client, location_data)
    except Exception as e:
        print(f"Warning: Could not get AI recommendations: {e}")
        response = []
else:
    print("Warning: Skipping AI recommendations (client or data missing)")
    response = []

@app.route("/ai")
@token_required
def get_ai_resp(current_user):
    return jsonify(response)

@app.route("/simple_log", methods=["POST"]) #Why?
@token_required
def route_simple_log(current_user):
    return simple_log()


@app.route("/simple_log/clear", methods=["POST"]) #Why?
@token_required
def route_simple_log_clear(current_user):
    return simple_log_clear()

# Leaderboard endpoints

@app.route("/calculate/tariff_points", methods=["POST"])
def route_tariff_points():
    data = request.get_json()
    user = data.get("user")
    prev_cost = float(data.get("previous_cost", 0))
    est_cost = float(data.get("estimated_cost", 0))

    earned = calculate_tariff_points(prev_cost, est_cost)
    total = update_user_points(user, earned)
    return jsonify({
        "user": user,
        "earned_points": earned,
        "total_points": total
    })
"""
@app.route("/calculate/smart_house_points", methods=["POST"])
def route_smart_house_points():
    data = request.get_json()
    user = data.get("user")
    energy_usage = float(data.get("energy_usage", 0))
    temperature = float(data.get("temperature", 0))
    motion = bool(data.get("motion", False))
    energy_saving_mode = bool(data.get("energy_saving_mode", False))

    earned = calculate_smart_house_points(
        user, energy_usage, temperature, motion, energy_saving_mode
    )
    total = update_user_points(user, earned)
    
    points_text = "point" if abs(earned) == 1 else "points"
    action = "earned" if earned >= 0 else "lost"
    
    return jsonify({
        "user": user,
        "earned_points": earned,
        "total_points": total,
        "message": f"You {action} {abs(earned)} {points_text}! Total: {total} points"
    })
"""

@app.route("/check-leaderboard-table", methods=["GET"])
def check_leaderboard_table():
    """Check if leaderboard table exists"""
    try:
        from auth import engine, text

        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'leaderboard'
                )
            """))
            exists = result.fetchone()[0]

            return jsonify({"table_exists": exists})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/leaderboard/populate-existing", methods=["POST"])
def populate_existing_users():
    """Populate leaderboard table with existing users using user_id"""
    try:
        from auth import engine, text
        
        with engine.connect() as conn:
            # Get all users with their IDs
            result = conn.execute(text("SELECT id, username FROM users"))
            users = result.fetchall()
            
            print(f"DEBUG: Found {len(users)} users to add to leaderboard")
            
            added_count = 0
            existing_count = 0
            
            for user_id, username in users:
                # Check if user already exists in leaderboard
                existing = conn.execute(
                    text("SELECT user_id FROM leaderboard WHERE user_id = :user_id"),
                    {"user_id": user_id}
                ).fetchone()
                
                if existing:
                    print(f"DEBUG: User {username} already in leaderboard, skipping")
                    existing_count += 1
                else:
                    # Insert new user using user_id
                    conn.execute(
                        text("INSERT INTO leaderboard (user_id, points) VALUES (:user_id, 0)"),
                        {"user_id": user_id}
                    )
                    added_count += 1
                    print(f"DEBUG: Added user {username} (ID: {user_id}) to leaderboard")
            
            conn.commit()
            
            # Verify the results
            leaderboard_count = conn.execute(text("SELECT COUNT(*) FROM leaderboard")).fetchone()[0]
            
            return jsonify({
                "message": f"Leaderboard population completed",
                "users_processed": len(users),
                "users_added": added_count,
                "users_already_existed": existing_count,
                "total_in_leaderboard": leaderboard_count
            })
            
    except Exception as e:
        print(f"ERROR in populate-existing: {e}")
        return jsonify({"error": str(e)}), 500

# Main leaderboard endpoints
@app.route("/leaderboard", methods=["GET"])
def route_leaderboard():
    """Get the current leaderboard"""
    from leaderBoard import get_leaderboard
    return jsonify({"leaderboard": get_leaderboard()})

@app.route("/points/update", methods=["POST"])
@token_required
def update_points(current_user):
    """Update points for current user (for testing)"""
    from leaderBoard import update_user_points
    data = request.get_json()
    points = data.get('points', 0)

    new_total = update_user_points(current_user['username'], points)

    return jsonify({
        "message": "Points updated",
        "username": current_user['username'],
        "points_added": points,
        "total_points": new_total
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)