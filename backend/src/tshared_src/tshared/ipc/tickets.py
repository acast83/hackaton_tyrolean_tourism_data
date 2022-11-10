import json
import datetime
import tshared.utils.ipc as ipc


async def recache_all_kanban_info_for_ticket_in_bucket(request, id_bucket):
    return await ipc.call(request, 'tickets', 'PATCH', f'/kanban-mk-cache-for-tickets-in-bucket/{id_bucket}', body={'do-patch': True})


async def get_single_ticket(request, id_ticket):
    return await ipc.call(request, 'tickets', "GET", f'/{id_ticket}')


# lookups

async def lookup_ticket_types(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'tickets', '/lookups/types', last_updated)


async def lookup_ticket_priorities(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'tickets', '/lookups/priorities', last_updated)


async def lookup_ticket_statuses(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'tickets', '/lookups/statuses', last_updated)


# CACHE

async def service_cache(request, id_tenant, sender_service, model, id_item, updated_fields, serialized_object):
    return await ipc.call(request, 'tickets', 'PATCH', '/service-cache', {
        'id_tenant': str(id_tenant),
        'sender_service': sender_service,
        'model': model,
        'id_item': str(id_item),
        'updated_fields': updated_fields,
        'serialized_object': json.dumps(serialized_object, default=lambda x: str(x))
    })

# {{ ipc_function }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}