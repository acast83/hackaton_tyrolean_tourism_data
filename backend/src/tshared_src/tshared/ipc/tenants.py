import uuid
import json
import datetime
import urllib.parse
import tshared.utils.ipc as ipc
from base3 import http


# Lookups


async def check_user_by_x_api_key(handler, x_api_key, config):
    import tshared.lookups.cache as lookups

    x_api_key = str(x_api_key)
    # from . import config
    if x_api_key not in config['api-keys']:
        raise http.HttpErrorUnauthorized(id_message='INVALID_API_KEY')
    a = config['api-keys'][x_api_key]

    username = a['tenant_username']
    tenant_code = a['tenant_code']

    res = await get_user_id_by_tenant_code_and_username(handler.request, tenant_code, username)

    handler.id_user = res['id_user']
    handler.id_tenant = res['id_tenant']
    handler.request.headers['Authorization'] = f'Bearer {res["token"]}'

    lookup_users = await lookups.LookupUsers.create(handler, force_key_value=['id', 'username'])

    return {'tenant': handler.id_tenant, 'user': {'id': handler.id_user, 'username': lookup_users[handler.id_user]}}


async def get_user_and_tenant_for_x_api_key(handler, x_api_key, config):
    if str(handler.id_user) == "00000000-0000-0000-0000-000000000000":
        return await check_user_by_x_api_key(handler, x_api_key, config)


async def get_user_and_tenant_using_http_headers(handler, config):
    if str(handler.id_user) == "00000000-0000-0000-0000-000000000000":
        if 'X-API-KEY' not in handler.request.headers:
            raise http.HttpForbiden(id_message='MISSING_API_KEY')

        return await check_user_by_x_api_key(handler, handler.request.headers['X-API-KEY'], config)


async def register_user(request, username, password, first_name, last_name, organization, id_role):
    return await ipc.call(request, 'tenants', 'POST', f'/users', body={
        'username': username,
        'password': password,
        'data': {'organization': organization},
        'first_name': first_name,
        'last_name': last_name,
        'role_id': str(id_role)
    })


async def lookup_tenants(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'tenants', '/lookups/tenants', last_updated)


async def lookup_users(request, last_updated: datetime.datetime = None):
    r = await ipc.lookup_base(request, 'tenants', '/lookups/users', last_updated)
    return r


async def lookup_user_groups(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'tenants', '/lookups/user_groups', last_updated)


async def lookup_user_permissions(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'tenants', '/lookups/permissions', last_updated)


async def lookup_user_roles(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'tenants', '/lookups/roles', last_updated)


# ...

async def get_property(request, key):
    return (await ipc.call(request, 'tenants', 'GET', f'/my-settings/{key}'))[0]


async def get_user_id_by_tenant_code_and_username(request, tenant_code, username):
    return (await ipc.call(request, 'tenants', 'GET', f'/user_id_by_tenant_code_and_username?code={tenant_code}&username={username}'))[0]


async def get_user_info(request, id_user, fields=None):
    fields = f'?fields={fields}' if fields else ''
    return (await ipc.call(request, 'tenants', 'GET', f'/users/{id_user}{fields}'))[0]


async def me(request, fields=None):
    fields = f'?fields={fields}' if fields else ''
    return (await ipc.call(request, 'tenants', 'GET', f'/me{fields}'))[0]


async def set_property(request, key, value):
    return await ipc.call(request, 'tenants', 'POST', f'/my-settings/{key}', body=value)


async def get_users(request, departments: str = None, search: str = None, distinct_user_grouping=None,
                    fields=None, order_by=None, group_by_user_group_code=None, no_paginate: bool = False, filters: dict = None):
    params = {}

    if not filters:
        filters = {}

    for p in (
            'departments', 'search', 'fields', 'order_by', 'group_by_user_group_code', 'distinct_user_grouping',
            'filters', 'no_paginate'):
        if eval(p) is not None:
            params[p] = eval(p) if p != 'filters' else json.dumps(eval(p))

    return await ipc.call(request, 'tenants', 'GET', f'/users?{urllib.parse.urlencode(params)}')


async def forgot_password(request, id_tenant: uuid.UUID, reset_password_uuid: uuid.UUID):
    return await ipc.call(request, 'tenants', 'POST', f'/{id_tenant}/users/forgot-password/{reset_password_uuid}')


async def activate_account(request, id_tenant: uuid.UUID, id_registrant: uuid.UUID):
    return await ipc.call(request, 'tenants', 'POST', f'/{id_tenant}/users/register/{id_registrant}')


async def find_user_by_uuid_and_tenant_code(request, uid_and_tenant_code: str):
    return await ipc.call(request, 'tenants', 'GET', f'/find_user_by_uuid_and_tenant_code/{uid_and_tenant_code}')


async def tenant_by_code(request, code):
    return await ipc.call(request, 'tenants', 'GET', f'/code/{code.upper()}')


async def lookup_tenants_prefered_language(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'tenants', '/lookups/prefered_language', last_updated)

# {{ ipc_function }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
