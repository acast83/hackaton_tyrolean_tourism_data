"""This is docstring.
"""

import asyncio
import json
import pathlib
from pathlib import Path
from typing import Optional, Union, Literal, Annotated
import os
import base64
import binascii
from decimal import Decimal
import time
import dotenv

import logging.config
import xmltodict
import zeep
from zeep.cache import InMemoryCache
from zeep.transports import AsyncTransport

from tshared.utils.short_unique_random_string import get_short_unique_random_string as get_unique_id

from tshared_src.tshared.utils.plintron_client import ServicesDetailsType
from tshared_src.tshared.utils.plintron_client import ModifyServicesOperationType
from tshared_src.tshared.utils.plintron_client import OfferingType
from tshared_src.tshared.utils.plintron_client import ProductListType
from tshared_src.tshared.utils.plintron_client import GetProductOfferingDetailsType
from tshared_src.tshared.utils.plintron_client import MultiProductPurchaseType
from tshared_src.tshared.utils.plintron_client import PlintronTypeConstructor

from tshared_src.tshared.utils.dict_utils import rm_nones
from tshared_src.tshared.utils.dict_utils import apply_over_dict

from tshared_src.tshared.utils.plintron_client.utils.mock_plintron_request import MockPlintronRequest


class PlintronClientException(Exception):
    """General exception class for PlintronClient."""
    pass


dotenv.load_dotenv(pathlib.Path(
    pathlib.Path(__file__).parent,
    '../../../../environments/credentials.env'
).resolve(strict=True))

if __name__ == "__main__":
    logging.config.dictConfig({
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {'format': '%(name)s: %(message)s'}
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'verbose',
            },
        },
        'loggers': {
            'zeep.transports': {
                'level': 'DEBUG',
                'propagate': True,
                'handlers': ['console'],
            },
        }
    }
    )

log = logging.getLogger('debugging')

# 0 - Receive the response from the application after complete processing
# 1 - Receive the synchronous response from the application
COMMUNICATION_METHOD: Literal[0, 1] = 0

# This channel reference is to indicate the kind of channel which is initiating the request.
# noinspection SpellCheckingInspection
CHANNEL_REFERENCE: Literal[
    'IVR', 'USSD', 'VMS',
    'CCARE', 'SCARE', 'POS-T',
    'POS-O',
] = "CCARE"

# The provisioning entity requesting the transaction.
ENTITY = os.getenv("PLINTRON_ENTITY")
if not ENTITY:
    raise PlintronClientException('PLINTRON_ENTITY was not supplied.')

# A unique transaction id from the sender, for the convenience of the sender.
# This should be a minimum of 1 digit and maximum of 19 digits.
MAX_LEN_TRANSACTION_ID = 19
TRANSACTION_ID = '0000_00000_00000_00000'
TRANSACTION_ID_BUFFER_FILE = Path(Path(__file__).parent, 'plintron_client_last_transaction_id').resolve()


WSDL_FILE = 'svc_services/services/controllers/plintron_client/ITGAPI.wsdl'


# noinspection SpellCheckingInspection
class PlintronClient:
    def __init__(self, wsdl):
        self._use_mocked_plintron = bool(int(os.getenv('USE_PLINTRON_MOCK', False)))

        self._wsdl = wsdl
        transport = AsyncTransport(cache=InMemoryCache())
        settings = zeep.Settings(raw_response=True)
        self._client = zeep.AsyncClient(wsdl=wsdl,
                                        settings=settings,
                                        transport=transport,
                                        )
        self._transaction_id = None
        self._transaction_id = self._get_transaction_id()
        self._type_constructor = PlintronTypeConstructor(client=self._client)

    @staticmethod
    def _get_transaction_id():
        return get_unique_id(length=MAX_LEN_TRANSACTION_ID)

    @staticmethod
    def __xml_response_to_dict(response: str) -> dict:
        return xmltodict.parse(response)

    @staticmethod
    def __check_status_code(response: dict) -> dict:
        message = response["ENVELOPE"]["HEADER"]["ERROR_DESC"]
        code = response["ENVELOPE"]["HEADER"]["ERROR_CODE"]

        if not (code == 0 or code == '0'):
            message = f'{code} - {message}'
            log.error(f"Plintron client: got none 0 error code. {message}")
            raise PlintronClientException(message)
        method_name = list(response["ENVELOPE"]["BODY"].keys())[0]
        return rm_nones(response["ENVELOPE"]["BODY"][method_name])
        # return response

    def __prepare_result(self, response: str) -> dict:
        response_dict = self.__xml_response_to_dict(response=response)
        return self.__check_status_code(response=response_dict)

    async def __base_request(self,
                             method_name: str,
                             arguments: Union[dict, zeep.xsd.CompoundValue],
                             *,
                             to_rm_nones=True):

        method = getattr(self._client.service, method_name, None)

        if method is None:
            raise PlintronClientException(f'Method does not exist: {method_name}')

        soapheaders = {
            "COMMUNICATION_METHOD": COMMUNICATION_METHOD,
            "CHANNEL_REFERENCE": CHANNEL_REFERENCE,
            "ENTITY": ENTITY,
            "TRANSACTION_ID": self._get_transaction_id()
        }

        if self._use_mocked_plintron:
            try:
                mock_client = MockPlintronRequest(method_name=method_name,
                                                  request=arguments)
                response = await mock_client.call()
            except Exception as e:
                log.error(f"Plintron client: Usage of mocked request failed. {e}")
                raise

        elif isinstance(arguments, dict):
            if to_rm_nones:
                arguments = rm_nones(arguments)
            arguments = apply_over_dict(
                arguments,
                value_apply=lambda x: "39" + str(x) if len(str(x)) == 10 else x,
                key_check=lambda x: x == 'MSISDN'
            )

            response = await method(
                **arguments,
                _soapheaders=soapheaders
            )
        elif isinstance(arguments, zeep.xsd.CompoundValue):
            response = await method(
                arguments,
                _soapheaders=soapheaders
            )
        else:
            log.error("Plintron client: Unexpected arguments type {type(arguments)}")
            raise PlintronClientException(f'Unexpected arguments type {type(arguments)}')
        log.info(f"Plintron client: response successfuly recieved. Response {str(response)[:30]}")
        return response

    async def get_account_details(self, *,
                                  imsi: Union[int, str, None] = None,
                                  msisdn: Union[int, str, None] = None,
                                  icc_id: Union[int, str, None] = None,
                                  account_id: Union[int, str, None] = None,
                                  get_preloaded_available_flag: Optional[bool] = None) -> dict:
        """
        Arguments:
            imsi:
                IMSI of the subscriber
            msisdn:
                MSISDN of the subscriber
            icc_id:
                ICC ID of the subscriber
            account_id:
                Account ID of the subscriber
            get_preloaded_available_flag:

        Returns:
            pass
        """
        """
        <xs:element name="GET_ACCOUNT_DETAILS_REQUEST">
          <xs:complexType>
            <xs:sequence>
              <xs:choice minOccurs="1" maxOccurs="3">
                <xs:element name="MSISDN" type="MSISDNType"/>
                <xs:element name="IMSI" type="IMSIType"/>
                <xs:element name="ICC_ID" type="ICCIDType"/>
                <xs:element name="ACCOUNT_ID" type="AccountIdType"/>
              </xs:choice>
              <xs:element name="GET_PRELOADED_AVAILABLE_FLAG" type="FlagTypeO" minOccurs="0"/>
            </xs:sequence>
          </xs:complexType>
        </xs:element>
        """

        if not any((imsi, msisdn, icc_id, account_id)):
            raise PlintronClientException('Please supply any off: IMSI, MSISDN, ICC_ID, ACCOUNT_ID')

        body = {'IMSI': imsi, 'MSISDN': msisdn, 'ICC_ID': icc_id, 'ACCOUNT_ID': account_id, }
        body_2 = {
            'GET_PRELOADED_AVAILABLE_FLAG':
                int(get_preloaded_available_flag) if get_preloaded_available_flag is not None else None}

        response = await self.__base_request('GetAccountDetailsOperation', {'_value_1': body,
                                                                            **body_2})
        return self.__prepare_result(response=response.text)

    async def get_subscriber_plan_details(self, *,
                                          imsi: Union[int, str, None] = None,
                                          msisdn: Union[int, str, None] = None,
                                          icc_id: Union[int, str, None] = None,
                                          sid_range: any = None
                                          ) -> dict:
        """
        Arguments:
            imsi:
                IMSI of the subscriber
            msisdn:
                MSISDN of the subscriber
            icc_id:
                ICC ID of the subscriber
            sid_range:

        """

        if not any((imsi, msisdn, icc_id, sid_range)):
            raise PlintronClientException(
                'Please supply any off: IMSI, MSISDN, ICC_ID, SID_RANGE'
            )

        body = {
            'IMSI': imsi,
            'MSISDN': msisdn,
            'ICC_ID': icc_id,
            'SID_RANGE': sid_range
        }

        response = await self.__base_request(
            'GetSubscriberPlanDetailsOperation',
            {'_value_1': body}
        )

        return self.__prepare_result(response=response.text)

    async def get_bundle_details(self, *,
                                 bundle_type: Literal["V,I,N", "I,N"],
                                 imsi: Union[int, str, None] = None,
                                 msisdn: Union[int, str, None] = None,
                                 icc_id: Union[int, str, None] = None,
                                 ) -> dict:
        """
        Bundle is a combination of allowances provided by the network operator
        to subscribers for all the network transactions (Voice, SMS and data).
        The subscriber must purchase bundle to get allowances for a specific
        period of time. The subscriber can purchase multiple bundles. This
        API can be triggered to retrieve the complete list and details of all
        the bundles purchased by a subscriber. The bundle details can be
        retrieved based on the bundle type (Bundle Top up, Free SIM with
        Bundle or Quick Top-up bundle). Following is a list of bundle types
        that must be sent in the API request:

        Arguments:
            imsi:
                IMSI of the subscriber
            msisdn:
                MSISDN of the subscriber
            icc_id:
                ICC ID of the subscriber
            bundle_type:
                Bundle Top up - "V,I,N"
                Free SIM with Bundle - "I,N" (MSISDN field empty)
                Quick Top-up Bundle - "I,N"
        """

        if not (any((imsi, msisdn, icc_id)) and bundle_type):
            raise PlintronClientException(
                'Please supply any off: IMSI, MSISDN, ICC_ID and BUNDLE_TYPE'
            )

        body = {
            'IMSI': imsi,
            'MSISDN': msisdn,
            'ICC_ID': icc_id,
            'BUNDLE_TYPE': bundle_type
        }

        response = await self.__base_request(
            'GetBundleDetailsOperation',
            {'DETAILS': body}
        )

        return self.__prepare_result(response=response.text)

    async def get_bundle_list(self, *,
                              imsi: Union[int, str, None] = None,
                              msisdn: Union[int, str, None] = None,
                              icc_id: Union[int, str, None] = None,
                              ) -> dict:
        """
        The subscribers can purchase different types of bundles and multiple
        bundles at a time. This API can be triggered to retrieve the list of
        Normal Bundles, VAS Bundles and Friend Bundles purchased by a
        subscriber.

        Arguments:
            imsi:
                IMSI of the subscriber
            msisdn:
                MSISDN of the subscriber
            icc_id:
                ICC_ID of the subscriber
        """

        if not any((imsi, msisdn, icc_id)):
            raise PlintronClientException('Please supply any off: IMSI, MSISDN, ICC_ID')

        body = {'IMSI': imsi, 'MSISDN': msisdn, 'ICC_ID': icc_id}

        response = await self.__base_request('GetBundleListOperation', {'DETAILS': body})

        return self.__prepare_result(response=response.text)

    async def get_auto_topup_denomination(self, reason_desc: str):
        """GetAutoTopupDenominationOperation
        The subscriber can enable auto topup feature for various denominations
        configured in the billing application. Before enabling the auto topup
        feature, the subscriber can request the network operator to provide
        the configured and available auto topup denominations.
        This API can be triggered to retrieve the existing auto topup
        denomination for the network operator from the billing application.
        """
        if not any((reason_desc,)):
            raise PlintronClientException('Please supply any off: reason_desc')

        body = {'REASON_DESC': reason_desc}

        response = await self.__base_request(
            'GetAutoTopupDenominationOperation',
            {'DETAILS': body}
        )

        return self.__prepare_result(response=response.text)

    async def get_auto_topup_settings(self, *, msisdn: Union[int, str]):
        """
        The subscriber can enable auto topup feature for various denominations
        configured in the billing application. This API can be triggered to
        retrieve the auto topup settings, such as maximum number of auto
        top-ups that can be performed for a subscriber in a week and the
        number of weeks the auto top-up process is to be performed for a
        subscriber.

        """
        if not any((msisdn,)):
            raise PlintronClientException('Please supply any off: msisdn')

        body = {'MSISDN': msisdn}

        response = await self.__base_request('GetAutoTopupSettingsOperation', {'DETAILS': body})

        return self.__prepare_result(response=response.text)

    async def get_bundle_free_usage_info(self, *,
                                         bundle_code: Union[int, str],
                                         imsi: Union[int, str, None] = None,
                                         msisdn: Union[int, str, None] = None,
                                         icc_id: Union[int, str, None] = None,
                                         account_id: Union[int, str, None] = None,
                                         response_level: Literal['B', 'D'] = None,
                                         package_id: Optional[int] = None
                                         ):
        """
        This operation is used to get the bundle details for a subscriber.
        """

        if not any((imsi, msisdn, icc_id, account_id)):
            raise PlintronClientException('Please supply any off: IMSI, MSISDN, ICC_ID, ACCOUNT_ID')

        body = {'IMSI': imsi, 'MSISDN': msisdn, 'ICC_ID': icc_id, 'ACCOUNT_ID': account_id}
        body_2 = {'BUNDLE_CODE': bundle_code, 'RESPONSE_LEVEL': response_level, 'PACKAGE_ID': package_id}

        response = await self.__base_request('GetBundleFreeUsageInfoOperation',
                                             {'_value_1': body, **body_2},
                                             )

        return self.__prepare_result(response=response.text)

    async def get_service_info(self, *,
                               imsi: Union[int, str, None] = None,
                               msisdn: Union[int, str, None] = None,
                               icc_id: Union[int, str, None] = None,
                               ):
        """
        """
        if not any((imsi, msisdn, icc_id)):
            raise PlintronClientException('Please supply any off: IMSI, MSISDN, ICC_ID')

        body = {'IMSI': imsi, 'MSISDN': msisdn, 'ICC_ID': icc_id}

        response = await self.__base_request('GetServiceInfoOperation', {'_value_1': body})

        return self.__prepare_result(response=response.text)

    async def get_subscriber_bundle_info(self, *,
                                         imsi: Union[int, str, None] = None,
                                         msisdn: Union[int, str, None] = None,
                                         icc_id: Union[int, str, None] = None,
                                         account_id: Union[int, str, None] = None,
                                         location: Optional[str] = None,
                                         location_type: Literal['VLR', 'CC'] = None,
                                         ):
        """

        """
        if not any((imsi, msisdn, icc_id, account_id)):
            raise PlintronClientException('Please supply any off: IMSI, MSISDN, ICC_ID, ACCOUNT_ID')

        body = {'IMSI': imsi, 'MSISDN': msisdn, 'ICC_ID': icc_id, 'ACCOUNT_ID': account_id}
        body_2 = {'LOCATION': location, 'LOCATION_TYPE': location_type}

        response = await self.__base_request('GetSubscriberBundleInfoOperation',
                                             {'_value_1': body, **body_2}
                                             )

        return self.__prepare_result(response=response.text)

    async def italy_get_subscriber_details(self, *,
                                           msisdn: Union[int, str, None] = None,
                                           icc_id: Union[int, str, None] = None,
                                           puk_code: Union[int, str, None] = None,
                                           reference_no: Union[int, str, None] = None,
                                           ):
        """
        ItalyGetSubscriberDetailsOperation
        """

        if not any((msisdn, icc_id)):
            raise PlintronClientException('Please supply any off: IMSI, MSISDN, ICC_ID')

        body = {'MSISDN': msisdn, 'ICCID': icc_id}
        body_2 = {'PUK_CODE': puk_code, 'REFERENCE_NO': reference_no}

        response = await self.__base_request('ItalyGetSubscriberDetailsOperation', {'DETAILS': {**body, **body_2}})

        return self.__prepare_result(response=response.text)

    async def subscribe_bundle(self, *,
                               bundle_code: Union[str, int],
                               imsi: Union[int, str, None] = None,
                               msisdn: Union[int, str, None] = None,
                               icc_id: Union[int, str, None] = None,
                               account_id: Union[int, str, None] = None,
                               amount_ind: Literal[0, 1, 2] = None,
                               ):
        """
        amount_ind:
            0 - It will deduct the amount
            1 - It won't deduct
            2 - Bundle cost will not be deducted from the subscriber balance by billing system.
        """

        if not any((imsi, msisdn, icc_id, account_id)):
            raise PlintronClientException('Please supply any off: IMSI, MSISDN, ICC_ID, ACCOUNT_ID')

        body = {'IMSI': imsi, 'MSISDN': msisdn, 'ICC_ID': icc_id, 'ACCOUNT_ID': account_id}
        body_2 = {
            'BUNDLE_CODE': bundle_code, 'AMOUNT_IND': amount_ind,
        }

        response = await self.__base_request('SubscribeBundleOperation', {'_value_1': body,
                                                                          **body_2})
        return self.__prepare_result(response=response.text)

    async def get_topup_denomination(self, *,
                                     reason_desc: str
                                     ):
        """
        Authorized method.
        """
        body = {'DETAILS': {'REASON_DESC': reason_desc}}
        response = await self.__base_request('GetTopupDenominationOperation', body)
        return self.__prepare_result(response=response.text)

    async def subscribe_special_topup(self, *,
                                      amount: int,
                                      imsi: Union[int, str, None] = None,
                                      msisdn: Union[int, str, None] = None,
                                      icc_id: Union[int, str, None] = None,
                                      ):
        """
        amount_ind:
            top-up amount in minor currency
        """
        if not any((imsi, msisdn, icc_id)):
            raise PlintronClientException('Please supply any off: IMSI, MSISDN, ICC_ID')

        body = {'IMSI': imsi, 'MSISDN': msisdn, 'ICC_ID': icc_id}
        body_2 = {'AMOUNT': amount,
                  }

        response = await self.__base_request('SubscribeSpecialTopupOperation', {'_value_1': body,
                                                                                **body_2})
        return self.__prepare_result(response=response.text)

    async def modify_balance(self, *,
                             amount: Union[int, float],
                             operation: Literal['A', 'S'],
                             imsi: Union[int, str, None] = None,
                             msisdn: Union[int, str, None] = None,
                             icc_id: Union[int, str, None] = None,
                             ):
        """
        operation:
            The operation need to be performed on current account balance
                'A' - Add
                'S' - Subtract
        """

        if not any((imsi, msisdn, icc_id)):
            raise PlintronClientException('Please supply any off: IMSI, MSISDN, ICC_ID')

        body = {'IMSI': imsi, 'MSISDN': msisdn, 'ICC_ID': icc_id}
        body_2 = {'AMOUNT': amount, 'OPERATION': operation
                  }

        response = await self.__base_request('ModifyBalanceOperation', {'_value_1': body,
                                                                        **body_2})
        return self.__prepare_result(response=response.text)

    async def get_call_history(self, *,
                               msisdn: Union[int, str],
                               year: str,
                               month: Literal["01", "02", "03", "04", "05", "06",
                                              "07", "08", "09", "10", "11", "12"],
                               icc_id: Union[int, str, None] = None,
                               ):
        body = {'MSISDN': msisdn, 'ICCID': icc_id, 'YEAR': year, 'MONTH': month}

        response = await self.__base_request('GetCallHistoryOperation', body)
        return self.__prepare_result(response=response.text)

    async def change_sim(self, *,
                         msisdn: Union[int, str],
                         new_imsi: Union[int, str, None] = None,
                         new_icc_id: Union[int, str, None] = None,
                         ) -> dict:
        """
        This API can be triggered to map a SIM/ICCID number to a subscriber
        retaining the old MSISDN number. When this API is triggered, the new
        SIM/ICCID number will be mapped to the existing MSISDN of the
        subscriber in the Plintron MVNE platform.

        Pre-requisite:
            When this API is triggered, the subscriber status must
            be in the "Active" state. This API can be used if the MVNO is
            using their own BSS elements. If the MVNO is using the BSS elements
            of the Plintron MVNE platform, then the SWAP_SIM API can be triggered
            to swap a subscriber's ICCID number with a new ICCID number in
            the Plintron MVNE platform. The common.xsd schema is used for this
            API. The common.xsd schema is used for this API.
        """

        if not any((new_imsi, new_icc_id)):
            raise PlintronClientException('Please supply any off: NEW_IMSI, NEW_ICC_ID')

        body = {'IMSI': new_imsi, 'MSISDN': msisdn, 'ICC_ID': new_icc_id}

        response = await self.__base_request('ChangeSimOperation', body)
        return self.__prepare_result(response=response.text)

    async def swap_sim(self, *,
                       old_msisdn: Union[int, str],
                       old_icc_id: Union[int, str, None],
                       new_icc_id: Union[int, str, None],
                       cip: Optional[int] = None,
                       retailer_id: Optional[str] = None,
                       old_pukcode: Union[int, str, None] = None,
                       new_pukcode: Union[int, str, None] = None,
                       imei: Optional[str] = None,
                       first_name: Optional[str] = None,
                       last_name: Optional[str] = None,
                       date_of_birth: Optional[str] = None,
                       document_type: Optional[str] = None,
                       document_id: Optional[str] = None,
                       doc_expiry_date: Optional[str] = None,
                       ) -> dict:
        """
        This API can be triggered to swap a subscriber's SIM/ICCID number with
        a new ICCID number retaining the old MSISDN number. When this API is
        triggered, the new SIM/ICCID number will be mapped to the existing
        MSISDN of the subscriber in the Plintron MVNE platform.

        Pre-requisite:
            When this API is triggered, the subscriber status must be in the
            "Active" state. If the MVNO is using their own BSS elements, then
            the CHANGE_SIM API can be triggered to swap a subscriber's ICCID
            number with a new ICCID number in the billing application.
            The SWAP_SIM.xsd schema is used for this API.
        """

        body = {'OLD_MSISDN': old_msisdn, 'OLD_ICC_ID': old_icc_id, 'NEW_ICC_ID': new_icc_id,
                'CIP': cip, 'RETAILER_ID': retailer_id,
                'OLD_PUKCODE': old_pukcode, 'NEW_PUKCODE': new_pukcode, 'IMEI': imei,
                'FIRST_NAME': first_name, 'LAST_NAME': last_name, 'DATE_OF_BIRTH': date_of_birth,
                'DOCUMENT_TYPE': document_type, 'DOCUMENT_ID': document_id,
                'DOC_EXPIRY_DATE': doc_expiry_date
                }

        response = await self.__base_request('SwapSimOperation', {'DETAILS': {**body}})
        return self.__prepare_result(response=response.text)

    async def activate_subscriber(self, *,
                                  tariff_plan_id: Union[int, str],
                                  balance: Union[int, str],
                                  language_id: Union[int, str],
                                  imsi: Union[int, str, None] = None,
                                  msisdn: Union[int, str, None] = None,
                                  icc_id: Union[int, str, None] = None,
                                  reseller_id: Optional[str] = None,
                                  postpaid_flag: Literal[0, 1] = None,
                                  template_id: Optional[int] = None,
                                  channel_partner_id: Optional[str] = None,
                                  prop_preset_flag: Literal[0, 1] = None,
                                  atr_id: Optional[str] = None,
                                  ) -> dict:
        """
        This operation is used for business activations in billing system.
        By default, subscribers loaded in billing system will be in idle state.

        sid_range: not implemented

        postpaid_flag:
            It shows the subscriber Type
                0 - Prepaid Subscriber
                1 - Postpaid Subscriber
        """

        if not any((imsi, msisdn, icc_id)):
            raise PlintronClientException('Please supply any off: IMSI, MSISDN, ICC_ID')

        body = {'IMSI': imsi, 'MSISDN': msisdn, 'ICC_ID': icc_id}
        body_2 = {
            'TARIFF_PLAN_ID': tariff_plan_id, 'BALANCE': balance, 'LANGUAGE_ID': language_id,
            'RESELLER_ID': reseller_id, 'POSTPAID_FLAG': postpaid_flag, 'TEMPLATE_ID': template_id,
            'CHANNEL_PARTNER_ID': channel_partner_id, 'PROP_PRESET_FLAG': prop_preset_flag,
            'ATR_ID': atr_id
        }

        response = await self.__base_request('ActivateSubscriberOperation', {**body,
                                                                             **body_2})
        return self.__prepare_result(response=response.text)

    async def deactivate_subscriber(self, *,
                                    reason_desc: str,
                                    imsi: Union[int, str, None] = None,
                                    msisdn: Union[int, str, None] = None,
                                    icc_id: Union[int, str, None] = None,
                                    ) -> dict:
        """
        When this API is triggered, the subscriber's lifecycle state will
        be moved from "ACTIVE" state to "GRACE" state in the billing state.
        When the subscriber's SIM is moved to the "GRACE" state, all the MO
        services will be blocked for the subscriber.

        Whenever a lifecycle status is changed for a subscriber in the
        billing application, then the billing application will trigger an
        internal notification to the HLR application to update the
        respective subscriber details.

        Pre-requisite:
            1. Once the subscriber is deactivated in the billing application,
            the REACTIVATE_SUBSCRIBER API must be triggered to move back the
            subscriber to the "ACTIVE" state in the billing system.
            2. When this API is triggered, the subscriber's SIM status must
            be in the "ACTIVE" state.The common.xsd schema is used for this
            API.

        reason_desc:
            Reason for deactivating. Max 100 bytes
        """

        if not any((imsi, msisdn, icc_id)):
            raise PlintronClientException('Please supply any off: IMSI, MSISDN, ICC_ID')

        body = {'IMSI': imsi, 'MSISDN': msisdn, 'ICC_ID': icc_id}
        body_2 = {'REASON_DESC': reason_desc
                  }

        # response = await self.__base_request('DeactivateSubscriberOperation', {'_value_1': body,
        #                                                                        **body_2})
        response = await self.__base_request('DeactivateSubscriberOperation', {**body,
                                                                               **body_2})
        return self.__prepare_result(response=response.text)

    async def reactivate_subscriber(self, *,
                                    reason_desc: str,
                                    imsi: Union[int, str, None] = None,
                                    msisdn: Union[int, str, None] = None,
                                    icc_id: Union[int, str, None] = None,
                                    ) -> dict:
        """
        In the billing application, when the subscriber's SIM lifecycle
        status is in the "GRACE" state, all the MO services are blocked for
        the subscribers. When this API is triggered, the subscriber's SIM
        status will be changed from "GRACE" state to "ACTIVE" state. When a
        subscriber's SIM is moved to the "ACTIVE" state, the subscriber can
        start using all the network services. This API can be used to
        re-activate a single or group of subscribers in the billing system.
        When the subscriber is re-activated, the subscriber tariff plan will
        be changed to the base tariff plan, which was mapped to the
        subscriber account during the activation process. Whenever a
        lifecycle status is changed for a subscriber in the billing
        application, then the billing application will trigger an internal
        notification to the HLR application to update the respective
        subscriber details.

        Pre-requisite: When this API is triggered, the subscriber's SIM status
        must be in the "GRACE" state.

        reason_desc:
            Reason for deactivating. Max 100 bytes
        """

        if not any((imsi, msisdn, icc_id)):
            raise PlintronClientException('Please supply any off: IMSI, MSISDN, ICC_ID')

        body = {'IMSI': imsi, 'MSISDN': msisdn, 'ICC_ID': icc_id}
        body_2 = {'REASON_DESC': reason_desc
                  }

        # response = await self.__base_request('ReactivateSubscriberOperation', {'_value_1': body,
        #                                                                        **body_2})
        response = await self.__base_request('ReactivateSubscriberOperation', {**body,
                                                                               **body_2})
        return self.__prepare_result(response=response.text)

    async def cancel_bundle(self, *,
                            bundle_code: Union[int, str],
                            imsi: Union[int, str, None] = None,
                            msisdn: Union[int, str, None] = None,
                            icc_id: Union[int, str, None] = None,
                            forcible_bundle_cancellation: Literal[1, 2, 3, 4, 5] = None,
                            reserve_bundle_code: Union[int, str, None] = None,
                            reserve_bundle_sequence_number: Union[int, str, None] = None,
                            payment_mode_indicator: Literal[0, 1] = None,
                            refund_amount: Union[int, str, None] = None,
                            tax: Union[int, str, None] = None,
                            vat: Union[int, str, None] = None,
                            product_refund_cost: Union[int, str, None] = None,
                            ) -> dict:
        """
        forcible_bundle_cancellation:
            Forcible Bundle cancellation number
            Payment Mode Indicator and Refund Amount parameters will be
            populated with a value when this tag value is 3 or 4. Otherwise,
            null tags will come in response.
            1 - When a subscriber wants to activate the reserve bundle immediately.
            2 - Through backend team
            3 - Bundle cancellation up on dis-satisfied services.
                Bundle will be cancelled and approved amount will be refunded
                to subscriber at the requested source of refund.
            4 - Bundle cancellation up on dis-satisfied services.
                Bundle will be retained and approved amount will be refunded
                to subscriber at the requested source of refund.
            5 - Bundle Cancellation Initiated, and bundle will be cancelled at EOD
        payment_mode_indicator:
            Payment Mode:
                0 - INBAL
                1 - CREDIT CARD
        """

        if not any((imsi, msisdn, icc_id)):
            raise PlintronClientException('Please supply any off: IMSI, MSISDN, ICC_ID')

        body = {'IMSI': imsi, 'MSISDN': msisdn, 'ICC_ID': icc_id}
        body_2 = {'BUNDLE_CODE': bundle_code,
                  'FORCIBLE_BUNDLE_CANCELLATION': forcible_bundle_cancellation,
                  'RESERVE_BUNDLE_CODE': reserve_bundle_code,
                  'RESERVE_BUNDLE_SEQUENCE_NUMBER': reserve_bundle_sequence_number,
                  'PAYMENT_MODE_INDICATOR': payment_mode_indicator, 'REFUND_AMOUNT': refund_amount,
                  'TAX': tax, 'VAT': vat, 'PRODUCT_REFUND_COST': product_refund_cost
                  }

        response = await self.__base_request('CancelBundleOperation', {'_value_1': body,
                                                                       **body_2})
        return self.__prepare_result(response=response.text)

    async def cancel_bundle_auto_renewal(self, *,
                                         bundle_code: Union[str, int],
                                         cancel_date: str,
                                         imsi: Union[int, str, None] = None,
                                         msisdn: Union[int, str, None] = None,
                                         icc_id: Union[int, str, None] = None,
                                         reason: Optional[str] = None,
                                         ) -> dict:
        """
        Bundle is a combination of allowances provided by the network operator
        to subscribers for all the network transactions (Voice, SMS and data).

        The subscriber must purchase bundle to get allowances for a specific
        period of time. When a subscriber purchase a bundle through a credit
        card, then the subscriber can enable the bundle auto-renewal feature.
        If the bundle auto-renewal feature is enabled, after the bundle
        validity period, the billing application deducts the bundle amount
        from the previously used credit card and the bundle will be
        auto-renewed for a subscriber. The subscriber can request the network
        operator to cancel the next auto-renewal process. When this API is
        triggered, then after the bundle validity period, the billing
        application will not initiate the auto-renewal process for the
        respective bundle of the subscriber.

        cancel_date:
            This Date format (dd/mm/yyyy or mm/dd/yyyy) may change based on
            the DateTimeFormat return by GET_LANGUAGE_LIST
            note: regex for parsing:
                '(((0[1-9]|[12]\\d|3[01])/(0[13578]|1[02])/((19|[2-9]\\d)\\d{2}))|
                  ((0[1-9]|[12]\\d|30)/(0[13456789]|1[012])/((19|[2-9]\\d)\\d{2}))|
                  ((0[1-9]|1\\d|2[0-8])/02/((19|[2-9]\\d)\\d{2}))|
                      (29/02/((1[6-9]|[2-9]\\d)(0[48]|[2468][048]|[13579][26])|
                      ((16|[2468][048]|[3579][26])00))))'",
                basicaly means => dd/mm/yyyy

        reason:
            Reason to Cancel Auto Renewal
        """

        if not any((imsi, msisdn, icc_id)):
            raise PlintronClientException('Please supply any off: IMSI, MSISDN, ICC_ID')

        body = self._type_constructor.cancel_bundle_type(bundle_code=bundle_code, msisdn=msisdn, imsi=imsi,
                                                         icc_id=icc_id, cancel_date=cancel_date, reason=reason)

        response = await self.__base_request('CancelBundleAutoRenewalOperation', {'DETAILS': body})
        return self.__prepare_result(response=response.text)

    async def enable_bundle_auto_renewal(self, *,
                                         bundle_code: Union[int, str],
                                         renewal_mode: Literal[0, 1],
                                         imsi: Union[int, str, None] = None,
                                         msisdn: Union[int, str, None] = None,
                                         icc_id: Union[int, str, None] = None,
                                         card_number: Union[int, str, None] = None,
                                         card_id: Union[int, str, None] = None,
                                         ) -> dict:
        """
        When a subscriber purchase a bundle through a credit card, then the
        subscriber can enable the bundle auto-renewal feature. If the bundle
        auto-renewal feature is enabled, after the bundle validity period, the
        billing application deducts the bundle amount from the previously used
        credit card and the bundle will be auto-renewed for a subscriber. The
        subscriber can request the network operator to enable the auto-renewal
        process for a bundle. Also, if the auto-renewal is already enabled for
        a bundle, then the subscribers can request the network operator to
        change the charge mode (Account balance or credit card) of the bundle
        auto-renewal process. This API can be triggered to enable auto-renewal
        or to change the bundle auto-renewal charge mode in the subscriber's
        account.

        renewal_mode:
            Charge mode of Subscriber
                0 - IN-BAL.
                1 - Credit Card
        card_number:
            Subscriber's Credit Card number (Full or masked Credit card
            Number - retrieved from GET_CREDIT_CARD_LIST API)
        card_id:
            Credit card ID (Card Key received in GET_CREDIT_CARD_LIST API)
        """

        if not any((imsi, msisdn, icc_id)):
            raise PlintronClientException('Please supply any off: IMSI, MSISDN, ICC_ID')

        body = self._type_constructor.enable_bundle_auto_renewal_type(imsi=imsi, msisdn=msisdn, icc_id=icc_id,
                                                                      bundle_code=bundle_code,
                                                                      renewal_mode=renewal_mode,
                                                                      card_number=card_number, card_id=card_id
                                                                      )

        response = await self.__base_request('EnableBundleAutoRenewalOperation', body)
        return self.__prepare_result(response=response.text)

    async def get_location_data(self, *,
                                information_type: Literal['B', 'E'],
                                req_domain: Literal[1, 2] = None,
                                imsi: Union[int, str, None] = None,
                                msisdn: Union[int, str, None] = None,
                                icc_id: Union[int, str, None] = None,
                                ) -> dict:
        """
        information_type:
            B-Basic
            E-Extended
            "Basic" shall retrieve the subscriber location (Current VLR, SGSN,
            MME Addresses from HLR)
            Extended shall retrieve "Basic" details and shall also retrieve
            the exact Location Information and the current subscriber state
            from the VLR/SGSN defined by the parameter Request Domain.
            VLR/SGSN has to support to get all the detailed info.

        req_domain:
        Mandatory only if the Information Type parameter is "Extended"
            1 - GSM only
            2 - GPRS only

        """

        if not any((imsi, msisdn, icc_id)):
            raise PlintronClientException('Please supply any off: IMSI, MSISDN, ICC_ID')

        if information_type == 'E' and req_domain is None:
            raise PlintronClientException('Please supply: req_domain argument')

        body = {'IMSI': imsi, 'MSISDN': msisdn, 'ICC_ID': icc_id}
        body_2 = {'TYPE': information_type, 'REQ_DOMAIN': req_domain}

        response = await self.__base_request('GetLocationDataOperation', {**body,
                                                                          **body_2})
        return self.__prepare_result(response=response.text)

    @staticmethod
    def __check_list_of_attachements(list_of_attachments: list[dict]) -> list[dict]:
        """
        list_of_attachments:
            EXTENSION: extensions of attached file
            VALUE: file represented as base64 encoded str or as bytes.
                If VALUE type is bytes it is considered that bytes colleted
                as follows:
                ```
                    with open('file_name.txt', 'rb') as f:
                        VALUE = f.read()
                ```
            example (base64 VALUE type):
                [
                     {'EXTENSION': 'pdf',
                      'VALUE': 'JVBERi0xLjQKJf////8KNTAgMCP ... DwvTGVuZ3Ro'},
                ]
        """

        for i in range(len(list_of_attachments)):
            try:
                temp_val = list_of_attachments[i]['VALUE']
            except KeyError:
                raise PlintronClientException('Check list_of_attachments format.')
            if isinstance(temp_val, bytes):
                try:
                    base64.b64decode(temp_val).decode()
                except binascii.Error:
                    list_of_attachments[i]['VALUE'] = base64.b64encode(temp_val).decode()
        return list_of_attachments

    async def italy_register_subscriber(self, *,
                                        icc_id: Union[int, str],
                                        preferred_language: str,
                                        title: str,
                                        last_name: str,
                                        first_name: str,
                                        gender: str,
                                        date_of_birth: str,
                                        place_of_birth: str,
                                        residence_country: str,
                                        italy_national: Literal['Yes', 'EU', 'NON_EU'],
                                        nationality: str,
                                        house_number: Union[int, str],
                                        house_name: str,
                                        post_code: Union[int, str],
                                        street: str,
                                        city: str,
                                        state: str,
                                        document_type: Literal['EU_ID', 'PASSPORT', 'ITALIAN_ID_CARD',
                                                               'ITALIAN_PERMIT', 'ITALIAN_DRIVING_LICENCE',
                                                               'ITALIAN_PASSPORT'],
                                        document_number: str,
                                        issuer: str,
                                        date_of_issue: str,
                                        valid_till: str,
                                        retailer_name: str,
                                        retailerid: str,
                                        chk_sms_marketing: Literal[0, 1],

                                        chk_terms: Literal['true', 'false'],
                                        chk_photocopy: Literal['true', 'false'],
                                        chk_age: Literal['true', 'false'],
                                        sms_update: Literal['true', 'false'],

                                        dynamic_allocation_status: Literal[0, 1],

                                        minor_dob: Optional[str] = None,  # conditional
                                        minor_title: Optional[str] = None,  # conditional
                                        minor_first_name: Optional[str] = None,  # conditional
                                        minor_last_name: Optional[str] = None,  # conditional
                                        minor_gender: Optional[str] = None,  # conditional
                                        accept_minor: Optional[Literal['true', 'false']] = None,  # conditional

                                        ivrlanguage: Optional[str] = None,
                                        comune_code: Optional[str] = None,  # conditional
                                        country_of_birth: Optional[str] = None,  # conditional
                                        type_of_subscriber: Literal[0, 1] = None,
                                        list_of_attachments: Optional[list[dict]] = None,  # conditional
                                        tax_code: Optional[str] = None,  # conditional

                                        province: Optional[str] = None,  # conditional
                                        email_id: Optional[str] = None,
                                        alternative_contact_number: Optional[str] = None,
                                        msisdn: Union[int, str, None] = None,  # conditional
                                        puk_code: Union[int, str, None] = None,  # conditional

                                        is_portin_enabled: Optional[Literal['true', 'false']] = None,

                                        pmsisdn: Optional[str] = None,  # conditional
                                        portin_reference_no: Optional[str] = None,  # conditional
                                        is_real_no: Optional[Literal['true', 'false']] = None,
                                        is_real_user_info_provided: Optional[Literal['true', 'false']] = None,
                                        real_user_info: Optional[list] = None,
                                        vat_number: Optional[str] = None,  # conditional
                                        entry_type: Literal[0, 1, 2] = None,  # conditional
                                        is_email: Optional[Literal['true', 'false']] = None,
                                        additional_1: Optional[str] = None,
                                        additional_2: Optional[str] = None,
                                        ) -> dict:
        """
        list_of_attachments:
            EXTENSION: extensions of attached file
            VALUE: file represented as base64 encoded str or as bytes.
                If VALUE type is bytes it is considered that bytes colleted
                as follows:
                ```
                    with open('file_name.txt', 'rb') as f:
                        VALUE = f.read()
                ```
            example (base64 VALUE type):
                [
                     {'EXTENSION': 'pdf',
                      'VALUE': 'JVBERi0xLjQKJf////8KNTAgMCP ... DwvTGVuZ3Ro'},
                ]
        Returns:
            {
                "ENVELOPE": {
                    "HEADER": {
                        "ERROR_CODE": "0",
                        "ERROR_DESC": "Success",
                    },
                    "BODY": {
                        "ITALY_REGISTER_SUBSCRIBER_RESPONSE": {
                            "CHANNEL_TRANSACTION_ID": "<some data>"
                            "TG_TRANSACTION_ID": "<some data>"
                        }
                    }
                }
            }
        """

        list_of_attachments = self.__check_list_of_attachements(list_of_attachments)
        body = {
            "MSISDN": msisdn, "PUK_CODE": puk_code,
            "ICCID": icc_id, "PREFERRED_LANGUAGE": preferred_language,
            "TITLE": title, "LAST_NAME": last_name,
            "FIRST_NAME": first_name, "GENDER": gender,
            "DATE_OF_BIRTH": date_of_birth, "PLACE_OF_BIRTH": place_of_birth,
            "PROVINCE": province, "EMAIL_ID": email_id,
            "ALTERNATIVE_CONTACT_NUMBER": alternative_contact_number, "RESIDENCE_COUNTRY": residence_country,
            "ITALY_NATIONAL": italy_national, "NATIONALITY": nationality,
            "HOUSE_NUMBER": house_number, "HOUSE_NAME": house_name,
            "POST_CODE": post_code, "STREET": street,
            "CITY": city, "STATE": state,
            "TAX_CODE": tax_code, "DOCUMENT_TYPE": document_type,
            "DOCUMENT_NUMBER": document_number, "ISSUER": issuer,
            "DATE_OF_ISSUE": date_of_issue, "VALID_TILL": valid_till,
            "LIST_OF_ATTACHMENTS": {"ATTACHMENT": list_of_attachments}, "RETAILER_NAME": retailer_name,
            "RETAILERID": retailerid, "CHK_SMS_MARKETING": chk_sms_marketing,
            "CHK_TERMS": chk_terms, "CHK_PHOTOCOPY": chk_photocopy,
            "CHK_AGE": chk_age, "SMS_UPDATE": sms_update,
            "DYNAMIC_ALLOCATION_STATUS": dynamic_allocation_status, "IVRLANGUAGE": ivrlanguage,
            "COMUNE_CODE": comune_code, "COUNTRY_OF_BIRTH": country_of_birth,
            "TYPE": type_of_subscriber, "MINOR_DOB": minor_dob,
            "MINOR_TITLE": minor_title, "MINOR_FIRST_NAME": minor_first_name,
            "MINOR_LAST_NAME": minor_last_name, "MINOR_GENDER": minor_gender,
            "ACCEPT_MINOR": accept_minor, "IS_PORTIN_ENABLED": is_portin_enabled,
            "PMSISDN": pmsisdn, "PORTIN_REFERENCE_NO": portin_reference_no,
            "IS_REAL_NO": is_real_no, "IS_REAL_USER_INFO_PROVIDED": is_real_user_info_provided,
            "REAL_USER_INFO": real_user_info, "VAT_NUMBER": vat_number,
            "ENTRY_TYPE": entry_type, "IS_EMAIL": is_email,
            "ADDITIONAL_1": additional_1, "ADDITIONAL_2": additional_2,
        }

        body = self._type_constructor.register_subscriber_italy_type(**body)

        response = await self.__base_request('ItalyRegisterSubscriberOperation',
                                             {'DETAILS': body},
                                             to_rm_nones=False)

        return self.__prepare_result(response=response.text)

    async def update_subscriber_italy(self, *,
                                      icc_id: Union[int, str],
                                      preferred_language: str,
                                      title: str,
                                      last_name: str,
                                      first_name: str,
                                      gender: str,
                                      date_of_birth: str,
                                      place_of_birth: str,
                                      residence_country: str,
                                      italy_national: Literal['Yes', 'EU', 'NON_EU'],
                                      nationality: str,
                                      house_number: str,
                                      house_name: str,
                                      post_code: str,
                                      street: str,
                                      city: str,
                                      state: str,
                                      document_type: Literal['EU_ID', 'PASSPORT', 'ITALIAN_ID_CARD',
                                                             'ITALIAN_PERMIT', 'ITALIAN_DRIVING_LICENCE',
                                                             'ITALIAN_PASSPORT'],
                                      document_number: str,
                                      issuer: str,
                                      date_of_issue: str,
                                      valid_till: str,
                                      retailer_name: str,
                                      retailerid: str,

                                      chk_sms_marketing: Literal[0, 1],

                                      chk_terms: Literal['true', 'false'],
                                      chk_photocopy: Literal['true', 'false'],
                                      chk_age: Literal['true', 'false'],

                                      minor_dob: Optional[str] = None,  # conditional
                                      minor_title: Optional[str] = None,  # conditional
                                      minor_first_name: Optional[str] = None,  # conditional
                                      minor_last_name: Optional[str] = None,  # conditional
                                      minor_gender: Optional[str] = None,  # conditional
                                      accept_minor: Optional[bool] = None,  # conditional

                                      comune_code: Optional[str] = None,  # conditional
                                      country_of_birth: Optional[str] = None,  # conditional
                                      list_of_attachments: Optional[list] = None,  # conditional
                                      tax_code: Optional[str] = None,  # conditional

                                      province: Optional[str] = None,  # conditional
                                      email_id: Optional[str] = None,
                                      alternative_contact_number: Optional[str] = None,
                                      msisdn: Union[int, str, None] = None,  # conditional
                                      puk_code: Union[int, str, None] = None,  # conditional

                                      is_real_user_info_provided: Optional[bool] = None,
                                      real_user_info: Optional[list] = None,
                                      vat_number: Optional[str] = None,  # conditional
                                      entry_type: Literal[0, 1, 2] = None,  # conditional
                                      is_email: Optional[str] = None,
                                      additional_1: Optional[str] = None,
                                      additional_2: Optional[str] = None,
                                      ) -> dict:

        list_of_attachments = self.__check_list_of_attachements(list_of_attachments)

        body = {
            "MSISDN": msisdn, "PUK_CODE": puk_code,
            "ICCID": icc_id, "PREFERRED_LANGUAGE": preferred_language,
            "TITLE": title, "LAST_NAME": last_name,
            "FIRST_NAME": first_name, "GENDER": gender,
            "DATE_OF_BIRTH": date_of_birth, "PLACE_OF_BIRTH": place_of_birth,
            "PROVINCE": province, "EMAIL_ID": email_id,
            "ALTERNATIVE_CONTACT_NUMBER": alternative_contact_number, "RESIDENCE_COUNTRY": residence_country,
            "ITALY_NATIONAL": italy_national, "NATIONALITY": nationality,
            "HOUSE_NUMBER": house_number, "HOUSE_NAME": house_name,
            "POST_CODE": post_code, "STREET": street,
            "CITY": city, "STATE": state,
            "TAX_CODE": tax_code, "DOCUMENT_TYPE": document_type,
            "DOCUMENT_NUMBER": document_number, "ISSUER": issuer,
            "DATE_OF_ISSUE": date_of_issue, "VALID_TILL": valid_till,
            "LIST_OF_ATTACHMENTS": {"ATTACHMENT": list_of_attachments}, "RETAILER_NAME": retailer_name,
            "RETAILERID": retailerid, "CHK_SMS_MARKETING": chk_sms_marketing,
            "CHK_TERMS": chk_terms, "CHK_PHOTOCOPY": chk_photocopy,
            "CHK_AGE": chk_age,
            "COMUNE_CODE": comune_code, "COUNTRY_OF_BIRTH": country_of_birth,
            "MINOR_DOB": minor_dob,
            "MINOR_TITLE": minor_title, "MINOR_FIRST_NAME": minor_first_name,
            "MINOR_LAST_NAME": minor_last_name, "MINOR_GENDER": minor_gender,
            "ACCEPT_MINOR": accept_minor,
            "IS_REAL_USER_INFO_PROVIDED": is_real_user_info_provided,
            "REAL_USER_INFO": real_user_info, "VAT_NUMBER": vat_number,
            "ENTRY_TYPE": entry_type, "IS_EMAIL": is_email,
            "ADDITIONAL_1": additional_1, "ADDITIONAL_2": additional_2,
        }
        body = self._type_constructor.update_subscriber_italy_type(**body)
        response = await self.__base_request('UpdateSubscriberItalyOperation', {'DETAILS': body})
        return self.__prepare_result(response=response.text)

    async def get_transaction_details(self, *,
                                      transaction_id: Union[int, str, None] = None,
                                      imsi: Union[int, str, None] = None,
                                      msisdn: Union[int, str, None] = None,
                                      icc_id: Union[int, str, None] = None,
                                      ) -> dict:
        """
        Whenever a subscriber purchase a bundle or do a top-up through
        web-site/mobile APP or during the auto-renewal process, the billing
        application generates and stores the Call Data Record (CDR) with
        complete transaction details in the Business Support System (BSS)
        database. This API can be triggered to retrieve and view the complete
        transaction details of a transaction from the BSS database based on
        the transaction ID.

        Pre-requisite:
            This API can be used if the MVNO is using the BSS
            elements of the Plintron MVNE platform. If the MVNO is using their
            own BSS elements, then the GET_TRANSACTION_HISTORY.htm API can be
            triggered to retrieve and view the complete transaction details of
            a transaction from the billing application based on the
            transaction ID.
        """
        if not any((imsi, msisdn, icc_id)):
            raise PlintronClientException('Please supply any off: IMSI, MSISDN, ICC_ID')

        body = {'IMSI': imsi, 'MSISDN': msisdn, 'ICCID': icc_id, 'TRANSACTIONID': transaction_id}
        body = self._type_constructor.get_transaction_det_type(**body)
        response = await self.__base_request('GetTransactionDetailsOperation', {'DETAILS': body})
        return self.__prepare_result(response=response.text)

    async def get_transaction_history(self, *,
                                      topup_type: Literal[1, 2],
                                      imsi: Union[int, str, None] = None,
                                      msisdn: Union[int, str, None] = None,
                                      icc_id: Union[int, str, None] = None,
                                      ) -> dict:
        """
        To get the transaction history of the subscriber.

        topup_type:
            The type of topup
                1 - Special Topup
                2 - Special Bundle Topup
        """

        if not any((imsi, msisdn, icc_id)):
            raise PlintronClientException('Please supply any off: IMSI, MSISDN, ICC_ID')

        body = {'IMSI': imsi, 'MSISDN': msisdn, 'ICC_ID': icc_id}
        body_2 = {'TOPUP_TYPE': topup_type}
        response = await self.__base_request('GetTransactionHistoryOperation', {'_value_1': body, **body_2})
        return self.__prepare_result(response=response.text)

    async def get_topup_history(self, *,
                                msisdn: Union[int, str],
                                year: str,
                                month: Literal[
                                    "01", "02", "03", "04", "05", "06",
                                    "07", "08", "09", "10", "11", "12",
                                ],
                                icc_id: Union[int, str, None] = None,
                                ) -> dict:
        """
        Whenever a subscriber do a top-up or during the auto-renewal process,
        the billing application generates and stores the Call Data Record
        (CDR) in the Business Support System (BSS) database. This API can be
        triggered to retrieve and view the complete top-up history for a
        subscriber from the BSS database for a period of time. The top-history
        for a subscriber can be retrieved and viewed for a month in a year.
        Based on the input received from the API, the top-up history for the
        subscriber will be retrieved for the respective month from the BSS
        database and sent as a response.
        """

        body = {'MSISDN': msisdn, 'ICCID': icc_id}
        body_2 = {'YEAR': year, 'MONTH': month}
        response = await self.__base_request('GetTopupHistoryOperation', {**body, **body_2})
        return self.__prepare_result(response=response.text)

    async def get_service_providers(self, *,
                                    sp_code: Optional[str] = None
                                    ) -> dict:
        """
        The purpose of this web method is to get the Service Providers list to
        MNP System from external Channel(s).

        sp_code: operator code
        """

        body = rm_nones({'DETAILS': {'SPCODE': sp_code}})

        response = await self.__base_request('GetServiceProvidersOperation', body)
        return self.__prepare_result(response=response.text)

    async def change_tariff_plan(self, *,
                                 tariff_plan_id: str,
                                 imsi: Union[int, str, None] = None,
                                 msisdn: Union[int, str, None] = None,
                                 icc_id: Union[int, str, None] = None,
                                 ) -> dict:
        """
        By default, a base tariff plan is mapped to the subscribers. When a
        new subscriber is activated in the Plintron MVNE platform, the
        subscriber will be charged for using the network services as per the
        base tariff plan. If a subscriber purchase a bundle, then the bundle
        tariff plan will be active only during the bundle validity period.
        After the bundle validity period, the subscriber will be charged as
        per the base tariff plan. This API can be triggered to change the
        subscriber's current tariff plan in the billing application.
        """

        if not any((imsi, msisdn, icc_id)):
            raise PlintronClientException('Please supply any off: IMSI, MSISDN, ICC_ID')

        body = {'IMSI': imsi, 'MSISDN': msisdn, 'ICC_ID': icc_id}

        response = await self.__base_request('ChangeTariffPlanOperation', {**body,
                                                                           'TARIFF_PLAN_ID': tariff_plan_id})
        return self.__prepare_result(response=response.text)

    async def check_portin_status(self, *,
                                  reference_number: Union[str, int],
                                  reference_type: Literal['MSISDN', 'PMSISDN', 'REQUESTID'],
                                  ) -> dict:
        """
        The purpose of this web method is to place a retrieve the query status
        of port-in Request to MNP System from external Channel(s).

        """
        body = {'REFERENCE_NUMBER': reference_number, 'REFERENCE_TYPE': reference_type}
        body = {'DETAILS': self._type_constructor.portin_request_details_type(**body)}

        response = await self.__base_request('CheckPortinStatusOperation', body)
        return self.__prepare_result(response=response.text)

    async def check_portout_status(self, *,
                                   reference_number: Union[str, int],
                                   reference_type: Literal['MSISDN', 'PMSISDN', 'REQUESTID'],
                                   ) -> dict:
        """
        The purpose of this web method is to place a retrieve the query status
        of port-in Request to MNP System from external Channel(s).

        """
        body = {'REFERENCE_NUMBER': reference_number, 'REFERENCE_TYPE': reference_type}
        body = {'DETAILS': self._type_constructor.portout_request_details_type(**body)}

        response = await self.__base_request('CheckPortoutStatusOperation', body)
        return self.__prepare_result(response=response.text)

    async def do_auto_topup(self, *,
                            msisdn: Union[str, int],
                            topup_amount: Union[float, str],
                            is_auto_topup: bool,
                            balance_limit: Union[float, str],
                            max_limit: Union[float, str],
                            per_week: Union[float, str],
                            ) -> dict:
        """
        The auto top-up feature can be configured in the billing application.
        If the auto top-up feature is enabled for a subscriber and if the
        subscriber account balance reaches the configured threshold limit,
        then the billing application will perform the automatic topup, using
        the saved credit card details and triggers a notification to the
        respective subscriber. This API can be triggered to enable the auto
        top-up feature for a subscriber in the billing application. This API
        can be triggered to configure the maximum number of auto top-ups that
        can be performed for a subscriber in a week and the number of weeks
        the auto top-up process is to be performed for a subscriber. Before
        triggering this API, the subscriber must have done one online topup.
        The credit card details used for the last successful top-up
        transaction will be used for the auto top-up feature.

        Pre-requisite:
            1. For all the credit card payments, the external payment gateway
               must be integrated with the Plintron MVNE platform.
            2. The Do_Online_Topup API must be triggered before triggering the
               Do_Auto_Topup API.

        msisdn: Mobile number of subscriber (with country code)
        topup_amount: Top Up Amount Ref to GetTopUpDenomination. For Example: The currency is $ for the USA.
        is_auto_topup: Auto Top up true or false
        balance_limit: Balance limit to do auto top up.
        max_limit: Maximum no of times top up can be done based on per week.
        per_week: No of weeks max limit
        """

        body = {
            "MSISDN": msisdn,
            "TOPUP_AMOUNT": topup_amount,
            "IS_AUTO_TOPUP": is_auto_topup,
            "BALANCE_LIMIT": balance_limit,
            "MAX_LIMIT": max_limit,
            "PER_WEEK": per_week,
        }
        body = {'DETAILS': self._type_constructor.do_auto_top_up_type(**body)}

        response = await self.__base_request('DoAutoTopupOperation', body)
        return self.__prepare_result(response=response.text)

    async def do_schedule_topup(self, *,
                                request_type: Literal[0, 1],
                                msisdn: Union[str, int],
                                topup_amount: Union[float, str] = None,
                                schedule_type: Literal[0, 1] = None,
                                number_of_days: int = None,
                                start_date: str = None,
                                ) -> dict:
        """
        This API can be triggered to enable or disable the schedule top-up
        feature for a subscriber. When the schedule top-up feature is enabled
        for a subscriber, then the subscriber can define the top-up amount
        and time interval for the schedule top-up (whether the top-up is to
        be scheduled after some days or on a particular day of every month).
        Before triggering this API, the subscriber must have done one online
        topup. The credit card details used for the last successful top-up
        transaction will be used for the schedule top-up feature.

        Pre-requisite:
            1. For all the credit card payments, the external payment gateway
               must be integrated with the Plintron MVNE platform.
            2. The Do_Online_Topup API must be triggered before triggering the
               Do_Schedule_Topup API.
        """

        body = {
            "REQUEST_TYPE": request_type,
            "MSISDN": msisdn,
            "TOPUP_AMOUNT": topup_amount,
            "SCHEDULE_TYPE": schedule_type,
            "NUMBER_OF_DAYS": number_of_days,
            "START_DATE": start_date,
        }
        if request_type == 0:
            if not all(
                    (topup_amount is not None, schedule_type is not None,
                     number_of_days is not None, start_date is not None,
                     )):
                raise PlintronClientException('If request_type is 0'
                                              'topup_amount, schedule_type,'
                                              'number_of_days, start_date'
                                              'is mandatory.')

        body = {'DETAILS': self._type_constructor.do_schedule_top_up_type(**body)}

        response = await self.__base_request('DoScheduleTopupOperation', body)
        return self.__prepare_result(response=response.text)

    async def suspend_subscriber(self, *,
                                 reason_desc: str,
                                 imsi: Union[int, str, None] = None,
                                 msisdn: Union[int, str, None] = None,
                                 icc_id: Union[int, str, None] = None,
                                 ) -> dict:
        """
        The MVNO can choose to temporally suspend (stop) a subscriber from
        using some or all the network services due to a failure to pay, fraud
        or lost device. Once the condition is back to normal, the suspension
        can be reversed and the subscriber will regain full access to their
        services. The MVNO can stop all the services or only the outbound
        services are blocked and subscriber continues to receive calls and
        messages. This API can be triggered to suspend (stop) the network
        services for a subscriber in the billing application.

        reason_desc: Reason for suspending. Max 100 bytes
        """

        if not any((imsi, msisdn, icc_id)):
            raise PlintronClientException('Please supply any off: IMSI, MSISDN, ICC_ID')

        body = {'IMSI': imsi, 'MSISDN': msisdn, 'ICC_ID': icc_id}
        body_2 = {'REASON_DESC': reason_desc}

        response = await self.__base_request('SuspendSubscriberOperation', {**body, **body_2})
        return self.__prepare_result(response=response.text)

    async def do_bundle_topup(self, *,
                              msisdn: str,
                              payment_mode: Literal['0', '1', '2', '3', '4', '5', '6'],

                              imsi: str = None,
                              icc_id: str = None,

                              bundle_name: str = None,
                              bundle_code: str = None,
                              bundle_validity: str = None,
                              bundle_type: str = None,

                              actual_amount: Decimal = None,
                              discounted_price: Decimal = None,
                              prereceiver_msisdn: str = None,
                              isdisable_auto_renewel: Literal[0, 1] = None,
                              email: str = None,
                              card_details: dict = None,
                              wp_payment: dict = None,
                              ip_address: str = None,
                              card_nickname: str = None,
                              card_id: str = None,
                              tax: Decimal = None,
                              tax_id: str = None,
                              no_of_month: str = None,
                              e911_address: dict = None,
                              transaction_id: str = None,
                              vat_id: str = None,
                              is_new_card: Literal[0, 1] = None,
                              promo_code: str = None,
                              promo_type: str = None,
                              promo_discount_amount: Decimal = None,
                              special_discount_code: str = None,
                              special_discount_amount: Decimal = None,
                              payment_id: str = None,
                              apm_input_details: str = None,
                              recurring: str = None,
                              gtn: str = None,
                              session_id: str = None,
                              application_type: str = None,
                              name_or_page_id: str = None,
                              url: str = None,
                              custom_field_1: str = None,
                              custom_field_2: str = None,
                              custom_field_3: str = None,
                              fee: Decimal = None,
                              nus_flag: Literal[0, 1] = None,
                              action_type: Literal[0, 1] = None,
                              customer_consent: Literal[0, 1] = None,
                              consent_expiry_date: str = None,
                              restrict_existing_promo: Literal[0, 1] = None,
                              is_device_included: Literal['Yes', 'No'] = None,
                              product_detail: dict = None,
                              shipping_address: dict = None,
                              shipping_charge: Decimal = None,
                              medium: str = None,
                              source: str = None,
                              campaign: str = None,
                              currency_exchange: Literal[0, 1] = None,
                              purchase_type: Literal[1, 2] = None,
                              modify_bundle_code: int = None,
                              modify_bundle_installment: str = None,
                              is_multiple_bundle_purchase: Literal['true', 'false'] = None,
                              multiple_bundle_info: dict = None,
                              direct_debit: dict = None,
                              loan_recovery: dict = None,
                              campaign_flag: str = None,
                              campaign_keyword: str = None,
                              ) -> dict:
        """
        The Do Bundle Topup web method is used to do a Bundle Top-up for a
        Login User. The below sections describes the Request and Response
        details of the web method.

        Note:
            This API supports both 2D and 3D Card payment and APM Payment
            Methods. For 3D Card Payment method ECO_DATA, PAREQ, TRANSACTION_ID
            and VAT_ID are Mandatory and it is Optional for APM Payment.

        Arguments:
            msisdn: Mobile Number (With country code)
            payment_mode: Mode of Payment
                0 - Main Balance
                1 - Credit or Debit card
                2 - Pay Pal
                3 - APM
                4 - External Payment
                5 - India Payment
                6 - Direct Debit
                If Payment_Mode is account Balance, then Tax and Fee Should not be given in Input
            imsi: IMSI of the Given MSISDN
            icc_id:
            bundle_name: Name of the bundle selected by the subscriber
            bundle_code: Code of the Bundle
            bundle_validity: Validity of the Bundle in Days
            bundle_type: Type of Bundle
            actual_amount: Actual Amount are the Face Value of the Bundle (accepts
            integer and decimal)
            discounted_price: Discounted Price of the Bundle (Applicable Only for
                National and International Bundle Card base Payment and accepts
                integer and decimal)
            prereceiver_msisdn: Pre Receiver MSISDN of Subscriber (Applicable Only
                if the Bundle Type is VAS) (Mandatory if the Bundle Type is VAS)
            isdisable_auto_renewel: 0 - to disable the auto renewal.
                By default auto renewal will be activated
            email: Email of subscriber
            card_details: In case the Payment Mode is 1-Credit or Debit base
                Payment then want to send the card Details
                BLK_CardDetailsTypeO(
                    CARD_TYPE: StringTypeO,
                    NAME_ON_CARD: StringTypeO, CARD_NO: CardNoTypeO,
                    ISSUE_DATE: StringTypeO, EXPIRY_DATE: StringTypeO,
                    ISSUE_NO: StringTypeO, CVV: CVVTypeO,
                    BILLING_ADDRESS: BLK_FREESIM_ADDRESSREQO,
                    FIRST_NAME: StringLen30TypeO, LAST_NAME: StringLen30TypeO
                )
                BLK_FREESIM_ADDRESSREQO(
                    POST_CODE: StringTypeO, STREET: StringTypeO, CITY: StringTypeO,
                    COUNTRY: StringTypeO, HOUSE_NO: StringTypeO,
                    COUNTY: StringTypeO, HOUSENO_EXTN: StringTypeO,
                    APARTMENT_NO: StringTypeO, BLOCK: StringTypeO,
                    LIFT: StringTypeO, FLOOR: StringTypeO, DOOR: StringTypeO,
                    ADMINISTRATIVE_AREA: StringTypeO, NEIGHBOURHOOD: StringTypeO,
                    STREET_NUMBER: StringTypeO, C_O: StringTypeO
                )
            wp_payment: (Based on the System Configuration it will work as Mandatory/optional)
                WpPayment3DTypeO(
                    USER_AGENT_HEADER: StringTypeO, ACCEPT_HEADER: StringTypeO,
                    SESSION_ID: StringTypeO, ECO_DATA: StringTypeO,
                    PARES: StringTypeO
                )
            ip_address: IP Address
            card_nickname: Nickname of the subscriber credit card
            card_id: Unique ID of the credit card It is mandatory, when tag
                IS_NEW_CARD value is 0
            tax: Tax amount received from GetTax method. Send it as empty ("") if
                tax calculation is not required. Send it as "0.0". if tax has to
                be calculated during payment. Send the tax amount along with the
                tax id if tax is already calculated through GetTax.
            tax_id: Tax Id received from the GetTax method
            no_of_month: number of month
            e911_address: E911 Address of the Subscriber
                ExternalSocInfoTypeO(
                    ADDRESS_LINE1: StringTypeO, ADDRESS_LINE2: StringTypeO,
                    CITY: StringTypeO, STATE_CODE: StringTypeO, ZIP: StringTypeO
                )
            transaction_id: Transaction id is Optional for 3D (first Request)
                payment and it is mandatory for 3D (second Request) and External
                Payment mode.
            vat_id: Vat id is mandatory for 3D payment method.
            is_new_card:
                0 - Payment using Old card.
                (if it is 0 NameOnCard, CardNo, CVV are mandatory.)
                1 - Payment using New card. Tag value is empty consider as 1.
            promo_code: Promo Code for a particular transaction to apply for discount
            promo_type: Promo type is applied for a particular transaction to
                apply for discount. Eg : 1- Bundle Amount
            promo_discount_amount: Promo discount amount for that promo code
            special_discount_code: Special Discount Code of the subscriber
            special_discount_amount: Special Discount Amount of the Subscriber
            payment_id: Payment Id of the subscriber. This tag is Mandatory for
                Ingenico 3D payment
            apm_input_details: APM details. This tag is mandatory for APM mode of
                Payment (i.e. PAYMENT_MODE is 3)
            recurring: Recurring of the APM payment eg: true or false
                If Payment Mode = 3 and IsDisableAutorenewel tag is 1 means this
                tag mandatory
            gtn: Gateway type Name of the APM Payment. If Payment Mode = 3 means
                this tag mandatory and this required for second request.
            session_id: Session Id of the APM payment. If Payment Mode = 3 means
                this tag mandatory.
            application_type: Application Type of the request for Credit Card and
                APM Payment
            name_or_page_id: Name or PageId of the request for Credit Card and APM
                Payment
            url: Url of the request for Credit Card and APM Payment i.e In which
                page client what to land the payment response
            custom_field_1: custom field of the request for Credit Card and
                APM Payment
            custom_field_2: --//--
            custom_field_3: --//--
            fee: FEE amount details
            nus_flag: nus flag of the Subscriber
                0 - Nus Discount not applicable for the subscriber
                1 - Nus Discount applicable for the subscriber
            action_type: action type of the subscriber
                0 - Prior Renewal not applicable for the subscriber
                1 - Prior Renewal applicable for the subscriber
            customer_consent: Consent of the customer. Customer consent is Enable
                when Auto Renewal tag is available.
                0 - Disable
                1 - Enable
            consent_expiry_date: Consent expiry date of the subscriber
            restrict_existing_promo: RESTRICT_EXISTING_PROMO of the subscriber
                0 - pre applied promo for the requested product is applicable for
                    the current transaction
                1 - pre applied promo for the requested product will not be
                    applicable for the current transaction
            is_device_included: Is device included of the subscriber
                device details applicable for the USA only
            product_detail: Product detail of the customer
                ArrayOfPRODUCT_DETAILSType(PRODUCT_DETAIL: ArrayOfPRODUCTDETAILType[])
                ArrayOfPRODUCTDETAILType(
                    TYPE: IntTypeO, NAME: StringTypeO, MODEL: StringTypeO,
                    SPECIFICATION: StringTypeO, PRICE: StringTypeO,
                    TAX_DETAILS: decTypeO, FEE_DETAILS: decTypeO
                )
            shipping_address: Shipping address of the subscriber
                ArrayOfSHIPPING_ADDRESSType(
                    FIRST_NAME: StringTypeO, LAST_NAME: StringTypeO,
                    ADDRESS_LINE1: StringTypeO, ADDRESS_LINE2: StringTypeO,
                    ADDRESS_LINE3: StringTypeO, CITY: StringTypeO,
                    POST_CODE: StringTypeO, COUNTRY_CODE: StringTypeO
                )
            shipping_charge: Shipping amount for that Purchase
            medium: Medium name of the affiliate
            source: Source name of the affiliate
            campaign: Campaign name of the affiliate
            currency_exchange: Currency exchange only applicable for payment mode
                1 and 3
                0 - Standard Currency
                1 - RON Currency
            purchase_type:
                Upgrade / Downgrade Amount is Configurable in RRBS & Only that
                amount will be considered
                Upgrade or Downgrade is applicable Only for Payment Mode 0
                (Main Balance)
                1->Upgrade
                2->Downgrade
            modify_bundle_code: Bundle Code Which is already Purchased and it
                should be either Active (or) Reserved
            modify_bundle_installment: Value Should be greater than or equal to 1.
                It Should include Current & Reserved Bundle Installments.
            is multiple bundle purchase: Is multiple bundle purchase of the
                subscriber.
            is_multiple_bundle_purchase:
            multiple_bundle_info: Multiple bundle info of the subscriber
                ArrayOfMULTIPLE_BUNDLE_INFOType(BUNDLE_INPUT: BundleInputTypeO[])
                BundleInputTypeO(
                    BUNDLE_NAME: StringTypeO, BUNDLE_CODE: NumericTypeO,
                    BUNDLE_VALIDITY: NumericTypeO, IMSI: ,
                    BUNDLE_TYPE: StringTypeO, ACTUAL_AMOUNT: decTypeO,
                    DISCOUNTED_PRICE: decTypeO, ISDISABLE_AUTO_RENEWEL: ZeroorOneO,
                    BUNDLE_TAX_DETAILS: TaxDetailsTypeO, NO_OF_MONTH: NumericTypeO,
                    BUNDLE_FEE: decTypeO
                )
                TaxDetailsTypeO(TAX: decTypeO, TAX_ID: StringTypeO)
            direct_debit: Direct Debit
                ArrayOfDIRECT_DEBITType(
                    IBAN: StringTypeO, ACCOUNT_HOLDER_NAME: StringTypeO,
                    FIRST_NAME: StringTypeO, LAST_NAME: StringTypeO,
                    ADDRESS_LINE1: StringTypeO, ADDRESS_LINE2: StringTypeO,
                    ADDRESS_LINE3: StringTypeO, CITY: StringTypeO,
                    POST_CODE: StringTypeO, STATE: StringTypeO
                )
            loan_recovery: Loan recovery
                LoanRecoveryDetailesType(
                    TOPUP_AMOUNT: StringTypeO, TAX: decTypeO, FEE: decTypeO
                )
            campaign_flag: Campaign_flag Of the subscriber
            campaign_keyword: Campaign keyword Of the subscriber

        For more information see plintron API documentation.
        """

        body = {
            'IMSI': imsi, 'ICC_ID': icc_id,
            'BUNDLE_NAME': bundle_name, 'BUNDLE_CODE': bundle_code,
            'BUNDLE_VALIDITY': bundle_validity, 'BUNDLE_TYPE': bundle_type,
            'ACTUAL_AMOUNT': actual_amount, 'DISCOUNTED_PRICE': discounted_price,
            'MSISDN': msisdn, 'PRERECEIVER_MSISDN': prereceiver_msisdn,
            'PAYMENT_MODE': payment_mode, 'ISDISABLE_AUTO_RENEWEL': isdisable_auto_renewel,
            'EMAIL': email, 'CARD_DETAILS': card_details,
            'WP_PAYMENT': wp_payment, 'IP_ADDRESS': ip_address,
            'CARD_NICKNAME': card_nickname, 'CARD_ID': card_id,
            'TAX': tax, 'TAX_ID': tax_id,
            'NO_OF_MONTH': no_of_month, 'E911_ADDRESS': e911_address,
            'TRANSACTION_ID': transaction_id, 'VAT_ID': vat_id,
            'IS_NEW_CARD': is_new_card, 'PROMO_CODE': promo_code,
            'PROMO_TYPE': promo_type, 'PROMO_DISCOUNT_AMOUNT': promo_discount_amount,
            'SPECIAL_DISCOUNT_CODE': special_discount_code, 'SPECIAL_DISCOUNT_AMOUNT': special_discount_amount,
            'PAYMENT_ID': payment_id, 'APM_INPUT_DETAILS': apm_input_details,
            'RECURRING': recurring, 'GTN': gtn,
            'SESSION_ID': session_id, 'APPLICATION_TYPE': application_type,
            'NAME_OR_PAGE_ID': name_or_page_id, 'URL': url,
            'CUSTOM_FIELD_1': custom_field_1, 'CUSTOM_FIELD_2': custom_field_2,
            'CUSTOM_FIELD_3': custom_field_3, 'FEE': fee,
            'NUS_FLAG': nus_flag, 'ACTION_TYPE': action_type,
            'CUSTOMER_CONSENT': customer_consent, 'CONSENT_EXPIRY_DATE': consent_expiry_date,
            'RESTRICT_EXISTING_PROMO': restrict_existing_promo, 'IS_DEVICE_INCLUDED': is_device_included,
            'PRODUCT_DETAIL': product_detail, 'SHIPPING_ADDRESS': shipping_address,
            'SHIPPING_CHARGE': shipping_charge, 'MEDIUM': medium,
            'SOURCE': source, 'CAMPAIGN': campaign,
            'CURRENCY_EXCHANGE': currency_exchange, 'PURCHASE_TYPE': purchase_type,
            'MODIFY_BUNDLE_CODE': modify_bundle_code, 'MODIFY_BUNDLE_INSTALLMENT': modify_bundle_installment,
            'IS_MULTIPLE_BUNDLE_PURCHASE': is_multiple_bundle_purchase, 'MULTIPLE_BUNDLE_INFO': multiple_bundle_info,
            'DIRECT_DEBIT': direct_debit, 'LOAN_RECOVERY': loan_recovery,
            'CAMPAIGN_FLAG': campaign_flag, 'CAMPAIGN_KEYWORD': campaign_keyword,
        }

        body = {'DETAILS': self._type_constructor.get_type(type='DoBundleTopUpType', **body)}
        response = await self.__base_request('DoBundleTopupOperation', **body)
        return self.__prepare_result(response=response.text)

    async def initiate_portin(self, *,
                              msisdn: str,
                              icc_id: str,
                              p_msisdn: str,
                              p_icc_id: str = None,
                              donor: str = None,
                              portin_date: str = None,
                              preferred_lang: str = None,
                              ) -> object:
        """
        Arguments:
            msisdn: MSISDN of the subscriber, MSISDN should be with country
                code. For GER, AUT: MSISDN without country code
            icc_id:
            p_msisdn: Port-in MSISDN of the subscriber, PMSISDN should be with
                country code. For GER,AUT : PMSISDN without country code
            p_icc_id: Port-In ICCID of the subscriber. PICCID should be
                mandatory for specific countries. For PRT, ROM, ITA, GBR, ESP,
                NLD and DEN, IRL: P_ICC_ID Should be Mandatory.
            donor: Current Operator Code. Donor operator code is mandatory for
                all country except: MNP_GBR. Donor operator code is optional
                for GBR country
            portin_date: Target date of the Port-In Request.
                Date Format: YYYY-MM-DD
                For ITA, ESP, AUS, GER, NLD,SWI,SWE,DEN,IRL:
                PortinDate Should be Mandatory
            preferred_lang: Language of the Subscriber Eg: English
        country_specific_param:
            CountrySpecificType(({ITA: ITAParamsType}))
        Returns:
            reference to object with methods for specific countries:
            GER, GBR, AUS, NOR, PRT, FRA, ITA, NLD, BEL,
            ROM, AUT, SWE, SWI, DEN, IRL, TUN, MKD, ZAF,
            RUS

            Each method returns:
            {
                header: {
                    ERROR_CODE: ns0:HeaderErrorCodeType,
                    ERROR_DESC: ns0:HeaderErrorDescType,
                    ASYNCH_RESPONSE_INDICATOR: ns0:HeaderAsynchResponseIndicat,
                    OTP_RES_DATA: ns0:HeaderOtpResType
                },
                body: {
                    REFERENCE_CODE: ,
                    RETURN_DESC: ,
                    VALIDITY_DATETIME: VALIDITYDATETIMETypeO
                }
            }
        """

        body = {
            "MSISDN": msisdn,
            "ICC_ID": icc_id,
            "P_MSISDN": p_msisdn,
            "P_ICC_ID": p_icc_id,
            "DONOR": donor,
            "PORTIN_DATE": portin_date,
            "PREFERRED_LANG": preferred_lang,
        }

        class CountrySpecificParam:
            def __init__(self, client_self, client_body):
                self._client_self = client_self
                self._client_body = client_body

            # noinspection PyShadowingNames
            # noinspection PyProtectedMember
            async def __prepare_request(self, body: dict):
                body = {'DETAILS': self._client_self._type_constructor.get_type(
                    type='InitiatePortinDetailsType', **body
                )}
                response = await self._client_self.__base_request('InitiatePortinDetailsType', **body)
                return self._client_self.__prepare_result(response=response.text)

            async def ita(self, *,
                          credittransfer_flag: Literal['Y', 'N'],
                          prevalidation_flag: Literal['Y', 'N'],
                          theft_flag: Literal['Y', 'N'],
                          service_type: Literal['PREPAID', 'POSTPAID'],

                          customer_name: str = None,
                          customer_surname: str = None,
                          gender: str = None,
                          customer_dob: str = None,
                          customer_placeofbirth: str = None,
                          province: str = None,
                          additional1: str = None,
                          additional2: str = None,
                          document_type: Literal['CI', 'PA', 'PS'] = None,
                          document_number: str = None,
                          fiscalcode_type: Literal['TAX', 'VAT'] = None,
                          tax_or_vatno: str = None,
                          company_name: str = None,
                          portinoffer_flag: Literal['Y', 'N'] = None,
                          bundlecode: str = None,
                          bundlename: str = None,
                          bundleamount: str = None,
                          ) -> dict:
                """
                Args:
                    customer_name: Customer name of the subscriber
                        If FISCALCODE_TYPE is 'TAX', CUSTOMER_NAME is Mandatory
                    customer_surname:  Customer surname of the subscriber
                        If FISCALCODE_TYPE is 'TAX', CUSTOMER_SURNAME is
                        Mandatory
                    gender: Customer gender of the subscriber. EX: F, M
                        If FISCALCODE_TYPE is 'TAX', GENDER is Mandatory
                    customer_dob: Customer date of birth of the subscriber
                        Date Format should be 'YYYY-MM-DD'
                        If FISCALCODE_TYPE is 'TAX', CUSTOMER_DOB is Mandatory
                    customer_placeofbirth: Customer Place of birth of the
                        subscriber. If FISCALCODE_TYPE is 'TAX',
                        CUSTOMER_PLACEOFBIRTH is Mandatory
                    province: (ZipType) Customer province of the subscriber
                        If FISCALCODE_TYPE is 'TAX', PROVINCE is Mandatory
                    credittransfer_flag: Credit transfer flag. EX: Y, N
                    prevalidation_flag: Pre validation flag of the subscriber.
                        EX: Y, N
                    theft_flag: Theft flag of the subscriber. EX: Y, N
                    service_type: Service type of the subscriber.
                        EX: PREPAID, POSTPAID
                    additional1: Additional MSISDN1 of the subscriber
                    additional2: Additional MSISDN2 of the subscriber
                    document_type: Document Type of the subscriber
                        EX: CI, PA, PS
                    document_number: Document number of the subscriber
                    fiscalcode_type: Fiscal Code Type of the subscriber
                        EX: TAX, VAT
                        If FISCALCODE_TYPE is 'TAX', then CUSTOMER_NAME,
                        CUSTOMER_SURNAME, GENDER, CUSTOMER_DOB, CUSTOMER_DOB
                        CUSTOMER_PLACEOFBIRTH and PROVINCE is mandatory
                    tax_or_vatno: TAX or VAT of the subscriber
                        1. If FISCALCODE_TYPE is 'VAT',  TAX_OR_VATNO
                        2. If FISCALCODE_TYPE is 'TAX',  TAX_OR_VATNO
                        EX: TAX Code length as '16'
                            VAT Code length as '11'
                    company_name: Company name of the subscriber
                    portinoffer_flag: Y/N mandatory/non mandatory configurable
                    bundlecode: Bundle Code of the Portin bundle, mandatory if
                        port in offer is enabled
                    bundlename: Bundle Name of the Portin bundle, mandatory if
                        port in offer is enabled
                    bundleamount: Bundle Amount of the Portin bundle, mandatory
                        if port in offer is enabled
                Returns:
                    Description in parent method

                """

                # noinspection PyProtectedMember
                csp = {
                    'COUNTRY_SPECIFIC_PARAM': self._client_self._type_constructor.get_type(
                        type='CountrySpecificType',
                        **{'ITA': self._client_self._type_constructor.get_type(
                            type='ITAParamsType',
                            **{
                                'CUSTOMER_NAME': customer_name,
                                'CUSTOMER_SURNAME': customer_surname,
                                'GENDER': gender,
                                'CUSTOMER_DOB': customer_dob,
                                'CUSTOMER_PLACEOFBIRTH': customer_placeofbirth,
                                'PROVINCE': province,
                                'CREDITTRANSFER_FLAG': credittransfer_flag,
                                'PREVALIDATION_FLAG': prevalidation_flag,
                                'THEFT_FLAG': theft_flag,
                                'SERVICE_TYPE': service_type,
                                'ADDITIONAL1': additional1,
                                'ADDITIONAL2': additional2,
                                'DOCUMENT_TYPE': document_type,
                                'DOCUMENT_NUMBER': document_number,
                                'FISCALCODE_TYPE': fiscalcode_type,
                                'TAX_OR_VATNO': tax_or_vatno,
                                'COMPANY_NAME': company_name,
                                'PORTINOFFER_FLAG': portinoffer_flag,
                                'BUNDLECODE': bundlecode,
                                'BUNDLENAME': bundlename,
                                'BUNDLEAMOUNT': bundleamount,
                            }
                        )
                        },
                    )
                }
                # noinspection PyShadowingNames
                body = {**self._client_body, **csp}
                return await self.__prepare_request(body=body)

        country_specific = CountrySpecificParam(client_self=self, client_body=body)
        return country_specific

    async def modify_bucket_allowance(self, *,
                                      imsi: Union[int, str, None] = None,
                                      msisdn: Union[int, str, None] = None,
                                      icc_id: Union[int, str, None] = None,
                                      bundle_code: str = None,
                                      subs_bucket_details: list[dict] = None,
                                      # tmo_products: dict = None,  # not in documentation
                                      ) -> dict:
        """
        Args:
            imsi:
            msisdn:
            icc_id:
            bundle_code:
            subs_bucket_details:
                [
                    {
                        "BUCKET_DETAILS": {
                            "SERVICE_TYPE": RrbsServiceTypeType,
                            "BUCKET_ID": BucketIdType,
                            "OPERATION_CODE": OperationCodeType,
                            "ALLOWANCE": BalanceType
                            }
                    },
                ]
                SERVICE_TYPE (Literal[1, 2, 3, 4]):
                    1 - Voice
                    2 - SMS
                    3 - Data
                    4 - Common
                BUCKET_ID (Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]):
                    1 - offnet 1
                    2 - offnet 2
                    3 - offnet 3
                    4 - Onnet
                    5 - MT Onnet
                    6 - MT offnet
                    7 - Common
                    8 - Data
                    9 - Data Domestic Roaming
                   10 - Data International Roaming
                OPERATION_CODE (Literal[1, 2, 3]):
                    1 - replace
                    2 - add
                    3 - subtract
                ALLOWANCE (int): How much allowance needs to be
                    add / replace / subtract

        Returns:
            {
                header: {
                    ERROR_CODE: ns0:HeaderErrorCodeType,
                    ERROR_DESC: ns0:HeaderErrorDescType,
                    ASYNCH_RESPONSE_INDICATOR: ns0:HeaderAsynchResponseIndicator,
                    OTP_RES_DATA: ns0:HeaderOtpResType
                },
                body: {
                    FREE_ONNET_MINS: , FREE_ONNET_SMS: ,
                    FREE_OFFNET_MINS1: , FREE_OFFNET_SMS1: ,
                    FREE_OFFNET_MINS2: , FREE_OFFNET_SMS2: ,
                    FREE_OFFNET_MINS3: , FREE_OFFNET_SMS3: ,
                    FREE_ONNET_MT_MINS: , FREE_ONNET_MT_SMS: ,
                    FREE_OFFNET_MT_MINS: , FREE_OFFNET_MT_SMS: ,
                    FREE_DATA: , COMMON_ALLOWANCE: ,
                }
            }
        """

        if not any((imsi, msisdn, icc_id)):
            raise PlintronClientException('Please supply any off: IMSI, MSISDN, ICC_ID')

        body = {'IMSI': imsi, 'MSISDN': msisdn, 'ICC_ID': icc_id}
        body_2 = {'BUNDLE_CODE': bundle_code,
                  'SUBS_BUCKET_DETAILS': subs_bucket_details}

        response = await self.__base_request('ModifyBucketAllowanceOperation',
                                             {'_value_1': body, **body_2}
                                             )
        return self.__prepare_result(response=response.text)

    async def modify_subscriber_status(self, *,
                                       status: Literal['A', 'B', 'T', 'F'],
                                       imsi: Union[int, str, None] = None,
                                       msisdn: Union[int, str, None] = None,
                                       icc_id: Union[int, str, None] = None,
                                       reason: str = None,
                                       comments: str = None,
                                       ) -> dict:
        """
        Args:
            status:
                A - Restore suspension.
                B - Suspend the subscriber.
                T - Temporary Black Listed.
                F - Fraudulent Block.
            imsi: Either IMSI or MSISDN or ICCID is mandatory
            msisdn:
            icc_id:
            reason: Reason to perform the operation
            comments: Commets for performing the operation

        Returns:
            {
                "ENVELOPE": {
                    "HEADER": {
                        "ERROR_CODE": "0",
                        "ERROR_DESC": "Success"
                    }
                }
                "BODY": {}
            }
        """

        if not any((imsi, msisdn, icc_id)):
            raise PlintronClientException('Please supply any off: IMSI, MSISDN, ICC_ID')

        body = {'IMSI': imsi, 'MSISDN': msisdn, 'ICC_ID': icc_id}
        body_2 = {
            'STATUS': status, 'REASON': reason, 'COMMENTS': comments
        }

        response = await self.__base_request('ModifySubscriberStatusOperation',
                                             {'_value_1': body, **body_2}
                                             )
        return self.__prepare_result(response=response.text)

    async def modify_odb(self, *,
                         operation: Literal['A', 'E'],
                         values: str,
                         imsi: Union[int, str, None] = None,
                         msisdn: Union[int, str, None] = None,
                         icc_id: Union[int, str, None] = None,
                         ) -> dict:
        """This API can be triggered to block or unblock the Operator
        Determined Barring (ODB) services, provided by the network operator.
        ODB services are certain incoming or outgoing service categories,
        which a subscriber can enable or disable through any channels of the
        network operator. When this API is triggered, the required ODB
        services will be enabled or disabled in the HLR application.

        Args:
            imsi: Either IMSI or MSISDN or ICCID is mandatory
            msisdn:
            icc_id:
            operation:
            values: The list of ODB short codes separated by ','
                The values are depicted in Table: ODB Data below.

                Example:
                    values="internationalOGCallsBarred,roamingOutsidePLMNOG_CallsBarred"

                Outgoing call related
                    allOG_CallsBarred:
                        Barring outgoing calls
                    internationalOGCallsBarred:
                        Barring outgoing international calls
                    internationalOGCallsNotToHPLMN_CountryBarred:
                        Barring outgoing international calls except those
                        directed to the home PLMN country
                    roamingOutsidePLMNOG_CallsBarred:
                        Barring of outgoing calls when roaming outside the
                        home PLMN country
                    interzonalOGCallsBarred:
                        Barring of outgoing inter-zonal calls
                    interzonalOGCallsNotToHPLMN_CountryBarred:
                        Barring of outgoing inter-zonal calls except those
                        directed to the home PLMN country
                    interzonalOGCallsAndInternationalOGCallsNotToHPLMN_CountryBarred:
                        Barring of outgoing international calls except those
                        directed to the home PLMN country AND barring of
                        outgoing inter-zonal calls
                Premium Call related
                    premiumRateInformationOGCallsBarred:
                        Barring of outgoing Premium Rate Calls (Information)
                    premiumRateEntertainementOGCallsBarred:
                        Barring of outgoing Premium Rate Calls (Entertainment)
                Supplementary Services related
                    ss_AccessBarred:
                        Barring of Supplementary Services Management, which
                        prevents user control of any supplementary service
                        (registration, erasure, activation, deactivation, user
                        invocation, interrogation, password registration and
                        mobile initiated USSD). However, this does not
                        prevent invocation by other action â e.g. an existing
                        call forwarding or barring state will remain
                Call Transfer related
                    allECT_Barred:
                        Barring of invocation of call transfer
                    chargeableECT_Barred:
                        Barring of invocation of call transfer where at least
                        one of the two calls is a call charged to the served
                        subscriber; i.e. the call is either an outgoing call
                        or an incoming call when the served subscriber roams
                        outside the HPLMN
                    internationalECT_Barred:
                        Barring of invocation of call transfer where at least
                        one of the two calls is a call charged to the served
                        subscriber at international rates, i.e. the call is
                        either an outgoing international call or an incoming
                        call when the served subscriber roams outside the HPLMN
                        country
                    interzonalECT_Barred:
                        Barring of invocation of call transfer where at least
                        one of the two calls is a call charged to the served
                        subscriber at inter-zonal rates, i.e. the call is
                        either an outgoing inter-zonal call or an incoming
                        call when the served subscriber roams to a VPLMN in a
                        different zone from the HPLMN
                Call Transfer related 2
                    doublyChargeableECT_Barred:
                        Barring of invocation of call transfer where both calls
                        are calls charged to the served subscriber, i.e. both
                        calls are either outgoing calls or incoming calls when
                        the served subscriber roams outside the HPLMN
                Call Transfer related 3
                    multipleECT_Barred:
                        Barring of further invocation of call transfer if there
                        is already one ongoing transferred call for the served
                        subscriber in the serving MSC/VLR
                Packet oriented services related
                    allPacketOrientedServicesBarred:
                        bar subscribers completely from the Packet Oriented
                        Services
                    roamerAccessToHPLMN_AP_Barred:
                        bar a subscriber from requesting Packet Oriented
                        Services from access points that are within the HPLMN
                        whilst the subscriber is roaming in a VPLMN
                    roamerAccessToVPLMN_AP_Barred:
                        bar a subscriber from requesting Packet Oriented
                        Services from access points that are within the roamed
                        to VPLMN
                Incoming Calls related
                    allIC_CallsBarred:
                        Barring incoming calls
                    roamingOutsidePLMNIC_CallsBarred:
                        Barring incoming calls when roaming outside the home
                        PLMN country
                    roamingOutsidePLMNICountryIC_CallsBarred:
                        Barring incoming calls when roaming outside the zone
                        of the home PLMN country
                Roaming related:
                    roamingOutsidePLMN_Barred:
                        Barring of Roaming outside the home PLMN
                    roamingOutsidePLMN_CountryBarred:
                        Barring of Roaming outside the home PLMN country
                Call Forwarding related:
                    registrationAllCF_Barred:
                        Barring of registration of any call forwarded-to number
                    registrationCFNotToHPLMN_Barred:
                        Barring or registration of any international call
                        forwarded-to number except to a number within the HPLMN
                        country
                    registrationInterzonalCF_Barred:
                        Barring of registration of any inter-zone call
                        forwarded-to number
                    registrationInterzonalCFNotToHPLMN_Barred:
                        Barring of registration of any inter-zone call
                        forwarded-to number except to a number within the HPLMN
                        country
                    registrationInternationalCF_Barred:
                        Barring of registration of any international call
                        forwarded-to number

        Returns:
            {
                'ENVELOPE': {
                    'HEADER': {
                        'ERROR_CODE': '0',
                        'ERROR_DESC': 'Success'
                    }
                    'BODY': {
                        'MODIFY_ODB_RESPONSE': {
                            'EXP_ODB_G': 'internationalOGCallsBarred,roamingOutsidePLMNOG_CallsBarred',
                        }
                    }
                }
            }

        """

        if not any((imsi, msisdn, icc_id)):
            raise PlintronClientException('Please supply any off: IMSI, MSISDN, ICC_ID')

        body = {'IMSI': imsi, 'MSISDN': msisdn, 'ICC_ID': icc_id}
        body_2 = {
            'OPERATION': operation, 'VALUES': values
        }

        response = await self.__base_request('ModifyOdbOperation',
                                             {'_value_1': body, **body_2}
                                             )
        return self.__prepare_result(response=response.text)

    async def modify_services(self, *,
                              operation: Literal['A', 'D', 'N', 'M'],
                              service_id: Annotated[int, 'ValueRange(1, 34)'],
                              services: Union[dict, ServicesDetailsType] = None,
                              reason: str = None,
                              imsi: Union[int, str, None] = None,
                              msisdn: Union[int, str, None] = None,
                              icc_id: Union[int, str, None] = None,
                              ) -> dict:
        """
        Args:
            operation:
                A - Activate
                D - Deactivate
                N - Activate all services (except CRBT)
                M - Modify the Service related details. Added for Modifying
                    the WIFI_ADDRESS. Can be used for the similar requirements
            service_id: If OPERATION is 'N' this argument is not required
                1 - MO Call
                2 - MT Call
                3 - MO Roaming Call
                4 - MT Roaming Call
                5 - MO SMS
                6 - MT SMS
                7 - MO Roaming SMS
                8 - MT Roaming SMS
                9 - IVR
               10 - USSD
               11 - VMS
               12 - SMS Top-up
               13 - Mobile Home Account (MHA)
               20 - MO Video Call
               21 - MT Video Call
               22 - MO Roaming Video Call
               23 - MT Roaming Video Call
               24 - CRBT
               25 - MO_DATA
               26 - MO_Roaming data
               27 - CBS
               28 - VOIP
               29 - Mo 4G Data
               30 - Mo 4G Roaming Data
               31 - Premium call
               32 - Bundle Topup
               33 - Other Service
            services: Information of services to be toggled.
                ServicesDetailsType([SERVICE: ServiceInformationType])

                ServiceInformationType(
                   TYPE: SubServiceType,
                   STATUS: ,
                   VALUE: SubServiceValueType,
                   EXPIRY_DATE: ,
                   OPTIN_INFO: ServiceOptinInfo,
                   RENEWAL_PAYMENT_MODE: ,
                   AUTORENEWAL: ,
                   SUB_SERVICES: SubServicesInfoType,
                   OFFER: ServiceOfferInfoType,
                   PROVIDER: StringTypeO
                )
            reason: Reason to modify
            imsi: Either IMSI or MSISDN or ICCID is mandatory
            msisdn:
            icc_id:

        Returns:
            {
                'ENVELOPE': {
                    'HEADER': {
                        'ERROR_CODE': '0',
                        'ERROR_DESC': 'Success'
                    }
                    'BODY': {
                        'MODIFY_SERVICES_RESPONSE': {
                            'NETWORK_ID': 1
            }}}}

        """
        ModifyServicesOperationType(
            icc_id=icc_id,
            imsi=imsi,
            msisdn=msisdn,
            operation=operation,
            service_id=service_id,
            services=services,
            reason=reason,
        )
        body = {'IMSI': imsi, 'MSISDN': msisdn, 'ICC_ID': icc_id}

        if services:
            if isinstance(services, ServicesDetailsType):
                services = services.dict(exclude_unset=True)
            services = self._type_constructor.get_type(type='ServicesDetailsType',
                                                       **services)
        body_2 = {
            'OPERATION': operation,
            'SERVICE_ID': service_id,
            'SERVICES': services,
            'REASON': reason,
        }
        response = await self.__base_request('ModifyServicesOperation',
                                             {'_value_1': body, **body_2}
                                             )
        return self.__prepare_result(response=response.text)

    async def get_product_offering_details(self, *,
                                           network_id: Union[str, int],

                                           msisdn: Optional[Union[str, int]] = None,
                                           imsi: Optional[Union[str, int]] = None,
                                           icc_id: Optional[Union[str, int]] = None,

                                           offering: Optional[OfferingType] = None,
                                           product_list: Optional[ProductListType] = None,
                                           multi_product_purchase: Optional[MultiProductPurchaseType] = None,

                                           payment_mode_indicator: Optional[int] = None,
                                           action_flag: Optional[int] = None,
                                           zip_code: Optional[str] = None,
                                           area_code: Optional[str] = None,
                                           billing_zip_code: Optional[str] = None,
                                           ) -> dict:
        """
        This operation is used to fetch the offering details of the requested
        offering code.

        Arguments:
            msisdn: Either IMSI or MSISDN or ICCID is mandatory
            imsi:
            icc_id:
            offering: Requested bundle code 
                Note: As per new enhancements in this API, Either OFFERING or
                PRODUCT_LIST or MULTI _PRODUCT_PURCHASE is expected in the
                request
            product_list: As per new enhancements in this API, Either OFFERING
                or PRODUCT_LIST or MULTI _PRODUCT_PURCHASE is expected in the
                request.
            multi_product_purchase: 
            network_id: Network ID of the Bundle Code 
            payment_mode_indicator: Payment Mode by which 'Fee and Tax'
                details for the Product List/Multi Product Purchase details
            action_flag: Interface/Screen from a particular channel,
                Subscriber wishes to purchase the Product.
                Note: Tax and Fee details are dependent on this flag.
            zip_code: Zipcode of the Subscriber, in case of Subscriber
                information is not received in the request.
                Note ->
                    This tag is optional, since subscriber information is
                    mandatory in this request. This zipcode will be considered
                    only if there is no subscriber information. Hence, no
                    validation will be done in billing system whether this
                    zipcode is matching with the subscribers zipcode.
            area_code: Area Code of the Subscriber, in case of Subscriber
                information is not received in the request.
                Note ->
                    This tag is optional, since subscriber information is
                    mandatory in this request. This zipcode will be considered
                    only if there is no subscriber information. Hence, no
                    validation will be done in billing system whether this
                    zipcode is matching with the subscribers zipcode.
            billing_zip_code: Credit Card Zipcode shall be required, if the
                tax calculation to be prioritized on Billing Zipcode Over
                Subscriber Zipcode. 
                Note ->
                    Only Priority will be sent to Billing Zipcode, But based
                    on internal validations, tax calculation may switch to
                    subscriber zipcode. This will be informed to the Channel
                    by "CALCULATED_ON" parameter in response 

        Returns:
            {
                "ENVELOPE": {
                    "HEADER": {
                        "ERROR_CODE": "998",
                        "ERROR_DESC": "Unauthorized operation",
                        "ASYNCH_RESPONSE_INDICATOR": "0"
                    },
                    "BODY": {
                        "GET_PRODUCT_OFFERING_DETAILS_RESPONSE": null
                    }
                }
            }
        """

        _value_1 = {
            '_value_1': {
                "MSISDN": msisdn,
                "IMSI": imsi,
                "ICC_ID": icc_id,
            }
        }
        body = {
            "NETWORK_ID": network_id,
            "OFFERING": offering,
            "PRODUCT_LIST": product_list,
            "MULTI_PRODUCT_PURCHASE": multi_product_purchase,
            "PAYMENT_MODE_INDICATOR": payment_mode_indicator,
            "ACTION_FLAG": action_flag,
            "ZIP_CODE": zip_code,
            "AREA_CODE": area_code,
            "BILLING_ZIP_CODE": billing_zip_code,
        }
        _ = GetProductOfferingDetailsType(**body, **_value_1).dict(exclude_none=True)
        response = await self.__base_request(
            'GetProductOfferingDetailsOperation',
            {**_value_1, **body}
        )
        return self.__prepare_result(response=response.text)


async def for_ivo(client):
    ivos_list = [
        8939540000004000335,
        8939540000004000343,
        8939540000004000350,
        8939540000004000368,
        8939540000004000376,
        8939540000004000384,
    ]
    for r in ivos_list:
        result = await client.get_bundle_list(icc_id=r)
        print(r)
        print(json.dumps(result, indent=4))
        print()


async def register_subscriber_example():

    # c = PlintronClient('svc_services/services/controllers/plintron_client/ITGAPI.wsdl')
    # wsdl = Path(Path(__file__).parent ,'/ITGAPI.wsdl').resolve(strict=True)

    current_file_folder = os.path.dirname(os.path.realpath(__file__))
    wsdl = current_file_folder+'/ITGAPI.wsdl'

    c = PlintronClient(wsdl)

    ivos_list = [
        8939540000004000335,
        8939540000004000343,
        8939540000004000350,
        8939540000004000368,
        8939540000004000376,
        8939540000004000384,
    ]

    icc_id = 893954_000000_4000_111
    icc_id = 8939540000004000350 # ?
    icc_id = 8939540000004000467

    result = await c.italy_get_subscriber_details(icc_id=icc_id)

    result = await c.get_account_details(icc_id=icc_id)

    msisdn = "39" + result['MSISDN']
    primary_imsi = result['PRIMARY_IMSI']       # 22254_00004_00011
    seconda_imsi = result['SECONDARY_IMSI']     # 20404_77914_00011

    # msisdn = "39" + "3760400011"
    # primary_imsi = 22254_00004_00011
    # seconda_imsi = 20404_77914_00011

    result = await c.italy_register_subscriber(
        icc_id=icc_id,
        msisdn='393760400018',
        preferred_language='toki pona',
        title='general',
        last_name='Reiterer',
        first_name='Robert',
        gender='Male',
        date_of_birth='22/09/1959',
        place_of_birth='MERANO .MERAN.',
        province='far',
        email_id='john.doe@gmail.com',
        alternative_contact_number='393760400046',
        residence_country='Italy',
        italy_national='Yes',
        nationality='Unknown',
        house_number=11,
        house_name='TheHouse',
        post_code=432048,
        street='OneStreet',
        city='City Name',
        state='Good One State',
        tax_code="RTRRRT59P22F132U",
        vat_number='321',
        document_type='ITALIAN_ID_CARD',
        document_number='AX4266611',
        issuer='Comune di Avelengo',
        date_of_issue='18/07/2022',
        valid_till='22/09/2028',
        list_of_attachments=[
            {
                'EXTENSION': 'pdf',
                'VALUE': 'JVBERi0xLjQKJf////8KNTAgMCBvYmoKPDwvTGVuZ3RoIDI0NzYKL1N1YnR5cGUgL1hN'
                         'TAovVHlwZSAvTWV0YWRhdGEKPj4Kc3RyZWFtCjw/eHBhY2tldCBiZWdpbj0n77u/JyBp'
                         'ZD0nVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkJz8+Cjx4OnhtcG1ldGEgeDp4bXB0az0i'
                         'My4xLTcwMSIgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iPgogIDxyZGY6UkRGIHhtbG5z'
                         'OnJkZj0iaHR0cDovL3d3dy53My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4LW5zIyI+'
                         'CiAgICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIiB4bWxuczp4bXA9Imh0dHA6'
                         'Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iPgogICAgICA8eG1wOkNyZWF0ZURhdGU+MjAx'
                         'NS0xMi0zMVQwNzo0NDozOVo8L3htcDpDcmVhdGVEYXRlPgogICAgICA8eG1wOkNyZWF0'
                         'b3JUb29sPk5pdHJvIFBybyA3ICAoNy4gMi4gMC4gMTIpPC94bXA6Q3JlYXRvclRvb2w+'
                         'CiAgICAgIDx4bXA6TW9kaWZ5RGF0ZT4yMDE1LTEyLTMxVDA3OjQ0OjQxWjwveG1wOk1v'
                         'ZGlmeURhdGU+CiAgICAgIDx4bXA6TWV0YWRhdGFEYXRlPjIwMTUtMTItMzFUMDc6NDQ6'
             },
            {
                'EXTENSION': 'pdf',
                'VALUE': 'JVBERi0xLjQKJf////8KNTAgMCBvYmoKPDwvTGVuZ3RoIDI0NzYKL1N1YnR5cGUgL1hN'
                         'TAovVHlwZSAvTWV0YWRhdGEKPj4Kc3RyZWFtCjw/eHBhY2tldCBiZWdpbj0n77u/JyBp'
                         'ZD0nVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkJz8+Cjx4OnhtcG1ldGEgeDp4bXB0az0i'
                         'My4xLTcwMSIgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iPgogIDxyZGY6UkRGIHhtbG5z'
                         'OnJkZj0iaHR0cDovL3d3dy53My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4LW5zIyI+'
                         'CiAgICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIiB4bWxuczp4bXA9Imh0dHA6'
                         'Ly9ucy5hZG9iZS5jb20veGFwLzEuMC8iPgogICAgICA8eG1wOkNyZWF0ZURhdGU+MjAx'
                         'NS0xMi0zMVQwNzo0NDozOVo8L3htcDpDcmVhdGVEYXRlPgogICAgICA8eG1wOkNyZWF0'
                         'b3JUb29sPk5pdHJvIFBybyA3ICAoNy4gMi4gMC4gMTIpPC94bXA6Q3JlYXRvclRvb2w+'
                         'CiAgICAgIDx4bXA6TW9kaWZ5RGF0ZT4yMDE1LTEyLTMxVDA3OjQ0OjQxWjwveG1wOk1v'
                         'ZGlmeURhdGU+CiAgICAgIDx4bXA6TWV0YWRhdGFEYXRlPjIwMTUtMTItMzFUMDc6NDQ6'
             }
        ],
        retailer_name='retailer_name',
        retailerid='123abc',
        chk_sms_marketing=1,
        chk_terms='true',
        chk_photocopy='true',
        chk_age='true',
        sms_update='true',
        dynamic_allocation_status=1,
        ivrlanguage='en',
        comune_code='F132',
    )
    try:
        x = json.dumps(result, indent=4)
    except Exception as e:
        raise
    print(x)


class IntService:
    def __init__(self, plintron_controller, int_operation, services: dict = None):
        self._int_operation = int_operation
        self._pc = plintron_controller
        self._service_id = None
        self._services = services

    async def _exec(self):
        return await self._pc._modify_services(
            operation=self._int_operation,
            service_id=self._service_id,
            services=self._services,
            reason='test',
        )

    def mo_call(self):
        self._service_id = 1
        return self._exec()

    def mt_call(self):
        self._service_id = 2
        return self._exec()

    def mo_roaming_call(self):
        self._service_id = 3
        return self._exec()

    def mt_roaming_call(self):
        self._service_id = 4
        return self._exec()

    def mo_sms(self):
        self._service_id = 5
        return self._exec()

    def mt_sms(self):
        self._service_id = 6
        return self._exec()

    def mo_roaming_sms(self):
        self._service_id = 7
        return self._exec()

    def mt_roaming_sms(self):
        self._service_id = 8
        return self._exec()

    def ivr(self):
        self._service_id = 9
        return self._exec()

    def ussd(self):
        self._service_id = 10
        return self._exec()

    def vms(self):
        self._service_id = 11
        return self._exec()

    def topup(self):
        """SMS top-up"""
        self._service_id = 12
        return self._exec()

    def mha(self):
        """Mobile home account"""
        self._service_id = 13
        return self._exec()

    def mo_video_call(self):
        self._service_id = 20
        return self._exec()

    def mt_video_call(self):
        self._service_id = 21
        return self._exec()

    def mo_roaming_video_call(self):
        self._service_id = 22
        return self._exec()

    def mt_roaming_video_call(self):
        self._service_id = 23
        return self._exec()

    def mca(self):
        """Not implemented"""
        raise NotImplemented('')

    def crbt(self):
        self._service_id = 24
        return self._exec()

    def mo_data(self):
        self._service_id = 25
        return self._exec()

    def mo_roaming_data(self):
        self._service_id = 26
        return self._exec()

    def ussd_call_back(self):
        self._service_id = 27
        return self._exec()

    def voip(self):
        self._service_id = 28
        return self._exec()

    def mo_4g_data(self):
        self._service_id = 29
        return self._exec()

    def mo_4g_roaming_data(self):
        self._service_id = 30
        return self._exec()

    def premium_call(self):
        self._service_id = 31
        return self._exec()

    def bundle_topup_indicator(self):
        self._service_id = 32
        return self._exec()

    def custom(self, service_id):
        """
        value '19' does not match regular expression facet
        1|2|3|4|5|6|7|8|9|10|11|12|13|20|21|22|23|24|25|26|27|28|29|30|31|32|33
        """
        self._service_id = service_id
        return self._exec()


class IntOperation:

    def __init__(self, plintron_controller):
        self._pc = plintron_controller
        self._operation = None

    def _create_int_service(self) -> IntService:
        return IntService(plintron_controller=self._pc, int_operation=self._operation)

    def activate(self, services: dict = None) -> IntService:
        self._operation = 'A'
        return self._create_int_service()

    def deactivate(self, services: dict = None) -> IntService:
        self._operation = 'D'
        return self._create_int_service()

    def activate_all(self, services: dict = None) -> IntService:
        self._operation = 'N'
        return self._create_int_service()

    def modify(self, services: dict = None) -> IntService:
        self._operation = 'M'
        return self._create_int_service()


class SimClient:
    def __init__(self, icc_id, client):
        self._icc_id = icc_id
        self._client: PlintronClient = client
        self._last_result = None
        self._print_last_result = True

    def __call__(self, icc_id):
        self._icc_id = icc_id
        return self

    def print_last_result(self):
        self._print_last_result = not self._print_last_result

    def print(self):
        if self._last_result:
            print(json.dumps(obj=self._last_result, indent=4))
        else:
            print(self._last_result)

    def _prepare_result(self, result: dict, keys: Union[list, tuple, set]) -> dict:
        print_all = not keys
        self._last_result = {k: v for k, v in result.items() if k in keys or print_all}

        if self._print_last_result:
            self.print()
        return self._last_result
    
    async def get_account_details(self, short=True):
        keys = (
            'ICC_ID',
            'MSISDN',
            'PRIMARY_IMSI',
            'SECONDARY_IMSI',
            'CURRENT_BALANCE',
            'LIFE_CYCLE_STATE',
            'IS_SUBSCRIBER_REGISTERED',
        )
        result = await self._client.get_account_details(icc_id=self._icc_id)

        return self._prepare_result(result=result, keys=keys if short else [])

    async def modify_balance(self, amount: Union[int, float]):
        operation = 'A' if amount > 0 else 'S'

        # noinspection PyTypeChecker
        result = await self._client.modify_balance(icc_id=self._icc_id,
                                                   amount=abs(amount),
                                                   operation=operation
                                                   )
        return self._prepare_result(result=result, keys=[])
    
    async def get_bundle_free_usage_info(self, bundle_code):
        result = await self._client.get_bundle_free_usage_info(icc_id=self._icc_id, bundle_code=bundle_code)

        return self._prepare_result(result=result, keys=[])

    async def get_bundle_list(self):
        result = await self._client.get_bundle_list(icc_id=self._icc_id)

        return self._prepare_result(result=result, keys=[])

    async def italy_get_subscriber_details(self):
        result = await self._client.italy_get_subscriber_details(icc_id=self._icc_id)

        return self._prepare_result(result=result, keys=[])

    async def subscribe_bundle(self, bundle_code):
        result = await self._client.subscribe_bundle(icc_id=self._icc_id,
                                                     bundle_code=bundle_code
                                                     )
        return self._prepare_result(result=result, keys=[])

    async def cancel_bundle(self, bundle_code):
        result = await self._client.cancel_bundle(icc_id=self._icc_id,
                                                  bundle_code=bundle_code,
                                                  forcible_bundle_cancellation=1,
                                                  )
        return self._prepare_result(result=result, keys=[])

    async def reactivate_subscriber(self, reason_desc='OK'):
        result = await self._client.reactivate_subscriber(icc_id=self._icc_id,
                                                          reason_desc=reason_desc,
                                                          )
        return self._prepare_result(result=result, keys=[])

    async def deactivate_subscriber(self, reason_desc='NG'):
        result = await self._client.deactivate_subscriber(icc_id=self._icc_id,
                                                          reason_desc=reason_desc,
                                                          )
        return self._prepare_result(result=result, keys=[])

    async def suspend_subscriber(self, reason_desc='NG'):
        result = await self._client.suspend_subscriber(icc_id=self._icc_id,
                                                       reason_desc=reason_desc,
                                                       )
        return self._prepare_result(result=result, keys=[])

    async def get_transaction_history(self):
        result = await self._client.get_transaction_history(icc_id=self._icc_id,
                                                            topup_type=2,
                                                            )
        return self._prepare_result(result=result, keys=[])

    async def get_call_history(self, year, month):
        self._print_last_result = False
        msisdn = (await self.get_account_details())['MSISDN']
        self._print_last_result = True
        result = await self._client.get_call_history(msisdn=msisdn,
                                                     year=year,
                                                     month=month,
                                                     )
        return self._prepare_result(result=result, keys=[])

    async def get_service_info(self, short=True):
        keys = ("SERVICE_INFO",)
        result = await self._client.get_service_info(icc_id=self._icc_id)

        return self._prepare_result(result=result, keys=keys if short else [])

    async def _modify_services(
        self,
        operation: Literal['A', 'D', 'N', 'M'],
        service_id: Annotated[int, 'ValueRange(1, 34)'],
        services: Union[dict, ServicesDetailsType] = None,
        reason: str = 'test',
        short=True,
        keys=(),
    ):
        result = await self._client.modify_services(
            icc_id=self._icc_id,
            operation=operation,
            service_id=service_id,
            services=services,
            reason=reason
        )

        return self._prepare_result(result=result, keys=keys if short else [])

    def modify_services(self, short=True) -> IntOperation:
        """
        operation: Literal['A', 'D', 'N', 'M'],
        service_id: Annotated[int, 'ValueRange(1, 34)'],
        services: Union[dict, ServicesDetailsType] = None,
        reason: str = None,
        """
        return IntOperation(plintron_controller=self)

    async def get_product_offering_details(self, short=True):
        keys = ("SERVICE_INFO",)
        result = await self._client.get_product_offering_details(
            icc_id=self._icc_id,
            network_id=8,
        )

        return self._prepare_result(result=result, keys=keys if short else [])


async def main():
    # os.environ['USE_PLINTRON_MOCK'] = '1'

    c = PlintronClient('tshared_src/tshared/utils/plintron_client/ITGAPI.wsdl')
    result_dump_file = Path(Path(__file__).parent, 'plintron_client_response.json')

    # icc_id = 8939540000004000459
    msisdn = '06' + '3760400045'
    msisdn = '39' + '3760400045'
    msisdn = '3760400045'
    imsi_primar = 22254_00004_00045
    imsi_second = 20404_77914_00045

    # icc_id = 8939540000004000467  # Igor's sim
    msisdn = "39" + "3760400046"
    primary_imsi = 22254_00004_00046
    seconda_imsi = 20404_77914_00046
    # icc_id = 8939540000004000475    # Slobodan's sim

    # icc_id = 893954_000000_4000_202
    icc_id = 893954_000000_4000_111
    icc_id = 8939540000004000111
    # msisdn = 3760400011
    # primary_imsi = 22254_00004_00011
    # seconda_imsi = 20404_77914_00011
    # icc_id = 8939540000004000186

    ivos_list = [
        8939540000004000335,
        8939540000004000343,
        8939540000004000350,
        8939540000004000368,
        8939540000004000376,
        8939540000004000384,
    ]

    icc_id_0 = 8939540000004000178
    icc_id_1 = 8939540000004000186
    icc_id_2 = 8939540000004000194

    s = SimClient(icc_id=icc_id, client=c)

    # await s.get_account_details()
    # await s.get_transaction_history()
    # await s.get_call_history(year=2022, month='08')
    # await s.italy_get_subscriber_details()
    # await s.subscribe_bundle(bundle_code=8001)
    # await s.subscribe_bundle(bundle_code=8002)
    # await s.subscribe_bundle(bundle_code=8003)
    # await s.cancel_bundle(bundle_code=8003)
    # await s.modify_balance(amount=100)

    # await s.modify_services().activate().mo_call()
    # await s.modify_services().activate().mt_call()
    # await s.modify_services().activate().mo_roaming_call()
    # await s.modify_services().activate().mt_roaming_call()
    # await s.modify_services().activate().mo_sms()
    # await s.modify_services().activate().mt_sms()
    # await s.modify_services().activate().mo_roaming_sms()
    # await s.modify_services().activate().mt_roaming_sms()
    # await s.modify_services().activate().ivr()
    # await s.modify_services().activate().ussd()
    # await s.modify_services().activate().vms()
    # await s.modify_services().activate().topup()
    # await s.modify_services().activate().mha()
    # await s.modify_services().activate().mo_video_call()
    # await s.modify_services().activate().mt_video_call()
    # await s.modify_services().activate().mo_roaming_video_call()
    # await s.modify_services().activate().mt_roaming_video_call()
    # await s.modify_services().deactivate().mca()        # not implemented

    # await s.modify_services().activate().crbt()
    # await s.modify_services().activate().mo_data()
    # await s.modify_services().activate().mo_roaming_data()
    # await s.modify_services().activate().ussd_call_back()
    # await s.modify_services().activate().voip()

    # await s.modify_services().activate().mo_4g_data()
    # await s.modify_services().activate().mo_4g_roaming_data()
    # await s.modify_services().activate().premium_call()     # does not work
    # await s.modify_services().activate().bundle_topup_indicator()
    # await s.modify_services().activate().custom(27)
    # await s.get_service_info(short=False)
    await s.get_product_offering_details(short=False)


if __name__ == '__main__':
    # asyncio.run(example(wsdl_file=WSDL_FILE))
    asyncio.run(main())

    # asyncio.run(register_subscriber_example())
