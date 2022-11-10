import json
import os
import aiohttp
import asyncio
from pydantic import BaseModel
from typing import Union, Literal

from base3.utils import load_config

from scripts.load_env_variables import load_env_variables
from tshared.utils.redis_queue_client import RedisQueueClient


__all__ = [
    "send_message",
    "send_logs_to_telegram",
    "publish_message",
    "SendMessageSimplified",
]


if __name__ == "__main__":
    load_env_variables(from_config_file='environments/environment.yaml',
                       config_file_sections=['monolith'],
                       )

#TELEGRAM_BOT_NAME = os.getenv('TELEGRAM_BOT_NAME')
#TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
#
#if TELEGRAM_BOT_NAME is None or TELEGRAM_TOKEN is None:
#    raise ValueError(f'TELEGRAM_BOT_NAME({TELEGRAM_BOT_NAME}) '
#                     f'or TELEGRAM_TOKEN({TELEGRAM_TOKEN}) '
#                     f'were not supplied.')

# ^ moved to function, because this is not exists on startup (sometimes) depends on services.yaml (local for example)

current_file_folder = os.path.dirname(os.path.realpath(__file__))
cfg = load_config('/', [current_file_folder + '/../../../config/services.yaml'])

# ^ should depends on which services.yaml - in docker it is not problem it is alwys this one because of overwritting
# but locally can be


class SendMessageSimplified(BaseModel):
    chat_id: Union[int, str]
    text: str
    parse_mode: str = None
    disable_web_page_preview: bool = None
    disable_notification: bool = None
    allow_sending_without_reply: bool = None


async def make_post_request(url: str, json_body: dict):
    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, json=json_body) as response:
            body = await response.json()
            status = response.status
        return body, status


def decode_message(message: str) -> str:
    try:
        message: dict = json.loads(message)
        return "\n".join([f"{k}: {v}" for k, v in message.items()])
    except json.JSONDecodeError as e:
        return message


def publish_message(message_text: Union[str, dict]):
    """
    Sends to queue:
        {
            'header': {'key': 'value'},
            'body': {
                'text': <text>
            }
        }
    """

    if not hasattr(publish_message, 'client'):
        wconfig = cfg["workers"]
        queue_name = wconfig["telegram-message-sender"]["queue"]

        client = RedisQueueClient()
        client.subscribe(queue_name=queue_name)

        publish_message.client = client

    if not isinstance(message_text, (str, dict)):
        raise TypeError(f'Wrong request type: {type(message_text)}')

    publish_message.client.publish(message_text)


async def send_message(request: Union[SendMessageSimplified, dict]):
    """
    request:
        {
            "chat_id": 123456798,
            "text": "Hi!"
        }
    """

    if isinstance(request, SendMessageSimplified):
        pass
    elif isinstance(request, dict):
        request = SendMessageSimplified(**request)
    else:
        raise TypeError(f'Wrong request type: {type(request)}')


    TELEGRAM_BOT_NAME = os.getenv('TELEGRAM_BOT_NAME')
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

    if TELEGRAM_BOT_NAME is None or TELEGRAM_TOKEN is None:
        raise ValueError(f'TELEGRAM_BOT_NAME({TELEGRAM_BOT_NAME}) '
                         f'or TELEGRAM_TOKEN({TELEGRAM_TOKEN}) '
                         f'were not supplied.')



    telegram_url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'

    response, status_code = await make_post_request(
        url=telegram_url,
        json_body=request.dict(exclude_none=True)
    )
    return response, status_code


def send_logs_to_telegram(message: Union[str, dict],
                          parse_mode: Literal[None, 'HTML', 'MarkdownV2'] = 'MarkdownV2'):
    def prepare_for_md(_text: str) -> str:
        _text = str(_text)
        for c in "_*[]()~`>#+-=|{}.!":
            _text = _text.replace(c, '\\' + c)
        return _text

    chat_ids = os.getenv('TELEGRAM_CHAT_IDS', '')
    if not chat_ids:
        print('No telegram ids supplied.')
        return
    else:
        chat_ids = [x.strip() for x in chat_ids.split(',') if x.strip()]

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()

    if isinstance(message, dict):
        message = "\n".join([f"*{prepare_for_md(k)}*: {prepare_for_md(v)}"
                             for k, v in message.items()])
    elif isinstance(message, str) and parse_mode == 'MarkdownV2':
        message = prepare_for_md(message)

    for chat_id in chat_ids:
        request = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': parse_mode,
        }
        result = loop.run_until_complete(send_message(request=request))
        print(result)


async def main():
    request = {
        'chat_id': '464332561',
        'text': 'Hi!'
    }
    await send_message(request=request)


def main_sync():
    request = {
        'chat_id': '464332561',
        'text': 'Hi!'
    }
    send_logs_to_telegram(message=request)


if __name__ == "__main__":
    # asyncio.run(main())
    main_sync()
