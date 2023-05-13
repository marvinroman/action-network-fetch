# Import necessary modules
import json
import logging
import os
import re
import requests
import arrow

# Set up logging
logging.basicConfig(
    format='%(asctime)s %(message)s',
    filename='public/fetch.log',
    level=logging.DEBUG
)

# Get settings from environment variables
API_KEYS = os.getenv("API_KEYS").split(',')
DOMAIN = os.getenv("DOMAIN")
EVENTS_URI = os.getenv("EVENTS_URI")
PAST_DAYS = int(os.getenv("PAST_DAYS"))
URL = f'https://{DOMAIN}/api/v2/{EVENTS_URI}'

def get_event_embed(event, headers):
    """
    Fetches the embed code for the event.

    :param event: Event object from API response
    :param headers: HTTP headers with OSDI API token
    :return: Dictionary containing the event's embed source and ID
    """
    links = event.get('_links', {})
    embed_url = links.get('action_network:embed', {}).get('href')
    if not embed_url:
        return {}

    # Make API call to get embed code
    response = requests.get(embed_url, headers=headers, timeout=10)
    response.raise_for_status()

    # Parse embed code for source and ID
    embed_full_no_styles = response.json().get("embed_full_no_styles", "")
    match = re.search("src='([^']+)'.*id='([^']+)'", embed_full_no_styles)

    if match:
        return {'src': match.group(1), 'id': match.group(2)}
    else:
        return {}

output = []

# Loop through API keys
for api_key in (key for key in API_KEYS):
    headers = {'OSDI-API-Token': api_key}
    params = {
        "filter": f"start_date gt '{arrow.get().shift(days=-PAST_DAYS).format('YYYY-MM-DD')}'"
    }
    response = requests.get(URL, headers=headers, params=params, timeout=10)
    response.raise_for_status()

    # Loop through pages of API response
    while response.json().get("_links", {}).get("next"):
        logging.debug('next page: %s', response.json().get("_links", {}).get("next"))

        # Loop through events in API response
        for event in response.json().get('_embedded', {}).get('osdi:events', []):

            # Only add confirmed events within the specified timeframe to output
            if event.get("status") == "confirmed":
                output.append({
                    "name": event.get("title"),
                    "group": event.get("action_network:sponsor", {}).get("title", ""),
                    "start": arrow.get(event.get("start_date", "")).format("YYYY-MM-DD HH:mm"),
                    "embed": get_event_embed(event, headers),
                    "end": arrow.get(event.get("end_date", "")).format("YYYY-MM-DD HH:mm") if event.get("end_date") else "",
                    "description": event.get("description", ""),
                    "featured_image_url": event.get("featured_image_url", ""),
                    "instructions": event.get("instructions", ""),
                    "location": event.get('location'),
                    "uid": event.get("identifiers"),
                    "link": event.get("browser_url"),
                    "color": "primary",
                    "timed": bool(event.get("end_date"))
                })

        # Get next page of API response
        response = requests.get(response.json().get("_links", {}).get("next", {}).get("href"), headers=headers, timeout=10)
        response.raise_for_status()

# Write out events to JSON file
with open('public/events.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=4)