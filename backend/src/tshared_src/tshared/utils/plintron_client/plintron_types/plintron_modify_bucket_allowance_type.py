from typing import Literal, Union, Optional

import pydantic
from decimal import Decimal

from tshared.utils.plintron_client.plintron_types.base_plintron_model import BasePlintronModel


__all__ = [
    "TMOBucketValueType",
    "TMOThresholdType",
    "TMOThresholdsType",
    "TMOProductLimitType",
    "TMOInnerProductType",
    "TMOProductsType",
    "BucketDetails",
    "SubsBucketDetailsType",
    "ModifyBucketAllowanceType",
]


YesNoType = str
ZeroorOneO = Literal[0, 1, '0', '1']
RrbsServiceTypeType = Literal[1, 2, 3, 4, '1', '2', '3', '4']
BucketIdType = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
OperationCodeType = Literal[1, 2, 3]
TMOModifyType = Literal['ACCUMULATE', 'SUBTRACT', 'REPLACE']
TMOOperationType = Literal['ADD', 'MODIFY', 'REMOVE']
BucketValueUnitType = Literal['MB', 'GB', 'KB']
TMOProductInnerType = Literal['ONNET', 'DOMESTIC', 'INTERNATIONAL']
ThresholdInnerType = Literal['Tier1', 'Tier2', 'Tier3', 'Tier4']
LimitValue = Decimal
ThresholdBehaviourType = Literal[
    "capped", "redirect", "notifyonly", "thr64kbps",
    "thr128kbps", "thr256kbps", "thr512kbps", "thr768kbps",
    "thr1024kbps", "thr1536kbps", "thr2560kbps", "thr25mbps",
    "notifythr64kbps", "notifythr128kbps", "notifythr256kbps",
    "notifythr512kbps", "notifythr768kbps", "notifythr1024kbps",
    "notifythr1536kbps", "notifythr2560kbps", "notifyThr25mbps",
]


class TMOBucketValueType(BasePlintronModel):
    """
    <xs:complexType name="TMOBucketValueType">
       <xs:sequence minOccurs="0">
          <xs:element name="UNIT" type="BucketValueUnitType"/>
          <xs:element name="VALUE" type="LimitValue"/>
       </xs:sequence>
    </xs:complexType>
    """
    unit: Optional[BucketValueUnitType]
    value: Optional[LimitValue]


class TMOThresholdType(BasePlintronModel):
    """
    <xs:complexType name="TMOThresholdType">
       <xs:sequence minOccurs="0">
          <xs:element name="THRESHOLD_TYPE" type="ThresholdInnerType"/>
          <xs:element name="THRESHOLD_VALUE" type="LimitValue"/>
          <xs:element name="BEHAVIOR" type="ThresholdBehaviourType"/>
          <xs:element name="THRESHOLD_ACTION" type="TMOOperationType" minOccurs="0"/>
       </xs:sequence>
    </xs:complexType>
    """
    threshold_type: Optional[ThresholdInnerType]
    threshold_value: Optional[LimitValue]
    behavior: Optional[ThresholdBehaviourType]
    threshold_action: Optional[TMOOperationType]


class TMOThresholdsType(BasePlintronModel):
    """
    <xs:complexType name="TMOThresholdsType">
       <xs:sequence minOccurs="0">
          <xs:element name="THRESHOLD" type="TMOThresholdType" minOccurs="0" maxOccurs="4" />
       </xs:sequence>
    </xs:complexType>

    TMOThresholdsType(THRESHOLD: TMOThresholdType[])
    """
    threshold: Optional[Union[list[TMOThresholdType], TMOThresholdType]] = pydantic.Field(default=[])


class TMOProductLimitType(BasePlintronModel):
    """
    <xs:complexType name="TMOProductLimitType">
       <xs:sequence minOccurs="0">
          <xs:element name="BUCKET_VALUE" type="TMOBucketValueType"/>
          <xs:element name="THRESHOLDS" type="TMOThresholdsType" minOccurs="0" />
       </xs:sequence>
    </xs:complexType>
    """
    bucket_value: Optional[TMOBucketValueType]
    thresholds: Optional[TMOThresholdsType]


class TMOInnerProductType(BasePlintronModel):
    """
    <xs:complexType name="TMOInnerProductType">
       <xs:sequence minOccurs="0">
          <xs:element name="TYPE" type="TMOProductInnerType"/>
          <xs:element name="OPERATION_TYPE" type="TMOOperationType" />
          <xs:element name="MODIFY_TYPE" type="TMOModifyType" minOccurs="0"/>
          <xs:element name="LIMIT" type="TMOProductLimitType" minOccurs="0"/>
       </xs:sequence>
    </xs:complexType>
    """
    type: Optional[TMOProductInnerType]
    operation_type: Optional[TMOOperationType]
    modify_type: Optional[TMOModifyType]
    limit: Optional[TMOProductLimitType]


class TMOProductsType(BasePlintronModel):
    """
    <xs:complexType name="TMOProductsType">
       <xs:sequence minOccurs="0">
          <xs:element name="PRODUCT" type="TMOInnerProductType" minOccurs="0" maxOccurs="3"/>
       </xs:sequence>
    </xs:complexType>

    TMOProductsType(PRODUCT: TMOInnerProductType[])
    """

    product: Union[list[TMOInnerProductType], TMOInnerProductType]


class BucketDetails(BasePlintronModel):
    """
    <xs:complexType>
      <xs:sequence>
        <xs:element name="BUCKET_DETAILS" maxOccurs="unbounded" minOccurs="0">
          <xs:complexType>
            <xs:sequence>
              <xs:element name="SERVICE_TYPE" type="RrbsServiceTypeType"/>
              <xs:element name="BUCKET_ID" type="BucketIdType"/>
              <xs:element name="OPERATION_CODE" type="OperationCodeType"/>
              <xs:element name="ALLOWANCE" type="BalanceType"/>
            </xs:sequence>
          </xs:complexType>
        </xs:element>
      </xs:sequence>
    </xs:complexType>
    """
    service_type: RrbsServiceTypeType
    bucket_id: Optional[BucketIdType]
    operation_code: Optional[OperationCodeType]
    allowance: Optional[Decimal]


class SubsBucketDetailsType(BasePlintronModel):
    bucket_details: Union[list[BucketDetails], BucketDetails]


class ModifyBucketAllowanceType(BasePlintronModel):
    """
    <xs:element name="MODIFY_BUCKET_ALLOWANCE_REQUEST">
      <xs:complexType>
        <xs:sequence>
          <xs:choice minOccurs="1" maxOccurs="3">
            <xs:element name="MSISDN" type="MSISDNType"/>
            <xs:element name="IMSI" type="IMSIType"/>
            <xs:element name="ICC_ID" type="ICCIDType"/>
          </xs:choice>
          <xs:element name="BUNDLE_CODE" type="BundleCodeType" minOccurs="0" nillable="true" />
          <xs:element name="SUBS_BUCKET_DETAILS" type="SubsBucketDetailsType" minOccurs="0">
          <xs:element name="TMO_PRODUCTS" type="TMOProductsType" minOccurs="0" />
        </xs:sequence>
      </xs:complexType>
    </xs:element>
    """
    msisdn: Optional[Union[str, int]]
    imsi: Optional[Union[str, int]]
    icc_id: Optional[Union[str, int]]
    
    bundle_code: Union[int, str]
    subs_bucket_details: Optional[SubsBucketDetailsType]
    tmo_products: Optional[TMOProductsType]
