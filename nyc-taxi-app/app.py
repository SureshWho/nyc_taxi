import os
import time
import redis
import logging

from   flask          import Flask
from   flask          import request
from   datetime       import datetime
from   redis.sentinel import Sentinel


app = Flask(__name__)

# get redis hostname and port number
redis_host = 'localhost'
if 'APP_REDIS_HOST' in os.environ:
    redis_host = os.environ['APP_REDIS_HOST']

redis_port = 6379
if 'APP_REDIS_PORT' in os.environ:
    redis_port = int(os.environ['APP_REDIS_PORT'])

# get redis hostname and port number
redis_sentinel = 'localhost'
if 'APP_REDIS_SENTINEL' in os.environ:
    redis_sentinel = os.environ['APP_REDIS_SENTINEL']

redis_sentinel_port = 26379
if 'APP_REDIS_SENTINEL_PORT' in os.environ:
    redis_sentinel_port = int(os.environ['APP_REDIS_SENTINEL_PORT'])

# get debug setting
debug_enabled = False
if 'NYC_TAXI_APP_DEBUG' in os.environ:
    debug_enabled = bool(int(os.environ['NYC_TAXI_APP_DEBUG']))

def is_debug_enabled ():
    return debug_enabled

def get_redis_slave():

    print ('Connecting redis sentinel with {}:{}'.format(redis_sentinel, redis_sentinel_port))
    sentinel = Sentinel([(redis_sentinel, redis_sentinel_port)], socket_timeout=0.1)
    slave   = sentinel.slave_for('mymaster', socket_timeout=0.1)

    #print ('Connecting redis with {}:{}'.format(redis_host, redis_port))
    #master = redis.Redis(host=redis_host, port=redis_port)

    return slave

print ("Starting ...Debug[{}] ".format(debug_enabled))
cache = get_redis_slave ()



def bytes_to_datetime(bytes):

    # convert into string
    str_t = bytes.decode("utf-8")

    # Convert string into datetime
    if '.' not in str_t:
        datetime_t = datetime.strptime(str_t, "%Y-%m-%dT%H:%M:%S%z")
    else:
        datetime_t = datetime.strptime(str_t, "%Y-%m-%dT%H:%M:%S.%f%z")

    return datetime_t


def get_rides():
    # get the completed rides from cache
    retry = 50

    # read with retry
    while retry != 0:
        try:
            rides   = cache.zrange('snapshot', 0, -1)
            retry   = 0
        except Exception as e:
            rides = []
            retry = retry - 1
    return rides

@app.route('/')
def hello():
    # return number of rides.
    rides = get_rides ()
    ret_str = '{}\n'.format(len(rides))

    return ret_str


@app.route('/debug')
def debug():

    # get the completed rides from cache
    rides   = get_rides ()

    # return number of rides. If debug enabled return all data
    ret_str = '{}\n'.format(len(rides))
    
    if (len(rides) != 0):
        fl = [rides[0], rides[len(rides)-1]]
        for rec in fl:
            datetime_t = bytes_to_datetime(rec).astimezone()
            ret_str = ret_str + str(rec) + '    Local:' + datetime_t.isoformat() + '\n'

    return ret_str

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=80)

