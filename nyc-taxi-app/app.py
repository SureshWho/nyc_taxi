import os
import time
import redis
import logging

from   flask import Flask

print ("Starting ...")
calls = 0

app = Flask(__name__)


redis_host = os.environ['REDIS_HOST']
redis_port = int(os.environ['REDIS_PORT'])

print ('Connecting redis with {}:{}'.format(redis_host, redis_port))
cache = redis.Redis(host=redis_host, port=redis_port)



@app.route('/')
def hello():
	calls = cache.incr('visited')
	return 'Hello there {}\n'.format(calls)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

if __name__ == "__main__":
  app.run(host='0.0.0.0', port=80)

