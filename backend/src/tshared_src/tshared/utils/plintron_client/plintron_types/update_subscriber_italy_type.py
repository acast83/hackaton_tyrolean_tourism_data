from typing import Union, Optional
from pydantic import validator

from tshared.utils.plintron_client.plintron_types.base_plintron_model import BasePlintronModel
from tshared.utils.plintron_client.plintron_types.plintron_italy_register_subscriber_type import ArrayOfATTACHMENT
from tshared.utils.plintron_client.plintron_types.plintron_italy_register_subscriber_type import ArrayOfREALUSER_DETAILS


__all__ = [
    "UpdateSubscriberItalyType",
]


class UpdateSubscriberItalyType(BasePlintronModel):
    """
      <xs:complexType name="REQUESTUPDATESUBSCRIBERITALY">
        <xs:sequence>
          <xs:element name="MSISDN" type="MSISDNType"/>
          <xs:element name="PUK_CODE" type="PUKCodeTypeM"/>
          <xs:element name="ICCID"  type="ICCIDType"/>
          <xs:element minOccurs="0" name="PREFERRED_LANGUAGE"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="TITLE"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="LAST_NAME"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="FIRST_NAME"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="GENDER"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="DATE_OF_BIRTH"  type="DATEO"/>
          <xs:element minOccurs="0" name="PLACE_OF_BIRTH"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="POST_CODE"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="EMAIL_ID"  type="EmailTypeO"/>
          <xs:element minOccurs="0" name="ALTERNATIVE_CONTACT_NUMBER"  type="MobileNumberTypeO"/>
          <xs:element minOccurs="0" name="RESIDENCE_COUNTRY"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="ITALY_NATIONAL"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="NATIONALITY"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="HOUSE_NUMBER"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="HOUSE_NAME"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="STREET"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="CITY"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="STATE"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="TAX_CODE"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="DOCUMENT_TYPE"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="DOCUMENT_NUMBER"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="ISSUER"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="DATE_OF_ISSUE"  type="DATEO"/>
          <xs:element minOccurs="0" name="VALID_TILL"  type="DATEO"/>
          <xs:element minOccurs="0" name="LIST_OF_ATTACHMENTS"  type="ItalyArrayOfATTACHMENT"/>
          <xs:element minOccurs="0" name="RETAILER_NAME"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="RETAILERID"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="CHK_SMS_MARKETING"  type="IntTypeO"/>
          <xs:element minOccurs="0" name="PROVINCE"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="COMUNE_CODE"  type="StringTypeO"/>
          <xs:element minOccurs="0" name="COUNTRY_OF_BIRTH"  type="StringTypeM"/>
          <xs:element minOccurs="0" name="MINOR_DOB" type="DATEO"/>
          <xs:element minOccurs="0" name="MINOR_TITLE" type="StringTypeO"/>
          <xs:element minOccurs="0" name="MINOR_FIRST_NAME" type="StringTypeO"/>
          <xs:element minOccurs="0" name="MINOR_LAST_NAME" type="StringTypeO"/>
          <xs:element minOccurs="0" name="MINOR_GENDER" type="StringTypeO"/>
          <xs:element minOccurs="0" name="REAL_USER_INFO"  type="ArrayOfREALUSER_DETAILS"/>
          <xs:element minOccurs="0" name="VAT_NUMBER" type="StringLen20zType"/>
          <xs:element minOccurs="0" name="ENTRY_TYPE" type="IntTypeO"/>
          <xs:element minOccurs="0" name="ADDITIONAL_1" type="Alphanumeric50TypeO"/>
          <xs:element minOccurs="0" name="ADDITIONAL_2" type="Alphanumeric50TypeO"/>
        </xs:sequence>
      </xs:complexType>
    """

    msisdn: Optional[str]
    puk_code: Optional[str]
    iccid: Optional[str]

    preferred_language: Optional[str]
    title: Optional[str]
    last_name: Optional[str]
    first_name: Optional[str]
    gender: Optional[str]
    date_of_birth: Optional[str]
    place_of_birth: Optional[str]
    post_code: Optional[str]
    email_id: Optional[str]
    alternative_contact_number: Optional[str]
    residence_country: Optional[str]
    italy_national: Optional[str]
    nationality: Optional[str]
    house_number: Optional[str]
    house_name: Optional[str]
    street: Optional[str]
    city: Optional[str]
    state: Optional[str]
    tax_code: Optional[str]
    document_type: Optional[str]
    document_number: Optional[str]
    issuer: Optional[str]
    date_of_issue: Optional[str]
    valid_till: Optional[str]
    list_of_attachments: Optional[ArrayOfATTACHMENT]
    retailer_name: Optional[str]
    retailerid: Optional[str]
    chk_sms_marketing: Optional[int]
    chk_terms: Optional[Union[bool, str]]
    chk_photocopy: Optional[Union[bool, str]]
    chk_age: Optional[Union[bool, str]]
    province: Optional[str]
    comune_code: Optional[str]
    country_of_birth: Optional[str]
    minor_dob: Optional[str]
    minor_title: Optional[str]
    minor_first_name: Optional[str]
    minor_last_name: Optional[str]
    minor_gender: Optional[str]
    accept_minor: Optional[Union[bool, str]]
    is_real_user_info_provided: Optional[Union[bool, str]]
    real_user_info: Optional[ArrayOfREALUSER_DETAILS]
    vat_number: Optional[str]
    entry_type: Optional[int]
    is_email: Optional[Union[bool, str]]
    additional_1: Optional[str]
    additional_2: Optional[str]

    @classmethod
    @validator('chk_terms', 'chk_photocopy', 'chk_age',
               'accept_minor',
               'is_real_user_info_provided', 'is_email')
    def _validate_boolean(cls, v):
        if v in ('0', '1'):
            v = int(v)

        if isinstance(v, int):
            if v in (0, 1):
                v = str(bool(v))
            else:
                raise ValueError(f'Invalid value for boolean argument: {v}.')

        v = str(v).lower()

        if v not in ('true', 'false'):
            raise ValueError(f'Invalid value for boolean argument: {v}.')
        return v


if __name__ == "__main__":
    a = {
             "MSISDN": "399999108804",
             "PUK_CODE": "79210639",
             "ICCID": "4565269622190088050",
             "PREFERRED_LANGUAGE": "",
             "TITLE": "mr",
             "LAST_NAME": "fsfffffffffffff",
             "FIRST_NAME": "sdfsdfffsf",
             "GENDER": "ffsdfsdfsdf",
             "DATE_OF_BIRTH": "07/08/2016",
             "PLACE_OF_BIRTH": "fsdf",
             "POST_CODE": "fsdf",
             "EMAIL_ID": "vignesh.vr@plintron.com",
             "ALTERNATIVE_CONTACT_NUMBER": "399999108804",
             "RESIDENCE_COUNTRY": "",
             "ITALY_NATIONAL": "",
             "NATIONALITY": "",
             "HOUSE_NUMBER": "",
             "HOUSE_NAME": "",
             "STREET": "",
             "CITY": "",
             "STATE": "",
             "TAX_CODE": "fsdfsdf5344535",
             "DOCUMENT_TYPE": "",
             "DOCUMENT_NUMBER": "",
             "ISSUER": "",
             "DATE_OF_ISSUE": "07/08/2016",
             "VALID_TILL": "",
             "LIST_OF_ATTACHMENTS": {
                 "ATTACHMENT": {
                     "EXTENSION": "",
                     "VALUE": ""
                 }
             },
             "RETAILER_NAME": "",
             "RETAILERID": "",
             "CHK_SMS_MARKETING": "0",
             "CHK_TERMS": "true",
             "CHK_PHOTOCOPY": "true",
             "CHK_AGE": "true",
             "PROVINCE": "EE",
             "COMUNE_CODE": "Z230",
             "COUNTRY_OF_BIRTH": "ACATE",
             "MINOR_DOB": "28/05/1991",
             "MINOR_TITLE": "Mr",
             "MINOR_FIRST_NAME": "Bright",
             "MINOR_LAST_NAME": "Jeeva Prakash",
             "MINOR_GENDER": "MALE",
             "ACCEPT_MINOR": "true",
             "IS_REAL_USER_INFO_PROVIDED": "true",
             "REAL_USER_INFO": {
                 "FIRST_NAME": "bright",
                 "LAST_NAME": "bright",
                 "CODE": "123",
                 "DOB": "13/05/2001",
                 "PLACE_OF_BIRTH": "chennai",
                 "DOCUMENT_TYPE": "passport",
                 "DOCUMENT_NUMBER": "AXE1234",
                 "DOCUMENT_ISSUER": "GOVERNMENT",
                 "DOCUMENT_ISSUE_DATE": "13/05/2014",
                 "GENDER": "Female",
                 "NATIONALITY": "INDIAN"
             },
             "VAT_NUMBER": "1234",
             "ENTRY_TYPE": "1",
             "IS_EMAIL": "true",
             "ADDITIONAL_1": "12dfdf34",
             "ADDITIONAL_2": "uygyhg1"
         }

    _ = UpdateSubscriberItalyType(**a)
    print(_)
