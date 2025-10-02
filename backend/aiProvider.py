"""
It generates 4 energy recommendations for grid operators using OpenAI.
Uses diff_data to get energy data for each location at the last known time (08.06.2025 12:00:00).
"""

import sys
def check_venv():
	if sys.prefix == sys.base_prefix:
		print("Warning: You are not running inside a Python virtual environment (venv). Activate your venv for best practice.")
		print("To activate: source venv/bin/activate (Linux/Mac) or .\\venv\\Scripts\\activate (Windows)")
check_venv()


import openai
import os
import json
import sys
from diff_data import get_timed_diffs

# Set your OpenAI API key here or via environment variable OPENAI_API_KEY

# System prompt for provider recommendations
SYSTEM_PROMPT = (
	"You are an expert energy grid operator. "
	"Given the latest energy data for each location, generate 4 recommendations for grid management. "
	"For each, generate a catchy, attention-grabbing title (e.g. 'Chișinău on the Brink!', 'Orhei's Solar Surge', 'Balti: Demand Spike Alert') and a one-sentence recommendation for that location. "
	"Format each as: Title\nRecommendation\n."
	"Dont use any kind of markdown"
	"Use simple UTF-8 plaintext"
)


# Summarize energy data by location
def get_location_energy_data(data, location_to_meters):
	
	time = "08.06.2025 12:00:00"
	location_energy = {}
	for location, meters in location_to_meters.items():
		# Convert all meter IDs to str for compatibility
		meter_ids = [str(m) for m in meters]
		loc_data = get_timed_diffs(data, meter_ids, time)
		total_import = sum(v.get("Import", 0) for v in loc_data.values())
		total_export = sum(v.get("Export", 0) for v in loc_data.values())
		location_energy[location] = {
			"Import": total_import,
			"Export": total_export,
		}
	return location_energy



def get_ai_recommendations(client, energy_data: dict, model: str = "gpt-3.5-turbo") -> list:
	# Prepares a summary for the AI.
	summary = "Energy summary for locations at 08.06.2025 12:00:00:\n"
	for location, vals in energy_data.items():
		summary += f"Location: {location}, Total Import: {vals['Import']}, Total Export: {vals['Export']}\n"
	prompt = summary + "\nGenerate 4 recommendations for grid operators. For each, provide a title and a one-sentence recommendation for that location."
	response = client.chat.completions.create(
		model=model,
		messages=[
			{"role": "system", "content": SYSTEM_PROMPT},
			{"role": "user", "content": prompt}
		]
	)
	# Parses a response into title/recommendation pairs.
	result = response.choices[0].message.content.strip()
	blocks = [block.strip() for block in result.split('\n\n') if block.strip()]
	pairs = []
	for block in blocks:
		lines = [line.strip() for line in block.split('\n') if line.strip()]
		if len(lines) >= 2:
			pairs.append({'title': lines[0], 'recommendation': lines[1]})
	return pairs

# if __name__ == "__main__":
# 	energy_data = get_location_energy_data()
# 	recommendations = get_ai_recommendations(energy_data)
# 	print("Recommendations:")
# 	for rec in recommendations:
# 		print(f"Title: {rec['title']}")
# 		print(f"Recommendation: {rec['recommendation']}")
# 		print()
