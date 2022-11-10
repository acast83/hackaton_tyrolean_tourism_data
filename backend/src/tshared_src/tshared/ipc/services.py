import datetime
import tshared.utils.ipc as ipc


async def lookup_services_service_groups(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'services', '/lookups/service_groups', last_updated)


async def get_all_service_lookups(request, ):
    return await ipc.call(request, 'services', 'GET', '/lookups?format_frontend_key=id&frontend_format=dict&format=frontend')


async def lookup_services_service_types(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'services', '/lookups/service_types', last_updated)


async def lookup_services_phone_number_origins(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'services', '/lookups/phone_number_origins', last_updated)


async def lookup_services_service_status(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'services', '/lookups/service_status', last_updated)


async def lookup_services_sim_status(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'services', '/lookups/sim_status', last_updated)


async def lookup_services_service_template_item_type(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'services', '/lookups/service_template_item_type', last_updated)


async def lookup_services_plintron_call_type(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'services', '/lookups/plintron_call_type', last_updated)

# {{ ipc_function }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}