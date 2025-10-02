

# todayDataById.py
# ---------------------------------------------
# This module provides functions to extract hourly energy import differences
# for a given meter ID, for the dates 07.06.2025 and 08.06.2025, from the main
# data.json file. It is optimized for fast repeated queries and is intended to
# be used by the frontend or other backend services.
#
# Main features:
# - Loads and parses the large data.json file only once
# - Builds a pandas DataFrame for efficient filtering
# - Computes hourly import differences for a meter and fills missing data
# - Returns two arrays (one for each day) for easy frontend consumption
# ---------------------------------------------

import json
import os
import sys
import pandas as pd
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'api')))


# Load the main data.json file containing all meter readings.
# The file is expected to be a dictionary mapping meter IDs to lists of readings.
DATA_PATH = os.path.join(os.path.dirname(__file__), '../data/data.json')
with open(DATA_PATH, encoding='utf-8') as f:
	data = json.load(f)


# Build a pandas DataFrame from the data.json structure for fast filtering.
# Each row represents a single reading for a meter, with the meter ID in the 'Meter' column.
def build_meter_dataframe(data):
	return (
		pd.concat({k: pd.DataFrame(v) for k, v in data.items()}, names=["Meter"])
		.reset_index(level=0)
		.reset_index(drop=True)
	)

# The DataFrame is built once and reused for all queries.
df = build_meter_dataframe(data)
# The column name for the timestamp in the data files.
CLOCK_COLMN_NAME = "Clock (8:0-0:1.0.0*255:2)"



def get_hourly_import_diffs_for_day(meter_id: str, day: str) -> list:
	"""
	For a given meter_id and day (format: 'DD.MM.YYYY'), returns a list of 24 hourly import differences.
	Each value is the difference in import energy between consecutive hours.
	If data is missing for an hour, fills with the last known value.
	Returns:
		List[float]: 24 hourly import differences (missing values filled).
	"""
	# Filter the DataFrame for the selected meter
	meter_df = df[df["Meter"] == meter_id]
	diffs = []
	for hour in range(24):
		t1 = f"{day} {hour:02d}:00:00"
		t2 = f"{day} {hour+1:02d}:00:00" if hour < 23 else None
		if t2:
			row1 = meter_df[meter_df[CLOCK_COLMN_NAME] == t1]
			row2 = meter_df[meter_df[CLOCK_COLMN_NAME] == t2]
			if not row1.empty and not row2.empty:
				import1 = row1.iloc[0]["Active Energy Import (3:1-0:1.8.0*255:2)"]
				import2 = row2.iloc[0]["Active Energy Import (3:1-0:1.8.0*255:2)"]
				diff_val = import2 - import1
				diffs.append(float(diff_val))
			else:
				# Missing data for this hour
				diffs.append(None)
		else:
			# Last hour, no next hour to compare
			diffs.append(None)
	# Fill None values with last non-None value for frontend compatibility
	filled = []
	last_val = None
	for val in diffs:
		if val is not None:
			filled.append(val)
			last_val = val
		else:
			filled.append(last_val)
	return filled



def get_today_and_tomorrow_import_diffs(meter_id: str):
	"""
	For a given meter_id, returns two arrays:
		- Hourly import differences for 07.06.2025
		- Hourly import differences for 08.06.2025
	Each array contains 24 values, with missing data filled as described above.
	Returns:
		Tuple[List[float], List[float]]
	"""
	arr_07 = get_hourly_import_diffs_for_day(meter_id, "07.06.2025")
	arr_08 = get_hourly_import_diffs_for_day(meter_id, "08.06.2025")
	return arr_07, arr_08


# Example usage for testing and debugging
if __name__ == "__main__":
	# Change testid to any valid meter ID from your data.json
	testid = "14461231"
	arr_07, arr_08 = get_today_and_tomorrow_import_diffs(testid)
	print("07.06.2025 diffs:", arr_07)
	print("08.06.2025 diffs:", arr_08)
