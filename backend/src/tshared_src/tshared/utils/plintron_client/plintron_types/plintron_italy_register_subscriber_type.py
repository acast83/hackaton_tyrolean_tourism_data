from typing import Literal, Union, Optional
from pydantic import validator

from tshared.utils.plintron_client.plintron_types.base_plintron_model import BasePlintronModel


__all__ = [
    "ATTACHMENT",
    "ArrayOfATTACHMENT",
    "ArrayOfREALUSER_DETAILS",
    "RegisterSubscriberITALYType",
    "ItalyRegisterSubscriberRequest",
]


class ATTACHMENT(BasePlintronModel):
    """
    <xs:complexType name="ATTACHMENT">
      <xs:sequence>
        <xs:element minOccurs="0" name="EXTENSION"  type="StringTypeO"/>
        <xs:element minOccurs="0" name="VALUE"  type="StringTypeO"/>
      </xs:sequence>
    </xs:complexType>
    """
    extension: Optional[str]
    value: Optional[str]


class ArrayOfATTACHMENT(BasePlintronModel):
    """
    ArrayOfATTACHMENT(ATTACHMENT: ATTACHMENT[])

    <xs:complexType name="ArrayOfATTACHMENT">
      <xs:sequence>
        <xs:element minOccurs="0" maxOccurs="unbounded" name="ATTACHMENT"  type="ATTACHMENT"/>
      </xs:sequence>
    </xs:complexType>
    """

    attachment: Union[ATTACHMENT, list[ATTACHMENT]]


class ArrayOfREALUSER_DETAILS(BasePlintronModel):
    """
    Not actually an array

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

    <xs:simpleType name="GenderType">
      <xs:restriction base="xs:string">
        <xs:enumeration value="F" />
        <xs:enumeration value="M" />
      </xs:restriction>
    </xs:simpleType>
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
    gender: Optional[Literal['F', 'M', 'Female', 'Male']]
    nationality: Optional[str]


class RegisterSubscriberITALYType(BasePlintronModel):
    """
    DETAILS: {}

    <xs:complexType name="RegisterSubscriberITALYType">
      <xs:sequence>
        <xs:element minOccurs="0" name="MSISDN" type="MobileNumberTypeO"/>
        <xs:element minOccurs="0" name="PUK_CODE"  type="PUKCodeTypeO"/>
        <xs:element name="ICCID"  type="ICCIDType"/>
        <xs:element name="PREFERRED_LANGUAGE"  type="StringTypeM"/>
        <xs:element name="TITLE"  type="StringTypeM"/>
        <xs:element name="LAST_NAME"  type="StringTypeM"/>
        <xs:element name="FIRST_NAME"  type="StringTypeM"/>
        <xs:element name="GENDER"  type="StringTypeM"/>
        <xs:element name="DATE_OF_BIRTH"  type="DATE"/>
        <xs:element name="PLACE_OF_BIRTH"  type="StringTypeM"/>
        <xs:element minOccurs="0" name="PROVINCE"  type="StringTypeO"/>
        <xs:element minOccurs="0" name="EMAIL_ID"  type="EmailTypeO"/>
        <xs:element minOccurs="0" name="ALTERNATIVE_CONTACT_NUMBER"  type="MobileNumberTypeO"/>
        <xs:element name="RESIDENCE_COUNTRY"  type="StringTypeM"/>
        <xs:element name="ITALY_NATIONAL"  type="StringTypeM"/>
        <xs:element name="NATIONALITY"  type="StringTypeM"/>
        <xs:element name="HOUSE_NUMBER"  type="StringTypeM"/>
        <xs:element name="HOUSE_NAME"  type="StringTypeM"/>
        <xs:element name="POST_CODE"  type="StringTypeM"/>
        <xs:element name="STREET"  type="StringTypeM"/>
        <xs:element name="CITY"  type="StringTypeM"/>
        <xs:element name="STATE"  type="StringTypeM"/>
        <xs:element minOccurs="0" name="TAX_CODE"  type="StringTypeO"/>
        <xs:element name="DOCUMENT_TYPE"  type="StringTypeM"/>
        <xs:element name="DOCUMENT_NUMBER"  type="StringTypeM"/>
        <xs:element name="ISSUER"  type="StringTypeM"/>
        <xs:element name="DATE_OF_ISSUE"  type="DATE"/>
        <xs:element name="VALID_TILL"  type="DATE"/>
        <xs:element minOccurs="0" name="LIST_OF_ATTACHMENTS"  type="ArrayOfATTACHMENT"/>
        <xs:element name="RETAILER_NAME"  type="StringTypeM"/>
        <xs:element name="RETAILERID"  type="StringTypeM"/>
        <xs:element name="CHK_SMS_MARKETING"  type="IntTypeM"/>
        <xs:element name="CHK_TERMS"  type="BooleanType"/>
        <xs:element name="CHK_PHOTOCOPY"  type="BooleanType"/>
        <xs:element name="CHK_AGE"  type="BooleanType"/>
        <xs:element name="SMS_UPDATE"  type="BooleanType"/>
        <xs:element name="DYNAMIC_ALLOCATION_STATUS"  type="IntTypeM"/>
        <xs:element minOccurs="0" name="IVRLANGUAGE"  type="StringTypeO"/>
        <xs:element minOccurs="0" name="COMUNE_CODE"  type="StringTypeO"/>
        <xs:element minOccurs="0" name="COUNTRY_OF_BIRTH"  type="StringTypeO"/>
        <xs:element minOccurs="0" name="TYPE"  type="StringTypeO"/>
        <xs:element minOccurs="0" name="MINOR_DOB" type="DATEO"/>
        <xs:element minOccurs="0" name="MINOR_TITLE" type="StringTypeO"/>
        <xs:element minOccurs="0" name="MINOR_FIRST_NAME" type="StringTypeO"/>
        <xs:element minOccurs="0" name="MINOR_LAST_NAME" type="StringTypeO"/>
        <xs:element minOccurs="0" name="MINOR_GENDER" type="StringTypeO"/>
        <xs:element minOccurs="0" name="ACCEPT_MINOR" type="BooleanTypeO"/>
        <xs:element minOccurs="0" name="IS_PORTIN_ENABLED" type="BooleanTypeO"/>
        <xs:element minOccurs="0" name="PMSISDN" type="MobileNumberTypeO"/>
        <xs:element minOccurs="0" name="PORTIN_REFERENCE_NO" type="StringTypeO"/>
        <xs:element minOccurs="0" name="IS_REAL_NO" type="BooleanTypeO"/>
        <xs:element minOccurs="0" name="IS_REAL_USER_INFO_PROVIDED" type="BooleanTypeO"/>
        <xs:element minOccurs="0" name="REAL_USER_INFO"  type="ArrayOfREALUSER_DETAILS"/>
        <xs:element minOccurs="0" name="VAT_NUMBER" type="StringLen20zType"/>
        <xs:element minOccurs="0" name="ENTRY_TYPE" type="IntTypeO"/>
        <xs:element minOccurs="0" name="IS_EMAIL" type="BooleanTypeO"/>
        <xs:element minOccurs="0" name="ADDITIONAL_1" type="Alphanumeric50TypeO"/>
        <xs:element minOccurs="0" name="ADDITIONAL_2" type="Alphanumeric50TypeO"/>
      </xs:sequence>
    </xs:complexType>
    """

    iccid: str
    preferred_language: str
    title: str
    last_name: str
    first_name: str
    gender: str
    date_of_birth: str
    place_of_birth: str
    residence_country: str
    italy_national: Literal['Yes', 'EU', 'NON_EU']
    nationality: str
    house_number: str
    house_name: str
    post_code: str
    street: str
    city: str
    state: str
    document_type: Literal['EU_ID', 'PASSPORT', 'ITALIAN_ID_CARD',
                           'ITALIAN_PERMIT', 'ITALIAN_DRIVING_LICENCE',
                           'ITALIAN_PASSPORT']
    document_number: str
    issuer: str
    date_of_issue: str
    valid_till: str
    retailer_name: str
    retailerid: str
    chk_sms_marketing: Literal[0, 1, '0', '1']
    chk_terms: Union[str, bool]
    chk_photocopy: Union[str, bool]
    chk_age: Union[str, bool]
    sms_update: Union[str, bool]
    dynamic_allocation_status: int

    msisdn: Optional[str]
    puk_code: Optional[str]
    province: Optional[str]
    email_id: Optional[str]
    alternative_contact_number: Optional[str]
    tax_code: Optional[str]
    list_of_attachments: Optional[ArrayOfATTACHMENT]
    ivrlanguage: Optional[str]
    comune_code: Optional[str]
    country_of_birth: Optional[str]
    type: Optional[str]
    minor_dob: Optional[str]
    minor_title: Optional[str]
    minor_first_name: Optional[str]
    minor_last_name: Optional[str]
    minor_gender: Optional[str]
    accept_minor: Optional[Union[str, bool]]
    is_portin_enabled: Optional[Union[str, bool]]
    pmsisdn: Optional[str]
    portin_reference_no: Optional[str]
    is_real_no: Optional[Union[bool, str]]
    is_real_user_info_provided: Optional[Union[bool, str]]
    real_user_info: Optional[ArrayOfREALUSER_DETAILS]
    vat_number: Optional[str]
    entry_type: Optional[Literal[0, 1, 2, '0', '1', '2']]
    is_email: Optional[Union[bool, str]]
    additional_1: Optional[str]
    additional_2: Optional[str]

    @classmethod
    @validator('chk_terms', 'chk_photocopy', 'chk_age', 'sms_update',
               'accept_minor', 'is_portin_enabled', 'is_real_no',
               'is_real_user_info_provided', 'is_email')
    def _validate_boolean(cls, v):
        if isinstance(v, int):
            if v in [0, 1]:
                v = str(bool(v))
            else:
                raise ValueError('')
        v = str(v).lower()

        if v not in ('true', 'false'):
            raise ValueError('')
        return v


class ItalyRegisterSubscriberRequest(BasePlintronModel):
    details: RegisterSubscriberITALYType


if __name__ == "__main__":
    import json

    a = {
        'iccid': '8939540000004000194', 'msisdn': '393760400019', 'preferred_language': 'en', 'title': 'EDU_TITLE_DR',
     'last_name': 'Jeremic', 'first_name': 'Igor', 'gender': 'MALE', 'date_of_birth': '01/01/1976',
     'place_of_birth': 'Serbia', 'province': 'far', 'email_id': 'igor@digitalcube.rs',
     'alternative_contact_number': ' 3937658422', 'residence_country': 'Italy', 'italy_national': 'Yes',
     'nationality': 'RS', 'house_number': '18', 'house_name': 'TheHouse', 'post_code': '11000',
     'street': 'Bul Crvene Armije', 'city': 'City Name', 'state': 'Good One State', 'tax_code': 'JRMGRI76A01Z158V',
     'vat_number': '1234', 'document_type': 'PASSPORT', 'document_number': '123456', 'issuer': 'Govermnent',
     'date_of_issue': '01/01/2021', 'valid_till': '01/01/2026', 'list_of_attachments': [{'EXTENSION': 'jpeg',
                                                                                         'VALUE': '/9j/4AAQSkZJRgABAQEAYABgAAD/4RDiRXhpZgAATU0AKgAAAAgABAE7AAIAAAAIAAAISodpAAQAAAABAAAIUpydAAEAAAAQAAAQyuocAAcAAAgM',
                                                                                         },
                                                                                        {'EXTENSION': 'jpg',
                                                                                         'VALUE': '/9j/4AAQSkZJRgABAQEBLAEsAAD/2wBDAAMCAgMCAgMDAwMEAwMEBQgFBQQEBQoHBwYIDAoMDAsKCwsNDhIQDQ4RDgsLEBYQERMUFRUVDA8XGBYUGBIUFRT/2wBDAQMEBAUEBQkFBQkUDQsNFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBQUFBT/wAARCAQIAyADAREAAhEBAxEB'}],
     'retailer_name': 'retailer_name', 'retailerid': '123abc', 'chk_sms_marketing': 1, 'chk_terms': 'true',
     'chk_photocopy': 'true', 'chk_age': 'true', 'sms_update': 'true', 'dynamic_allocation_status': 1,
     'ivrlanguage': 'en', 'comune_code': 'F132'}

    a = {
         "MSISDN": "393510002132",
         "ICCID": "8939350010000002374",
         "PREFERRED_LANGUAGE": "ENGLISH",
         "TITLE": "Mr",
         "LAST_NAME11": "VISHVA",
         "FIRST_NAME": "VIGNESH",
         "GENDER": "Male",
         "DATE_OF_BIRTH": "07/07/1993",
         "PLACE_OF_BIRTH": "india",
         "PROVINCE": "EE",
         "EMAIL_ID": "vignesh.vr@plintron.com",
         "ALTERNATIVE_CONTACT_NUMBER": "8148260097",
         "RESIDENCE_COUNTRY": "ITALY",
         "ITALY_NATIONAL": "EU",
         "NATIONALITY": "INDIAN",
         "HOUSE_NUMBER": "12",
         "HOUSE_NAME": "vicky",
         "POST_CODE": "10024",
         "STREET": "STREET",
         "CITY": "CITY",
         "STATE": "STATE",
         "TAX_CODE": "",
         "DOCUMENT_TYPE": "PASSPORT",
         "DOCUMENT_NUMBER": "12345",
         "ISSUER": "vignesh",
         "DATE_OF_ISSUE": "06/06/2010",
         "VALID_TILL": "06/06/2020",
         "LIST_OF_ATTACHMENTS": {
             "ATTACHMENT": [
                 {
                     "EXTENSION": "pdf",
                     "VALUE": "JVBERi0xLjQKJf////8KNTAgMCBvYmoKPDwvTGVuZ3RoIDI0NzYKL1N1YnR5cGUgL1hN \nTAovVHlwZSAvTWV0YWRhdGEKPj4Kc3RyZWFtCjw/eHBhY2tldCBiZWdpbj0n77u/JyBp \nZD0nVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkJz8+Cjx4OnhtcG1ldGEgeDp4bXB0az0i \nMy4xLTcwMSIgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iPgogIDxyZGY6UkRGIHhtbG5z \nOnJkZj0iaHR0cDovL3d3dy53My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4LW5zIyI+ \nCiAgICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIiB4bWxuczp4bXA9Imh0dHA6 \nLy9ucy5hZG9iZS5jb20veGFwLzEuMC8iPgogICAgICA8eG1wOkNyZWF0ZURhdGU+MjAx \nNS0xMi0zMVQwNzo0NDozOVo8L3htcDpDcmVhdGVEYXRlPgogICAgICA8eG1wOkNyZWF0 \nb3JUb29sPk5pdHJvIFBybyA3ICAoNy4gMi4gMC4gMTIpPC94bXA6Q3JlYXRvclRvb2w+ \nCiAgICAgIDx4bXA6TW9kaWZ5RGF0ZT4yMDE1LTEyLTMxVDA3OjQ0OjQxWjwveG1wOk1v \nZGlmeURhdGU+CiAgICAgIDx4bXA6TWV0YWRhdGFEYXRlPjIwMTUtMTItMzFUMDc6NDQ6"
                 },
                 {
                     "EXTENSION": "pdf",
                     "VALUE": "JVBERi0xLjQKJf////8KNTAgMCBvYmoKPDwvTGVuZ3RoIDI0NzYKL1N1YnR5cGUgL1hN \nTAovVHlwZSAvTWV0YWRhdGEKPj4Kc3RyZWFtCjw/eHBhY2tldCBiZWdpbj0n77u/JyBp \nZD0nVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkJz8+Cjx4OnhtcG1ldGEgeDp4bXB0az0i \nMy4xLTcwMSIgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iPgogIDxyZGY6UkRGIHhtbG5z \nOnJkZj0iaHR0cDovL3d3dy53My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4LW5zIyI+ \nCiAgICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIiB4bWxuczp4bXA9Imh0dHA6 \nLy9ucy5hZG9iZS5jb20veGFwLzEuMC8iPgogICAgICA8eG1wOkNyZWF0ZURhdGU+MjAx \nNS0xMi0zMVQwNzo0NDozOVo8L3htcDpDcmVhdGVEYXRlPgogICAgICA8eG1wOkNyZWF0 \nb3JUb29sPk5pdHJvIFBybyA3ICAoNy4gMi4gMC4gMTIpPC94bXA6Q3JlYXRvclRvb2w+ \nCiAgICAgIDx4bXA6TW9kaWZ5RGF0ZT4yMDE1LTEyLTMxVDA3OjQ0OjQxWjwveG1wOk1v \nZGlmeURhdGU+CiAgICAgIDx4bXA6TWV0YWRhdGFEYXRlPjIwMTUtMTItMzFUMDc6NDQ6"
                 },
                 {
                     "EXTENSION": "pdf",
                     "VALUE": "JVBERi0xLjQKJf////8KNTAgMCBvYmoKPDwvTGVuZ3RoIDI0NzYKL1N1YnR5cGUgL1hN \nTAovVHlwZSAvTWV0YWRhdGEKPj4Kc3RyZWFtCjw/eHBhY2tldCBiZWdpbj0n77u/JyBp \nZD0nVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkJz8+Cjx4OnhtcG1ldGEgeDp4bXB0az0i \nMy4xLTcwMSIgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iPgogIDxyZGY6UkRGIHhtbG5z \nOnJkZj0iaHR0cDovL3d3dy53My5vcmcvMTk5OS8wMi8yMi1yZGYtc3ludGF4LW5zIyI+ \nCiAgICA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIiB4bWxuczp4bXA9Imh0dHA6 \nLy9ucy5hZG9iZS5jb20veGFwLzEuMC8iPgogICAgICA8eG1wOkNyZWF0ZURhdGU+MjAx \nNS0xMi0zMVQwNzo0NDozOVo8L3htcDpDcmVhdGVEYXRlPgogICAgICA8eG1wOkNyZWF0 \nb3JUb29sPk5pdHJvIFBybyA3ICAoNy4gMi4gMC4gMTIpPC94bXA6Q3JlYXRvclRvb2w+ \nCiAgICAgIDx4bXA6TW9kaWZ5RGF0ZT4yMDE1LTEyLTMxVDA3OjQ0OjQxWjwveG1wOk1v \nZGlmeURhdGU+CiAgICAgIDx4bXA6TWV0YWRhdGFEYXRlPjIwMTUtMTItMzFUMDc6NDQ6"
                 }
             ]
         },
         "RETAILER_NAME": "Vishnu",
         "RETAILERID": "RT12345",
         "CHK_SMS_MARKETING": "1",
         "CHK_TERMS": "true",
         "CHK_PHOTOCOPY": "true",
         "CHK_AGE": "true",
         "SMS_UPDATE": "true",
         "DYNAMIC_ALLOCATION_STATUS": "1",
         "IVRLANGUAGE": "",
         "COMUNE_CODE": "Z230",
         "COUNTRY_OF_BIRTH": "ACATE",
         "TYPE": "1",
         "MINOR_DOB": "28/05/1991",
         "MINOR_TITLE": "Mr",
         "MINOR_FIRST_NAME": "Bright",
         "MINOR_LAST_NAME": "Jeeva Prakash",
         "MINOR_GENDER": "MALE",
         "ACCEPT_MINOR": "true",
         "IS_PORTIN_ENABLED": "true",
         "PMSISDN": "8976543245",
         "PORTIN_REFERENCE_NO": "12",
         "IS_REAL_NO": "true",
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
    _ = RegisterSubscriberITALYType(**a)
    print(_)
