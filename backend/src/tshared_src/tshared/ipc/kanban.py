import uuid
import tshared.utils.ipc as ipc
import datetime


async def fetch_info_based_on_bucked_id(request, id_bucket: uuid.UUID):
    return await ipc.call(request, 'kanban', 'GET', f'/buckets/{id_bucket}/info')


async def board_structure(request, id_board: uuid.UUID):
    return await ipc.call(request, 'kanban', 'GET', f'/boards/{id_board}/structure_info')


async def update_item(request, id_kanban_item, data):
    try:
        return await ipc.call(request, 'kanban', 'PATCH', f'/item/{id_kanban_item}/update', body={'data': data})
    except Exception as e:
        raise


async def get_bucket_summary(request, id_bucket):
    try:
        return await ipc.call(request, 'kanban', 'GET', f'/buckets/{id_bucket}/summary')
    except Exception as e:
        raise


async def bucket_structure(request, id_bucket: uuid.UUID):
    return await ipc.call(request, 'kanban', 'GET', f'/buckets/{id_bucket}/info')


async def check_bucket_existance(request, id_bucket: uuid.UUID):
    return await ipc.call(request, 'kanban', 'GET', f'/buckets/{id_bucket}/exists')


async def lookup_kanban_kanban_application(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'kanban', '/lookups/kanban_application', last_updated)


async def create_kanban_item(request, id_bucket: uuid.UUID, instance: str, id_instance, return_kanban_data: bool):
    return await ipc.call(request, 'kanban', 'POST', f'/buckets/{id_bucket}/assign/{instance}',
                          body={"id_instance": id_instance, "return_kanban_data": return_kanban_data})


async def get_kanban_items_for_bucket(request, id_bucket: uuid.UUID):
    return await ipc.call(request, 'kanban', 'GET', f'/buckets/{id_bucket}/items')


async def get_kanban_item(request, id_item: uuid.UUID):
    return await ipc.call(request, 'kanban', 'GET', f'/items/{id_item}')

# {{ ipc_function }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
