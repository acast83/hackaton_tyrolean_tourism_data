import datetime
import tshared.utils.ipc as ipc


# lookups

async def lookup_wiki_statuses(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'wiki', '/lookups/statuses', last_updated)

# {{ ipc_function }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
