import datetime
import tshared.utils.ipc as ipc


# lookups

async def lookup_sla_group(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'sla', '/lookups/groups', last_updated)


async def lookup_sla_additional(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'sla', '/lookups/additional', last_updated)


async def lookup_sla_main(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'sla', '/lookups/main', last_updated)


async def lookup_sla_business_components(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'sla', '/lookups/business_components', last_updated)


async def lookup_sla_business_component_groups(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'sla', '/lookups/business_component_groups', last_updated)


async def lookup_status(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'sla', '/lookups/status', last_updated)


async def lookup_billing_period(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'sla', '/lookups/billing_period', last_updated)


async def get_user_settings(request, table):
    return await ipc.call(request, 'tenants', 'GET', f'/my-settings/{table}')

# {{ ipc_function }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
