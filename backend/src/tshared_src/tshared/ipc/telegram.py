import tshared.utils.ipc as ipc
import datetime


async def send_message(request, msg: str):
    return await ipc.call(request, 'telegram', 'POST', '/send_message')


async def lookup_telegram_message_sending_status(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'telegram', '/lookups/message_sending_status', last_updated)


# {{ ipc_function }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
