"""
aiProvider.py
---------------------------------------------
Generates 4 energy recommendations for grid operators using OpenAI.
Uses diff_data to get energy data for each location at the last known time (08.06.2025 12:00:00).
Each recommendation is one clear, actionable sentence.
---------------------------------------------
"""


import openai
import os
import sys
from diff_data import get_timed_diffs
import json


# Set your OpenAI API key here or via environment variable OPENAI_API_KEY

# System prompt for provider recommendations
SYSTEM_PROMPT = (
	"You are an expert energy grid operator. "
	"Given the latest energy data for each location, generate exactly 4 recommendations for grid management. "
	"For each recommendation produce a short, attention-grabbing title and a one-sentence actionable recommendation for that location. "
	"Return the output as a JSON array with 4 objects, each object having the fields:\n  title (string)\n  recommendation (string)\n" 
	"Example output (valid JSON):\n[ { \"title\": \"Balti: Demand Spike Alert\", \"recommendation\": \"Redispatch 20 MW from nearby reservoirs to Balti in the next hour.\" }, ... ]\n"
	"If you cannot produce valid JSON, fall back to plain text where each recommendation is separated by a blank line and each recommendation contains a title on the first line and the recommendation on the second line. "
	"Do not use markdown in any form. Use simple UTF-8 plaintext."
)

def _parse_text_fallback(text: str) -> list:
	"""Try to parse title/recommendation pairs from free text.

	Heuristics:
	- Split on double newlines to find blocks.
	- For each block, take the first non-empty line as title and the rest joined as recommendation.
	- If blocks are fewer than 4, try to split by sentence endings and build up to 4 items.
	"""
	import re

	blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
	pairs = []
	for block in blocks:
		lines = [l.strip() for l in block.split('\n') if l.strip()]
		if len(lines) >= 2:
			title = lines[0]
			recommendation = ' '.join(lines[1:]).strip()
			pairs.append({'title': title, 'recommendation': recommendation})
		else:
			# try to split the single-line block into title and recommendation with punctuation
			m = re.split(r"[:\-–—]\s*", block, maxsplit=1)
			if len(m) == 2:
				pairs.append({'title': m[0].strip(), 'recommendation': m[1].strip()})
	# If still fewer than 4, try to extract sentences and craft simple titles
	if len(pairs) < 4:
		sentences = re.split(r"(?<=[.!?])\s+", text)
		for i, sent in enumerate(sentences):
			if len(pairs) >= 4:
				break
			s = sent.strip()
			if len(s) < 20:
				continue
			title = (s[:50] + '...') if len(s) > 50 else s.split('.')[0]
			pairs.append({'title': title, 'recommendation': s})
	return pairs[:4]


def get_ai_recommendations(client, energy_data: dict, model: str = "gpt-4o-mini") -> list:
	# Prepare a summary for the AI
	summary = "Energy summary for locations at 08.06.2025 12:00:00:\n"
	sorted_locations = sorted(energy_data.items(), key=lambda item: item[1], reverse=True)
	top_locs = [item[0] for item in sorted_locations[:4]]
	selected = {loc: energy_data[loc] for loc in top_locs}  # dictionary with selected data

	for location, vals in selected.items():
		summary += f"Location: {location}, Total Import: {vals}\n"

	prompt = summary + "\nGenerate 4 recommendations for the following locations for grid operators. For each, provide a title and a one-sentence recommendation for that location. Return JSON as an array of objects with keys 'title' and 'recommendation'."

	response = client.chat.completions.create(
		model=model,
		messages=[
			{"role": "system", "content": SYSTEM_PROMPT},
			{"role": "user", "content": prompt}
		]
	)

	"""
	Title: Rezina
	Description: Increase local generation capacity by 15% to meet rising demand during peak hours.

	Title: Cahul
	Description: Implement demand response programs to reduce consumption during critical periods.
	"""
	# Try parsing JSON first
	text = response.choices[0].message.content.strip()
	try:
		parsed = json.loads(text)
		# Validate parsed structure
		if isinstance(parsed, list):
			pairs = []
			for item in parsed[:4]:
				if isinstance(item, dict) and 'title' in item and 'recommendation' in item:
					pairs.append({'title': str(item['title']).strip(), 'recommendation': str(item['recommendation']).strip()})
			if len(pairs) > 0:
				return pairs
	except Exception:
		pass

	# Fallback to text parsing heuristics
	return _parse_text_fallback(text)

if __name__ == "__main__":
	energy_data = {"Balti": 27876095,
	"Cahul": 35090435,
	"Chisinau": 31165585,
	"Comrat": 33084887,
	"Cricova": 28944101,
	"Edinet": 31459213,
	"Floresti": 33328896,
	"Hincesti": 34423357,
	"Orhei": 22273335,
	"Rezina": 40183940,
	"Soroca": 25077732,
	"Stefan Voda": 31567167,
	"Tiraspol": 28081344,
	"Ungheni": 31092545,
	"Vadul lui Voda": 21735612}

	OPENAI_API_KEY = "openAIkey"
	client = openai.OpenAI(api_key=OPENAI_API_KEY)

	recommendations = get_ai_recommendations(client, energy_data)
	print("Recommendations:")
	for rec in recommendations:
		print(f"Title: {rec['title']}")
		print(f"Recommendation: {rec['recommendation']}")