# pylint: disable=invalid-name,import-error,consider-using-f-string,missing-module-docstring

import json
import logging
import os
import re
import requests
import arrow

# get settings
API_KEY = os.getenv("API_KEY")
DOMAIN = os.getenv("DOMAIN")
EVENTS_URI = os.getenv("EVENTS_URI")
FUTURE_DAYS = int(os.getenv("FUTURE_DAYS"))

# Setup logging
logging.basicConfig(format='%(asctime)s %(message)s',
                    filename='public/fetch.log', level=logging.DEBUG)

# setup API url
headers = {"OSDI-API-Token": API_KEY}
url = "https://{domain}/api/v2/{uri}".format(domain=DOMAIN, uri=EVENTS_URI)
logging.debug("url: %s", url)

# initiate variables
current_page = 1
total_pages = 2
output = []

def getEmbed(event_object):
    """ fetches the embed code for the event

    Args:
        event_object (Object): the event currently being processed

    Returns:
        Object: object that includes the parsed src & id
    """

    if bool(event_object.get("_links")) is False:
        return {}

    links = event_object.get("_links")

    if bool(links.get("action_network:embed")) is False:
        return {}

    embed_url = links.get("action_network:embed")

    # make API call
    embed_response = requests.get(embed_url.get("href"), headers=headers, timeout=10)
    # convert embed_response to JSON object
    json_embed_response = embed_response.json()

    embed_full_no_styles = json_embed_response.get("embed_full_no_styles")

    match = re.search("src='([^']+)'.*id='([^']+)'", embed_full_no_styles)

    if match:
        return {
            "src": match.group(1), "id": match.group(2)
        }
    else:
        return {}


# loop through pages
while current_page <= total_pages:
    # set current page to fetch
    params = {"page": current_page}
    # make API call
    response = requests.get(url, headers=headers, params=params, timeout=10)
    # convert response to JSON object
    json_response = response.json()

    # get paging information
    current_page = json_response["page"]
    total_pages = json_response["total_pages"]
    logging.debug("current_page: %s, total_pages: %s",
                  current_page, total_pages)

    # loop through returned events
    for event in json_response["_embedded"]["osdi:events"]:

        # setup calendar boundaries
        first_available = arrow.get()
        last_available = arrow.get().shift(days=FUTURE_DAYS)

        # if the event is between the calendar boundaries then add to output
        if arrow.get(event.get("start_date")).is_between(first_available, last_available) and event.get("status") == "confirmed":
            output.append({
                "name": event.get("title"), "start": arrow.get(event.get("start_date")).format("YYYY-MM-DD HH:mm"), "embed": getEmbed(event), "end": arrow.get(event.get("end_date")).format("YYYY-MM-DD HH:mm") if event.get("end_date") else "", "description": event.get("description", ""), "link": event.get("browser_url"), "color": "primary", "timed": bool(event.get("end_date"))
            })

    # move paging forward
    current_page += 1

# write out content
with open('public/events.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=4)
