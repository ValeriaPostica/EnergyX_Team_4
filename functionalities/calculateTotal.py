"""
This script is ran just one time for calculating the maximum energy consum for all location given all data , and saves everything in a json file found in data-> daniel-data
DONT RUN THIS SCRIPT ANYMORE

"""


import os
import glob
import json
import pandas as pd

# Path to all CSVs

# DATA_DIR = os.path.join(os.path.dirname(__file__), '../backend/data')
# # Path to meter-to-location mapping
# METER_MAP_PATH = r''
# # Output file
# OUTPUT_PATH = r''

def main():
	# Load meter-to-location mapping
	with open(METER_MAP_PATH, encoding='utf-8') as f:
		location_to_meters = json.load(f)
	# Reverse mapping: meter_id -> location
	meter_to_location = {}
	for location, meters in location_to_meters.items():
		for m in meters:
			meter_to_location[str(m)] = location

	# Find all CSV files
	csv_files = glob.glob(os.path.join(DATA_DIR, '*.csv'))
	# Dict: meter_id -> [all import values]
	meter_imports = {}
	for file in csv_files:
		try:
			df = pd.read_csv(file, dtype=str)
			for _, row in df.iterrows():
				meter = str(row['Meter'])
				import_val = float(row['Active Energy Import (3:1-0:1.8.0*255:2)'])
				if meter not in meter_imports:
					meter_imports[meter] = []
				meter_imports[meter].append(import_val)
		except Exception as e:
			print(f"Error reading {file}: {e}")

	# Calculate total difference per meter
	meter_diffs = {}
	for meter, vals in meter_imports.items():
		if len(vals) >= 2:
			meter_diffs[meter] = vals[-1] - vals[0]
		else:
			meter_diffs[meter] = 0

	# Aggregate by location
	location_totals = {}
	for meter, diff in meter_diffs.items():
		location = meter_to_location.get(meter)
		if location:
			location_totals[location] = location_totals.get(location, 0) + diff

	# Save to JSON
	with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
		json.dump(location_totals, f, indent=2)
	print(f"Saved total consumption per location to {OUTPUT_PATH}")

if __name__ == "__main__":
	main()
"""
This script is ran just one time for calculating the maximum energy consum for all location given all data , and saves everything in a json file found in data-> daniel-data
DONT RUN THIS SCRIPT ANYMORE

"""
