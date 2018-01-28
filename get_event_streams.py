#!/usr/bin/env python

import pprint
import requests

# YOU NEED TO CREATE AN auth.py FILE WITH CLIENT_ID AND API_KEY STRINGS
from auth import CLIENT_ID, API_KEY

api_endpoint = 'https://api.amp.cisco.com/v1/event_streams'

session = requests.Session()
session.auth = (CLIENT_ID, API_KEY)

event_types = session.get(api_endpoint).json()

pprint.pprint(event_types)
