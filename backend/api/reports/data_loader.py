import pandas as pd
import numpy as np
import json
import os
import random

# Helper Function to Load JSON Data
def _load_json_data(filename):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, '..', '..', 'data')
    file_path = os.path.join(data_dir, filename)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # If 'processed.json' is a nested list like [[43, 45...]], it gets flattened
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], list):
                return data[0]
            
            # If 'regions_index.json' has a "regions" key
            if isinstance(data, dict) and "regions" in data:
                return data["regions"]
                
            return data
    except FileNotFoundError:
        print(f"Warning: Data file not found at {file_path}. Using empty data.")
        return []
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return []

# main function
def get_report_data(start_date, end_date):
    # Load the list of consumer IDs
    contour_ids = _load_json_data('device_ids.json') 
    # Load the usage values (The flat list [[43, 43...]])
    usage_values = _load_json_data('processed.json') 
    # Load regions (for display purposes)
    regions_list = _load_json_data('regions_index.json')
    # Constants
    TARIFF_RATE = 0.15  # Currency per kWh
    
    # Hourly data
    if not usage_values:
        # Fallback if file is empty
        usage_values = [0] * 24 

    num_points = len(usage_values)
    
    try:
        start_dt = pd.to_datetime(start_date)
    except:
        start_dt = pd.Timestamp.now()

    # Generate timestamps matching the number of data points in processed.json
    timestamps = pd.date_range(start=start_dt, periods=num_points, freq='H')

    # Create the DataFrame for the Chart
    df_timeseries = pd.DataFrame({
        'timestamp': timestamps,
        'kwh_total': usage_values
    })

    # Calculate total kWh and total cost
    total_kwh = sum(usage_values)
    total_cost = total_kwh * TARIFF_RATE

    # Distribute usage (For Top 10 Table)
    if not contour_ids:
        # Fallback if device_ids.json is missing
        top_consumers = []
    else:
        # Average usage per person
        avg_usage = total_kwh / len(contour_ids)
        
        consumer_data = []
        for cid in contour_ids:
            # Variation: +/- 30% of average
            variation = random.uniform(0.7, 1.3) 
            est_kwh = avg_usage * variation
            
            consumer_data.append({
                'contour_id': cid,
                'kwh': est_kwh,
                'cost': est_kwh * TARIFF_RATE
            })
        
        # Convert to DataFrame to easily sort and slice
        df_consumers = pd.DataFrame(consumer_data)
        
        # Sort by kWh descending and take Top 10
        top_consumers = (
            df_consumers.sort_values('kwh', ascending=False)
            .head(10)
            .to_dict('records')
        )

    # Return report data 
    return {
        "df_raw": df_timeseries,       # Chart Data (real timestamps + real processed values)
        "total_kwh": total_kwh,        # Real Sum
        "total_cost": total_cost,      # Calculated Cost
        "top_consumers": top_consumers,# Estimated distribution based on Real Total
        "regions": regions_list        # List of regions
    }