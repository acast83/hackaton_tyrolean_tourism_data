import redis
from time import sleep


def get_redis_instance(*args, **kwargs):
    kwargs['decode_responses'] = True
    host = kwargs.get('host')
    hosts = ('localhost', 'redis') if host is None else (kwargs['host'],)

    while True:
        for host in hosts:
            try:
                kwargs['host'] = host
                r = redis.Redis(*args, **kwargs)

                if r.ping():
                    return r
            except redis.exceptions.RedisError:
                pass
        sleep(1)
