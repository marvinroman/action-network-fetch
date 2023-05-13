# pylint: disable=invalid-name,import-error,consider-using-f-string,missing-module-docstring,line-too-long,redefined-outer-name

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

# get settings
API_KEYS = os.getenv("API_KEYS").split(',')
DOMAIN = os.getenv("DOMAIN")
EVENTS_URI = os.getenv("EVENTS_URI")
PAST_DAYS = int(os.getenv("PAST_DAYS"))
URL = f'https://{DOMAIN}/api/v2/{EVENTS_URI}'

def get_event_embed(event, headers):
    """Fetches the embed code for the event."""

    links = event.get('_links', {})
    embed_url = links.get('action_network:embed', {}).get('href')
    if not embed_url:
        return {}

    # make API call
    response = requests.get(embed_url, headers=headers, timeout=10)
    response.raise_for_status()
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

    # loop through pages
    while response.json().get("_links", {}).get("next"):
        logging.debug('next page: %s', response.json().get("_links", {}).get("next"))

        # loop through returned events
        for event in response.json().get('_embedded', {}).get('osdi:events', []):

            # if the event is between the calendar boundaries then add to output
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

        # get next page
        response = requests.get(response.json().get("_links", {}).get("next", {}).get("href"), headers=headers, timeout=10)
        response.raise_for_status()

# write out content
with open('public/events.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=4)
