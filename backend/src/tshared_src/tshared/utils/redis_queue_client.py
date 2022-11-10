import json
import logging
from typing import Callable, Optional
import inspect
import os
import redis


class RedisQueueClientException(Exception):
    pass


class RedisQueueClient:
    def __init__(self, redis_instance=None, name: str = 'default_redis_queue_client'):
        if redis_instance:
            self.redis = redis_instance
        else:
            self.redis = self._get_redis()
        self.queue = None
        self.handlers = []
        self.log = logging.getLogger('workers')
        self.name = name

    @staticmethod
    def _get_redis():
        server_env_state = os.getenv('SERVER_ENVIRONMENT', 'other')

        if server_env_state in (
            # 'local',
            'prod',
            'docker',
            'stage',
            'mirror',
            'dev',
            'dev2',
        ):
            return redis.Redis(host='redis')  # fixme read from config
        else:
            return redis.Redis()

    def subscribe(self, queue_name: str):
        self.queue = queue_name

    def add_handler(self, handler: Callable[[bytes], any]):
        self.handlers.append(handler)

    async def listen(self, timeout: Optional[int] = 1):
        if self.queue is None:
            raise RedisQueueClientException('Please subscribe to a queue.')
        if not self.handlers:
            raise RedisQueueClientException('Please add at least one handler.')

        while True:
            message = self.redis.brpop(self.queue, timeout=timeout)

            if not message:
                # print('notting')
                self.log.info(f'{self.name}: notting happened')
                continue

            for handler in self.handlers:
                if inspect.iscoroutinefunction(handler):
                    result = await handler(message[1])
                else:
                    result = handler(message[1])

                rv = f' RESULT: {str(result)}' if result else ''
                self.log.info(f'{self.name}: HANDLED: {message}.{rv}')

    def publish(self, message):
        if self.queue is None:
            raise RedisQueueClientException('Please subscribe to a queue.')

        # change redis wth async redis
        self.redis.rpush(self.queue, json.dumps(message))
        self.log.info(f'{self.name}: PUBLISHED: {message}.')
