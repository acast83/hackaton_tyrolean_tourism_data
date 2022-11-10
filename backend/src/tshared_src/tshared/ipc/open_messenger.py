import datetime
import tshared.utils.ipc as ipc


async def lookup_open_messenger_type(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'open_messenger', '/lookups/type', last_updated)


async def lookup_open_messenger_statuses(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'open_messenger', '/lookups/statuses', last_updated)

# {{ ipc_function }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
