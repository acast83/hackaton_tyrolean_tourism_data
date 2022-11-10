from typing import Literal, Union, Optional

from tshared.utils.plintron_client.plintron_types.base_plintron_model import BasePlintronModel


__all__ = [
    "ArrayOfREALUSER_DETAILS",
    "GetSubscriberDetailsType",
]


BooleanType = Literal['true', 'false', False, True]
GenderTypeM = Literal['Male', 'Female', 'Others']


class ArrayOfREALUSER_DETAILS(BasePlintronModel):
    """
    Not an array just object

    <xs:complexType name="ArrayOfREALUSER_DETAILS">
    <xs:sequence>
    <xs:element minOccurs="0" name="FIRST_NAME" type="StringTypeO"/>
    <xs:element minOccurs="0" name="LAST_NAME" type="StringTypeO"/>
    <xs:element minOccurs="0" name="CODE" type="StringTypeO"/>
    <xs:element minOccurs="0" name="DOB" type="DATEO"/>
    <xs:element minOccurs="0" name="PLACE_OF_BIRTH" type="StringTypeO"/>
    <xs:element minOccurs="0" name="DOCUMENT_TYPE" type="StringTypeO"/>
    <xs:element minOccurs="0" name="DOCUMENT_NUMBER" type="StringTypeO"/>
    <xs:element minOccurs="0" name="DOCUMENT_ISSUER" type="StringTypeO"/>
    <xs:element minOccurs="0" name="DOCUMENT_ISSUE_DATE" type="DATEO"/>
    <xs:element minOccurs="0" name="GENDER" type="GenderTypeO"/>
    <xs:element minOccurs="0" name="NATIONALITY" type="StringTypeO"/>
    </xs:sequence>
    </xs:complexType>
    """

    first_name: Optional[str]
    last_name: Optional[str]
    code: Optional[str]
    dob: Optional[str]
    place_of_birth: Optional[str]
    document_type: Optional[str]
    document_number: Optional[str]
    document_issuer: Optional[str]
    document_issue_date: Optional[str]
    gender: Optional[GenderTypeM]
    nationality: Optional[str]


class GetSubscriberDetailsType(BasePlintronModel):
    """
    <xs:complexType name="GetSubscriberDetailsType">
    <xs:sequence minOccurs="0">
    <xs:element minOccurs="0" name="MSISDN"  type="MSISDNTypeO"/>
    <xs:element minOccurs="0" name="ICCID"  type="ICCIDTypeO"/>
    <xs:element minOccurs="0" name="RETAILER_ID"  type="StringTypeO"/>
    <xs:element minOccurs="0" name="PREFERRED_LANGUAGE"  type="StringTypeO"/>
    <xs:element minOccurs="0" name="TITLE"  type="StringTypeO"/>
    <xs:element minOccurs="0" name="LAST_NAME"  type="StringTypeO"/>
    <xs:element minOccurs="0" name="FIRST_NAME"  type="StringTypeO"/>
    <xs:element minOccurs="0" name="GENDER"  type="StringTypeO"/>
    <xs:element minOccurs="0" name="POST_CODE"  type="StringTypeO"/>
    <xs:element minOccurs="0" name="RESIDENCE_COUNTRY"  type="StringTypeO"/>
    <xs:element minOccurs="0" name="NATIONALITY"  type="StringTypeO"/>
    <xs:element minOccurs="0" name="DATE_OF_BIRTH"  type="DATEO"/>
    <xs:element minOccurs="0" name="PLACE_OF_BIRTH"  type="StringTypeO"/>
    <xs:element minOccurs="0" name="EMAIL_ID"  type="EmailTypeO"/>
    <xs:element minOccurs="0" name="ALTERNATIVE_CONTACT_NUMBER"  type="MobileNumberTypeO"/>
    <xs:element minOccurs="0" name="TAX_CODE"  type="StringTypeO"/>
    <xs:element minOccurs="0" name="DOCUMNET_TYPE"  type="StringTypeO"/>
    <xs:element minOccurs="0" name="DOCUMNET_NUMBER"  type="StringTypeO"/>
    <xs:element minOccurs="0" name="ISSUSER"  type="StringTypeO"/>
    <xs:element minOccurs="0" name="DATE_OF_ISSUE"  type="DATEO"/>
    <xs:element minOccurs="0" name="VAILD_TILL"  type="DATEO"/>
    <xs:element minOccurs="0" name="CHK_SMS_MARKETING"  type="BooleanTypeO"/>
    <xs:element minOccurs="0" name="CHK_TERMS"  type="BooleanTypeO"/>
    <xs:element minOccurs="0" name="CHK_PHOTOCOPY"  type="BooleanTypeO"/>
    <xs:element minOccurs="0" name="PUK_CODE"  type="PUKCodeTypeO"/>
    <xs:element minOccurs="0" name="STATE"  type="StringTypeO"/>
    <xs:element minOccurs="0" name="HOUSE_NUMBER"  type="StringTypeO"/>
    <xs:element minOccurs="0" name="CITY"  type="StringTypeO"/>
    <xs:element minOccurs="0" name="RETAILER_NAME"  type="StringTypeO"/>
    <xs:element minOccurs="0" name="CHK_AGE"  type="BooleanTypeO"/>
    <xs:element minOccurs="0" name="STREET"  type="StringTypeO"/>
    <xs:element minOccurs="0" name="HOUSE_NAME"  type="StringTypeO"/>
    <xs:element minOccurs="0" name="PROVINCE"  type="StringTypeO"/>
    <xs:element minOccurs="0" name="COMUNE_CODE"  type="StringTypeO"/>
    <xs:element minOccurs="0" name="COUNTRY_OF_BIRTH"  type="StringTypeO"/>
    <xs:element minOccurs="0" name="MINOR_DOB" type="DATEO"/>
    <xs:element minOccurs="0" name="MINOR_TITLE" type="StringTypeO"/>
    <xs:element minOccurs="0" name="MINOR_FIRST_NAME" type="StringTypeO"/>
    <xs:element minOccurs="0" name="MINOR_LAST_NAME" type="StringTypeO"/>
    <xs:element minOccurs="0" name="MINOR_GENDER" type="StringTypeO"/>
    <xs:element minOccurs="0" name="ACCEPT_MINOR" type="BooleanTypeO"/>
    <xs:element minOccurs="0" name="IS_REAL_USER_INFO_PROVIDED" type="BooleanTypeO"/>
    <xs:element minOccurs="0" name="REAL_USER_INFO"  type="ArrayOfREALUSER_DETAILS"/>
    <xs:element minOccurs="0" name="VAT_NUMBER" type="StringLen20zType"/>
    <xs:element minOccurs="0" name="ENTRY_TYPE" type="IntTypeO"/>
    <xs:element minOccurs="0" name="ADDITIONAL_1" type="Alphanumeric50TypeO"/>
    <xs:element minOccurs="0" name="ADDITIONAL_2" type="Alphanumeric50TypeO"/>
    </xs:sequence>
    </xs:complexType>
    """

    msisdn: Optional[Union[str, int]]
    iccid: Optional[Union[str, int]]
    retailer_id: Optional[Union[str, int]]
    preferred_language: Optional[str]
    title: Optional[str]
    last_name: Optional[str]
    first_name: Optional[str]
    gender: Optional[str]
    post_code: Optional[str]
    residence_country: Optional[str]
    nationality: Optional[str]
    date_of_birth: Optional[str]
    place_of_birth: Optional[str]
    email_id: Optional[str]
    alternative_contact_number: Optional[str]
    tax_code: Optional[str]
    documnet_type: Optional[str]
    documnet_number: Optional[str]
    issuser: Optional[str]
    date_of_issue: Optional[str]
    vaild_till: Optional[str]
    chk_sms_marketing: Optional[BooleanType]
    chk_terms: Optional[BooleanType]
    chk_photocopy: Optional[BooleanType]
    puk_code: Optional[str]
    state: Optional[str]
    house_number: Optional[str]
    city: Optional[str]
    retailer_name: Optional[str]
    chk_age: Optional[BooleanType]
    street: Optional[str]
    house_name: Optional[str]
    province: Optional[str]
    comune_code: Optional[str]
    country_of_birth: Optional[str]
    minor_dob: Optional[str]
    minor_title: Optional[str]
    minor_first_name: Optional[str]
    minor_last_name: Optional[str]
    minor_gender: Optional[str]
    accept_minor: Optional[BooleanType]
    is_real_user_info_provided: Optional[BooleanType]
    real_user_info: Optional[ArrayOfREALUSER_DETAILS]
    vat_number: Optional[str]
    entry_type: Optional[int]
    additional_1: Optional[str]
    additional_2: Optional[str]
