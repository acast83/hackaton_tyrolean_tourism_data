from typing import Union, Optional

from tshared.utils.plintron_client.plintron_types.base_plintron_model import BasePlintronModel
from tshared.utils.plintron_client.plintron_types.sid_range_data_type import SIDRangeDataType


__all__ = [
    "ReactivateSubscriberRequestType",
    "MultiTransactionReactivateSubscriberRequestType",
    "BulkApiReactivateSubscriberRequest",
    "BulkApiReactivateSubscriberResponse",
]


class ReactivateSubscriberRequestType(BasePlintronModel):
    """
    <xs:element name="REACTIVATE_SUBSCRIBER_REQUEST" type="ReactivateSubscriberRequestType"/>
    <xs:complexType name="ReactivateSubscriberRequestType">
       <xs:sequence>
          <xs:choice minOccurs="0" maxOccurs="1">
             <xs:element name="IMSI" type="IMSIType" />
             <xs:element name="MSISDN" type="MSISDNType" />
             <xs:element name="ICC_ID" type="ICCIDType" />
             <xs:element name="SID_RANGE" type="SIDRangeDataType" />
          </xs:choice>
          <xs:element name="REASON_DESC" type="StringLen100Type"/>
       </xs:sequence>
    </xs:complexType>
    """

    imsi: Optional[Union[str, int]]
    msisdn: Optional[Union[str, int]]
    icc_id: Optional[Union[str, int]]
    sid_range: Optional[SIDRangeDataType]
    reason_desc: str


class MultiTransactionReactivateSubscriberRequestType(BasePlintronModel):
    """
    <xs:complexType name="MultiTransactionReactivateSubscriberRequestType">
        <xs:sequence>
            <xs:element name="TRANSACTION" type="ReactivateSubscriberRequestType"   minOccurs="1" maxOccurs="1000" />
        </xs:sequence>
    </xs:complexType>
    """
    transaction: list[ReactivateSubscriberRequestType]


class BulkApiReactivateSubscriberRequest(BasePlintronModel):
    """
    <xs:element name="BULK_API_REACTIVATE_SUBSCRIBER_REQUEST">
        <xs:complexType>
            <xs:sequence>
                <xs:choice minOccurs="1" maxOccurs="1">
                    <xs:element name="MULTIPLE_TRANSACTIONS" type="MultiTransactionReactivateSubscriberRequestType" />
                    <xs:element name="RANGE_TRANSACTION" type="ReactivateSubscriberRequestType" />
                </xs:choice>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
    """
    multiple_transactions: Optional[MultiTransactionReactivateSubscriberRequestType]
    range_transaction: Optional[ReactivateSubscriberRequestType]


class BulkApiReactivateSubscriberResponse(BasePlintronModel):
    """
    <xs:element name="BULK_API_REACTIVATE_SUBSCRIBER_RESPONSE">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="JOB_ID" type="xs:string" />
            </xs:sequence>
        </xs:complexType>
    </xs:element>
    """
    job_id: str


