from typing import Literal, Union, Optional
from decimal import Decimal

from tshared.utils.plintron_client.plintron_types.base_plintron_model import BasePlintronModel


__all__ = [
    "ProductDetailsType",
    "ProductListType",
    "MultiProductPurchaseType",
    "OfferingType",
    "GetProductOfferingDetailsType",
]


class BaseGetProductOfferingDetails(BasePlintronModel):
    class Config:
        allow_population_by_field_name = True
        alias_generator = str.upper
        validate_all = True


class ProductDetailsType(BasePlintronModel):
    """
    <xs:complexType name="ProductDetailsType">
      <xs:sequence minOccurs="0">
        <xs:element name="NAME" type="xs:string"/>
        <xs:element name="TYPE" type="ProductType"/>
        <xs:element name="CODE" type="BundleCodeTypeO"/>
        <xs:element name="TRANSACTION_AMOUNT" type="BalanceTypeO"/>
        <xs:element name="PROMO_CODE" type="NameTypeO" minOccurs="0"/>
       <xs:element name="NO_OF_MONTHS" type="NumberLen3zTypeO" minOccurs="0"/>
        <xs:element name="NUS_ID" type="StringTypeO" minOccurs="0"/>
       <xs:element name="NUS_EXPIRY" type="RrbsDateTypeO" minOccurs="0"/>
      </xs:sequence>
    </xs:complexType>

    <xs:simpleType name="ProductType">
      <xs:restriction base="xs:string">
        <xs:enumeration value="BUNDLE"/>
        <xs:enumeration value="2"/>
        <xs:enumeration value="TOPUP"/>
        <xs:enumeration value="1"/>
        <xs:enumeration value="MISC_SERVICES"/>
        <xs:enumeration value="3"/>
        <xs:enumeration value="OBA_DUE_COLLECTION"/>
        <xs:enumeration value="DELIVERY_SERVICE"/>
        <xs:enumeration value="WIFI_SERVICE"/>
      </xs:restriction>
    </xs:simpleType>

    <xs:simpleType name="RrbsDateType">
      <xs:restriction base="xs:string">
        <xs:pattern value="\d{2}-\d{2}-\d{4}
                           |[A-Z][A-Z][A-Z]
                           |[0-9]{1,9}
                           |\d{2}-[A-Z][A-Z][A-Z]-\d{2,4}
                           |\d{2}/\d{2}/\d{4}
                           |[A-Z][A-Z][A-Z][A-Z]
                           |\d{2}:\d{2}:\d{2}
                           "/>
      </xs:restriction>
    </xs:simpleType>
    """

    name: str
    type: Literal[
        'BUNDLE', '2', 'TOPUP', '1', 'MISC_SERVICES',
        '3', 'OBA_DUE_COLLECTION', 'DELIVERY_SERVICE',
        'DELIVERY_SERVICE', 'WIFI_SERVICE'
    ]
    code: Optional[str]
    transaction_amount: Optional[Decimal]
    promo_code: Optional[str]
    no_of_months: Optional[int]
    nus_id: Optional[str]
    nus_expiry: Optional[str]


class ProductListType(BasePlintronModel):
    """
     ProductListType(
        PRODUCT: ProductDetailsType[]
     )
    """

    product: Union[ProductDetailsType, list[ProductDetailsType]]


class MultiProductPurchaseType(BasePlintronModel):
    """
    <xs:complexType name="MultiProductPurchaseType">
      <xs:sequence minOccurs="0">
        <xs:element name="TRANSACTION_COST" type="BalanceType"/>
        <xs:element name="TRANSACTION_PROMO_CODE" type="NameTypeO"/>
        <xs:element name="PRODUCT_LIST" type="ProductListType"/>
      </xs:sequence>
    </xs:complexType>

     <xs:simpleType name="BalanceType">
       <xs:restriction base="xs:decimal">
           <xs:totalDigits value ="15"/>
           <xs:fractionDigits value="4"/>
           <xs:pattern value="[0-9]{1,10}[\.]?[0-9]{0,4}"/>
       </xs:restriction>
     </xs:simpleType>
    """

    transaction_cost: Decimal
    transaction_promo_code: Optional[str]
    product_list: ProductListType


class OfferingType(BasePlintronModel):
    code: str


class GetProductOfferingDetailsType(BasePlintronModel):
    """
    <xs:element name="GET_PRODUCT_OFFERING_DETAILS_REQUEST">
      <xs:complexType>
        <xs:sequence>
            <xs:choice minOccurs="0" maxOccurs="3">
                <xs:element name="MSISDN" type="MSISDNTypeO"/>
                <xs:element name="IMSI" type="IMSITypeO"/>
                <xs:element name="ICC_ID" type="ICCIDTypeO"/>
            </xs:choice>
            <xs:element name="OFFERING" minOccurs="0">
              <xs:complexType>
                <xs:sequence minOccurs="0">
                <xs:element name="CODE" type="BundleCodeType" />
                </xs:sequence>
              </xs:complexType>
            </xs:element>
            <xs:element name="NETWORK_ID" type="NetworkIdType" />
            <xs:element name="PAYMENT_MODE_INDICATOR" type="PaymentModeTypeO" minOccurs="0"/>
            <xs:element name="ACTION_FLAG" type="NetworkIdTypeO" minOccurs="0"/>
            <xs:element name="ZIP_CODE" type="xs:string" minOccurs="0"/>
            <xs:element name="AREA_CODE" type="StringLen3zTypeO" minOccurs="0"/>
            <xs:choice minOccurs="0" maxOccurs="1">
              <xs:element name="PRODUCT_LIST" type="ProductListType"/>
              <xs:element name="MULTI_PRODUCT_PURCHASE" type="MultiProductPurchaseType"/>
            </xs:choice>
          <xs:element name="BILLING_ZIP_CODE" type="xs:string" minOccurs="0"/>
        </xs:sequence>
      </xs:complexType>
     </xs:element>

    <xs:simpleType name="BundleCodeType">
      <xs:restriction base="xs:string">
        <xs:pattern value="[a-zA-Z0-9]{1,20}"/>
      </xs:restriction>
    </xs:simpleType>

    <xs:simpleType name="PaymentModeType">
      <xs:restriction base="xs:integer">
            <xs:pattern value="[0-9]{1}"/>
      </xs:restriction>
    </xs:simpleType>

    <xs:simpleType name="NetworkIdType">
      <xs:restriction base="xs:integer">
          <xs:pattern value="[0-9]{1,2}"/>
      </xs:restriction>
    </xs:simpleType>
    """

    msisdn: Optional[Union[str, int]]
    imsi: Optional[Union[str, int]]
    icc_id: Optional[Union[str, int]]

    offering: Optional[OfferingType]
    product_list: Optional[ProductListType]
    multi_product_purchase: Optional[MultiProductPurchaseType]

    network_id: Union[str, int]
    payment_mode_indicator: Optional[int]
    action_flag: Optional[int]
    zip_code: Optional[str]
    area_code: Optional[str]
    billing_zip_code: Optional[str]
