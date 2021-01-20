import redis
from flask import Flask

hello = Flask(__name__)
cache = redis.Redis(host='redis')

def refresh_count():
    while True:
        return cache.incr('refresh_count')

@hello.route('/')
def hi():
    return 'Hello Flask! Refresh count: {}.\n'.format(refresh_count())
