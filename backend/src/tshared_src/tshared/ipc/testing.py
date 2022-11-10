import uuid
import datetime
import urllib.parse

import tshared.utils.ipc as ipc


async def lookup_testing_flow_types(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'testing', '/lookups/flow_types', last_updated)


async def lookup_testing_tlookup_testing(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'testing', '/lookups/tlookup_testing', last_updated)


# {{ ipc_function }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}