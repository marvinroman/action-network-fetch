## Overview
The script fetches event data from an external API, filters the events by date and status, and then creates an array of event objects. It also fetches the embed code for each event and includes it in the event object. Finally, it writes the array of event objects to a JSON file so that it can be fetched by calendars.

## Dependencies
The script requires the following dependencies:

* `arrow`
* `requests`

## Configuration
The script relies on a number of environment variables to configure its behavior. These variables include:

* `API_KEYS`: A comma-separated list of API keys to use when making requests to the external API.
* `DOMAIN`: The domain name of the external API.
* `EVENTS_URI`: The URI to use when fetching events from the external API.
* `PAST_DAYS`: The number of days in the past to include events for.

## Functions
The script includes one main function:

### `getEmbed(event_object, headers)`
This function fetches the embed code for a given event object. It takes two arguments:

* `event_object`: The event object to fetch the embed code for.
* `headers`: The headers to include in the request to fetch the embed code.

The function returns an object that includes the parsed `src` and `id` attributes from the embed code.

## Main Loop
The main loop of the script iterates over each API key in `API_KEYS`. For each key, it makes requests to the external API to fetch event data, filters the events by date and status, and adds the events to an array. It also fetches the embed code for each event and adds it to the event object. Finally, it writes the array of event objects to a JSON file.

## Output
The script writes an array of event objects to a JSON file at `public/events.json`. The event objects include the following properties:

* `name`: The name of the event.
* `group`: The name of the group sponsoring the event.
* `start`: The start date and time of the event, formatted as `YYYY-MM-DD HH:mm`.
* `embed`: An object that includes the `src` and `id` attributes of the embed code for the event.
* `end`: The end date and time of the event, formatted as `YYYY-MM-DD HH:mm`, or an empty string if the event has no end time.
* `description`: A description of the event.
* `featured_image_url`: The URL of a featured image for the event.
* `instructions`: Any instructions for attendees of the event.
* `location`: The location of the event.
* `uid`: An array of identifiers for the event.
* `link`: The URL of the event's page on the external API.
* `color`: A color to use when displaying the event.
* `timed`: `true` if the event has an end time, `false` otherwise.