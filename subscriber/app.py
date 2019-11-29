import os
import time
import copy
import json
import redis
import threading
import logging


from   flask        import Flask
from   datetime     import datetime
from   datetime     import timedelta
from   google.cloud import pubsub_v1

# holds last one hour trips in minutes Mins * 60

profile_min       =  1000 * 1000
profile_max       = 0
total_msgs        = 0
total_rides       = 0
batch_sz          = 1024
max_timestamp     = 0.0
previous_time     = datetime.now()

### get environment variables ###

# get subsub batch size from environment variable 
if 'SUBSCRIBER_BATCH_SZ' in os.environ:
	batch_sz = int(os.environ['SUBSCRIBER_BATCH_SZ'])

# get subsub batch size from environment variable 
subscription_name = 'projects/prj-nyc-taxis/subscriptions/NYC-TAXI_SERVICE'
if 'SUBSCRIBER_SUBCRIPTION_NAME' in os.environ:
	subscription_name = os.environ['SUBSCRIBER_SUBCRIPTION_NAME']

# get subsub batch size from environment variable
topic_name = 'projects/pubsub-public-data/topics/taxirides-realtime'
if 'SUBSCRIBER_TOPIC_NAME' in os.environ:
	topic_name = os.environ['SUBSCRIBER_TOPIC_NAME']

# get redis hostname and port number
redis_host = 'localhost'
if 'REDIS_HOST' in os.environ:
	redis_host = os.environ['REDIS_HOST']

redis_port = 6379
if 'REDIS_PORT' in os.environ:
	redis_port = int(os.environ['REDIS_PORT'])

# get cache time settings
cache_time_in_secs = 1 * 60
if 'SUBSCRIBER_CACHE_TIME_IN_SECS' in os.environ:
	cache_time_in_secs = int(os.environ['SUBSCRIBER_CACHE_TIME_IN_SECS'])

# get debug setting
debug_enabled = False
if 'SUBSCRIBER_DEBUG' in os.environ:
	debug_enabled = bool(int(os.environ['SUBSCRIBER_DEBUG']))

def is_debug_enabled ():
	return debug_enabled

print ("Starting ...with\nTopic [{}]\nSubscription [{}]\nbatch size [{}] Debug[{}]"
	.format(topic_name, subscription_name, batch_sz, is_debug_enabled ()))

app = Flask(__name__)

def convert_message(message):
	'''
	converts the given message into member and score values to store into redis ZSET
	'''

	#convert msg into dictionary
	dic      = json.loads(message.data.decode('utf-8'))
	time_str = dic["timestamp"]
	
	# some data does not have the microseconds
	if '.' not in time_str:
		score_dt = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S%z")
	else:
		score_dt = datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%f%z")

    # convert timedate structure into timestamp
	return (time_str, score_dt.timestamp(), dic['ride_status'])


def process_msg_synchronously(subscriber):

	global total_msgs, profile_min, profile_max, max_timestamp, previous_time, total_rides

    # measure processing time
	start = time.process_time()

	try:
		response = subscriber.pull(subscription_name, max_messages = batch_sz)
	except Exception as e:
		print ('Service is not ready will try again')
		time.sleep (5)
		return 

	# process the messages
	ack_ids = []
	mappings = {}
	old_max_timestamp = max_timestamp
	for msg in response.received_messages:
		ack_ids.append(msg.ack_id)
		(time_str, time_score, ride_status) = convert_message(msg.message)
		if (ride_status == 'dropoff'):
			mappings[time_str] = time_score
			max_timestamp = max(max_timestamp, time_score);

	# if no rides completed ACK all MSG, if some rides completed ACK only in redis write is successful
	if (len(mappings) == 0):
		subscriber.acknowledge(subscription_name, ack_ids)
	else:
		redis_ret = cache.zadd('snapshot', mappings)
		if (redis_ret != 0):
			subscriber.acknowledge(subscription_name, ack_ids)

	# just keep only last N secods data
	if (old_max_timestamp != max_timestamp):
		cache.zremrangebyscore('snapshot', -1, max_timestamp - cache_time_in_secs)

    # measure processing time
	if is_debug_enabled():
		total_rides  += len(mappings)
		total_msgs   += len(ack_ids)
		if (total_msgs > 10000):
			profile_max = profile_max * 1000 * 1000
			profile_min = profile_min * 1000 * 1000
			now = datetime.now()
			delta = now - previous_time
			previous_time = now
			print(" Msgs[{}] Max[{:5.2f}]us Min[{:5.2f}]us Rides[{}] Delta[{}]".format(total_msgs, profile_max, profile_min, total_rides, delta))
			profile_min =  1000 * 1000; profile_max = 0; total_msgs = 0; total_rides = 0
		tdiff       = time.process_time() - start
		profile_min = min(tdiff, profile_min)
		profile_max = max(tdiff, profile_max)

	return


print ('Connecting redis with {}:{}'.format(redis_host, redis_port))
cache = redis.Redis(host=redis_host, port=redis_port)


subscriber = pubsub_v1.SubscriberClient()

try:
    subscriber.get_subscription(subscription_name)
except Exception as e:
	if type(e).__name__ == 'NotFound':
		print ("Creating subscription...")
		subscription = subscriber.create_subscription(name=subscription_name, topic=topic_name)

@app.route('/')
def hello():
	global total_msgs, profile_min, profile_max
	ret_str = " Msgs [{}] Max [{:5.2f}]us Min [{:5.2f}]us \n".format(total_msgs, profile_max * 1000 * 1000, profile_min * 1000 * 1000)
	profile_min =  1000 * 1000; profile_max = 0; total_msgs = 0
	return ret_str

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

'''
if __name__ == "__main__":
	app.run(host='0.0.0.0', port=90)

threads = []
t = threading.Thread(target=apprun)
threads.append(t)
t.start()
'''

# process the MSGs
print ("Receiving PubSub...")
while True: process_msg_synchronously (subscriber)




