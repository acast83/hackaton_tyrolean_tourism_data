import uuid
import datetime
import urllib.parse

import tshared.utils.ipc as ipc


async def lookup_olo_olo_process(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'olo', '/lookups/olo_process', last_updated)


async def lookup_olo_olo_operator(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'olo', '/lookups/olo_operator', last_updated)


async def lookup_olo_olo_operation_group(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'olo', '/lookups/olo_operation_group', last_updated)


async def lookup_olo_olo_operation_type(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'olo', '/lookups/olo_operation_type', last_updated)


async def lookup_olo_olo_operation_status(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'olo', '/lookups/olo_operation_status', last_updated)


async def lookup_olo_olo_operation_steps(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'olo', '/lookups/olo_operation_steps', last_updated)


async def lookup_olo_olo_direction(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'olo', '/lookups/olo_direction', last_updated)


async def lookup_olo_olo_interface(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'olo', '/lookups/olo_interface', last_updated)


# {{ ipc_function }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}