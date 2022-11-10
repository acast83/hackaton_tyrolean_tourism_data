from typing import Union
import zeep
from copy import deepcopy

import tshared.utils.ipc as ipc
from tshared_src.tshared.utils.dict_utils import rm_nones
from tshared_src.tshared.utils.dict_utils import apply_over_dict
from tshared_src.tshared.utils.dict_utils import format_dict


class MockPlintronRequestException(Exception):
    pass


class MockPlintronRequest:
    def __init__(self, method_name: str,
                 request: Union[dict, zeep.xsd.CompoundValue]
                 ):
        self._method = self._prepare_method_name(method_name)
        self._body = self._prepare_body(request)

    async def _call(self, token: str, http_method: str, prefix: str):
        """
        /plintron_mock/method
        """

        prefix = self._prepare_prefix(prefix)
        url = f'{prefix}/plintron_mock/{self._method}'
        body = self._body

        class TempRequest:
            headers = {'Authorization': None if not token else f'Bearer {token}'}

        try:
            # test = await ipc.api(token, 'GET', 'http://localhost/api/v3/tenants/about')
            # result = await ipc.api(token, http_method, url, body=body)
            result, code = await ipc.call(request=TempRequest(),
                                          service='plintron_mock',
                                          method=http_method,
                                          endpoint=f'/{self._method}',
                                          body=self._body,
                                          raw_response=True
                                          )
            return result
        except Exception as e:
            raise MockPlintronRequestException(f"Call to {url} failed: {str(e)}. \n"
                                               f"Token: {token}. \n"
                                               f"Body: {format_dict(self._body)} \n"
                                               f"BodyType: {type(self._body)}\n"
                                               f"BodyTypes: {format_dict(apply_over_dict(obj=self._body, value_apply=lambda x: type(x)))}",
                                               )

    async def call(self, token: str = None, prefix: str = None):
        class Temp:
            def __init__(self, request: bytes):
                self.text = request.decode()

        result = await self._call(token=token,
                                  http_method='POST',
                                  prefix=prefix)

        return Temp(result)

    def _prepare_method_name(self, method_name: str):
        """
        Arguments:
            method_name:

        Returns:
            smth
        """

        if method_name.endswith('Operation'):
            method_name = method_name[:len(method_name) - len('Operation')]
        method_name = self._from_camel_case_to_hyphenated(method_name)
        return method_name

    @staticmethod
    def _from_camel_case_to_hyphenated(name):
        result = ''

        for i, c in enumerate(name):
            if c.isupper() and i != 0:
                result += '-'
            c = c.lower()
            result += c
        return result

    @staticmethod
    def _lower_dict_keys(obj: dict):
        def int_func(_obj: dict) -> dict:
            return apply_over_dict(_obj, key_check=lambda x: True, key_apply=lambda x: x.lower())
        
        result = int_func(obj)

        result = apply_over_dict(
                     result,
                     value_check=lambda x: isinstance(x, list),
                     value_apply=lambda x: [int_func(o) for o in x]
                 )
        return result

    @staticmethod
    def _decode_zeep_object(request) -> dict:
        def check(x):
            c = isinstance(x, zeep.xsd.CompoundValue) or 'zeep' in str(x.__class__)
            return c

        def apply(y):
            return apply_over_dict(
                       obj=dict(y.__values__),
                       value_check=check,
                       value_apply=lambda x: dict(x.__values__),
                   )

        request = apply_over_dict(
                      obj=request,
                      value_check=check,
                      value_apply=apply,
                  )

        request = apply_over_dict(
                      obj=request,
                      value_check=lambda x: isinstance(x, list),
                      value_apply=lambda x: [
                                                apply_over_dict(
                                                    obj=o,
                                                    value_check=check,
                                                    value_apply=apply,
                                                )
                                                for o in x
                                            ],
                  )
        return request

    def _prepare_body(self, request: Union[dict, zeep.xsd.CompoundValue]):
        """
        Arguments:
            request:

        Returns:
        """

        try:
            result = self._decode_zeep_object(request)
        except Exception as e:
            raise MockPlintronRequestException(f'Wrong request type: {type(request)}. Error {str(e)}')

        result = self._lower_dict_keys(result)

        if "DETAILS" in result and len(list(result.keys())) == 1:
            result = result["DETAILS"]
        if "details" in result and len(list(result.keys())) == 1:
            result = result["details"]
        if "_value_1" in result:
            for key in list(result.keys()):
                if key == "_value_1":
                    value_1 = result.pop(key)
                    for _key, _value in value_1.items():
                        result[_key] = _value

        return {'request': rm_nones(result)}

    @staticmethod
    def _prepare_prefix(prefix):
        if prefix is None:
            return 'http://localhost/api/v3'
        else:
            return prefix
