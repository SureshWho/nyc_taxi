import os
import time
import copy
import json

from   datetime import datetime
from   datetime import timedelta
from   google.cloud import pubsub_v1
from   flask import Flask
import redis

import logging

# holds last one hour trips in minutes Mins * 60
STORE_LAST_N_MINS = 1 * 60
tdiff = 0.0
calls = 0;

def copy_one_hr_trips(message):
	global tdiff, calls

	# make a dictionary and add it to the  trips
	start = time.process_time()

	# convert the trip snapshot into dictionary
	dic      = json.loads(message.data.decode('utf-8'))
	calls    = calls + 1
	time_str = dic["timestamp"]
	
	if '.' not in time_str:
		score_dt = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S%z")
	else:
		score_dt = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%f%z")

	# print (member, score)
	redis_ret = cache.zadd('snapshot', {time_str: score_dt.timestamp()})

	if (redis_ret != 0):
		max = (score_dt - timedelta(seconds = STORE_LAST_N_MINS)).timestamp()
		cache.zremrangebyscore('snapshot', max - STORE_LAST_N_MINS, max)

	tdiff = time.process_time() - start

	return

def get_trip_count():
	length = cache.zcard('snapshot');
	return (0, calls, length, STORE_LAST_N_MINS, int(tdiff * 1000 * 1000))

def callback(message):
	#print(message.data)
	copy_one_hr_trips (message)
	message.ack()

subscriber = pubsub_v1.SubscriberClient()

topic_name = 'projects/pubsub-public-data/topics/taxirides-realtime'
subscription_name = 'projects/prj-nyc-taxis/subscriptions/nyc-taxi'

#topic_name = 'projects/{project_id}/topics/{topic}'.format(
#    project_id=os.getenv('GOOGLE_CLOUD_PROJECT'),
#    topic='MY_TOPIC_NAME',  # Set this to something appropriate.
#)
#subscription_name = 'projects/{project_id}/subscriptions/{sub}'.format(
#    project_id=os.getenv('GOOGLE_CLOUD_PROJECT'),
#    sub='MY_SUBSCRIPTION_NAME',  # Set this to something appropriate.
#)
try:
    subscriber.get_subscription(subscription_name)
except IOError as e:
    print (e)

    subscription = subscriber.create_subscription(
    name=subscription_name, topic=topic_name)

future = subscriber.subscribe(subscription_name, callback)

'''
try:
	subscriber.get_subscription(subscription_name)
except IOError as e:
	print (e)

	subscription = subscriber.create_subscription(
    name=subscription_name, topic=topic_name)

future = subscriber.subscribe(subscription_name, callback)

try:
    # When timeout is unspecified, the result method waits indefinitely.
    future.result(timeout=30)
except Exception as e:
    print(
        'Listening for messages on {} threw an Exception: {}.'.format(
            subscription_name, e))
'''

app   = Flask(__name__)

redis_host = 'localhost'
redis_port = '6379'

if __name__ != "__main__":
	redis_host = os.environ['REDIS_HOST']
	redis_port = os.environ['REDIS_PORT']	

print ('Connecting redis with {}:{}'.format(redis_host, redis_port))
cache = redis.Redis(host=redis_host, port=int(redis_port))


@app.route('/')
def hello():
    (trips, calls, cached_trips, cache_size, time_taken) = get_trip_count()
    return 'Trips:[{}] Calls Received:[{}] Items in Cache:[{}] Cache time:[{}]secs Serving time:[{}us] .\n'.format(trips, calls, cached_trips, cache_size, time_taken)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=80)

