import uuid
import urllib.parse, json

import tshared.utils.ipc as ipc
from base3 import http
import base64


# lookups

async def get(request, document_id, fields=None):
    url = f'/-/{document_id}' + (f'?fields={fields}' if fields else '')

    return await ipc.call(request, 'documents', 'GET', url)


async def get_by_instance_and_id_instance_no_paginate(request, instance: str, id_instance: uuid.UUID,
                                                      filter: dict = None, order_by: str = 'created', limit: int = None,
                                                      fields: str = None):
    p = urllib.parse.urlencode({
        'filters': json.dumps(filter),
        'order_by': order_by,
        'no_paginate': True,
        'limit': limit,
        # 'fields': fields
    })

    url = f'/{instance}/{id_instance}?{p}'

    return await ipc.call(request, 'documents', 'GET', url)


async def get_all_documents4_id_instance(request, instance, id_instance):
    return await ipc.call(request, 'documents', 'GET', f'/{instance}/{id_instance}')


async def update_thumbnail(request, document_id, full_path):
    try:
        with open(full_path, 'rb') as f:
            source_binary = f.read()
            encoded = base64.b64encode(source_binary)

    except Exception as e:
        raise http.HttpInternalServerError(id_message='FILE_DOES_NOT_EXIST_OR_NO_READ_PERMISSION', message=full_path)

    res = (await ipc.call(request, 'documents', 'PATCH', f'/-/{document_id}',
                          body={
                              'thumbnail_data_b64': encoded.decode('utf-8')
                          }))

    return res


async def send_base64_content(request, instance, id_instance, fname, document_type_code, data):
    return (await ipc.call(request, 'documents', 'POST', f'/{instance}/{id_instance}',
                           body={
                               'filename': fname,
                               'bse64encoded': data,
                               'document_type_code': document_type_code
                           }))


async def upload_file(request, instance, id_instance, full_path, target_fname=None, document_type_code=None):
    try:
        with open(full_path, 'rb') as f:
            source_binary = f.read()
            encoded = base64.b64encode(source_binary)

    except Exception as e:
        raise http.HttpInternalServerError(id_message='FILE_DOES_NOT_EXIST_OR_NO_READ_PERMISSION', message=full_path)

    fname = full_path.split('/')[-1] if not target_fname else target_fname

    return (await ipc.call(request, 'documents', 'POST', f'/{instance}/{id_instance}',
                           body={
                               'filename': fname,
                               'bse64encoded': encoded.decode('utf-8'),
                               'document_type_code': document_type_code
                           }))


async def delete_all_documents_for_id_instance(request, instance, id_instance):
    return (await ipc.call(request, 'documents', 'DELETE', f'/{instance}/{id_instance}'))

# {{ ipc_function }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
