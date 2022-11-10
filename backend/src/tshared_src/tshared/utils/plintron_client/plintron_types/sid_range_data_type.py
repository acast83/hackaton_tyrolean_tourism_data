from typing import Union, Optional
from pydantic import Field

from tshared.utils.plintron_client.plintron_types.base_plintron_model import BasePlintronModel


__all__ = [
    "SIDRangeDataType",
    "ICCIDListType",
    "MSISDNListType",
    "IMSIListType",
    "RangeType",
    "RangeDataType",
]


class RangeDataType(BasePlintronModel):
    """
     <xs:complexType name="IMSIRangeDataType">
       <xs:sequence>
         <xs:element name="FROM" type="IMSIType" />
         <xs:element name="TO" type="IMSIType" />
       </xs:sequence>
     </xs:complexType>
    """
    from_: Union[int, str] = Field(alias='FROM')
    to: Union[int, str]


class RangeType(BasePlintronModel):
    """
    <xs:complexType name="IMSIRangeType">
     <xs:sequence>
        <xs:element name="RANGE" type="IMSIRangeDataType" minOccurs="1" maxOccurs="10" />
     </xs:sequence>
    </xs:complexType>
    """
    range: Union[list[RangeDataType], RangeDataType]


class IMSIListType(BasePlintronModel):
    """
    <xs:complexType name="IMSIListType">
      <xs:sequence>
        <xs:element name="IMSI" type="IMSIType" minOccurs="1" maxOccurs="1000" />
      </xs:sequence>
    </xs:complexType>
    """
    imsi = list[Union[str, int]]


class MSISDNListType(BasePlintronModel):
    """
    <xs:complexType name="MSISDNListType">
       <xs:sequence>
          <xs:element name="MSISDN" type="MSISDNType" minOccurs="1" maxOccurs="1000" />
       </xs:sequence>
    </xs:complexType>
    """
    msisdn = list[Union[str, int]]


class ICCIDListType(BasePlintronModel):
    """
      <xs:complexType name="ICCIDListType">
         <xs:sequence>
            <xs:element name="ICC_ID" type="ICCIDType" minOccurs="1" maxOccurs="1000" />
         </xs:sequence>
      </xs:complexType>
    """
    icc_id = list[Union[str, int]]


class SIDRangeDataType(BasePlintronModel):
    """
    <xs:complexType name="SIDRangeDataType">
       <xs:sequence>
          <xs:choice minOccurs="1" maxOccurs="1">
             <xs:element name="IMSI_RANGE" type="IMSIRangeType" />
             <xs:element name="MSISDN_RANGE" type="MSISDNRangeType" />
             <xs:element name="ICC_ID_RANGE" type="ICCIDRangeType" />
             <xs:element name="IMSI_LIST" type="IMSIListType" />
             <xs:element name="MSISDN_LIST" type="MSISDNListType" />
             <xs:element name="ICC_ID_LIST" type="ICCIDListType" />
          </xs:choice>
       </xs:sequence>
    </xs:complexType>
    """

    imsi_range: Optional[RangeType]
    msisdn_range: Optional[RangeType]
    icc_id_range: Optional[RangeType]

    imsi_list: Optional[IMSIListType]
    msisdn_list: Optional[MSISDNListType]
    icc_id_list: Optional[ICCIDListType]
