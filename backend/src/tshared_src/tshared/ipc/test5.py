import uuid
import datetime
import urllib.parse

import tshared.utils.ipc as ipc


async def lookup_test5_tlookup_testing(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'test5', '/lookups/tlookup_testing', last_updated)


async def lookup_test5_tlookup_222_testing(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'test5', '/lookups/tlookup_222_testing', last_updated)


# {{ ipc_function }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}