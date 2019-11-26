import os
import time
import copy
import json
import redis
from   flask        import Flask
from   datetime     import datetime
from   datetime     import timedelta
from   google.cloud import pubsub_v1

# holds last one hour trips in minutes Mins * 60
STORE_LAST_N_MINS = 1 * 60
profile_min =  1000 * 1000
profile_max = 0
calls = 0

print ("Starting ...")

app = Flask(__name__)


def copy_one_hr_trips(message):
	global calls, profile_min, profile_max

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
		maxi = (score_dt - timedelta(seconds = STORE_LAST_N_MINS)).timestamp()
		cache.zremrangebyscore('snapshot', maxi - STORE_LAST_N_MINS, maxi)

	tdiff = time.process_time() - start
	profile_min = min(tdiff, profile_min)
	profile_max = max(tdiff, profile_max)

	return

def dummy (message):
	global calls, profile_min, profile_max

	# make a dictionary and add it to the  trips
	start = time.process_time()
	calls    = calls + 1

	tdiff = time.process_time() - start
	profile_min = min(tdiff, profile_min)
	profile_max = max(tdiff, profile_max)

	return

def get_trip_count():
	length = cache.zcard('snapshot');
	return (0, calls, length, STORE_LAST_N_MINS, int(tdiff * 1000 * 1000))

def callback(message):
	#print(message.data)
	#copy_one_hr_trips (message)
	dummy (message)
	message.ack()


redis_host = os.environ['REDIS_HOST']
redis_port = int(os.environ['REDIS_PORT'])

print ('Connecting redis with {}:{}'.format(redis_host, redis_port))
cache = redis.Redis(host=redis_host, port=redis_port)

subscriber = pubsub_v1.SubscriberClient()

topic_name = 'projects/pubsub-public-data/topics/taxirides-realtime'
subscription_name = 'projects/prj-nyc-taxis/subscriptions/nyc-taxi-5'


try:
    subscriber.get_subscription(subscription_name)
except IOError as e:
    print (e)

    subscription = subscriber.create_subscription(
    name=subscription_name, topic=topic_name)

future = subscriber.subscribe(subscription_name, callback)

'''
while True:
	try:
    	# When timeout is unspecified, the result method waits indefinitely.
		future.result(30)
	except Exception as e:
		print(
			'Listening for messages on {} threw an Exception: {}.'.format(
			subscription_name, e))
	print (" Calls [{}] Max [{:5.2f}]us Min [{:5.2f}]us".format(calls, profile_max * 1000 * 1000, profile_min * 1000 * 1000))
	profile_min =  1000 * 1000; profile_max = 0; calls = 0
'''

print ("!!! Should not come here !!!")


@app.route('/')
def hello():
	global calls, profile_min, profile_max
	ret_str = " Calls [{}] Max [{:5.2f}]us Min [{:5.2f}]us \n".format(calls, profile_max * 1000 * 1000, profile_min * 1000 * 1000)
	profile_min =  1000 * 1000; profile_max = 0; calls = 0
	return ret_str

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=90)

