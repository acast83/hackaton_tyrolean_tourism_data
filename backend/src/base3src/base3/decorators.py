import jwt
import json
from functools import wraps
from inspect import signature
import inspect
from base3 import http_exceptions as http
from typing import Union
import uuid
import datetime
from base3.http import BaseHttpException
import dateutil.parser
# from scripts.swagger_docstring_parser import DocumentationOAPI

from tshared.utils.setup_logger import get_logger_for


def convert_to_type_or_raise_exception(name, p, t):
    try:
        if t == int:
            return int(p)

        elif t == float:
            return float(p)

        elif t == datetime.datetime:
            return dateutil.parser.parse(p)

        elif t == datetime.date:
            return dateutil.parser.parse(p).date()

        elif t == datetime.time:
            return dateutil.parser.parse(p).time()

        elif t == uuid.UUID:
            return uuid.UUID(p)

        elif t == dict:
            if type(p) == str:
                return json.loads(p) if p else None
            if type(p) == dict:
                return p

        elif t == bool:
            if str(p).lower() in ('true', '1', 'yes'):
                return True
            return False

    except Exception as e:
        tt = str(t).split("'")[1]
        raise http.HttpInvalidParam(id_message='INVALID_PARAM',
                                    message=f"Invalid type for param {p}, {tt} is expected")

    return p


def pack_error(origin_self, e):
    try:
        origin_self.set_status(e.status())
        err = e._dict()
    except:
        origin_self.set_status(http.status.INTERNAL_SERVER_ERROR)
        err = {'error': True}

    origin_self.write(json.dumps(err))


def generate_documentation(funct):
    return '''
components:
  schemas:
    Tenant:
      type: object
      properties:
        id:
          type: string
          format: uuid
    '''

    return funct.__doc__


class api:

    def __init__(self, *args, **kwargs):

        # TODO: Implenthis
        self.only_from_service = kwargs.get('only_from_service',
                                            False)  # kwargs['only_from_service'] if 'only_from_service' in kwargs else False

        self.logger_name = route.get('logger_name', None)
        self.service_name = route.get('service_name', None)

        self.raw = kwargs['raw'] if 'raw' in kwargs else False

        self.auth = kwargs['auth'] if 'auth' in kwargs else True
        self.weak = kwargs['weak'] if 'weak' in kwargs else False
        self.weak_restricted_on_local = kwargs[
            'weak_restricted_on_local'] if 'weak_restricted_on_local' in kwargs else False
        self.test_only = kwargs['test_only'] if 'test_only' in kwargs else False
        self.content_type = kwargs['content_type'] if 'content_type' in kwargs else 'application/json'
        self.content_disposition = kwargs.get('content_disposition')
        self.deprecated = kwargs['deprecated'] if 'deprecated' in kwargs else False
        self.permissions = kwargs['permissions'] if 'permissions' in kwargs else []

    def __call__(self, funct):
        setattr(funct, 'deprecated', self.deprecated)

        @wraps(funct)
        async def wrapper(_origin_self, *args, **kwargs):

            _token = None
            _origin_self.id_tenant = None
            _origin_self.id_user = None
            _origin_self.id_session = None
            _origin_self.log = get_logger_for(_origin_self)

            # if 'HandlerSendEnqueuedEmail' in str(funct):
            #     print("STOP")
            #
            # if not self.auth and self.weak and self.weak_restricted_on_local:
            #     print("SELF ORIGIN", self)

            if hasattr(_origin_self, 'request') and hasattr(_origin_self.request,
                                                            'arguments') and 'documentation' in _origin_self.request.arguments:
                if hasattr(funct, '__doc__') and funct.__doc__:

                    # use signature and read properies, and took this properties from docstring
                    sig = signature(funct)

                    self.content_type = 'text/html; charset=UTF-8'
                    _origin_self.set_status(200)
                    _origin_self.write(generate_documentation(funct))
                else:
                    self.content_type = 'application/json; charset=UTF-8'
                    _origin_self.set_status(404)
                    _origin_self.write(b'{"error":"documentation not found"}')

                return wrapper

            if self.test_only:
                from base3.test import test_mode
                if not test_mode:
                    raise http.HttpInvalidParam(id_message='RESERVED_FOR_TESTING_IN_DEVELOPMENT',
                                                message="API is not available, it is reserved only for integration/unit testing")

            if self.auth:
                if 'Authorization' not in _origin_self.request.headers and not self.weak:

                    _origin_self.send_error(http.status.UNAUTHORIZED, message='Unauthorized', id_message='UNAUTHORIZED')
                    return

                else:

                    if 'Authorization' in _origin_self.request.headers:
                        _token = _origin_self.request.headers['Authorization']

                        from base3.config_keys import _public_key

                        try:
                            res = jwt.decode(_token.replace('Bearer ', ''), _public_key, algorithms='RS256')
                        except Exception as e:
                            # TODO: Log
                            _origin_self.send_error(http.status.UNAUTHORIZED, message='Unauthorized',
                                                    id_message='UNAUTHORIZED')
                            return

                        _origin_self.id_session = uuid.UUID(res['id'])
                        _origin_self.id_tenant = uuid.UUID(res['id_tenant'])
                        _origin_self.id_user = uuid.UUID(res['id_user'])
                        _expires = res['expires']

                        if _expires and datetime.datetime.now().timestamp() > _expires:
                            _origin_self.send_error(http.status.UNAUTHORIZED, message='Session Expired',
                                                    id_message='SESSION_EXPIRED')

                    if not _token and self.weak:
                        _origin_self.id_tenant = uuid.UUID('00000000-0000-0000-0000-000000000000')
                        _origin_self.id_user = uuid.UUID('00000000-0000-0000-0000-000000000000')
                        _origin_self.id_session = uuid.UUID('00000000-0000-0000-0000-000000000000')

                    if not _token and not self.weak:
                        _origin_self.send_error(http.status.UNAUTHORIZED, message='Unauthorized',
                                                id_message='UNAUTHORIZED')
                        return

            sig = signature(funct)

            body = {}
            if _origin_self.request.body:
                try:
                    body = json.loads(_origin_self.request.body.decode('utf-8'))
                except Exception as e:
                    body = {}

            params = {}

            try:

                arg_pos = -1
                for p in sig.parameters:
                    if p == 'self':
                        continue

                    arg_pos += 1

                    pp = sig.parameters[p]

                    if _origin_self.path_args and len(_origin_self.path_args) > arg_pos:
                        params[p] = _origin_self.path_args[arg_pos]
                    else:
                        v = _origin_self.get_arguments(pp.name)

                        if len(v) > 1:
                            raise http.HttpInvalidParam(id_message='INVALID_PARAM',
                                                        message="Multiple params for single key is not supported")

                        if len(v) == 1:
                            params[p] = v[0]

                    # TODO: Process all other datatypes !

                    sp = sig.parameters[p]

                    if p in body and p in params:
                        if sp.default is sig.empty:
                            raise http.HttpInvalidParam(id_message='INVALID_PARAM',
                                                        message=f"Same param '{p}' presented in body and in query argument")

                    elif p not in params and p not in body:
                        if sp.default is sig.empty:
                            print("f", funct, p)
                            raise http.HttpInvalidParam(id_message='MISSING_PARAM',
                                                        message=f"Mandatory argument {p} is not provided")
                        else:
                            params[p] = sp.default
                    elif p in params and p not in body:
                        pass
                    else:
                        params[p] = body[p]

                    if params[p]:
                        params[p] = convert_to_type_or_raise_exception(p, params[p], sp.annotation)

            except http.HttpInternalServerError as ie:
                get_logger_for(_origin_self).critical(f"Internal Server Error ::::: {ie} ??")
                return pack_error(_origin_self, ie)

            except Exception as e:
                get_logger_for(_origin_self).critical(e)
                return pack_error(_origin_self, e)

            _args = []

            try:
                # if 'TCScheduleMeetingToGroup.post' in str(funct):
                #     print("F",funct)

                get_logger_for(_origin_self).debug(f'CALLING FUNCTION {funct} ({_args},{params})')

                res = await funct(_origin_self, *_args, **params)
                # print("X")
            except BaseHttpException as e:
                get_logger_for(_origin_self).fatal(e)
                print("_EXCEPTION", e)

                _origin_self.set_status(e._status)

                res = {}
                for k in ('id_message', 'message'):
                    if hasattr(e, k):
                        res[k] = getattr(e, k)

                if self.content_type == 'application/json':
                    _origin_self.write(json.dumps(res, indent=1, default=lambda x: str(x)))
                else:
                    _origin_self.write(res)

                return wrapper

            except Exception as e:
                get_logger_for(_origin_self).error(e)
                print("_EXCEPTION2", e, type(e), dir(e))

                _origin_self.set_status(http.status.INTERNAL_SERVER_ERROR)
                return wrapper

            if type(res) == tuple and len(res) == 3:
                _origin_self.set_status(res[2])
                _origin_self.set_header('Content-Type', res[1])

                if self.content_disposition:
                    _origin_self.set_header('Content-Disposition', self.content_disposition)

                _origin_self.write(res[0])

            elif type(res) == tuple and len(res) == 2:
                _origin_self.set_status(res[1])

                if self.content_disposition:
                    _origin_self.set_header('Content-Disposition', self.content_disposition)

                if self.content_type == 'application/json':
                    if res[0]:
                        _origin_self.write(json.dumps(res[0], indent=1, default=lambda x: str(x)))
                else:
                    _origin_self.write(res)

            else:
                status_code = http.status.OK if res is not None else http.status.NO_CONTENT
                _origin_self.set_status(status_code)

                if self.raw:
                    _origin_self.set_status(200)

                if res:
                    if self.content_type == 'application/json':
                        res = json.dumps(res, indent=1, default=lambda x: str(x))
                        _origin_self.write(res)
                    else:
                        _origin_self.write(res)

        return wrapper


class route:
    uri = []
    _handlers = []
    _global_settings = {}
    _handler_names = set()

    @staticmethod
    def all():
        return route._handlers

    # @staticmethod
    # def all_routes_with_methods():
    #     res = DocumentationOAPI(route._handlers)
    #     return res.to_dict()

    @staticmethod
    def print_all_routes():
        print("---[", 'routes', "]" + ('-' * 107))
        for r in route.all():
            print("ROUTE", r)
        print("-" * 120)
        print('total', len(route.all()), 'routes')
        print("-" * 120)

    @staticmethod
    def set(key, value):
        route._global_settings[key] = value

    @staticmethod
    def get(key, default=None):
        if key in route._global_settings:
            return route._global_settings[key]

        return default

    @staticmethod
    def register_handler(uri, handler, static):
        for h in route._handlers:
            if h[0] == uri:
                raise http.HttpInternalServerError(f"Error creating api, endopoint '{uri}'  already exists")

        route._handlers.append((uri, handler, static))

    @staticmethod
    def handlers():
        return sorted(route._handlers, reverse=True)

    @staticmethod
    def handler_names():
        return route._handler_names

    @staticmethod
    def set_handler_names(hn):
        route._handler_names = hn

    def __init__(self, URI='/?', *args, **kwargs):

        self.uri = []
        self._uri = URI

        # if type(URI) == str:
        #     URI = [URI, URI.replace('_','-')]

        uris = [URI] if type(URI) == str else URI

        static = kwargs['static'] if 'static' in kwargs else None

        specified_prefix = kwargs['PREFIX'] if 'PREFIX' in kwargs else None

        for uri in uris:
            parts = uri.split('/')
            rparts = []
            for p in parts:
                rparts.append("([^/]*)" if len(p) and p[0] == ':' else p)

            self.uri.append({'specified_prefix': specified_prefix, 'route': '/'.join(rparts), 'static': static})

    def __call__(self, cls):

        scls = str(cls).replace("<class '", "").replace("'>", "")
        svc = scls.split('.')

        self.handler_name = svc[-1]

        route_handler_names = route.handler_names()

        if self.handler_name in route_handler_names:
            raise http.HttpInternalServerError(
                f"Handler with class {self.handler_name} already defined in project, use unique class name")

        route_handler_names.add(self.handler_name)
        route.set_handler_names(route_handler_names)

        prefix = route.get('prefix', '')

        for duri in self.uri:
            uri = duri['route']
            default_prefix = prefix + ('/' if len(uri) > 0 and uri[0] != '/' else '')
            if duri['specified_prefix'] is not None:
                default_prefix = duri['specified_prefix'].strip()

            static = duri['static']

            furi = default_prefix + uri

            furi = furi.strip()
            if furi[-1] == '/':
                furi += '?'
            elif furi[-1] != '?':
                furi += '/?'

            cls._uri = default_prefix + self._uri

            route.register_handler(furi, cls, static)

        return cls
