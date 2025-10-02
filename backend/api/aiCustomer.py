import sys

def check_venv():
	# Check if running inside a virtual environment
	if sys.prefix == sys.base_prefix:
		print("Warning: You are not running inside a Python virtual environment (venv). Activate your venv for best practice.")
		print("To activate: source venv/bin/activate (Linux/Mac) or .\\venv\\Scripts\\activate (Windows)")
  
check_venv()
"""
aiCustomer.py
---------------------------------------------
Console tool for interacting with OpenAI's GPT models, with a system prompt.
The AI acts as a professional in energy consumption for customers, giving clear, concise advice in one sentence.
---------------------------------------------
"""

import openai
import os


# Set your OpenAI API key here or via environment variable OPENAI_API_KEY


# System prompt to define AI's role and response style
SYSTEM_PROMPT = (
	"You are an expert energy consultant for residential customers. "
	"Your job is to provide actionable, practical advice to help people reduce energy consumption and save money at home. "
	"Always answer in one short, clear sentence, focused on the most effective tip for the situation. "
	"Avoid technical jargon and keep your advice easy to understand.(Dont repeat yourself)"
)

def get_ai_response(client, prompt: str, model: str = "gpt-3.5-turbo") -> str:
	"""
	Sends a prompt to OpenAI with a system message and returns the response as a string.
	"""
	response = client.chat.completions.create(
		model=model,
		messages=[
			{"role": "system", "content": SYSTEM_PROMPT},
			{"role": "user", "content": prompt}
		]
	)
	return response.choices[0].message.content.strip()

if __name__ == "__main__":

	OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
	print("Enter your prompt for the AI (type 'exit' to quit):")
	while True:
		user_input = input("Prompt: ").strip()
		if user_input.lower() == "exit":
			break
		try:
			result = get_ai_response(openai.OpenAI(api_key=OPENAI_API_KEY), user_input)
			print("AI Response:", result)
		except Exception as e:
			print("Error:", e)


