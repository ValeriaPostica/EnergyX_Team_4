# notifications.py

THRESHOLD = 1200   # decide a threshold or make it dynamic

def detect_high_usage(location_data, threshold=THRESHOLD):
    """Returns a list of locations with usage above threshold."""
    alerts = []

    if not isinstance(location_data, dict):
        return alerts

    for location, usage in location_data.items():
        try:
            if usage > threshold:
                alerts.append({
                    "location": location,
                    "usage": usage,
                    "alert": f"High usage detected in {location}: {usage}"
                })
        except Exception:
            continue

    return alerts


def get_ai_suggestion(client, location, usage):
    prompt = (
        f"Energy usage in {location} is {usage}, which is above the expected threshold. "
        f"Suggest one actionable step for the energy provider."
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message["content"]
