import warnings
import pathlib
import copy

warnings.filterwarnings("ignore", category=DeprecationWarning)

from tornado.testing import AsyncHTTPTestCase
from tornado.ioloop import IOLoop
import json
from base3 import http

from uuid import uuid4 as UUIDUUID4

import base64
import uuid

test_mode = False
test_port = None


class MockedRedis:
    store = {}

    def set(self, key, value):
        value = value.encode()
        MockedRedis.store[key] = value

    def get(self, key):
        return MockedRedis.store[key]

    def flushall(self):
        MockedRedis.store = {}


def b64file(fn):
    with open(fn, 'rb') as f:
        content = f.read()
    res = base64.encodebytes(content)
    return res.decode('utf-8')


def my_uuid4():
    if not hasattr(my_uuid4, 'next'):
        my_uuid4.next = 0
        my_uuid4.history = []

    res = UUIDUUID4()

    # res = uuid.UUID(f'00000000-0000-0000-0000-{my_uuid4.next:012d}')
    my_uuid4.history.append(str(res))
    my_uuid4.next += 1
    return res


def is_uuid(s):
    if type(s) == uuid.UUID:
        return True
    try:
        uuid.UUID(s)
    except:
        return False
    return True


def clear_uuid_values_in_list(lst):
    pos = -1
    for item in lst:
        pos += 1
        if type(item) == dict:
            clear_uuid_values(lst[pos])
            continue
        if type(item) == list:
            clear_uuid_values_in_list(lst[pos])
            continue
        if is_uuid(item):
            lst[pos] = '__IGNORE_THIS_UUID__'


def clear_uuid_values(dct):
    if type(dct) == list:
        clear_uuid_values_in_list(dct)
        return

    for key in dct:
        val = dct[key]

        if type(val) == list:
            clear_uuid_values_in_list(val)
            continue


        elif type(val) == dict:
            clear_uuid_values(val)
            continue

        if is_uuid(val):
            dct[key] = '__IGNORE_THIS_UUID__'


#
# def rsubset(sub, s):
#     for key in sub.keys():
#
#         if key not in s:
#             return False
#
#         if type(sub[key]) != type(s[key]):
#             return False
#
#         if type(sub[key]) == dict:
#             if not rsubset(sub[key], s[key]):
#                 return False
#
#         elif sub[key] != s[key]:
#             return False
#
#     return True
#


def l_in_l(a, b):
    if type(a) != type(b):
        return False

    if len(a) != len(b):
        return False

    for k in range(len(a)):
        if type(a[k]) != type(b[k]):
            return False

        if type(a[k]) in (list, type):
            if not l_in_l(a[k], b[k]):
                return False
        elif type(a[k]) == dict:
            if not d_in_d(a[k], b[k]):
                return False

        else:
            if a[k]!=b[k]:
                return False

    return True


def d_in_d(a, b):
    if type(a) != type(b):
        return False

    if type(a) in (list, tuple):
        return l_in_l(a, b)

    elif type(a) == dict:

        for ka in a:

            if ka not in b:
                return False

            elif type(a[ka]) != type(b[ka]):
                return False

            elif type(a[ka]) not in (dict, list, tuple):
                if a[ka] != b[ka]:
                    return False

            elif type(a[ka]) in (list, tuple):
                if not l_in_l(a[ka], b[ka]):
                    return False

            elif type(a) == dict:
                if not d_in_d(a[ka], b[ka]):
                    return False

        return True

    else:
        return a == b

class BaseTest(AsyncHTTPTestCase):

    def setUp(self):

        # turn on test_mode - so other libraries will have info if test base3.test.test_mode
        global test_mode, test_port
        test_mode = True

        super(BaseTest, self).setUp()

        test_port = self.get_http_port()

        self.r = None
        self.last_result = None
        self.last_method = None
        self.last_body = None
        pass

    def get_new_ioloop(self):
        return IOLoop.current()

    def get_app(self):
        return self.my_app

    def save_last_result(self, add_request_body=False):

        def get_test_method_name():
            return self._testMethodName

        def get_http_method(uri_):
            return self.last_method

        def get_file_path(route_, prefix_, code_, http_method_, request_body=False):
            path_parts = pathlib.Path(route_.replace(prefix_, '')).parts
            service_name = path_parts[1]
            if service_name.find('?') > 0:
                service_name = service_name[:service_name.find('?')]
            name = self._testMethodName[5:]  # remove 'test_' from beggining

            if request_body:
                return pathlib.Path(pathlib.Path.cwd(), results_dir_name, service_name,
                                    f"{http_method_}_{code_}_{name}.request_body.json")

            return pathlib.Path(pathlib.Path.cwd(), results_dir_name, service_name,
                                f"{http_method_}_{code_}_{name}.json")

        def save_result(file_path_, result_dict_):
            with file_path_.open('w') as f:
                json_result = json.dumps(result_dict_, indent=2)
                f.write(json_result)

        # TODO: implement
        # split folders from filename

        results_dir_name = 'documentation'

        test_method_name = get_test_method_name()
        http_method = get_http_method(test_method_name)

        file_path = get_file_path(route_=self.last_uri,
                                  prefix_=self.config['application']['prefix'],
                                  code_=self.code,
                                  http_method_=http_method)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        save_result(file_path, self.last_result)

        if add_request_body:
            file_path = get_file_path(route_=self.last_uri,
                                      prefix_=self.config['application']['prefix'],
                                      code_=self.code,
                                      request_body=True,
                                      http_method_=http_method)

            save_result(file_path, self.last_body)

    def show_last_result(self, marker='LAST_RES'):
        if hasattr(self, 'last_uri'):
            print(f"{marker} :: URI", self.last_uri)
        if hasattr(self, 'code'):
            print(f"{marker} :: code =", self.code, "EXECUTE TIME", self.execution_time)
        if hasattr(self, 'r'):
            print(f"{marker} :: Last result content")
            print(json.dumps(self.r, indent=4, ensure_ascii=False))

    def api(self, token, method, url, body=None,
            expected_code=(http.status.OK, http.status.CREATED, http.status.NO_CONTENT),
            expected_result=None,
            binary=False,
            expected_result_subset=None,
            expected_result_rsubset=None,
            expected_result_contain_keys=None, expected_length=None, expected_length_for_key: tuple = None,
            raw_response=False, headers=None, default_timeout=600,
            expected_result_list_as_set=None,
            ignore_uuid_values=False, expected_raw=None
            ):

        self.last_method = method
        self.last_body = body
        self.last_uri = copy.deepcopy(body)

        #        if '/api/v3' in url:
        #            print("STOP")

        url = '/api/v3' + url

        if not headers:
            headers = {}

        url = url.strip()
        self.last_uri = url

        method = method.upper()

        if not body:
            if method in ('PUT', 'POST', 'PATCH'):
                body = {}

        if method in ('GET', 'DELETE', 'OPTIONS'):
            body = None
        else:
            try:
                body = json.dumps(body, default=lambda x:str(x))
            except Exception as e:
                raise

        # from base3 import config
        # headers = {config.conf['authorization']['key']: token} if token else {}

        headers.update({'Authorization': 'Bearer ' + token} if token else {})

        import time
        stime = time.time()
        self.execution_time = 'n/a'
        try:
            self.http_client.configure(None,
                                       connect_timeout=default_timeout,
                                       request_timeout=default_timeout
                                       )

            response = self.fetch(url, method=method,
                                  body=body,
                                  headers=headers,
                                  #                                  connect_timeout=default_timeout,
                                  request_timeout=default_timeout)
        except Exception as e:
            print('error serializing output ', e, e)
            print("body", type(body), body)
            print('_' * 100)
            print("")
            self.assertTrue(False)

        self.code = response.code
        if expected_code in ('4XX', '4xx'):
            expected_code = (400, 401, 402, 403, 404, 405, 406)
        if expected_code:
            if type(expected_code) == tuple:
                self.assertIn(response.code, expected_code)
            else:
                self.assertEqual(expected_code, response.code, msg=response.body)

        if raw_response:
            self.execution_time = time.time() - stime
            self.last_result = response.body

            if expected_raw is not None:
                self.assertEqual(response.body.decode('utf-8').strip(), expected_raw.strip())

            return response.body

        if binary:
            self.last_result = response.body
            return response.body
        resp_txt = response.body.decode('utf-8')

        try:
            res = json.loads(resp_txt) if resp_txt else {}
            self.r = res
            self.last_result = res
        except:
            print("Error decoding following response")
            print(resp_txt)
            print("-" * 100)
            self.assertTrue(False)

        res4ret = copy.deepcopy(res)
        if ignore_uuid_values:
            clear_uuid_values(res)
            if expected_result:
                clear_uuid_values(expected_result)
            if expected_result_subset:
                clear_uuid_values(expected_result_subset)
            if expected_result_rsubset:
                clear_uuid_values(expected_result_rsubset)

        if expected_result_list_as_set:
            self.assertEqual(set(expected_result_list_as_set), set(res))

        if expected_result:
            self.assertEqual(expected_result, res)

        if expected_result_rsubset:
            _x = d_in_d(expected_result_rsubset, res)
            self.assertTrue(_x, msg='\n{}\n'.format(json.dumps({
                'puklo': True,
                'ocekujem': expected_result_rsubset,
                'dobio sam': res,
            }, indent=4)))

        if expected_result_contain_keys:
            for key in expected_result_contain_keys:
                self.assertTrue(key in res)

        if expected_result_subset:
            for key in expected_result_subset:
                self.assertTrue(key in res)
                self.assertEqual(expected_result_subset[key], res[key])

        if expected_length is not None:
            self.assertEqual(expected_length, len(res))

        if expected_length_for_key is not None:
            self.assertTrue(len(res[expected_length_for_key[0]]) == expected_length_for_key[1])

        self.r = res4ret
        self.last_result = res4ret
        self.execution_time = time.time() - stime

        return res
