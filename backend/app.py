from flask import Flask, jsonify
from flask import request
from flask_cors import CORS
import diff_data
import aiProvider
import aiCustomer
import os
import openai
import model.xlstm_runner
from model.xlstm_runner import m_eval
from gauss_tarrif import hourly_consumption

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# Use relative paths for local development
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")

CALC_DATA_JSON = os.path.join(DATA_DIR, "calc.json")
METER_TO_LOCATION = os.path.join(DATA_DIR, "daniel_data", "meter_to_location.json")
TOTAL_CONSUMPTION_JSON = os.path.join(DATA_DIR, "daniel_data", "location_total_consumption.json")

app = Flask(__name__)
CORS(app)

import json
data = {}
# Opening JSON file
with open(diff_data.DATA_JSON_FILE) as json_file:
    data:dict = json.load(json_file)

keys = list(data.keys())

# Create a mapping from user ID to index position
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

ai_data = aiProvider.get_location_energy_data(data, meter_data)

@app.route("/id/<id>")
def hello(id):
    return data[str(id)]

@app.route("/diff/<id>")
def diffs(id):
    return diff_data.get_diffs(data[str(id)])

@app.route("/")
@app.route("/keys")
def keys_route():
    return keys

# @app.route("/calc")
# def calc():
#     return diff_data.calc_consump(data)

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
    return diff_data.get_color_json(data, str(time_value))

@app.route("/region/all")
def get_regions():
    return calc_data

@app.route("/ai")
def get_ai_resp():
    return aiProvider.get_ai_recommendations(client, ai_data)

@app.route("/ai/chat", methods=['POST'])
def chat_q():
    json_data = request.get_json()  # parse JSON body
    if not json_data or "message" not in json_data:
        return jsonify({"error": "Missing 'message' field"}), 400
    
    message = json_data["message"]
    return {"response": aiCustomer.get_ai_response(client, message)}

@app.route("/consumptions")
def give_consumption():
    return consumption_data

@app.route("/pred/week")
def w_pred():
    return m_eval(user_index=0, week=True)

@app.route("/pred")
def pred():
    return m_eval(user_index=0)


@app.route("/pred/week/<user_id>")
def w_pred_user(user_id):
    try:
        user_id_int = int(user_id)
        user_index = get_user_index(user_id_int)
        return m_eval(user_index=user_index, week=True)
    except ValueError:
        return jsonify({"error": "Invalid user ID"}), 400

@app.route("/pred/<user_id>")
def pred_user(user_id):
    try:
        user_id_int = int(user_id)
        user_index = get_user_index(user_id_int)
        print(f"DEBUG: pred_user called with user_id={user_id_int}, mapped to user_index={user_index}")
        return m_eval(user_index=user_index)
    except ValueError:
        return jsonify({"error": "Invalid user ID"}), 400

@app.route("/debug/user_mapping/<user_id>")
def debug_user_mapping(user_id):
    """Debug route to check user ID to index mapping"""
    try:
        user_id_int = int(user_id)
        user_index = get_user_index(user_id_int)
        return jsonify({
            "user_id": user_id_int,
            "user_index": user_index,
            "total_users": len(keys),
            "available_user_ids": keys[:10] if len(keys) > 10 else keys  # Show first 10 or all if less
        })
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
        predictions = m_eval(user_index=location_index, week=False, location=location_index)
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
        predictions = m_eval(user_index=location_index, week=True, location=location_index)
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)