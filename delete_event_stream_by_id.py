#!/usr/bin/env python

import argparse
import pika
import pprint
import requests

# YOU NEED TO CREATE AN auth.py FILE WITH CLIENT_ID AND API_KEY STRINGS
from auth import CLIENT_ID, API_KEY

parser = argparse.ArgumentParser()
parser.add_argument('event_stream_id', metavar='event_stream_id',
                    nargs=1, help='event stream id')
parser.parse_args()
event_stream_id = parser.parse_args().event_stream_id[0]

api_endpoint = 'https://api.amp.cisco.com/v1/event_streams'

session = requests.Session()
session.auth = (CLIENT_ID, API_KEY)


deleted_stream = session.delete(
    "{}/{}".format(api_endpoint, event_stream_id)).json()

pprint.pprint(deleted_stream)
