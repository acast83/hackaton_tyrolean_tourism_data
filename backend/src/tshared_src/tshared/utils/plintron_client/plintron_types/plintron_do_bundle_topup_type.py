from typing import Literal, Union, Optional

import pydantic
from pydantic import validator
from decimal import Decimal

from tshared.utils.plintron_client.plintron_types.base_plintron_model import BasePlintronModel


__all__ = [
    "LoanRecoveryDetailesType",
    "ArrayOfDIRECT_DEBITType",
    "TaxDetailsTypeO",
    "BundleInputTypeO",
    "ArrayOfMULTIPLE_BUNDLE_INFOType",
    "ArrayOfSHIPPING_ADDRESSType",
    "ArrayOfPRODUCTDETAILType",
    "ArrayOfPRODUCT_DETAILSType",
    "ApmAddress",
    "ApmDetail",
    "ExternalSocInfoTypeO",
    "WpPayment3DTypeO",
    "BlkFreesimAddressreq",
    "BLK_CardDetailsTypeO",
    "DoBundleTopUpType",
]


YesNoType = str
ZeroorOneO = Literal[0, 1, '0', '1']


class LoanRecoveryDetailesType(BasePlintronModel):
    """
    <xs:complexType name="LoanRecoveryDetailesType">
    <xs:sequence>
    <xs:element minOccurs="0" name="TOPUP_AMOUNT" type="StringTypeO"/>
    <xs:element minOccurs="0" name="TAX" type="decTypeO"/>
    <xs:element minOccurs="0" name="FEE" type="decTypeO"/>
    </xs:sequence>
    </xs:complexType>
    """
    topup_amount: Optional[str]
    tax: Optional[Union[Decimal, int, float]]
    fee: Optional[Union[Decimal, int, float]]


class ArrayOfDIRECT_DEBITType(BasePlintronModel):
    """
    <xs:complexType name="ArrayOfDIRECT_DEBITType">
    <xs:sequence>
    <xs:element minOccurs="0" name="IBAN" type="StringTypeO"/>
    <xs:element minOccurs="0" name="ACCOUNT_HOLDER_NAME" type="StringTypeO"/>
    <xs:element minOccurs="0" name="FIRST_NAME" type="StringTypeO"/>
    <xs:element minOccurs="0" name="LAST_NAME" type="StringTypeO"/>
    <xs:element minOccurs="0" name="ADDRESS_LINE1" type="StringTypeO"/>
    <xs:element minOccurs="0" name="ADDRESS_LINE2" type="StringTypeO"/>
    <xs:element minOccurs="0" name="ADDRESS_LINE3" type="StringTypeO"/>
    <xs:element minOccurs="0" name="CITY" type="StringTypeO"/>
    <xs:element minOccurs="0" name="POST_CODE" type="StringTypeO"/>
    <xs:element minOccurs="0" name="STATE" type="StringTypeO"/>
    </xs:sequence>
    </xs:complexType>
    """
    iban: Optional[str]
    account_holder_name: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]
    address_line1: Optional[str]
    address_line2: Optional[str]
    address_line3: Optional[str]
    city: Optional[str]
    post_code: Optional[str]
    state: Optional[str]


class TaxDetailsTypeO(BasePlintronModel):
    """
      <xs:complexType name="TaxDetailsTypeO">
        <xs:sequence>
          <xs:element minOccurs="0" name="TAX"  type="decTypeO"/>
          <xs:element minOccurs="0" name="TAX_ID"  type="StringTypeO"/>
        </xs:sequence>
      </xs:complexType>
    """
    tax: Optional[Union[Decimal, int, float]]
    tax_id: Optional[str]


class BundleInputTypeO(BasePlintronModel):
    """
      <xs:complexType name="BundleInputTypeO">
        <xs:sequence>
          <xs:element minOccurs="0" name="BUNDLE_NAME"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="BUNDLE_CODE"   type="NumericTypeO"/>
          <xs:element minOccurs="0" name="BUNDLE_VALIDITY"  type="NumericTypeO"/>
          <xs:element minOccurs="0" name="IMSI"  type="IMSITypeO"/>
          <xs:element minOccurs="0" name="BUNDLE_TYPE"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="ACTUAL_AMOUNT"  type="decTypeO"/>
          <xs:element minOccurs="0" name="DISCOUNTED_PRICE"  type="decTypeO"/>
          <xs:element minOccurs="0"  name="ISDISABLE_AUTO_RENEWEL"   type="ZeroorOneO"/>
          <xs:element name="BUNDLE_TAX_DETAILS" type="TaxDetailsTypeO"/>
          <xs:element minOccurs="0" name="NO_OF_MONTH"  type="NumericTypeO"/>
          <xs:element minOccurs="0" name="BUNDLE_FEE"  type="decTypeO"/>
        </xs:sequence>
      </xs:complexType>
    """
    bundle_tax_details: TaxDetailsTypeO

    bundle_name: Optional[str]
    bundle_code: Optional[Union[str, int, float]]
    bundle_validity: Optional[Union[str, int, float]]
    imsi: Optional[Union[int, str]]
    bundle_type: Optional[str]
    actual_amount: Optional[Union[Decimal, int, float]]
    discounted_price: Optional[Union[Decimal, int, float]]
    isdisable_auto_renewel: Optional[Union[ZeroorOneO, str, int]]
    no_of_month: Optional[Union[int, str]]
    bundle_fee: Optional[Union[Decimal, int, float]]


class ArrayOfMULTIPLE_BUNDLE_INFOType(BasePlintronModel):
    """
    <xs:complexType name="ArrayOfMULTIPLE_BUNDLE_INFOType">
    <xs:sequence>
    <xs:element minOccurs="0" maxOccurs="unbounded" name="BUNDLE_INPUT" type="BundleInputTypeO"/>
    </xs:sequence>
    </xs:complexType>

    ArrayOfMULTIPLE_BUNDLE_INFOType(BUNDLE_INPUT: BundleInputTypeO[])
    """
    
    bundle_input: Union[BundleInputTypeO,
                        dict,
                        list[BundleInputTypeO]] = pydantic.Field(default=[])


class ArrayOfSHIPPING_ADDRESSType(BasePlintronModel):
    """
    <xs:complexType name="ArrayOfSHIPPING_ADDRESSType">
    <xs:sequence>
    <xs:element minOccurs="0" name="FIRST_NAME" type="StringTypeO"/>
    <xs:element minOccurs="0" name="LAST_NAME" type="StringTypeO"/>
    <xs:element minOccurs="0" name="ADDRESS_LINE1" type="StringTypeO"/>
    <xs:element minOccurs="0" name="ADDRESS_LINE2" type="StringTypeO"/>
    <xs:element minOccurs="0" name="ADDRESS_LINE3" type="StringTypeO"/>
    <xs:element minOccurs="0" name="CITY" type="StringTypeO"/>
    <xs:element minOccurs="0" name="POST_CODE" type="StringTypeO"/>
    <xs:element minOccurs="0" name="COUNTRY_CODE" type="StringTypeO"/>
    </xs:sequence>
    </xs:complexType>
    """
    first_name: Optional[str]
    last_name: Optional[str]
    address_line1: Optional[str]
    address_line2: Optional[str]
    address_line3: Optional[str]
    city: Optional[str]
    post_code: Optional[str]
    country_code: Optional[str]


class ArrayOfPRODUCTDETAILType(BasePlintronModel):
    """
    <xs:complexType name="ArrayOfPRODUCTDETAILType">
    <xs:sequence>
    <xs:element minOccurs="0" name="TYPE" type="IntTypeO"/>
    <xs:element minOccurs="0" name="NAME" type="StringTypeO"/>
    <xs:element minOccurs="0" name="MODEL" type="StringTypeO"/>
    <xs:element minOccurs="0" name="SPECIFICATION" type="StringTypeO"/>
    <xs:element minOccurs="0" name="PRICE" type="StringTypeO"/>
    <xs:element minOccurs="0" name="TAX_DETAILS" type="decTypeO"/>
    <xs:element minOccurs="0" name="FEE_DETAILS" type="decTypeO"/>
    </xs:sequence>
    </xs:complexType>
    """
    type: Optional[int]
    name: Optional[str]
    model: Optional[str]
    specification: Optional[str]
    price: Optional[str]
    tax_details: Optional[Union[Decimal, int, float]]
    fee_details: Optional[Union[Decimal, int, float]]


class ArrayOfPRODUCT_DETAILSType(BasePlintronModel):
    """
    <xs:complexType name="ArrayOfPRODUCT_DETAILSType">
    <xs:sequence minOccurs="0">
    <xs:element minOccurs="0" maxOccurs="unbounded" name="PRODUCT_DETAIL" type="ArrayOfPRODUCTDETAILType"/>
    </xs:sequence>
    </xs:complexType>

    ArrayOfPRODUCT_DETAILSType(PRODUCT_DETAIL: ArrayOfPRODUCTDETAILType[])
        V
    """
    product_detail: Union[ArrayOfPRODUCTDETAILType,
                          list[ArrayOfPRODUCTDETAILType]] = pydantic.Field(default=[])


class ApmAddress(BasePlintronModel):
    """
      <xs:complexType name="APM_ADDRESS">
        <xs:sequence>
          <xs:element minOccurs="0" name="FIRST_NAME" type="StringTypeO"/>
          <xs:element minOccurs="0" name="LAST_NAME" type="StringTypeO"/>
          <xs:element minOccurs="0" name="ADDRESS_LINE1" type="StringTypeO"/>
          <xs:element minOccurs="0" name="ADDRESS_LINE2" type="StringTypeO"/>
          <xs:element minOccurs="0" name="ADDRESS_LINE3" type="StringTypeO"/>
          <xs:element minOccurs="0" name="CITY"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="POST_CODE" type="StringTypeO"/>
          <xs:element minOccurs="0" name="COUNTRY_CODE" type="StringTypeO"/>
        </xs:sequence>
      </xs:complexType>
    """
    first_name: Optional[str]
    last_name: Optional[str]
    address_line1: Optional[str]
    address_line2: Optional[str]
    address_line3: Optional[str]
    city: Optional[str]
    post_code: Optional[str]
    country_code: Optional[str]


class ApmDetail(BasePlintronModel):
    """
      <xs:complexType name="APM_DETAIL">
        <xs:sequence>
          <xs:element minOccurs="0" name="APM_ID" type="NumericTypeO"/>
          <xs:element minOccurs="0" name="APM_NAME" type="StringTypeO"/>
          <xs:element minOccurs="0" name="BANK_SWIFT_CODE" type="StringTypeO"/>
          <xs:element minOccurs="0" name="SHOPPER_BANK_CODE" type="StringTypeO"/>
          <xs:element minOccurs="0" name="ADDRESS_DETAILS" type="APM_ADDRESS"/>
          <xs:element minOccurs="0" name="ISSUER_ID" type="StringLen30TypeO"/>
          <xs:element minOccurs="0" name="ACCOUNT_HOLDER_NAME" type="StringLen30TypeO"/>
        </xs:sequence>
      </xs:complexType>
    """
    apm_id: Optional[str]
    apm_name: Optional[str]
    bank_swift_code: Optional[str]
    shopper_bank_code: Optional[str]
    address_details: Optional[ApmAddress]
    issuer_id: Optional[str]
    account_holder_name: Optional[str]


class ExternalSocInfoTypeO(BasePlintronModel):
    """
      <xs:complexType name="ExternalSocInfoTypeO">
        <xs:sequence>
          <xs:element name="ADDRESS_LINE1" type="StringTypeO"  minOccurs="0"/>
          <xs:element name="ADDRESS_LINE2" type="StringTypeO"  minOccurs="0"/>
          <xs:element name="CITY" type="StringTypeO"  minOccurs="0"/>
          <xs:element name="STATE_CODE" type="StringTypeO"  minOccurs="0"/>
          <xs:element name="ZIP" type="StringTypeO"  minOccurs="0"/>
        </xs:sequence>
      </xs:complexType>
    """
    address_line1: Optional[str]
    address_line2: Optional[str]
    city: Optional[str]
    state_code: Optional[str]
    zip: Optional[str]


class WpPayment3DTypeO(BasePlintronModel):
    """
      <xs:complexType name="WpPayment3DTypeO">
        <xs:sequence>
          <xs:element minOccurs="0" name="USER_AGENT_HEADER"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="ACCEPT_HEADER"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="SESSION_ID"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="ECO_DATA"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="PARES"  type="StringTypeO"/>
        </xs:sequence>
      </xs:complexType>
    """
    user_agent_header: Optional[str]
    accept_header: Optional[str]
    session_id: Optional[str]
    eco_data: Optional[str]
    pares: Optional[str]


class BlkFreesimAddressreq(BasePlintronModel):
    """
      <xs:complexType name="BLK_FREESIM_ADDRESSREQO">
        <xs:sequence minOccurs="0">
          <xs:element minOccurs="0" name="POST_CODE"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="STREET"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="CITY"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="COUNTRY"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="HOUSE_NO"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="COUNTY" type="StringTypeO"/>
          <xs:element minOccurs="0" name="HOUSENO_EXTN"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="APARTMENT_NO"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="BLOCK"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="LIFT"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="FLOOR"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="DOOR"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="ADMINISTRATIVE_AREA"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="NEIGHBOURHOOD"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="STREET_NUMBER"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="C_O"  type="StringTypeO"/>
        </xs:sequence>
      </xs:complexType>
    """
    post_code: Optional[str]
    street: Optional[str]
    city: Optional[str]
    country: Optional[str]
    house_no: Optional[str]
    county: Optional[str]
    houseno_extn: Optional[str]
    apartment_no: Optional[str]
    block: Optional[str]
    lift: Optional[str]
    floor: Optional[str]
    door: Optional[str]
    administrative_area: Optional[str]
    neighbourhood: Optional[str]
    street_number: Optional[str]
    c_o: Optional[str]


class BLK_CardDetailsTypeO(BasePlintronModel):
    """
      <xs:complexType name="BLK_CardDetailsTypeO">
        <xs:sequence>
          <xs:element minOccurs="0" name="CARD_TYPE"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="NAME_ON_CARD"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="CARD_NO"  type="CardNoTypeO"/>
          <xs:element minOccurs="0" name="ISSUE_DATE"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="EXPIRY_DATE"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="ISSUE_NO"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="CVV"  type="CVVTypeO->string"/>
          <xs:element minOccurs="0" name="BILLING_ADDRESS"  type="BLK_FREESIM_ADDRESSREQO"/>
          <xs:element minOccurs="0" name="FIRST_NAME" type="StringLen30TypeO"/>
          <xs:element minOccurs="0" name="LAST_NAME" type="StringLen30TypeO"/>
        </xs:sequence>
      </xs:complexType>
    """
    card_type: Optional[str]
    name_on_card: Optional[str]
    card_no: Optional[str]
    issue_date: Optional[str]
    expiry_date: Optional[str]
    issue_no: Optional[str]
    cvv: Optional[str]
    billing_address: Optional[BlkFreesimAddressreq]
    first_name: Optional[str]
    last_name: Optional[str]


class DoBundleTopUpType(BasePlintronModel):
    """
    <xs:complexType name="DoBundleTopUpType">
        <xs:sequence>
        <xs:element minOccurs="0" name="BUNDLE_NAME"  type="StringTypeO"/>
        <xs:element minOccurs="0" name="BUNDLE_CODE" type="StringTypeO"/>
        <xs:element minOccurs="0" name="BUNDLE_VALIDITY"  type="StringTypeO"/>
        <xs:element minOccurs="0" name="IMSI"  type="IMSITypeO"/>
        <xs:element minOccurs="0" name="BUNDLE_TYPE"  type="StringTypeO"/>
        <xs:element minOccurs="0" name="ACTUAL_AMOUNT"  type="decTypeO"/>
        <xs:element minOccurs="0" name="DISCOUNTED_PRICE"  type="decTypeO"/>
        <xs:element name="MSISDN" type="MSISDNType"/>
        <xs:element minOccurs="0" name="PRERECEIVER_MSISDN"  type="MSISDNTypeO"/>
        <xs:element name="PAYMENT_MODE" type="IntTypeM"/>
        <xs:element minOccurs="0" name="ISDISABLE_AUTO_RENEWEL" type="ZeroorOneO"/>
        <xs:element minOccurs="0" name="EMAIL" type="EmailTypeO"/>
        <xs:element minOccurs="0" name="CARD_DETAILS"  type="BLK_CardDetailsTypeO"/>
        <xs:element minOccurs="0" name="WP_PAYMENT"  type="WpPayment3DTypeO"/>
        <xs:element minOccurs="0" name="ICC_ID"  type="StringTypeO"/>
        <xs:element minOccurs="0" name="IP_ADDRESS"  type="StringTypeO"/>
        <xs:element minOccurs="0" name="CARD_NICKNAME"  type="StringTypeO"/>
        <xs:element minOccurs="0" name="CARD_ID"  type="StringTypeO"/>
        <xs:element minOccurs="0" name="TAX"  type="decTypeO"/>
        <xs:element minOccurs="0" name="TAX_ID"  type="StringTypeO"/>
        <xs:element minOccurs="0" name="NO_OF_MONTH"  type="StringTypeO"/>
        <xs:element minOccurs="0" name="E911_ADDRESS"  type="ExternalSocInfoTypeO"/>
        <xs:element minOccurs="0" name="TRANSACTION_ID"  type="StringTypeO"/>
        <xs:element minOccurs="0" name="VAT_ID"  type="StringTypeO"/>
        <xs:element minOccurs="0" name="IS_NEW_CARD"  type="ZeroorOneO"/>        
        <xs:element minOccurs="0" name="PROMO_CODE"  type="PromoCodeTypeO"/>
        <xs:element minOccurs="0" name="PROMO_TYPE"  type="StringTypeO"/>
        <xs:element minOccurs="0" name="PROMO_DISCOUNT_AMOUNT"  type="decTypeO"/>
        <xs:element minOccurs="0" name="SPECIAL_DISCOUNT_CODE"  type="StringTypeO"/>
        <xs:element minOccurs="0" name="SPECIAL_DISCOUNT_AMOUNT"  type="decTypeO"/>
        <xs:element minOccurs="0" name="PAYMENT_ID"  type="StringTypeO"/>
        <xs:element minOccurs="0" name="APM_INPUT_DETAILS" type="APM_DETAIL"/>
        <xs:element minOccurs="0" name="RECURRING" type="StringTypeO"/>
        <xs:element minOccurs="0" name="GTN" type="StringTypeO"/>
        <xs:element minOccurs="0" name="SESSION_ID" type="StringTypeO"/>
        <xs:element minOccurs="0" name="APPLICATION_TYPE" type="StringTypeO"/>
        <xs:element minOccurs="0" name="NAME_OR_PAGE_ID" type="StringTypeO"/>
        <xs:element minOccurs="0" name="URL" type="StringTypeO"/>
        <xs:element minOccurs="0" name="CUSTOM_FIELD_1" type="StringTypeO"/>
        <xs:element minOccurs="0" name="CUSTOM_FIELD_2" type="StringTypeO"/>
        <xs:element minOccurs="0" name="CUSTOM_FIELD_3" type="StringTypeO"/>
        <xs:element minOccurs="0" name="FEE" type="decTypeO"/>
        <xs:element minOccurs="0" name="NUS_FLAG" type="StringTypeO"/>
        <xs:element minOccurs="0" name="ACTION_TYPE" type="StringTypeO"/>
        <xs:element minOccurs="0" name="CUSTOMER_CONSENT" type="StringTypeO"/>
        <xs:element minOccurs="0" name="CONSENT_EXPIRY_DATE" type="DATEO"/>
        <xs:element minOccurs="0" name="RESTRICT_EXISTING_PROMO" type="NumericLenTypeO"/>
        <xs:element minOccurs="0" name="IS_DEVICE_INCLUDED" type="YesorNoType"/>
        <xs:element minOccurs="0" name="PRODUCT_DETAIL" type="ArrayOfPRODUCT_DETAILSType"/>
        <xs:element minOccurs="0" name="SHIPPING_ADDRESS" type="ArrayOfSHIPPING_ADDRESSType"/>
        <xs:element minOccurs="0" name="SHIPPING_CHARGE" type="decTypeO"/>
        <xs:element minOccurs="0" name="MEDIUM" type="StringLen50TypeO"/>
        <xs:element minOccurs="0" name="SOURCE" type="StringLen50TypeO"/>
        <xs:element minOccurs="0" name="CAMPAIGN" type="StringLen50TypeO"/>
        <xs:element minOccurs="0" name="CURRENCY_EXCHANGE" type="IntTypeO"/>
        <xs:element minOccurs="0" name="PURCHASE_TYPE" type="IntTypeO"/>
        <xs:element minOccurs="0" name="MODIFY_BUNDLE_CODE" type="IntTypeO"/>
        <xs:element minOccurs="0" name="MODIFY_BUNDLE_INSTALLMENT" type="StringTypeO"/>
        <xs:element minOccurs="0" name="IS_MULTIPLE_BUNDLE_PURCHASE" type="BooleanTypeO"/>
        <xs:element minOccurs="0" name="MULTIPLE_BUNDLE_INFO" type="ArrayOfMULTIPLE_BUNDLE_INFOType"/>
        <xs:element minOccurs="0" name="DIRECT_DEBIT" type="ArrayOfDIRECT_DEBITType"/>
        <xs:element minOccurs="0" name="LOAN_RECOVERY" type="LoanRecoveryDetailesType"/>
        <xs:element minOccurs="0" name="CAMPAIGN_FLAG" type="StringTypeO"/>
        <xs:element minOccurs="0" name="CAMPAIGN_KEYWORD" type="StringTypeO"/>
        </xs:sequence>
    </xs:complexType>   
    """
    msisdn: Union[int, str]
    payment_mode: int

    bundle_name: Optional[str]
    bundle_code: Optional[str]
    bundle_validity: Optional[str]
    imsi: Optional[Union[str, int]]
    bundle_type: Optional[str]
    actual_amount: Optional[Union[Decimal, int, float]]
    discounted_price: Optional[Union[Decimal, int, float]]
    prereceiver_msisdn: Optional[Union[str, int]]
    isdisable_auto_renewel: Optional[ZeroorOneO]
    email: Optional[str]
    card_details: Optional[BLK_CardDetailsTypeO]
    wp_payment: Optional[WpPayment3DTypeO]
    icc_id: Optional[str]
    ip_address: Optional[str]
    card_nickname: Optional[str]
    card_id: Optional[str]
    tax: Optional[Union[Decimal, int, float]]
    tax_id: Optional[str]
    no_of_month: Optional[str]
    e911_address: Optional[ExternalSocInfoTypeO]
    transaction_id: Optional[str]
    vat_id: Optional[str]
    is_new_card: Optional[ZeroorOneO]
    promo_code: Optional[str]
    promo_type: Optional[str]
    promo_discount_amount: Optional[Union[Decimal, int, float]]
    special_discount_code: Optional[str]
    special_discount_amount: Optional[Union[Decimal, int, float]]
    payment_id: Optional[str]
    apm_input_details: Optional[ApmDetail]
    recurring: Optional[str]
    gtn: Optional[str]
    session_id: Optional[str]
    application_type: Optional[str]
    name_or_page_id: Optional[str]
    url: Optional[str]
    custom_field_1: Optional[str]
    custom_field_2: Optional[str]
    custom_field_3: Optional[str]
    fee: Optional[Union[Decimal, int, float]]
    nus_flag: Optional[str]
    action_type: Optional[str]
    customer_consent: Optional[str]
    consent_expiry_date: Optional[str]
    restrict_existing_promo: Optional[Union[int, str]]
    is_device_included: Optional[Union[YesNoType, str]]
    product_detail: Optional[ArrayOfPRODUCT_DETAILSType]
    shipping_address: Optional[ArrayOfSHIPPING_ADDRESSType]
    shipping_charge: Optional[Union[Decimal, int, float]]
    medium: Optional[str]
    source: Optional[str]
    campaign: Optional[str]
    currency_exchange: Optional[Union[int, str]]
    purchase_type: Optional[int]
    modify_bundle_code: Optional[int]
    modify_bundle_installment: Optional[str]
    is_multiple_bundle_purchase: Optional[str]
    multiple_bundle_info: Optional[ArrayOfMULTIPLE_BUNDLE_INFOType]
    direct_debit: Optional[ArrayOfDIRECT_DEBITType]
    loan_recovery: Optional[LoanRecoveryDetailesType]
    campaign_flag: Optional[str]
    campaign_keyword: Optional[str]

    @classmethod
    @validator('is_device_included'
               )
    def _validate_yes_no(cls, v):
        if isinstance(v, bool):
            v = 'YES' if v else 'NO'
        v = str(v).upper()

        if v not in ('YES', 'NO'):
            raise ValueError(f'Wrong value for YesNo type: {v}')
        return v


if __name__ == "__main__":
    body_1 = {
        "BUNDLE_NAME": "40005_name",
        "BUNDLE_CODE": "40005",
        "BUNDLE_VALIDITY": "",
        "IMSI": "",
        "BUNDLE_TYPE": "",
        "ACTUAL_AMOUNT": 1.1,
        "DISCOUNTED_PRICE": "1.2",
        "MSISDN": "984215561",
        "PRERECEIVER_MSISDN": "",
        "PAYMENT_MODE": "1",
        "ISDISABLE_AUTO_RENEWEL": "1",
        "EMAIL": "sdsasd@gmail.com",
        "CARD_DETAILS": {
            "CARD_TYPE": "",
            "NAME_ON_CARD": "",
            "CARD_NO": "",
            "ISSUE_DATE": "",
            "EXPIRY_DATE": "",
            "ISSUE_NO": "",
            "CVV": "",
            "BILLING_ADDRESS": {
                "POST_CODE": "",
                "STREET": "",
                "CITY": "",
                "COUNTRY": "",
                "HOUSE_NO": "",
                "COUNTY": "",
                "HOUSENO_EXTN": "",
                "APARTMENT_NO": "",
                "BLOCK": "",
                "LIFT": "",
                "FLOOR": "",
                "DOOR": ""
            },
            "FIRST_NAME": "cristiano",
            "LAST_NAME": "m"
        },
        "WP_PAYMENT": {
            "USER_AGENT_HEADER": "",
            "ACCEPT_HEADER": "",
            "SESSION_ID": "",
            "ECO_DATA": "",
            "PARES": ""
        },
        "ICC_ID": "",
        "IP_ADDRESS": "",
        "CARD_NICKNAME": "",
        "CARD_ID": "",
        "TAX": "1.3",
        "TAX_ID": "",
        "NO_OF_MONTH": "",
        "E911_ADDRESS": {
            "ADDRESS_LINE1": "",
            "ADDRESS_LINE2": "",
            "CITY": "",
            "STATE_CODE": "",
            "ZIP": ""
        },
        "TRANSACTION_ID": "",
        "VAT_ID": "",
        "IS_NEW_CARD": "1",
        "PROMO_CODE": "",
        "PROMO_TYPE": "",
        "PROMO_DISCOUNT_AMOUNT": "1.5",
        "SPECIAL_DISCOUNT_CODE": "",
        "SPECIAL_DISCOUNT_AMOUNT": "1.6",
        "PAYMENT_ID": "",
        "APPLICATION_TYPE": "MyAccounts",
        "NAME_OR_PAGE_ID": "ABC",
        "URL": "http://192.168.110.159:5001/redirectpayment/paymentresponse.aspx",
        "CUSTOM_FIELD_1": "A",
        "CUSTOM_FIELD_2": "B",
        "CUSTOM_FIELD_3": "C",
        "FEE": "1.7",
        "NUS_FLAG": "1",
        "ACTION_TYPE": "1",
        "CUSTOMER_CONSENT": "1",
        "CONSENT_EXPIRY_DATE": "11/02/2021",
        "RESTRICT_EXISTING_PROMO": "1",
        "IS_DEVICE_INCLUDED": "yes",
        "PRODUCT_DETAIL": {
            "PRODUCT_DETAIL": {
                "TYPE": "0",
                "NAME": "Mobile",
                "MODEL": "Redmi",
                "SPECIFICATION": "48 Mb camera",
                "PRICE": "15000",
                "TAX_DETAILS": ".8",
                "FEE_DETAILS": ".8"
            }
        },
        "SHIPPING_ADDRESS": "",
        "SHIPPING_CHARGE": "1.7",
        "MEDIUM": "WEB",
        "SOURCE": "BROWSER",
        "CAMPAIGN": "TEST",
        "CURRENCY_EXCHANGE": "2",
        "PURCHASE_TYPE": "1",
        "MODIFY_BUNDLE_CODE": "1",
        "MODIFY_BUNDLE_INSTALLMENT": "",
        "IS_MULTIPLE_BUNDLE_PURCHASE": "true",
        "MULTIPLE_BUNDLE_INFO": {
            "BUNDLE_INPUT": {
                "BUNDLE_NAME": "BUNDLE",
                "BUNDLE_CODE": "5555",
                "BUNDLE_VALIDITY": "",
                "IMSI": "",
                "BUNDLE_TYPE": "National",
                "ACTUAL_AMOUNT": "10",
                "DISCOUNTED_PRICE": "10",
                "ISDISABLE_AUTO_RENEWEL": "1",
                "BUNDLE_TAX_DETAILS": {
                    "TAX": "1.24",
                    "TAX_ID": "turtur"
                },
                "NO_OF_MONTH": "1",
                "BUNDLE_FEE": ""
            }
        },
        "LOAN_RECOVERY": {
            "TOPUP_AMOUNT": "10",
            "TAX": "10",
            "FEE": "10"
        },
        "CAMPAIGN_FLAG": "open",
        "CAMPAIGN_KEYWORD": "camp1"
    }
    body_2 = {
        "BUNDLE_NAME": "BUNDLE",
        "BUNDLE_CODE": "5555",
        "BUNDLE_VALIDITY": "",
        "IMSI": "",
        "BUNDLE_TYPE": "National",
        "ACTUAL_AMOUNT": "10",
        "DISCOUNTED_PRICE": "20",
        "MSISDN": "449564500003",
        "PRERECEIVER_MSISDN": "",
        "PAYMENT_MODE": "3",
        "ISDISABLE_AUTO_RENEWEL": "1",
        "EMAIL": "vignesh.vr@plintron.com",
        "ICC_ID": "",
        "IP_ADDRESS": "192.168.110.159",
        "CARD_NICKNAME": "",
        "CARD_ID": "",
        "TAX": "1",
        "TAX_ID": "",
        "NO_OF_MONTH": "1",
        "TRANSACTION_ID": "MBPA0000080889",
        "VAT_ID": "",
        "PROMO_CODE": "",
        "PROMO_TYPE": "",
        "PROMO_DISCOUNT_AMOUNT": "1",
        "SPECIAL_DISCOUNT_CODE": "",
        "SPECIAL_DISCOUNT_AMOUNT": "1",
        "PAYMENT_ID": "",
        "APM_INPUT_DETAILS": {
            "APM_ID": "50",
            "APM_NAME": "IDEAL",
            "BANK_SWIFT_CODE": "ING",
            "SHOPPER_BANK_CODE": "ING",
            "ADDRESS_DETAILS": {
                "FIRST_NAME": "vickey",
                "LAST_NAME": "v",
                "ADDRESS_LINE1": "street",
                "ADDRESS_LINE2": "city",
                "ADDRESS_LINE3": "country",
                "CITY": "chennai",
                "POST_CODE": "10024"
            },
            "ISSUER_ID": "",
            "ACCOUNT_HOLDER_NAME": ""
        },
        "RECURRING": "true",
        "GTN": "APM",
        "SESSION_ID": "wesdehfghsdjfj",
        "APPLICATION_TYPE": "MyAccounts",
        "NAME_OR_PAGE_ID": "ABC",
        "URL": "http://192.168.110.159:5001/redirectpayment/paymentresponse.aspx",
        "CUSTOM_FIELD_1": "A",
        "CUSTOM_FIELD_2": "B",
        "CUSTOM_FIELD_3": "C",
        "FEE": "1",
        "NUS_FLAG": "1",
        "ACTION_TYPE": "1",
        "CUSTOMER_CONSENT": "1",
        "CONSENT_EXPIRY_DATE": "11/02/2021",
        "RESTRICT_EXISTING_PROMO": "1",
        "IS_DEVICE_INCLUDED": "yes",
        "PRODUCT_DETAIL": {
            "PRODUCT_DETAIL": {
                "TYPE": "0",
                "NAME": "Mobile",
                "MODEL": "Redmi",
                "SPECIFICATION": "48 Mb camera",
                "PRICE": "15000",
                "TAX_DETAILS": ".8",
                "FEE_DETAILS": ".8"
            }
        },
        "SHIPPING_ADDRESS": "",
        "SHIPPING_CHARGE": "7",
        "MEDIUM": "WEB",
        "SOURCE": "BROWSER",
        "CAMPAIGN": "TEST",
        "CURRENCY_EXCHANGE": "7",
        "PURCHASE_TYPE": "1",
        "MODIFY_BUNDLE_CODE": "1",
        "MODIFY_BUNDLE_INSTALLMENT": "",
        "IS_MULTIPLE_BUNDLE_PURCHASE": "true",
        "MULTIPLE_BUNDLE_INFO": {
            "BUNDLE_INPUT": {
                "BUNDLE_NAME": "BUNDLE",
                "BUNDLE_CODE": "5555",
                "BUNDLE_VALIDITY": "",
                "IMSI": "",
                "BUNDLE_TYPE": "National",
                "ACTUAL_AMOUNT": "10",
                "DISCOUNTED_PRICE": "10",
                "ISDISABLE_AUTO_RENEWEL": "1",
                "BUNDLE_TAX_DETAILS": {
                    "TAX": "1.24",
                    "TAX_ID": "turtur"
                },
                "NO_OF_MONTH": "1",
                "BUNDLE_FEE": "7"
            }
        },
        "LOAN_RECOVERY": {
            "TOPUP_AMOUNT": "10",
            "TAX": "10",
            "FEE": "10"
        },
        "CAMPAIGN_FLAG": "open",
        "CAMPAIGN_KEYWORD": "camp1"
    }
    body_3 = {
        "BUNDLE_NAME": "BUNDLE",
        "BUNDLE_CODE": "5555",
        "BUNDLE_VALIDITY": "",
        "IMSI": "",
        "BUNDLE_TYPE": "National",
        "ACTUAL_AMOUNT": "10",
        "DISCOUNTED_PRICE": "20",
        "MSISDN": "449564500003",
        "PRERECEIVER_MSISDN": "",
        "PAYMENT_MODE": "6",
        "ISDISABLE_AUTO_RENEWEL": "1",
        "EMAIL": "vignesh.vr@plintron.com",
        "ICC_ID": "",
        "IP_ADDRESS": "192.168.110.159",
        "CARD_NICKNAME": "",
        "CARD_ID": "",
        "TAX": "7",
        "TAX_ID": "",
        "NO_OF_MONTH": "1",
        "TRANSACTION_ID": "MBPA0000080889",
        "VAT_ID": "",
        "PROMO_CODE": "",
        "PROMO_TYPE": "",
        "PROMO_DISCOUNT_AMOUNT": "7",
        "SPECIAL_DISCOUNT_CODE": "",
        "SPECIAL_DISCOUNT_AMOUNT": "7",
        "PAYMENT_ID": "",
        "RECURRING": "true",
        "GTN": "APM",
        "SESSION_ID": "wesdehfghsdjfj",
        "APPLICATION_TYPE": "MyAccounts",
        "NAME_OR_PAGE_ID": "ABC",
        "URL": "http://192.168.110.159:5001/redirectpayment/paymentresponse.aspx",
        "CUSTOM_FIELD_1": "A",
        "CUSTOM_FIELD_2": "B",
        "CUSTOM_FIELD_3": "C",
        "FEE": "7",
        "NUS_FLAG": "1",
        "ACTION_TYPE": "1",
        "CUSTOMER_CONSENT": "1",
        "CONSENT_EXPIRY_DATE": "11/02/2021",
        "RESTRICT_EXISTING_PROMO": "1",
        "IS_DEVICE_INCLUDED": "yes",
        "PRODUCT_DETAIL": {
            "TYPE": "0",
            "NAME": "Mobile",
            "MODEL": "Redmi",
            "SPECIFICATION": "48 Mb camera",
            "PRICE": "15000",
            "TAX_DETAILS": ".8",
            "FEE_DETAILS": ".8"
        },
        "SHIPPING_ADDRESS": "",
        "SHIPPING_CHARGE": "7",
        "MEDIUM": "WEB",
        "SOURCE": "BROWSER",
        "CAMPAIGN": "TEST",
        "CURRENCY_EXCHANGE": "7",
        "PURCHASE_TYPE": "1",
        "MODIFY_BUNDLE_CODE": "1",
        "MODIFY_BUNDLE_INSTALLMENT": "",
        "IS_MULTIPLE_BUNDLE_PURCHASE": "true",
        "MULTIPLE_BUNDLE_INFO": {
            "BUNDLE_INPUT": {
                "BUNDLE_NAME": "BUNDLE",
                "BUNDLE_CODE": "5555",
                "BUNDLE_VALIDITY": "",
                "IMSI": "",
                "BUNDLE_TYPE": "National",
                "ACTUAL_AMOUNT": "10",
                "DISCOUNTED_PRICE": "10",
                "ISDISABLE_AUTO_RENEWEL": "1",
                "BUNDLE_TAX_DETAILS": {
                    "TAX": "1.24",
                    "TAX_ID": "turtur"
                },
                "NO_OF_MONTH": "1",
                "BUNDLE_FEE": "7"
            }
        },
        "DIRECT_DEBIT": {
            "IBAN": "BE71564514030369",
            "ACCOUNT_HOLDER_NAME": "vicky",
            "FIRST_NAME": "vickey",
            "LAST_NAME": "v",
            "ADDRESS_LINE1": "street",
            "ADDRESS_LINE2": "city",
            "ADDRESS_LINE3": "country",
            "CITY": "chennai",
            "POST_CODE": "10024",
            "STATE": "Tamilnadu"
        },
        "LOAN_RECOVERY": {
            "TOPUP_AMOUNT": "10",
            "TAX": "10",
            "FEE": "10"
        },
        "CAMPAIGN_FLAG": "open",
        "CAMPAIGN_KEYWORD": "camp1"
    }
    body_1 = body_1
    body_2 = body_2
    body_3 = body_3
    _ = DoBundleTopUpType(**body_1)
    _ = DoBundleTopUpType(**body_2)
    _ = DoBundleTopUpType(**body_3)
