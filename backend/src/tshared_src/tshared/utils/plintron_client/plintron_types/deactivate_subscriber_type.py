from typing import Union, Optional

from tshared.utils.plintron_client.plintron_types.base_plintron_model import BasePlintronModel
from tshared.utils.plintron_client.plintron_types.sid_range_data_type import SIDRangeDataType

__all__ = [
    "DeactivateSubscriberRequestType",
    "MultiTransactionDeactivateSubscriberRequestType",
    "BulkApiDeactivateSubscriberRequest",
    "BulkApiDeactivateSubscriberResponse",
]


class DeactivateSubscriberRequestType(BasePlintronModel):
    """
    <xs:element name="DEACTIVATE_SUBSCRIBER_REQUEST" type="DeactivateSubscriberRequestType"/>
      <xs:complexType name="DeactivateSubscriberRequestType">
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


class MultiTransactionDeactivateSubscriberRequestType(BasePlintronModel):
    """
    <xs:complexType name="MultiTransactionDeactivateSubscriberRequestType">
        <xs:sequence>
            <xs:element name="TRANSACTION" type="DeactivateSubscriberRequestType"   minOccurs="1" maxOccurs="1000" />
        </xs:sequence>
    </xs:complexType>
    """
    transaction = list[DeactivateSubscriberRequestType]


class BulkApiDeactivateSubscriberRequest(BasePlintronModel):
    """
    <xs:element name="BULK_API_DEACTIVATE_SUBSCRIBER_REQUEST">
        <xs:complexType>
            <xs:sequence>
                <xs:choice minOccurs="1" maxOccurs="1">
                    <xs:element name="MULTIPLE_TRANSACTIONS" type="MultiTransactionDeactivateSubscriberRequestType" />
                    <xs:element name="RANGE_TRANSACTION" type="DeactivateSubscriberRequestType" />
                </xs:choice>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
    """
    multiple_transactions: Optional[MultiTransactionDeactivateSubscriberRequestType]
    range_transaction: Optional[DeactivateSubscriberRequestType]


class BulkApiDeactivateSubscriberResponse(BasePlintronModel):
    """
    <xs:element name="BULK_API_DEACTIVATE_SUBSCRIBER_RESPONSE">
        <xs:complexType>
            <xs:sequence>
                <xs:element name="JOB_ID" type="xs:string" />
            </xs:sequence>
        </xs:complexType>
    </xs:element>
    """
    job_id: str
