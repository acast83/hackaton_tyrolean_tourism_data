from typing import Literal, Union, Optional
from decimal import Decimal

from tshared.utils.plintron_client.plintron_types.base_plintron_model import BasePlintronModel
from tshared.utils.plintron_client.plintron_types.sid_range_data_type import SIDRangeDataType


__all__ = [
    "ActivateSubscriberRequestType",
    "SubscriberInfoType",
    "ActivateSubscriberResponseType",
    "MultiTransactionActivateSubscriberRequestType",
    "BulkApiActivateSubscriberRequest",
    "BulkApiActivateSubscriberResponse",
]


Balance = Union[int, float, Decimal]
Flag = Union[Literal[0, 1, '0', '1'], bool]


class ActivateSubscriberRequestType(BasePlintronModel):
    """
    <xs:complexType name="ActivateSubscriberRequestType">
      <xs:sequence>
        <xs:choice minOccurs="1" maxOccurs="3">
           <xs:element name="MSISDN" type="MSISDNType"/>
           <xs:element name="IMSI" type="IMSIType"/>
           <xs:element name="ICC_ID" type="ICCIDType"/>
           <xs:element name="SID_RANGE" type="SIDRangeDataType" />
        </xs:choice>
        <xs:element name="TARIFF_PLAN_ID" type="IdType"/>
        <xs:element name="BALANCE" type="BalanceType"/>
        <xs:element name="LANGUAGE_ID" type="LanguageIdType"/>
        <xs:element name="RESELLER_ID" type="NameType" minOccurs="0" nillable="true"/>
        <xs:element name="POSTPAID_FLAG" type="FlagType" minOccurs="0" nillable="true"/>
        <xs:element name="TEMPLATE_ID" type="NumberLen5Type" minOccurs="0" />
        <xs:element name="CHANNEL_PARTNER_ID" type="NameLen50TypeO" minOccurs="0" />
        <xs:element name="PROP_PRESET_FLAG" type="Value0or1TypeO" minOccurs="0" />
        <xs:element name="ATR_ID" type="NameLen50TypeO" minOccurs="0" />
      </xs:sequence>
    </xs:complexType>
    """

    msisdn: Optional[Union[str, int]]
    imsi: Optional[Union[str, int]]
    icc_id: Optional[Union[str, int]]
    sid_range: Optional[SIDRangeDataType]

    tariff_plan_id: int
    balance: Balance
    language_id: int

    reseller_id: Optional[str]
    postpaid_flag: Optional[Flag]
    template_id: Optional[int]
    channel_partner_id: Optional[str]
    prop_preset_flag: Optional[Flag]
    atr_id: Optional[str]


class SubscriberInfoType(BasePlintronModel):
    """
    <xs:complexType name="SubscriberInfoType">
        <xs:sequence minOccurs="0">
            <xs:element name="MSISDN" type="MSISDNTypeO"/>
            <xs:element name="ICC_ID" type="ICCIDTypeO"/>
            <xs:element name="PRIMARY_IMSI" type="IMSITypeO"/>
            <xs:element name="SECONDARY_IMSI" type="IMSITypeO"/>
            <xs:any namespace="##any" processContents="skip" minOccurs="0" maxOccurs="unbounded"/>
        </xs:sequence>
    </xs:complexType>
    """
    msisdn: Optional[Union[int, str]]
    icc_id: Optional[Union[int, str]]
    primary_imsi: Optional[Union[int, str]]
    secondary_imsi: Optional[Union[int, str]]


class ActivateSubscriberResponseType(BasePlintronModel):
    """
    <xs:element name="ACTIVATE_SUBSCRIBER_RESPONSE">
      <xs:complexType>
        <xs:sequence minOccurs="0">
          <xs:element name="NETWORK_ID" type="NetworkIdTypeO" minOccurs="1" />
          <xs:element name="SUBSCRIBER_DETAILS" type="SubscriberInfoType" minOccurs="1"/>
          <xs:any namespace="##any" processContents="skip" minOccurs="0" maxOccurs="unbounded"/>
        </xs:sequence>
      </xs:complexType>
    </xs:element>
    """
    network_id: int
    subscriber_details: Optional[SubscriberInfoType]


class MultiTransactionActivateSubscriberRequestType(BasePlintronModel):
    """
    <xs:complexType name="MultiTransactionActivateSubscriberRequestType">
        <xs:sequence>
            <xs:element name="TRANSACTION" type="ActivateSubscriberRequestType"   minOccurs="1" maxOccurs="1000" />
        </xs:sequence>
    </xs:complexType>
    """
    transaction = list[ActivateSubscriberRequestType]


class BulkApiActivateSubscriberRequest(BasePlintronModel):
    """
    <xs:element name="BULK_API_ACTIVATE_SUBSCRIBER_REQUEST">
        <xs:complexType>
            <xs:sequence>
                <xs:choice minOccurs="1" maxOccurs="1">
                    <xs:element name="MULTIPLE_TRANSACTIONS" type="MultiTransactionActivateSubscriberRequestType" />
                    <xs:element name="RANGE_TRANSACTION" type="ActivateSubscriberRequestType" />
                </xs:choice>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
    """
    multiple_transactions: Optional[MultiTransactionActivateSubscriberRequestType]
    range_transaction: Optional[ActivateSubscriberRequestType]


class BulkApiActivateSubscriberResponse(BasePlintronModel):
    """
    <xs:element name="BULK_API_ACTIVATE_SUBSCRIBER_RESPONSE">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="JOB_ID" type="xs:string" />
            </xs:sequence>
        </xs:complexType>
    </xs:element>
    """
    job_id = list[str]


if __name__ == "__main__":
    multiple_transactions = {
        "MULTIPLE_TRANSACTIONS": {
            "TRANSACTION": [
                {
                    "MSISDN": "9600050200",
                    "TARIFF_PLAN_ID": "1132",
                    "BALANCE": "120",
                    "LANGUAGE_ID": "2",
                    "POSTPAID_FLAG": "0",
                    "TEMPLATE_ID": "565"
                },
                {
                    "MSISDN": "9600050201",
                    "TARIFF_PLAN_ID": "1143",
                    "BALANCE": "104",
                    "LANGUAGE_ID": "2",
                    "POSTPAID_FLAG": "0",
                    "TEMPLATE_ID": "566"
                },
                {
                    "MSISDN": "9600050202",
                    "TARIFF_PLAN_ID": "1344",
                    "BALANCE": "900",
                    "LANGUAGE_ID": "2",
                    "POSTPAID_FLAG": "0",
                    "TEMPLATE_ID": "567"
                }
            ]
        }
    }
    _ = BulkApiActivateSubscriberRequest(**multiple_transactions)

    range_transaction = {
        "RANGE_TRANSACTION": {
            "SID_RANGE": {
                "IMSI_RANGE": {
                    "RANGE": {
                        "FROM": "123456789098765",
                        "TO": "123456789098865"
                    }
                }
            },
            "TARIFF_PLAN_ID": "1",
            "BALANCE": "2",
            "LANGUAGE_ID": "1",
            "RESELLER_ID": "3",
            "POSTPAID_FLAG": "0",
            "TEMPLATE_ID": "567"
        }
    }
    _ = BulkApiActivateSubscriberRequest(**range_transaction)

    imsi_list = {
        "MULTIPLE_TRANSACTIONS": {
            "TRANSACTION": {
                "SID_RANGE": {
                    "IMSI_LIST": {
                        "IMSI": [
                            "123456789098765",
                            "111111111123456",
                            "222222222209875"
                        ]
                    }
                },
                "TARIFF_PLAN_ID": "1",
                "BALANCE": "2",
                "LANGUAGE_ID": "1",
                "RESELLER_ID": "3",
                "POSTPAID_FLAG": "0",
                "TEMPLATE_ID": "567"
            }
        }
    }
    _ = BulkApiActivateSubscriberRequest(**imsi_list)

    range_transaction_2 = {
        "BULK_API_ACTIVATE_SUBSCRIBER_REQUEST": {
            "RANGE_TRANSACTION": {
                "SID_RANGE": {
                    "IMSI_RANGE": {
                        "RANGE": {
                            "FROM": "12345678912345",
                            "TO": "12345678913344"
                        }
                    }
                },
                "REASON_DESC": "test"
            }
        }
    }
    _ = BulkApiActivateSubscriberRequest(**range_transaction_2)

    list_of_transactions = {
        "TRANSACTION": [
            {
                "MSISDN": "9600050200",
                "TARIFF_PLAN_ID": "1134",
                "BALANCE": "100",
                "LANGUAGE_ID": "2",
                "POSTPAID_FLAG": "0"
            },
            {
                "MSISDN": "9600050201",
                "TARIFF_PLAN_ID": "1144",
                "BALANCE": "100",
                "LANGUAGE_ID": "2",
                "POSTPAID_FLAG": "0"
            },
            {
                "MSISDN": "9600050202",
                "TARIFF_PLAN_ID": "1344",
                "BALANCE": "100",
                "LANGUAGE_ID": "2",
                "POSTPAID_FLAG": "0"
            },
            {
                "MSISDN": "9600050203",
                "TARIFF_PLAN_ID": "1124",
                "BALANCE": "100",
                "LANGUAGE_ID": "2",
                "POSTPAID_FLAG": "0"
            },
            {
                "MSISDN": "9600050204",
                "TARIFF_PLAN_ID": "1324",
                "BALANCE": "100",
                "LANGUAGE_ID": "2",
                "POSTPAID_FLAG": "0"
            }
        ]
    }

    _ = BulkApiActivateSubscriberRequest(**list_of_transactions)
