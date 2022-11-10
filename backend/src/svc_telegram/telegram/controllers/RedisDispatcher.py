import redis
import json
import os

from ..models.TelegramModelsMethods import *
from ..models.TelegramModelsTypes import *


REDIS_MESSAGES_QUEUE = os.environ.get('REDIS_MESSAGES_QUEUE')
REDIS = redis.Redis(host=os.environ.get('REDIS_HOST'), port=os.environ.get('REDIS_PORT'), db=0)


class TestTest:
    def __init__(self, telegram_id: int = None,
                 message: Message = None):
        if ((telegram_id is None and message is None)
                or (telegram_id is not None and message is not None)):
            raise Exception("Extra argument is supplied.")
        self._message = message

        if telegram_id:
            self.telegram_id = telegram_id
        else:
            self.telegram_id = message.from_user.id

    @staticmethod
    def _prepare_message(**kwargs):
        return {
            "content_type": kwargs.pop('content_type', MessageEncodeTypes.textMessage),
            "content": {**kwargs}
        }

    @staticmethod
    def _send(obj: dict):
        send_message(encode_message(**obj))

    def message(self, text: str, **kwargs):
        o = self._prepare_message(chat_id=self.telegram_id,
                                  text=text,
                                  content_type=MessageEncodeTypes.textMessage,
                                  **kwargs)
        self._send(o)


def answer_to(message: Message):
    return TestTest(message=message)


def send_to(telegram_id: int):
    return TestTest(telegram_id=telegram_id)


def send_message(*messages: str):
    print(f'\t>>> to-telegram: {messages}')
    REDIS.rpush(REDIS_MESSAGES_QUEUE, *messages)


def encode_message(**kwargs) -> str:
    """
    Expected:
    {
        "content": {"chat_id": 56564654, "text": "Hello!"},
        "content_type": "sendMessage"
    }

    content_type: one of the methods from __link__*
    content: dict object that follows one of the method models from __link__*

    *__link__: https://core.telegram.org/bots/api#available-methods
    """

    content_type = kwargs.pop('content_type', MessageEncodeTypes.textMessage)
    if kwargs.get('content'):
        content = kwargs['content']
    else:
        content = kwargs

    if content_type == MessageEncodeTypes.textMessage:
        t = {'content_type': content_type,
             'content': content
             }
        return ObjectForTelegramWorker(**t).json(exclude_unset=True)
    else:
        raise NotImplemented(f'content type {content_type} is not implemented yet.')
