import os
import time
import copy
import json
import redis
import threading
import logging


from   flask          import Flask
from   datetime       import datetime
from   datetime       import timedelta
from   google.cloud   import pubsub_v1
from   redis.sentinel import Sentinel

### get environment variables ###

# get subsub batch size from environment variable
batch_sz = 1024
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
if 'SUBS_REDIS_HOST' in os.environ:
    redis_host = os.environ['SUBS_REDIS_HOST']

redis_port = 6379
if 'SUBS_REDIS_PORT' in os.environ:
    redis_port = int(os.environ['SUBS_REDIS_PORT'])

# get redis hostname and port number
redis_sentinel = 'localhost'
if 'SUBS_REDIS_SENTINEL' in os.environ:
    redis_sentinel = os.environ['SUBS_REDIS_SENTINEL']

redis_sentinel_port = 26379
if 'SUBS_REDIS_SENTINEL_PORT' in os.environ:
    redis_sentinel_port = int(os.environ['SUBS_REDIS_SENTINEL_PORT'])

# get cache time settings
cache_time_in_secs = 1 * 60
if 'SUBSCRIBER_CACHE_TIME_IN_SECS' in os.environ:
    cache_time_in_secs = int(os.environ['SUBSCRIBER_CACHE_TIME_IN_SECS'])

# get debug setting
debug_enabled = True
if 'SUBSCRIBER_DEBUG' in os.environ:
    debug_enabled = bool(int(os.environ['SUBSCRIBER_DEBUG']))

# App heal time after redis exception in secs
app_heal_time = 5
if 'SUBSCRIBER_HEAL_TIME' in os.environ:
    app_heal_time = int(os.environ['SUBSCRIBER_HEAL_TIME'])

def is_debug_enabled ():
    return debug_enabled

print ("Starting ...with\nTopic [{}]\nSubscription [{}]\nbatch size [{}] Debug[{}]"
    .format(topic_name, subscription_name, batch_sz, is_debug_enabled ()))

app = Flask(__name__)

# Profile time take to process the message
g_profile_max    = 0
g_profile_min    = 1000 * 1000
g_previous_time  = datetime.now()
g_total_msgs     = 0
g_total_rides    = 0
def profile(total_msgs, total_rides, tdiff, once_in=10000):
    '''
    Profile time take to process messages
    
    Description:
    Profile time take to process the message.

    Arguments:
    total_msgs         - Number of msgs received in last batch
    total_rides        - Total rides made in last batch
    tdiff              - Time took to process the entire batch
    once_in            - run profile once in N messages received

    Return:
    None
    
    Tips:
    - Place holder
    '''
    global g_profile_max, g_profile_min, g_previous_time, g_total_msgs, g_total_rides

    if is_debug_enabled() | True:

        # Keep a continous count
        g_total_msgs  = g_total_msgs  + total_msgs
        g_total_rides = g_total_rides + total_rides

        # print only if we receive N messages
        if (g_total_msgs > 10000):
            # convert into mirco seconds for printing
            g_profile_max = g_profile_max * 1000 * 1000
            g_profile_min = g_profile_min * 1000 * 1000

            # take time difference between now and last time called
            now             = datetime.now()
            delta           = now - g_previous_time
            g_previous_time = now

            # log necessary info
            print(" Msgs[{}] Max[{:09.2f}]us Min[{:9.2f}]us Rides[{:3d}] Delta[{}]".format(g_total_msgs, g_profile_max, g_profile_min, g_total_rides, delta))
            g_profile_min =  1000 * 1000; g_profile_max = 0; g_total_msgs = 0; g_total_rides = 0

        # Get the max and min time taken.
        g_profile_min = min(tdiff, g_profile_min)
        g_profile_max = max(tdiff, g_profile_max)

    return

# Converts the BYTE message to dictionary.
def convert_message(message):
    '''
    Converts the BYTE message to dictionary.
    
    Description:
    Converts the BYTE message to dictionary, and return only the fields of
    interest timestamp and ride_status. {timestamp_string:timestamp_float} will be stored in redis as a key, value pair.

    Arguments:
    pubsub message in BYTE format

    Return:
    Timestamp as string, Timestamp as float, and ride status
    
    Tips:
    - Place holder
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


# Delete last N trip to keep only last T seconds of trip information
g_old_timestamp      = 0.0
g_healling_time      = datetime.now()
def cache_delete_n_old_msgs(cache, recent_trip_timestamp, cache_time_in_secs):
    '''
    Delete last N trips.
    
    Description:
    Reads maximum of <batch_sz> messages from the PubSub topic, converts msgs into {Key:value} 
    pairs and writes into Redis as a sorted set. If for some reason Redis service is not available,
    function will return pending messages to be writen next time.

    Arguments:
    cache                  - Redis object for writing
    recent_trip_timestamp  - Timestamp for the last trip.
    cache_time_in_secs     - How many (how long) trips should be kept in the cache

    Return:
    0 - Something wrong
    
    Tips:
    - Place holder
    '''

    global g_old_timestamp, g_healling_time

    # wait for system to heal after connecton lost or any other cache write exception
    if (datetime.now() - g_healling_time) < timedelta (seconds=app_heal_time):
        return 0

    # just keep only last N secods trips. Do not delete the window if already deleted once [TODO Needed??]
    redis_ret = 1
    if (recent_trip_timestamp != g_old_timestamp):
        try:
            redis_ret = cache.zremrangebyscore('snapshot', -1, recent_trip_timestamp - cache_time_in_secs)
        except Exception as e:
            redis_ret            = 0;
            g_healling_time      = datetime.now()
            if is_debug_enabled (): print ("Exception: {}", e)
            get_redis_master()

    if redis_ret != 0:
        g_old_timestamp = recent_trip_timestamp

    return redis_ret



# Writes trip information into Redis cache.
def cache_write_and_ack_msgs(cache, subscriber, subscription_name, trip_mappings, ack_ids):
    '''
    Writes trip information into Redis cache.
    
    Description:
    Reads maximum of <batch_sz> messages from the PubSub topic, converts msgs into {Key:value} 
    pairs and writes into Redis as a sorted set. If for some reason Redis service is not available,
    function will return pending messages to be writen next time.

    Arguments:
    cache              - Redis object for writing
    subscriber         - Subscriber object for PubSub reading
    subscription_name  - Google Cloud Subcription name
    ack_ids            - Messages to be ACKed
    trip_mappings      - Trip info {key:score} mappings to write into Redis
    batch_sz           - Maximum how may messages should red from the PubSub

    Return:
    ack_ids       - Unacked IDs for the unwriten trips.
    trip_mappings - Unwriten trip info
    
    Tips:
    - Place holder
    '''

    # Write the MSG. Exceptions are errors
    global g_healling_time

    # wait for system to heal after connecton lost or any other cache write exception
    if (datetime.now() - g_healling_time) < timedelta(seconds=app_heal_time):
        return trip_mappings, ack_ids

    redis_ret = 0
    try:
        redis_ret = cache.zadd('snapshot', trip_mappings)
        if (redis_ret == 0): print ("Write failed")
    except Exception as e:
        redis_ret = 0
        g_healling_time      = datetime.now()
        if is_debug_enabled (): print ("Exception: {}", e)
        get_redis_master()

    # if write was success, ack all msgs, otherwise return then as pending messages
    if (redis_ret != 0):
        subscriber.acknowledge(subscription_name, ack_ids)
        ack_ids       = []
        trip_mappings = {}
    
    return trip_mappings, ack_ids 


# Collects ack ids and trip mapping infor
def exact_ack_ids_and_trip_info (received_messages):
    '''
    Returns ACK_IDs and Dropoff trip mapping information from received msgs
    
    Description:
    Return ACK_IDs for all the messages received, trip_mappings dropoff trips and timestamp of the
    recent trip.

    Arguments:
    received_messages - Redis object for writing

    Return:
    ack_ids_snapshots       - ACK IDs for tnormal messges
    ack_ids_trips           - ACK IDs for trip messages
    trip_mappings           - trip mapping information for drop off trips.
    recent_trip_timestamp   - Timestamp of the recent trip
    
    Tips:
    - Place holder
    '''
    recent_trip_timestamp  = 0
    ack_ids_snapshot       = []
    ack_ids_trips          = []
    trip_mappings          = {}

    # Collect ACK_IDs for all the messages and trip info for dropoff trips.
    for msg in received_messages:
        (time_str, time_score, ride_status) = convert_message(msg.message)

        # For dropoff message get the trip mappings {Timestamp_str:timestamp_as_score} 
        if (ride_status != 'dropoff'):
            ack_ids_snapshot.append(msg.ack_id)
        else:
            ack_ids_trips.append(msg.ack_id)
            trip_mappings[time_str] = time_score
            recent_trip_timestamp   = max(recent_trip_timestamp, time_score);
            
    return ack_ids_snapshot, ack_ids_trips, trip_mappings, recent_trip_timestamp


# Processes PubSub messages in synchronous mode.
def process_msgs_synchronously(cache, subscriber, subscription_name, pending_trip_mappings, pending_ack_ids, cache_time_in_secs, batch_sz):
    '''
    Processes PubSub messages in synchronous mode.
    
    Description:
    Reads maximum of <batch_sz> messages from the PubSub topic, converts msgs into {Key:value} 
    pairs and writes into Redis as a sorted set. If for some reason Redis service is not available,
    function will return pending messages to be writen next time.

    Arguments:
    cache              - Redis object for writing
    subscriber         - Subscriber object for PubSub reading
    subscription_name  - Google Cloud Subcription name
    cache_time_in_secs - How long want to keep the message in Redis cache
    batch_sz           - Maximum how may messages should red from the PubSub

    Return:
    NONE
    
    Tips:
    - Place holder
    '''

    # measure processing time for debugging
    start         = time.process_time()
    
    try:
        # Pull enough <batch_sz> message. If some error in pulling, just return
        # Since msgs are not ACKed, will be received again.
        response = subscriber.pull(subscription_name, max_messages = batch_sz)
    except Exception as e:
        if is_debug_enabled (): print ("Exception: Service not available {}", e)
        time.sleep (5)
        return ({}, [])

    # Collect ACK_IDs and trip mapping informtion
    ack_ids_snapshot, ack_ids_trips, trip_mappings, recent_trip_timestamp = exact_ack_ids_and_trip_info (response.received_messages)

    # add the previous trip pending msgs also
    #print (trip_mappings, pending_trip_mappings)
    ack_ids_trips = ack_ids_trips + pending_ack_ids
    trip_mappings = {**trip_mappings,**pending_trip_mappings}
    #print (trip_mappings)

    # ACK the snapshot (non trip) messages ASAP
    if (len(ack_ids_snapshot) != 0):
        subscriber.acknowledge(subscription_name, ack_ids_snapshot)

    # Write and ACK the trip messages
    if (len(ack_ids_trips) != 0):

        # Write to redis and ACK them if success
        pending_trip_mappings, pending_ack_ids = cache_write_and_ack_msgs(cache, subscriber, subscription_name, trip_mappings, ack_ids_trips)

        # Just keep only last N seconds trip infomation, delete others
        cache_delete_n_old_msgs(cache, recent_trip_timestamp, cache_time_in_secs)

    # measure processing time
    tdiff = time.process_time() - start

    # for debugging. will calculate how much time to process a single message
    profile (len(ack_ids_trips)+len(ack_ids_snapshot), len(trip_mappings), tdiff)

    # return any unacked and un write trips
    return pending_trip_mappings, pending_ack_ids


def get_redis_master():
    global cache

    retry = 50
    print ('Connecting redis sentinel with {}:{}'.format(redis_sentinel, redis_sentinel_port))

    while retry > 0:
        try:
            sentinel   = Sentinel([(redis_sentinel, redis_sentinel_port)], socket_timeout=0.5)
            master = sentinel.master_for('mymaster', socket_timeout=0.5)
            retry = 0
            cache = master
        except Exception as e:
            retry = retyr - 1

    return master

cache      = get_redis_master()
subscriber = pubsub_v1.SubscriberClient()

try:
    subscriber.get_subscription(subscription_name)
except Exception as e:
    if type(e).__name__ == 'NotFound':
        print ("Creating subscription...")
        duration = datetime.now() + timedelta(seconds=3600)
        subscription = subscriber.create_subscription(name=subscription_name, topic=topic_name, ack_deadline_seconds=30)

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
pending_trip_mappings = {}
pending_ack_ids       = []

while True: 
    pending_trip_mappings, pending_ack_ids = process_msgs_synchronously (cache, subscriber, subscription_name, 
                                                        pending_trip_mappings, pending_ack_ids, cache_time_in_secs, batch_sz)

    if (len(pending_ack_ids) != 0):
        if is_debug_enabled (): print ("Pending {}".format(len(pending_ack_ids)))







