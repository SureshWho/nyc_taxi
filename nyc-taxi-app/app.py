import os
import time
import redis
import logging

from   flask import Flask
from   flask import request


app = Flask(__name__)

# get redis hostname and port number
redis_host = 'localhost'
if 'REDIS_HOST' in os.environ:
	redis_host = os.environ['REDIS_HOST']

redis_port = 6379
if 'REDIS_PORT' in os.environ:
	redis_port = int(os.environ['REDIS_PORT'])

# get debug setting
debug_enabled = False
if 'NYC_TAXI_APP_DEBUG' in os.environ:
	debug_enabled = bool(int(os.environ['NYC_TAXI_APP_DEBUG']))

print ("Starting ...Redis Host[{}] Redis Port[{}] Debug[{}] ".format(redis_host, redis_port, debug_enabled))

def is_debug_enabled ():
	return debug_enabled

print ('Connecting redis with {}:{}'.format(redis_host, redis_port))
cache = redis.Redis(host=redis_host, port=redis_port)



@app.route('/')
def hello():

	# get the completed rides from cache
	rides   = cache.zrange('snapshot', 0, -1)

	# return number of rides. If debug enabled return all data
	ret_str = '{}\n'.format(len(rides))

	return ret_str


@app.route('/debug')
def debug():

	# return number of rides. If debug enabled return all data
	ret_str = hello ()
	for rec in rides:
		ret_str = ret_str + str(rec) + '\n'

	return ret_str

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=80)

