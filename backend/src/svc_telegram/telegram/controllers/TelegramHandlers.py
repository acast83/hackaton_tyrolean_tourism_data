import uuid
import json

import asyncio

import tshared.ipc.tenants as ipc_tenants

from ..models.TelegramModelsTypes import *
from ..models.TelegramModelsMethods import *
from .TelegramDispatcher import dp
from .RedisDispatcher import send_message, encode_message, answer_to, send_to
from .. import models


__all__ = ["handler_help", "handler_start"]


def _has_payload(message_text: str):
    return message_text.startswith(("/start ", "/startgroup "))


async def _save_link_user_to_telegram_id(telegram_id: int, user_id: str, id_tenant: str):
    account = await models.LinkedAccounts.filter(created_by=user_id).get_or_none()
    if not account:
        user_id = uuid.UUID(user_id, version=4)
        id_tenant = uuid.UUID(id_tenant, version=4)
        new_user = await models.LinkedAccounts.safe_create({'telegram_id': telegram_id,
                                                            'id_tenant': id_tenant,
                                                            'created_by': user_id,
                                                            'last_updated_by': user_id,
                                                            'user_id': user_id})
        await new_user.save()
    send_to(telegram_id).message("You successfully registered.")


@dp.message_handler(commands=['help'])
async def handler_help(message: Message):
    answer_to(message).message("There is no help!")


@dp.message_handler(lambda message: 'foobar' in message.text.lower())
async def handler_foobar(message: Message):
    answer_to(message).message("You have foobar in your message!")


@dp.message_handler(commands=['start'])
async def handler_start(message: Message):
    if _has_payload(message.text):
        telegram_id = message.from_user.id
        _, uid_and_tenant_code = message.text.strip().split()

        response, _ = await ipc_tenants.find_user_by_uuid_and_tenant_code(dp.route.request,
                                                                          uid_and_tenant_code=uid_and_tenant_code)
        await _save_link_user_to_telegram_id(telegram_id=telegram_id,
                                             user_id=response['id'],
                                             id_tenant=response['id_tenant'])
