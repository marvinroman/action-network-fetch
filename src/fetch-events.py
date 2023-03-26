#!/usr/local/bin/python

import json
import logging
import os
import arrow
import requests

# Setup logging
logging.basicConfig(format='%(asctime)s %(message)s', filename='dist/fetch.log', level=logging.INFO)

# get settings
API_KEY = os.getenv("API_KEY")
DOMAIN = os.getenv("DOMAIN")
EVENTS_URI = os.getenv("EVENTS_URI")
FUTURE_DAYS = int(os.getenv("FUTURE_DAYS"))

# setup API url
headers = {"OSDI-API-Token": API_KEY}
url="https://{domain}/api/v2/{uri}".format(domain=DOMAIN,uri=EVENTS_URI)
logging.debug("url: %s", url)

# initiate variable
current_page = 1
total_pages = 2
output = []

# loop through pages
while current_page <= total_pages:
    
    # set current page to fetch
    params={"page": current_page}
    # make API call
    response=requests.get(url, headers=headers, params=params)
    # convert response to JSON object
    json_response=response.json()
    
    # get paging information
    current_page = json_response["page"]
    total_pages = json_response["total_pages"]
    logging.debug("current_page: %s, total_pages: %s", current_page, total_pages)
    
    # loop through returned events
    for event in json_response["_embedded"]["osdi:events"]:
        
        # setup calendar boundaries
        first_available = arrow.get("2021-02-04")
        last_available = arrow.get("2021-02-04").shift(days=FUTURE_DAYS)
        
        # if the event is between the calendar boundaries then add to output
        if arrow.get(event["start_date"]).is_between(first_available, last_available):
            output.append({
                "name": event["title"]
                , "start": event["start_date"]
                , "end": event["end_date"]
                , "description": event["description"]
                , "link": event["browser_url"]
                , "color": "cyan"
                , "timed": True
            })

    # move paging forward
    current_page += 1

# write out content
with open('dist/events.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=4)
