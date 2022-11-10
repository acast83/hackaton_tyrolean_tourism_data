from typing import Literal, Union, Optional
from pydantic import Field, validator
import json

from tshared.utils.plintron_client.plintron_types.base_plintron_model import BasePlintronModel


__all__ = [
    "ServiceOfferInfoType",
    "SubServiceInfoType",
    "SubServicesInfoType",
    "ServiceOptinInfo",
    "E911AddressType",
    "SubServiceValueType",
    "ServiceInformationType",
    "ServicesDetailsType",
    "ModifyServicesOperationType",
]


class ServiceOfferInfoType(BasePlintronModel):
    """
    ServiceOfferInfoType(
        CODE: OfferCodeType,
        NAME: StringTypeO,
    )
    """

    code: str
    name: Optional[str]


class SubServiceInfoType(BasePlintronModel):
    """
    SubServiceInfoType(
        TYPE: SubServiceSubCategoryType,
        ({ACTION: Value1or2Type} | {STATUS: Value0or1Type}),
    )
    """

    type: Literal['ONNET', 'OFFNET', 'MNO', 'INTERNATIONAL']
    action: Literal[1, 2, '1', '2'] = None
    status: Literal[0, 1, '0', '1'] = None

    @classmethod
    @validator('action', 'status')
    def validate_sim_card_info_2(cls, v, values, field):
        def is_both_assigned(first, second) -> bool:
            return (field.name == first
                    and second in values)

        def is_both_nones(first, second) -> bool:
            # noinspection PyShadowingNames
            def is_other_none(first, second) -> bool:
                return (is_both_assigned(first, second)
                        and v is None
                        and values[second] is None)
            return (is_other_none(first, second)
                    or is_other_none(second, first))

        def is_both_set(first, second) -> bool:
            # noinspection PyShadowingNames
            def is_other_set(first, second) -> bool:
                return (is_both_assigned(first, second)
                        and (values[second] is not None
                             and v is not None))

            return (is_other_set(first, second)
                    or is_other_set(second, first))

        if is_both_set('action', 'status'):
            raise ValueError('Both set')

        if is_both_nones('action', 'status'):
            raise ValueError('Both nones')

        return v


class SubServicesInfoType(BasePlintronModel):
    """
    SubServicesInfoType(
        [SUB_SERVICE: SubServiceInfoType]
    )

    <xs:complexType name="SubServicesInfoType">
      <xs:sequence minOccurs="0" maxOccurs="4">
        <xs:element name="SUB_SERVICE" type="SubServiceInfoType" minOccurs="0"/>
      </xs:sequence>
    </xs:complexType>
    """
    sub_service: Optional[Union[SubServiceInfoType,
                                list[SubServiceInfoType]
                                ]] = Field(default=[],
                                           alias='SUB_SERVICE')


class ServiceOptinInfo(BasePlintronModel):
    """
    ServiceOptinInfo(
        TYPE: ServiceOptionType,
        NAME: ,
    )
    """
    type: Literal['BUNDLE', 'TOPUP', 'SLOT']
    name: Optional[str]


class E911AddressType(BasePlintronModel):
    """
    E911ADDRESS_INFO(
        ADDRESSLINE1: NameType,
        ADDRESSLINE2: NameType,
        CITY: NameType,
        STATECODE: StateCodeType,
        ZIP: ZipCodeType,
    )
    """

    addressline1: str
    addressline2: Optional[str]
    city: str = Field(alias='CITY')
    statecode: str = Field(alias='STATECODE')
    zip: str = Field(alias='ZIP')


class SubServiceValueType(BasePlintronModel):
    """
    SubServiceValueType(
        E911ADDRESS: E911ADDRESS_INFO
    )
    """
    e911address: Optional[E911AddressType]


class ServiceInformationType(BasePlintronModel):
    """
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
        PROVIDER: StringTypeO,
    )
    """

    type: Literal['WIFI_ADDRESS', 'MO_CALL', 'MO_SMS', 'ACR']
    status: Optional[Literal[0, 1, '0', '1']]
    value: Optional[SubServiceValueType]
    expiry_date: Optional[str]
    optin_info: Optional[ServiceOptinInfo]
    renewal_payment_mode: Optional[Literal[0, 1, '0', '1']]
    autorenewal: Optional[Literal[0, 1, '0', '1']]
    sub_services: Optional[SubServicesInfoType]
    offer: Optional[ServiceOfferInfoType]
    provider: Optional[str]


class ServicesDetailsType(BasePlintronModel):
    """
    ServicesDetailsType(
        [SERVICE: ServiceInformationType]
    )
    """
    service: Optional[Union[ServiceInformationType,
                            list[ServiceInformationType]]] = Field(default=[],
                                                                   alias='SERVICE')


class ModifyServicesOperationType(BasePlintronModel):
    """
    ModifyServicesOperation(
        ({MSISDN: MSISDNType} | {IMSI: IMSIType} | {ICC_ID: ICCIDType})[],
        OPERATION: OperationType,
        SERVICE_ID: ServiceIdRestType,
        SERVICES: ServicesDetailsType,
        REASON: a,
    )

    """

    msisdn: Optional[Union[str, int]]
    imsi: Optional[Union[str, int]]
    icc_id: Optional[Union[str, int]]
    operation: Literal['A', 'D', 'N', 'M']
    service_id: Optional[Union[str, int]]
    services: Optional[ServicesDetailsType]
    reason: Optional[str]

    @classmethod
    @validator('service_id')
    def validate_service_id(cls, v):
        if v is not None:
            v = int(v)
            if not (1 <= v <= 33):
                raise ValueError('Service Id should be between 1 and 33 included both sides.')
        return v


if __name__ == "__main__":
    test = {
      "MSISDN": "9600050200",
      "OPERATION": "A",
      "SERVICE_ID": "33",
      "SERVICES": {
        "SERVICE": {
          "TYPE": "WIFI_ADDRESS",
          "VALUE": {
            "E911ADDRESS": {
              "ADDRESSLINE1": "1 RAVINIA DR",
              "ADDRESSLINE2": "sample street",
              "CITY": "ATLANTA",
              "STATECODE": "GA",
              "ZIP": "30346"
            }
          },
          "RENEWAL_PAYMENT_MODE": "0",
          "AUTORENEWAL": "1"
        }
      }
    }
    test_2 = {
      "MSISDN": "9600050200",
      "OPERATION": "A",
      "SERVICE_ID": "28",
    }
    a = ModifyServicesOperationType(**test)
    b = ModifyServicesOperationType(**test_2)
    c = ModifyServicesOperationType(
        icc_id='123',
        operation='A', service_id='1',
        services=ServicesDetailsType(service=[
                    ServiceInformationType(
                        type='WIFI_ADDRESS', status='1',
                        value=SubServiceValueType(
                            e911address=E911AddressType(
                                addressline1='one', addressline2='two',
                                city='three', statecode='four', zip='five',
                            )
                        ),
                        expiry_date='123qwe',
                        optin_info=ServiceOptinInfo(type='BUNDLE', name='hello'),
                        renewal_payment_mode=1,
                        autorenewal=1,
                        sub_services=SubServicesInfoType(
                            sub_service=[
                                SubServiceInfoType(type='ONNET', action=1)
                            ]
                        ),
                        offer=ServiceOfferInfoType(code='123', name='my_name'),
                        provide='qwe2',
                    )
                ],
        ),
        reason='foobar'
    )
    result = a.dict(by_alias=True)
    print(json.dumps(result, indent=2))
