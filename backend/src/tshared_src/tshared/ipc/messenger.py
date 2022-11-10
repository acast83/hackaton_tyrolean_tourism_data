import uuid
import datetime
import urllib.parse

import tshared.utils.ipc as ipc


async def lookup_messenger_chat_notification_channel(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'messenger', '/lookups/chat_notification_channel', last_updated)


async def set_seen(request, id_message):
    return await ipc.call(request, 'messenger', 'PATCH', f'/messages/{id_message}/seen', body={'__void': None})


async def messages(request, instance, id_instance, format='short', timestamp=None):
    attrs = {'format': format}
    if timestamp:
        attrs['timestamp'] = str(timestamp)
    p = urllib.parse.urlencode(attrs)
    return await ipc.call(request, 'messenger', 'GET', f'/{instance}/{id_instance}/messages?{p}')


async def count_messages(request, instance, id_instance, timestamp):
    attrs = {}
    if timestamp:
        attrs['timestamp'] = str(timestamp)

    p = urllib.parse.urlencode(attrs)
    url = f'/{instance}/{id_instance}/messages/count?{p}'
    return await ipc.call(request, 'messenger', 'GET', url)


async def get_message(request, id_message, format='short'):
    attrs = {'format': format}
    p = urllib.parse.urlencode(attrs)
    return await ipc.call(request, 'messenger', 'GET', f'/messages/{id_message}?{p}')


async def delete_message(request, id_message, force=False):
    force = 'true' if force else 'false'
    return await ipc.call(request, 'messenger', 'DELETE', f'/messages/{id_message}?force={force}')


async def send_message(request, instance, id_instance, message, parents=None, mentions=None):
    body = {'message': message}
    if parents:
        body['parents'] = parents
    if mentions:
        body['mentions'] = mentions

    return await ipc.call(request, 'messenger', 'POST', f'/{instance}/{id_instance}/messages',
                          body=body)

# {{ ipc_function }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
