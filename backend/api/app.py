from flask import Flask, jsonify
from flask import request
from flask_cors import CORS
import diff_data
import aiProvider
import aiCustomer
import os
import openai
from model.xlstm_runner import m_eval
from retrieve_data import get_series, general_info
# Commented our lines below and above use ai implementations
from gauss_tarrif import hourly_consumption
from simple_log_handler import simple_log, simple_log_clear
import json
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


client = None

try:
    client = openai.OpenAI(api_key=OPENAI_API_KEY)
except Exception as e:
    print(f"Warning: Could not initialize OpenAI client: {e}")
    
# Use relative paths for local development
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

CALC_DATA_JSON = os.path.join(DATA_DIR, "calc.json")
METER_TO_LOCATION = os.path.join(DATA_DIR, "daniel_data", "meter_to_location.json")
TOTAL_CONSUMPTION_JSON = os.path.join(DATA_DIR, "daniel_data", "location_total_consumption.json")

app = Flask(__name__)
CORS(app)

data = {}
# Opening JSON file
with open(diff_data.DATA_JSON_FILE) as json_file:
    data:dict = json.load(json_file)

keys = list(data.keys())

# Path to a simple plain-text log file. We'll truncate it at startup so it's empty when app runs.
SIMPLE_LOG_PATH = os.path.join(DATA_DIR, "simple_log.txt")
try:
    os.makedirs(os.path.dirname(SIMPLE_LOG_PATH), exist_ok=True)
    # Truncate the file at startup
    open(SIMPLE_LOG_PATH, "w", encoding="utf-8").close()
except Exception as e:
    print(f"Warning: could not create/truncate simple_log: {e}")

# zCreate a mapping from user ID to index position
def get_user_index(user_id):
    """
    Convert user ID to its index position in the data.json keys list.
    Returns the index if found, otherwise returns 0 as default.
    """
    user_id_str = str(user_id)
    if user_id_str in keys:
        return keys.index(user_id_str)
    else:
        print(f"Warning: User ID {user_id} not found in data. Using index 0 as default.")
        return 0

consumption_data = {}
# Opening JSON file
with open(TOTAL_CONSUMPTION_JSON) as json_file:
    consumption_data:dict = json.load(json_file)


calc_data = {}
with open(CALC_DATA_JSON) as json_file:
    calc_data:dict = json.load(json_file)

meter_data = {}
with open(METER_TO_LOCATION) as json_file:
    meter_data:dict = json.load(json_file)

@app.route("/id/<id>")
def hello(id):
    return data[str(id)]

@app.route("/diff/<id>/<day>")
def diffs(id, day):
    return get_series(id, day)

@app.route("/")
@app.route("/keys")
def keys_route():
    return keys

@app.route("/calc")
def calc():
    return diff_data.calc_consump(data)

@app.route("/general_info")
def general_info_route():
    diffs = general_info()
    return jsonify(diffs)

## 7->11, 18->22

@app.route("/tariff/<hour>/<previousCost>")
def tariff(hour, previousCost):
    print(hour, type(hour))
    try:
        hour = int(hour)
        previousCost = int(previousCost)
        if hour < 0 or hour > 24:
            return jsonify({"error": "Hour must be between 0 and 24"}), 400
    except Exception:
        return jsonify({"error": "Hour must be a valid integer"}), 400

    # Make sure hourly_consumption is defined and accessible
    consumption = round(hourly_consumption(hour) * previousCost * 0.15 + previousCost * 0.85, 2)
    return jsonify({"price": consumption})


@app.route("/color", methods=['POST'])
def give_color() :
    json_data = request.get_json()  # parse JSON body
    if not json_data or "time" not in json_data:
        return jsonify({"error": "Missing 'time' field"}), 400

    time_value = json_data["time"]
    x = diff_data.get_color_json(data, str(time_value)) 
    print(x)
    return x

@app.route("/region/all")
def get_regions():
    return calc_data

@app.route("/ai")
def get_ai_resp():

    if client is None:
        return jsonify({"error": "OpenAI client not initialized"}), 500

    return aiProvider.get_ai_recommendations(client, consumption_data)

@app.route("/ai/chat", methods=['POST'])
def chat_q():
    if client is None:
        return jsonify({"error": "OpenAI client not initialized"}), 500
    json_data = request.get_json()  # parse JSON body
    if not json_data or "message" not in json_data:
        return jsonify({"error": "Missing 'message' field"}), 400
    
    message = json_data["message"]
    return {"response": aiCustomer.get_ai_response(message)}

@app.route("/consumptions")
def give_consumption():
    return consumption_data

@app.route("/pred/<user_id>")
def pred_user(user_id):
    series = get_series(user_id)
    try:
        return m_eval(series=series, week=False)
    except ValueError:
        return jsonify({"error": "Invalid user ID"}), 400

# Location-based prediction routes
@app.route("/pred/location/<location_name>")
def pred_location(location_name):
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
        
        # Get predictions using location index
        predictions = m_eval(series=[], week=False, location=location_index)
        return jsonify(predictions)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/pred/location/<location_name>/week")
def pred_location_week(location_name):
    """Get weekly predictions for a specific location"""
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
        
        # Get weekly predictions using location index
        predictions = m_eval(series=[], week=True, location=location_index)
        return jsonify(predictions)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/locations")
def get_locations():
    """Get list of available locations"""
    try:
        regions_index_path = os.path.join(BASE_DIR, "data", "model_data", "regions_index.json")
        with open(regions_index_path, "r", encoding="utf-8") as f:
            regions_data = json.load(f)
        return jsonify(regions_data["regions"])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/simple_log", methods=["POST"])
def route_simple_log():
    return simple_log()


@app.route("/simple_log/clear", methods=["POST"])
def route_simple_log_clear():
    return simple_log_clear()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)