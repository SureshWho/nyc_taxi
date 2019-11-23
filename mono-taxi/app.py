import os
import time
import copy
import json

from   datetime import datetime
from   datetime import timedelta
from   google.cloud import pubsub_v1
from   flask import Flask

import logging
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# holds last one hour trips in minutes Mins * 60
STORE_LAST_N_MINS = 1 * 60
tips_list = []
time_list = []
diff = 0.1
tdiff = 0.0
calls = 0;

def copy_one_hr_trips(message):
	global tips_list, time_list, tdiff, calls, diff

	# make a dictionary and add it to the  trips
	start = time.process_time()
	calls = calls + 1


	data = []
	data = message.data

    # copy time and data into a seperate list
	current_time = datetime.now()
	dic = json.loads(message.data.decode('utf-8'))
	tips_list.append(dic)
	#tips_list.append(data)
	time_list.append(current_time)

	# Pop all the old items
	diff = (current_time - time_list[0]).seconds
	while ((((current_time - time_list[0]).seconds) / STORE_LAST_N_MINS) >= 1):
		tips_list.pop(0)
		time_list.pop(0)

	#if (dic['ride_status'] == 'dropoff'):
	#	print (dic['ride_status'], current_time)

	tdiff = time.process_time() - start

	return

def get_trip_count():
	current_time = datetime.now()
	time_index = 0
	while (((current_time - time_list[time_index]).seconds / STORE_LAST_N_MINS) >= 1):
		time_index = time_index + 1;


	trips = [ trip for trip in tips_list[time_index:] if trip['ride_status'] == 'dropoff']

	return (len(trips), calls, len(time_list), diff, int(tdiff * 1000 * 1000))

def callback(message):
	#print(message.data)
	copy_one_hr_trips (message)
	message.ack()

subscriber = pubsub_v1.SubscriberClient()

topic_name = 'projects/pubsub-public-data/topics/taxirides-realtime'
subscription_name = 'projects/prj-nyc-taxis/subscriptions/test'

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

try:
    # When timeout is unspecified, the result method waits indefinitely.
    future.result(timeout=30)
except Exception as e:
    print(
        'Listening for messages on {} threw an Exception: {}.'.format(
            subscription_name, e))

app = Flask(__name__)

@app.route('/')
def hello():
    (trips, calls, cached_trips, cache_size, time_taken) = get_trip_count()
    return 'Trips:[{}] Calls Received:[{}] Items in Cache:[{}] Cache time:[{}]secs Serving time:[{}us] .\n'.format(trips, calls, cached_trips, cache_size, time_taken)

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=80)






