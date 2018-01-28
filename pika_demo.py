#!/usr/bin/env python

import pprint as pp

import pika
import requests

from auth import CLIENT_ID, API_KEY

''' Here's a basic example for using event_streams.

First, we need to create an event_stream that filters on some criteria. In this example we create a stream for any "Threat Detected" events, event_type: 1090519054.

```
curl -X POST -H 'accept: application/json' -H 'content-type: application/json' --compressed -H 'Accept-Encoding: gzip, deflate' -d '{"name":"DQrbpudi","event_type":[1090519054]}' -u 'CLIENT_ID:API_KEY' 'https://api.amp.cisco.com/v1/event_streams' | jq
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100   290  100   245  100    45    217     39  0:00:01  0:00:01 --:--:--   217
{
  "version": "v1.2.0",
  "metadata": {
    "links": {
      "self": "https://api.amp.cisco.com/v1/event_streams"
    }
  },
  "data": {
    "id": 6,
    "name": "DQrbpudi",
    "amqp_credentials": {
      "user_name": "username",
      "password": "password",
      "queue_name": "event_stream_6",
      "host": "export-streaming.amp.cisco.com",
      "port": "443",
      "proto": "https"
    }
  }
}
```

The above POST will create the event_stream. You can also get a list including the newly created event_stream and any other event_streams you've created in the past.

```
curl -X GET -H 'accept: application/json' -H 'content-type: application/json' --compressed -H 'Accept-Encoding: gzip, deflate' -u 'CLIENT_ID:API_KEY' 'https://api.amp.cisco.com/v1/event_streams' | jq
```

Now let's start our script.

Here's the JSON response above dumped into a dictionary.
'''

session = requests.Session()
session.auth = (CLIENT_ID, API_KEY)

all_streams = session.get("https://api.amp.cisco.com/v1/event_streams").json()

pp.pprint(all_streams)

new_stream = session.post("https://api.amp.cisco.com/v1/event_streams",
                          json={"name": "DQrbpudi", "event_type": [1090519054]})
pp.pprint(new_stream.json())

response = session.get("https://api.amp.cisco.com/v1/event_streams/{}".format(new_stream.json()['data']['id'])).json()

pp.pprint(response)

'''First we'll craft our AMQP URL from the JSON response.
'''

amqp_url = 'amqps://{user_name}:{password}@{host}:{port}'.format(**response['data']['amqp_credentials'])
queue = response['data']['amqp_credentials']['queue_name']
parameters = pika.URLParameters(amqp_url)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

'''From here on out we're basically using the RabbitMQ tutorial so look there for more detailed explanations.

    https://www.rabbitmq.com/tutorials/tutorial-one-python.html
'''

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

'''Here's what the output should look like if you create an eicar test file on one of your endpoings.

    ./pika_demo.py
     [*] Connecting to:	'amqps://username:password@export-streaming.amp.cisco.com:443/%2F?ssl_options=%7B%27keyfile%27%3A+%27key.pem%27%2C+%27certfile%27%3A+%27certificate.pem%27%7D'
     [*] Waiting for messages. To exit press CTRL+C
     [x] Received meth:	<Basic.Deliver(['consumer_tag=ctag1.d7a99d528b364cf0bf7c93b567ef2894', 'delivery_tag=1', 'exchange=events_api_stream', 'redelivered=False', 'routing_key=df2b7653-ef93-4bf8-801f-2b97b9bb7a01.d05a5933-880a-41ac-8bb4-949a9c8786c2.1090519054'])>
     [x] Received prop:	<BasicProperties(['content_type=application/octet-stream', 'delivery_mode=2', "headers={'CC': [u'df2b7653-ef93-4bf8-801f-2b97b9bb7a01.d05a5933-880a-41ac-8bb4-949a9c8786c2.1090519054.7fc1ff7e-062d-408a-9350-6b4f3c0ea7f4']}", 'priority=0'])>
     [x] Received body:	'{"id":1503580638684881251,"timestamp":1503580638,"timestamp_nanoseconds":684881000,"date":"2017-08-24T13:17:18+00:00","event_type":"Threat Detected","event_type_id":1090519054,"detection":"Eicar-Test-Signature","detection_id":"12605922338023111","group_guids":["7fc1ff7e-062d-408a-9350-6b4f3c0ea7f4"],"computer":{"connector_guid":"d05a5933-880a-41ac-8bb4-949a9c8786c2","hostname":"WACLARK-M-M0EV","external_ip":"173.38.117.92","user":"u","active":true,"network_addresses":[{"ip":"10.150.54.101","mac":"24:a0:74:f0:3b:7a"},{"ip":"","mac":"72:00:08:c4:1d:20"},{"ip":"10.150.176.124","mac":"98:5a:eb:d7:f4:c1"}],"links":{"computer":"https://api.amp.cisco.com/v1/computers/d05a5933-880a-41ac-8bb4-949a9c8786c2","trajectory":"https://api.amp.cisco.com/v1/computers/d05a5933-880a-41ac-8bb4-949a9c8786c2/trajectory","group":"https://api.amp.cisco.com/v1/groups/7fc1ff7e-062d-408a-9350-6b4f3c0ea7f4"}},"file":{"disposition":"Unknown","file_name":"pbhistory.plist","file_path":"/Users/waclark/Library/Application Support/iTerm2/pbhistory.plist","identity":{"sha256":"E2B523A215898D8839D220F97A64774C84E517F5DE09A6992C847E03DF9A4A57"},"parent":{"process_id":35102,"disposition":"Unknown","file_name":"iTerm2","identity":{"sha256":"72ECBD137E3B3F876C72E81314E4CFD093DBDB08BB05D5BB09636799CA038957"}}}}'

'''
