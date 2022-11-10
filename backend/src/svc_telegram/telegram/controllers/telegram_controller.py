import os

from typing import Optional, Union
from collections import namedtuple
import asyncio
from tortoise import Tortoise
import logging

from svc_telegram.telegram.models import TelegramMessage
from svc_telegram.telegram.models import TelegramMessageRetry
from svc_telegram.telegram.models import LookupMessageSendingStatus

import tshared.utils.ipc as ipc
from base3.utils import load_config
from scripts.load_env_variables import load_env_variables
import json

if __name__ == "__main__":
    load_env_variables(from_config_file='environments/environment.yaml',
                       config_file_sections=['monolith'],
                       )

log2 = logging.getLogger('workers')


class TelegramController:
    def __init__(self):
        pass

    @staticmethod
    async def db_init(tortoise_config: dict):

        if 'aerich' in tortoise_config['apps']:
            del tortoise_config['apps']['aerich']

        await Tortoise.init(config=tortoise_config)

    @staticmethod
    async def create_message(receivers_telegram_id, message_body):
        return await TelegramMessage.create_message_and_retry(
            receivers_telegram_id=receivers_telegram_id,
            message_body=message_body,
        )

    @staticmethod
    async def get_retry(retry_id=None, message_id=None):
        return await TelegramMessageRetry.get_retry(
            retry_id=retry_id, message_id=message_id
        )

    @staticmethod
    async def get_retries():
        return await TelegramMessageRetry.all()

    @staticmethod
    async def get_message(message_id):
        return await TelegramMessage.get(id=message_id)

    @staticmethod
    async def get_default_message_status():
        return await LookupMessageSendingStatus.get(code='PENDING')

    @staticmethod
    async def get_success_message_status():
        return await LookupMessageSendingStatus.get(code='SENT')

    @staticmethod
    async def get_fail_message_status():
        return await LookupMessageSendingStatus.get(code='FAILED')

    @staticmethod
    async def update_successfully_sent_message(message: TelegramMessage):
        message = await TelegramMessage.get(id=message.id)
        await message.update_message_success()
        return message

    @staticmethod
    async def update_failed_message(
            message: TelegramMessage, note: str = None
    ):
        message = await TelegramMessage.get(id=message.id)
        await message.update_message_fail(note=note)
        return message

    @staticmethod
    async def update_retry_failed(retry: TelegramMessageRetry):
        await retry.decrement()
        return retry
