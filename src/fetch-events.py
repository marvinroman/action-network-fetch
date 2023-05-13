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
    # convert embed_response to JSON object
    json_response = response.json()
    embed_full_no_styles = json_response.get("embed_full_no_styles", "")
    match = re.search("src='([^']+)'.*id='([^']+)'", embed_full_no_styles)

    if match:
        return {'src': match.group(1), 'id': match.group(2)}
    else:
        return {}

output = []

# Loop through API keys
for api_key in (key for key in API_KEYS):
    current_page = 1
    total_pages = 2
    headers = {'OSDI-API-Token': api_key}

    # loop through pages
    while current_page <= total_pages:
        params = {
            "page": current_page,
            "filter": f"start_date gt '{arrow.get().shift(days=-PAST_DAYS).format('YYYY-MM-DD')}'"
        }
        response = requests.get(URL, headers=headers, params=params, timeout=10)
        json_response = response.json()

        # get paging information
        current_page = json_response.get('page', current_page)
        total_pages = json_response.get('total_pages', total_pages)
        logging.debug('current_page: %s, total_pages: %s', current_page, total_pages)

        # loop through returned events
        for event in json_response.get('_embedded', {}).get('osdi:events', []):

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

        # move paging forward
        current_page += 1

# write out content
with open('public/events.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=4)
