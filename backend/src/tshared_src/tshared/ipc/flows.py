import datetime
import urllib.parse
import tshared.utils.ipc as ipc
import uuid
import tshared.lookups
from tshared.utils.ipc import get_system_user_mocked_handler_for_tenant


async def lookup_base(request, svc, url, last_updated: datetime.datetime = None):
    params = ''
    if last_updated:
        params = '?' + urllib.parse.urlencode({'last_updated': str(last_updated)})

    url += params

    return await ipc.call(request, svc, 'GET', url)


async def lookup_flow_types(request, last_updated: datetime.datetime = None):
    res = await lookup_base(request, 'flows', '/lookups/flow_types', last_updated)
    return res


async def count(handler, instance: str, id_instance: uuid.UUID, type_code: str = None, command: str = None):
    if not hasattr(count, 'lookup_flows'):
        count.lookup_flows = await tshared.lookups.LookupFlowTypes.create(handler)

    params = urllib.parse.urlencode({
        'type_id': count.lookup_flows.get(key=type_code, index='code')['id'] if type_code else None,
        'command': command
    })

    return await ipc.call(handler.request, 'flows', 'GET', f'/{instance}/{id_instance}/count?{params}')


async def multiply_flows(handler, list_of_new_flow_messages: list, expected_count_in_result: bool = False):
    params = ''
    if expected_count_in_result:
        params = '?expected_count_in_result=true'

    return await ipc.call(handler.request, 'flows', 'POST', f'/multiply?{params}', body={
        'list_of_new_flow_messages': list_of_new_flow_messages
    })


async def get(request, instance, id_instance):
    return await ipc.call(request, 'flows', 'GET', f'/{instance}/{id_instance}')


async def system_flow(tenant_code: str,
                      instance: str, id_instance: uuid.UUID,
                      type_code: str, message: str = None, data: dict = None,
                      expected_count_in_result=False, parents: dict = None
                      ):

    _handler = await get_system_user_mocked_handler_for_tenant(tenant_code)
    # from collections import namedtuple
    #
    # import base3.test
    #
    # prefix = 'http://v3/api/v3'
    # if base3.test.test_mode:
    #     prefix = f'http://localhost:{base3.test.test_port}'
    #
    #
    # id_tenant = (await ipc.api(None, 'GET', prefix + f'/api/v3/tenants/code/{tenant_code.upper()}'))['id']
    #
    # res = await ipc.api(None, 'POST', prefix + f'/api/v3/tenants/{id_tenant}/sessions?show_user_id=true', body={'username': 'system', 'password': 'system123'})
    # token = res['token']
    # id_user = res['id']
    #
    # Request = namedtuple('request', 'id_tenant id_user headers')
    # request = Request(id_tenant, id_user, {'Authorization': token})
    #
    # Handler = namedtuple('handler', 'id_tenant request')
    # _handler = Handler(id_tenant, request)

    return await flow(_handler, instance, id_instance, type_code, message, data, expected_count_in_result, parents)


async def flow(handler, instance: str, id_instance: uuid.UUID, type_code: str, message: str = None, data: dict = None,
               expected_count_in_result=False, parents: dict = None
               ):
    if not hasattr(flow, 'lookup_flows'):
        flow.lookup_flows = await tshared.lookups.LookupFlowTypes.create(handler)

    params = ''
    if expected_count_in_result:
        params = '?expected_count_in_result=true'

    try:
        type_id = flow.lookup_flows.get(key=type_code, index='code')['id']
    except Exception as e:
        raise

    return await ipc.call(handler.request, 'flows', 'POST', f'/{instance}/{id_instance}{params}', body={
        'type_id': type_id,
        'html': message,
        'data': data,
        'parents': parents
    })


async def lookup_flows_flow_visibility(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'flows', '/lookups/flow_visibility', last_updated)


async def lookup_flows_flow_priorities(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'flows', '/lookups/flow_priorities', last_updated)

# {{ ipc_function }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
