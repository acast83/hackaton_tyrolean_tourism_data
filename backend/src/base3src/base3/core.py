import json
import tornado.web
from typing import Optional, Awaitable
from typing import Any
from base3 import http


class Base_():

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        pass

    def prepare(self) -> Optional[Awaitable[None]]:
        self.set_header('Content-Type', 'application/json; charset=UTF-8')
        return super().prepare()

    def request_body(self):
        body = json.loads(self.request.body) if self.request.body else {}
        body['id_tenant'] = self.id_tenant if hasattr(self, 'id_tenant') else None
        body['created_by'] = self.id_user if hasattr(self, 'id_user') else None
        body['last_updated_by'] = self.id_user if hasattr(self, 'id_user') else None

        return body

    def validate_request_body(self, Pydantic_Model):
        body = self.request_body()
        try:
            return Pydantic_Model(**body)
        except Exception as e:
            raise http.HttpInvalidParam(id_message="INVALID_PARAMETERS", message=str(e))

    def get_method_arguments(self, MethodModel):
        arg_dict = {}
        for key in self.request.arguments:
            arg = self.get_query_arguments(key)[0]
            try:
                arg_dict[key] = json.loads(arg)
            except:
                arg_dict[key] = arg
        try:
            return MethodModel(**arg_dict)
        except Exception as e:
            raise http.HttpInvalidParam(id_message="INVALID_PARAMETERS", message=str(e))

    def write_error(self, status_code: int, **kwargs: Any) -> None:
        body = {}

        body.update({
            'method': self.request.method,
            'uri': self.request.path,
            'code': status_code,
            'id_message': kwargs['id_message'] if 'id_message' in kwargs else 'no-id_message-available',
            'message': kwargs['message'] if 'message' in kwargs else 'no-message-available',
        })

        self.finish(body)

    def options(self, *args, **kwargs):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, PUT, PATCH, GET, DELETE, OPTIONS, LINK, UNLINK, LOCK')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Headers',
                        'Origin, X-CSRFToken, Content-Type, Accept, Authorization, Cache-Control, jwt')
        self.set_status(200)
        self.finish('OK')

    def set_default_headers(self) -> None:
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, PUT, PATCH, GET, DELETE, OPTIONS, LINK, UNLINK, LOCK')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Headers',
                        'Origin, X-CSRFToken, Content-Type, Accept, Authorization, Cache-Control, jwt')

    def initialize(self, *args, **kwargs) -> None:
        if 'path' in kwargs:
            self.root = kwargs['path']


#        print('__INITIALIZE__',"ARGS",args,"KWARGS",kwargs)
#        pass

class Base(Base_, tornado.web.RequestHandler):
    pass


class BaseHTML(Base):
    def prepare(self) -> Optional[Awaitable[None]]:
        r = super().prepare()
        self.set_header('Content-Type', 'text/html; charset=UTF-8')
        return r