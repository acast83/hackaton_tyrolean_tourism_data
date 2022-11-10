import logging
import json
from tornado.httpclient import AsyncHTTPClient
from base3 import http
import os
from base3.utils import load_config
import datetime
import urllib.parse
import redis

current_file_folder = os.path.dirname(os.path.realpath(__file__))
cfg_folder = current_file_folder + '/../../../config'
try:
    config = load_config(cfg_folder, ['services.yaml'])
except Exception as e:
    raise


async def get_system_user_mocked_handler_for_tenant(tenant_code):
    from collections import namedtuple

    import base3.test

    prefix = 'http://v3/api/v3'
    if base3.test.test_mode:
        prefix = f'http://localhost:{base3.test.test_port}'

    id_tenant = (await api(None, 'GET', prefix + f'/api/v3/tenants/code/{tenant_code.upper()}'))['id']

    res = await api(None, 'POST', prefix + f'/api/v3/tenants/{id_tenant}/sessions?show_user_id=true', body={'username': 'system', 'password': 'system123'})
    token = res['token']
    id_user = res['id']

    Request = namedtuple('request', 'id_tenant id_user headers')
    request = Request(id_tenant, id_user, {'Authorization': token})

    Handler = namedtuple('handler', 'id_tenant request')
    _handler = Handler(id_tenant, request)

    return _handler


async def lookup_base(request, svc, url, last_updated: datetime.datetime = None):
    params = ''
    if last_updated:
        params = '?' + urllib.parse.urlencode({'last_updated': str(last_updated)})

    url += params

    return await call(request, svc, 'GET', url)


async def call(request, service, method, endpoint, body=None, readonly=False, raw_response=False):
    result = await _call(request, service, method, endpoint, body=body, readonly=readonly, raw_response=raw_response)

    return result


async def _call(request, service, method, endpoint, body=None, readonly=False, default_timeout=600, raw_response=False):
    global config

    method = method.upper()

    from base3.test import test_mode, test_port

    # TODO: Read the conf

    api_prefix = config['application']['prefix']
    port = test_port if test_mode else config['application']['port']

    host = 'localhost'
    if not test_mode:
        try:
            r = redis.Redis(host='redis')
            host = r.get(f'v3_services_host_{service}').decode('utf-8')
        except:
            host = 'localhost'

    url = f'http://{host}:{port}{api_prefix}/{service}{endpoint}'

    http_client = AsyncHTTPClient()

    headers = {}

    if 'Authorization' in request.headers and request.headers['Authorization']:
        headers['Authorization'] = request.headers['Authorization']

    try:
        http_client.configure(None,
                              connect_timeout=default_timeout,
                              request_timeout=default_timeout
                              )

        response = await http_client.fetch(url,
                                           method=method,
                                           body=json.dumps(body) if body else None,
                                           headers=headers, request_timeout=default_timeout
                                           )
    except Exception as e:
        print("URL", url)
        print("E", e)

        raise
    code = response.code
    body = None

    try:
        if raw_response:
            body = response.body
        else:
            body = json.loads(response.body.decode())
    except Exception as e:
        pass

    return body, code


async def api(token, method, url, body=None, expected_code=[http.status.OK, http.status.CREATED, 204], expected_result=None,
              silent=False, on_fail=None, authorization_key='Authorization', default_timeout=600000, raw_response=False):
    http_client = AsyncHTTPClient()

    headers = {}

    if token:
        if authorization_key == 'jwt':
            headers[authorization_key] = token
        else:
            headers[authorization_key] = 'Bearer ' + token

    try:
        response = await http_client.fetch(url,
                                           method=method,
                                           body=json.dumps(body) if body else None,
                                           headers=headers, request_timeout=default_timeout
                                           )
    except Exception as e:
        if silent:
            return {}

        if on_fail:
            on_fail()

        raise

    if expected_code:
        if type(expected_code) != list:
            expected_code = [expected_code]

        if response.code not in expected_code:
            if not silent:
                if on_fail:
                    on_fail()

                raise NameError(f'unexpected status code, result is {response.code}, and expected is {expected_code}')

    if response.body:
        if not raw_response:
            try:
                return json.loads(response.body.decode())
            except Exception as e:
                return response.body

        return response.body
