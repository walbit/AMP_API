#!/usr/bin/env python

import argparse
import pprint
import random
import requests
import string

# YOU NEED TO CREATE AN auth.py FILE WITH CLIENT_ID AND API_KEY STRINGS
from auth import CLIENT_ID, API_KEY

random_name = ''.join(random.choice(
    string.ascii_uppercase + string.digits) for _ in range(10))

parser = argparse.ArgumentParser()
parser.add_argument('event_type_id', metavar='event_type_id',
                    nargs=1, help='event type id')
parser.parse_args()
event_type = int(parser.parse_args().event_type_id[0])

api_endpoint = 'https://api.amp.cisco.com/v1/event_streams'

session = requests.Session()
session.auth = (CLIENT_ID, API_KEY)

event_stream = session.post(
    api_endpoint, json={"name": random_name, "event_type": [event_type]}).json()

pprint.pprint(event_stream)
