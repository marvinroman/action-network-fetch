#!/usr/local/bin/python

import json
import logging
# import os
# import time
import httplib2

# from dotenv import dotenv_values
from threading import Timer

# Setup logging
logging.basicConfig(format='%(asctime)s %(message)s', filename='/dist/fetch.log', level=logging.DEBUG)

API_KEY = os.getenv("API_KEY")

logging.debug("API_KEY: %s", API_KEY)


