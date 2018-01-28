#!/usr/bin/env python

import argparse
import pika
import pprint
import requests

# YOU NEED TO CREATE AN auth.py FILE WITH CLIENT_ID AND API_KEY STRINGS
from auth import CLIENT_ID, API_KEY

parser = argparse.ArgumentParser()
parser.add_argument('event_stream_name', metavar='event_stream_name',
                    nargs=1, help='event stream name')
parser.parse_args()
event_stream_name = parser.parse_args().event_stream_name[0]

api_endpoint = 'https://api.amp.cisco.com/v1/event_streams'

session = requests.Session()
session.auth = (CLIENT_ID, API_KEY)

event_streams = session.get(api_endpoint).json()['data']

event_stream = {}

for e in event_streams:
    if e['name'] is event_stream_name:
        event_stream = e


amqp_url = 'amqps://{user_name}:{password}@{host}:{port}'.format(
    **e['amqp_credentials'])
queue = e['amqp_credentials']['queue_name']
parameters = pika.URLParameters(amqp_url)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()


parameters = pika.URLParameters(amqp_url)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()


def callback(ch, method, properties, body):
    print(" [x] Received meth:\t%r" % method)
    print(" [x] Received prop:\t%r" % properties)
    print(" [x] Received body:\t%r" % body)


channel.basic_consume(callback, queue, no_ack=True)

print(" [*] Connecting to:\t%r" % amqp_url)
print(" [*] Waiting for messages. To exit press CTRL+C")
channel.start_consuming()
