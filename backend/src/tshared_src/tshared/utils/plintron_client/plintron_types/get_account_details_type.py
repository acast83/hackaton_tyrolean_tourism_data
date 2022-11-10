from typing import Literal, Union, Optional
from pydantic import validator
from datetime import date, datetime
from decimal import Decimal

# from svc_services import BasePlintronModel
from tshared.utils.plintron_client.plintron_types.base_plintron_model import BasePlintronModel


__all__ = [
    "GetAccountDetailsResponseType",
    "GetAccountDetailsRequestType",
    "SubsSubCategoriesType",
    "SubCategoryType",
]


Balance = Union[int, float, Decimal]
RrbsDate = Union[str, date]

# Subscriber Status
# 0 - Not Blacklisted
# 1 - Blacklisted
SubscriberStatus = Literal[0, 1, '0', '1']

# SIM Status
# 0 - Not blocked
# 1 - Blocked
# 2 - Paused Subscriber (SIM Custody)
# 3 - Fraudulent Block
# 4 - Permanent Block
SimStatus = Literal[0, 1, 2, 3, 4, '0', '1', '2', '3', '4']

# Possible Life Cycle states of a subscriber are
# - Idle
# - Active
# - Grace1
# - Grace2
# - Expired
LifeCycleState = Literal['Idle', 'Active', 'Grace1', 'Grace2', 'Expired']

# Subscriber Type
# 1 - Pre-paid
# 2 - Post-paid
# 3 - Enterprise Pre-paid
# 4 - Reserved
# 5 - Enterprise Post-paid
SubsType = Literal[1, 2, 3, 4, 5, '1', '2', '3', '4', '5']

# Call Back Service Status
# 1 - Enabled
# 0 - Disabled
Cbs = Literal[0, 1, '0', '1']

# A Subscriber level Indicator which indicates whether a subscriber can perform
# a TOPUP or not.
# 0 - Topup service disabled
# 1 - Top-up service enabled
TopupInd = Literal[0, 1, '0', '1']

# MNP indicator
# 0 - Regular
# 1 - Ported-in
# 2 - Ported-out
MnpInd = Literal[0, 1, 2, '0', '1', '2']

# Possible values are:
# 0 - NA
# 1 - Parent (Parent of the Family account)
# 2 - Child (Child in the Family account)
# 3 - Common Family Account (Common Family account is created to combine Parent
#     and Child and to share the services within family members.)
FamilyMember = Literal[0, 1, 2, 3, '0', '1', '2', '3']

# Status of the family account
# 0 - Inactive
# 1 - Active
FamilyStatus = Literal[0, 1, '0', '1']
Flag = Union[Literal[0, 1, '0', '1'], bool]

"""
SubCategoryTypeType
   <xs:simpleType name="SubCategoryTypeType">
      <xs:restriction base="xs:string">
         <xs:enumeration value="NUS" />
      </xs:restriction>
   </xs:simpleType>
"""

SubCategoryTypeType = Literal['NUS']
"""
   <xs:simpleType name="ResSimCategoryType">
      <xs:restriction base="xs:string">
         <xs:enumeration value="GO_ONLINE_SIM"/>    
         <xs:enumeration value="NORMAL_SIM"/>    
      </xs:restriction>
   </xs:simpleType>
"""
ResSimCategory = Literal['GO_ONLINE_SIM', 'NORMAL_SIM']
DateWithTimeType = Union[str, datetime]


def validate_flag(v):
    if isinstance(v, str):
        v = v.lower()
        if v in ('true', 'false'):
            v = v == 'true'
        elif v in ('0', '1'):
            pass
    return str(int(v))


class SubCategoryType(BasePlintronModel):
    """
           <xs:complexType name="SubCategoryType">
              <xs:sequence minOccurs="0">
                 <xs:element name="TYPE" type="SubCategoryTypeType"/>
                 <xs:element name="STATUS" type="Value0or1Type"/>
                 <xs:element name="ID" type="StringTypeM"/>
                 <xs:element name="EXPIRY" type="RrbsDateTypeO"/>
                 <xs:element name="LAST_UPDATED_ON" type="RrbsDateTypeO"/>
                 <xs:element name="REMAINING_COUNTER" type="NumberLen5zTypeO"/>
              </xs:sequence>
           </xs:complexType>
    """
    type: Optional[SubCategoryTypeType]
    status: Optional[Flag]
    id: Optional[str]
    expiry: Optional[RrbsDate]
    last_updated_on: Optional[RrbsDate]
    remaining_counter: Optional[int]

    @classmethod
    @validator('status')
    def validate_flag(cls, v):
        return validate_flag(v)


class SubsSubCategoriesType(BasePlintronModel):
    """
     <xs:complexType name="SubsSubCategoriesType">
       <xs:sequence minOccurs="0" >
         <xs:element name="SUB_CATEGORY" type="SubCategoryType"/>
       </xs:sequence>
     </xs:complexType>
    <xs:complexType name="SubCategoryType">
       <xs:sequence minOccurs="0">
          <xs:element name="TYPE" type="SubCategoryTypeType"/>
          <xs:element name="STATUS" type="Value0or1Type"/>
          <xs:element name="ID" type="StringTypeM"/>
          <xs:element name="EXPIRY" type="RrbsDateTypeO"/>
          <xs:element name="LAST_UPDATED_ON" type="RrbsDateTypeO"/>
          <xs:element name="REMAINING_COUNTER" type="NumberLen5zTypeO"/>
       </xs:sequence>
    </xs:complexType>
    """
    sub_categories: Union[list[SubCategoryType], SubCategoryType]


class GetAccountDetailsResponseType(BasePlintronModel):
    """
    <xs:element name="GET_ACCOUNT_DETAILS_RESPONSE">
      <xs:complexType>
        <xs:sequence minOccurs="0">
          <xs:element name="MSISDN" type="MSISDNWithoutCCTypeO" minOccurs="0" />
          <xs:element name="NETWORK_ID" type="NetworkIdTypeO" minOccurs="0" />
          <xs:element name="MHA_PIN" type="IdTypeO" minOccurs="0" />
          <xs:element name="ACCOUNT_STATUS" type="IdTypeO" minOccurs="0" />
          <xs:element name="VALIDITY_DATE" type="RrbsDateTypeO" minOccurs="0" />
          <xs:element name="CURRENT_BALANCE" type="BalanceTypeO" minOccurs="0" />
          <xs:element name="LANGUAGE_ID" type="LanguageIdTypeO" minOccurs="0" />
          <xs:element name="VMS_PIN" type="IdTypeO" minOccurs="0" />
          <xs:element name="TRANS_PIN" type="IdTypeO" minOccurs="0" />
          <xs:element name="PLAN_ID" type="IdTypeO" minOccurs="0" />
          <xs:element name="SUBSCRIBER_STATUS" type="IdTypeO" minOccurs="0" />
          <xs:element name="SIM_STATUS" type="IdTypeO" minOccurs="0" />
          <xs:element name="LIFE_CYCLE_STATE" type="NameTypeO" minOccurs="0" />
          <xs:element name="SUBS_TYPE" type="SubTypeO" minOccurs="0" />
          <xs:element name="MAIN_BALANCE" type="BalanceTypeO" minOccurs="0" />
          <xs:element name="CBS" type="IdTypeO" minOccurs="0" />
          <xs:element name="PROMO_BALANCE" type="BalanceTypeO" minOccurs="0" />
          <xs:element name="PROMO_BALANCE_VALIDITY_DATE" type="RrbsDateTypeO" minOccurs="0" />
          <xs:element name="TOPUP_IND" type="IdTypeO" minOccurs="0" />
          <xs:element name="MNP_IND" type="IdTypeO" minOccurs="0" />
          <xs:element name="ACCOUNT_ID" type="AccountIdTypeO" minOccurs="0" />
          <xs:element name="FAMILY_ACCOUNT_ID" type="FamilyAccIdTypeO" minOccurs="0" />
          <xs:element name="FAMILY_ACCOUNT_BALANCE" type="BalanceTypeO" minOccurs="0" />
          <xs:element name="FAMILY_MEMBER_TYPE" type="FamilyMemberTypeO" minOccurs="0" />
          <xs:element name="FAMILY_STATUS" type="FamilyStatusTypeO" minOccurs="0" />
          <xs:element name="LTE_EXPIRY_DATE" type="RrbsDateTypeO" minOccurs="0" />
          <xs:element name="DISCOUNT_CODE_AVAILABLE" type="FlagTypeO"  minOccurs="0" />
          <xs:element name="DEDICATED_ACCOUNT_BALANCE" type="BalanceTypeO" minOccurs="0" />
          <xs:element name="ACTUAL_CREDIT_LIMIT" type="BalanceTypeO" minOccurs="0" />
          <xs:element name="AVAILABLE_CREDIT_LIMIT" type="BalanceTypeO" minOccurs="0" />
          <xs:element name="BUNDLE_TOPUP_INDICATOR" type="FlagTypeO"  minOccurs="0" />
          <xs:element name="OBA_BUNDLE_CODE" type="BundleCodeTypeO" minOccurs="0" />
          <xs:element name="OBA_DUE_AMOUNT" type="BalanceTypeO" minOccurs="0" />
          <xs:element name="FIRST_ACTIVATION_DATE" type="RrbsDateTypeO" minOccurs="0" />
          <xs:element name="LAST_TOPUP_DATE" type="RrbsDateTypeO" minOccurs="0" />
          <xs:element name="FLH_SUBSCRIPTION_STATUS" type="FlagTypeO"  minOccurs="0" />
          <xs:element name="IMMEDIATE_EXPIRY_PROMO_BALANCE" type="BalanceTypeO"  minOccurs="0" />
          <xs:element name="IMMEDIATE_PROMO_EXPIRY_DATE" type="RrbsDateTypeO"  minOccurs="0" />
          <xs:element name="ICC_ID" type="ICCIDTypeO" minOccurs="0"/>
          <xs:element name="PRIMARY_IMSI" type="IMSITypeO" minOccurs="0"/>
          <xs:element name="SECONDARY_IMSI" type="IMSITypeO" minOccurs="1"/>
          <xs:element name="PCN_STATUS" type="IdTypeO" minOccurs="0" />
          <xs:element name="PDN_STATUS" type="IdTypeO" minOccurs="1" />
          <xs:element name="IS_SUBSCRIBER_REGISTERED" type="Value0or1Type"/>
          <xs:element name="REGISTRATION_DATE" type="RrbsDateTypeO" minOccurs="1"/>
          <xs:element name="RLH_STATUS" type="xs:string" minOccurs="0"/>
          <xs:element name="RLH_STATUS_UPDATED_DATE" type="RrbsDateTypeO" minOccurs="1"/>
          <xs:element name="LOAN_BALANCE" type="BalanceTypeO"/>
          <xs:element name="LOAN_EXPIRY_DATE" type="RrbsDateTypeO"/>
          <xs:element name="LOAN_OUTSTANDING" type="BalanceTypeO" minOccurs="1"/>
          <xs:element name="LAST_ACTIVITY_DATE" type="RrbsDateTypeO" minOccurs="1"/>
          <xs:element name="SUBS_CATEGORY" type="Value1or2Type" minOccurs="1"/>
          <xs:element name="ZIPCODE" type="xs:string" minOccurs="1"/>
          <xs:element name="RSH" type="Value0or1Type" minOccurs="0"/>
          <xs:element name="SUBS_SUB_CATEGORIES" type="SubsSubCategoriesType" minOccurs="0"/>
          <xs:element name="PORTED_OUT_IVR" type="Value0or1Type" minOccurs="0"/>
          <xs:element name="ATR_ID" type="NameLen50TypeO" minOccurs="0"/>
          <xs:element name="SIM_CATEGORY" type="ResSimCategoryType" minOccurs="0"/>
          <xs:element name="OBA_FLAG" type="Value0or1Type" minOccurs="0"/>
          <xs:element name="SIM_ACTIVATED_DATE" type="DateWithTimeTypeO" minOccurs="0"/>
          <xs:element name="PRELOADED_AVAILABLE_FLAG" type="FlagTypeO" minOccurs="0"/>
          <xs:element name="WHOLESALE_PACKAGE_ID" type="NameLen50TypeO" minOccurs="0"/>
          <xs:element name="VVM_ENABLED" type="Value0or1Type" minOccurs="0"/>
          <xs:element name="CATEGORY" type="AlphaNumericLen20TypeO" minOccurs="1"/>
          <xs:any namespace="##any" processContents="skip" minOccurs="0" maxOccurs="unbounded"/>
        </xs:sequence>
      </xs:complexType>
    </xs:element>
    """

    msisdn: Optional[str]
    network_id: Optional[int]
    mha_pin: Optional[int]
    account_status: Optional[int]
    validity_date: Optional[RrbsDate]
    current_balance: Optional[Balance]
    language_id: Optional[int]
    vms_pin: Optional[int]
    trans_pin: Optional[int]
    plan_id: Optional[int]
    subscriber_status: Optional[SubscriberStatus]
    sim_status: Optional[SimStatus]
    life_cycle_state: Optional[LifeCycleState]
    subs_type: Optional[SubsType]
    main_balance: Optional[Balance]
    cbs: Optional[Cbs]
    promo_balance: Optional[Balance]
    promo_balance_validity_date: Optional[RrbsDate]
    topup_ind: Optional[TopupInd]
    mnp_ind: Optional[MnpInd]
    account_id: Optional[str]
    family_account_id: Optional[str]
    family_account_balance: Optional[Balance]
    family_member_type: Optional[FamilyMember]
    family_status: Optional[FamilyStatus]
    lte_expiry_date: Optional[RrbsDate]
    discount_code_available: Optional[Flag]
    dedicated_account_balance: Optional[Balance]
    actual_credit_limit: Optional[Balance]
    available_credit_limit: Optional[Balance]
    bundle_topup_indicator: Optional[Flag]
    oba_bundle_code: Optional[str]
    oba_due_amount: Optional[Balance]
    first_activation_date: Optional[RrbsDate]
    last_topup_date: Optional[RrbsDate]
    flh_subscription_status: Optional[Flag]
    immediate_expiry_promo_balance: Optional[Balance]
    immediate_promo_expiry_date: Optional[RrbsDate]
    icc_id: Optional[Union[int, str]]
    primary_imsi: Optional[Union[int, str]]
    secondary_imsi: Optional[Union[int, str]]
    pcn_status: Optional[int]
    pdn_status: Optional[int]
    is_subscriber_registered: Optional[Flag]
    registration_date: Optional[RrbsDate]
    rlh_status: Optional[str]
    rlh_status_updated_date: Optional[RrbsDate]
    loan_balance: Optional[Balance]
    loan_expiry_date: Optional[RrbsDate]
    loan_outstanding: Optional[Balance]
    last_activity_date: Optional[RrbsDate]
    subs_category: Optional[Flag]
    zipcode: Optional[str]
    rsh: Optional[Flag]
    subs_sub_categories: Optional[SubsSubCategoriesType]
    ported_out_ivr: Optional[Flag]
    atr_id: Optional[str]
    sim_category: Optional[ResSimCategory]
    oba_flag: Optional[Flag]
    sim_activated_date: Optional[DateWithTimeType]
    preloaded_available_flag: Optional[Flag]
    wholesale_package_id: Optional[str]
    vvm_enabled: Optional[Flag]
    category: Optional[str]
    """
    """

    def is_active(self):
        return str(self.life_cycle_state).lower() == 'active'

    @classmethod
    @validator(
        "discount_code_available",
        "bundle_topup_indicator",
        "flh_subscription_status",
        "is_subscriber_registered",
        "subs_category",
        "rsh",
        "ported_out_ivr",
        "oba_flag",
        "preloaded_available_flag",
        "vvm_enabled",
    )
    def validate_flag(cls, v):
        return validate_flag(v)


class GetAccountDetailsRequestType(BasePlintronModel):
    """
    <xs:element name="GET_ACCOUNT_DETAILS_REQUEST">
      <xs:complexType>
        <xs:sequence>
          <xs:choice minOccurs="1" maxOccurs="3">
            <xs:element name="MSISDN" type="MSISDNType"/>
            <xs:element name="IMSI" type="IMSIType"/>
            <xs:element name="ICC_ID" type="ICCIDType"/>
            <xs:element name="ACCOUNT_ID" type="AccountIdType"/>
          </xs:choice>
          <xs:element name="GET_PRELOADED_AVAILABLE_FLAG" type="FlagTypeO" minOccurs="0"/>
        </xs:sequence>
      </xs:complexType>
    </xs:element>
    """
    msisdn: Optional[Union[int, str]]
    imsi: Optional[Union[int, str]]
    icc_id: Optional[Union[int, str]]
    account_id: Optional[Union[int, str]]
    get_preloaded_available_flag: Optional[Flag]

    @classmethod
    @validator(
        "get_preloaded_available_flag",
    )
    def validate_flag(cls, v):
        return validate_flag(v)


if __name__ == "__main__":
    from typing import Callable


    def apply_over_dict(obj: dict,
                        check_func: Callable[[any], bool] = lambda x: True,
                        apply_func: Callable[[any], any] = lambda x: x,
                        key_check: Callable[[any], bool] = lambda x: True,
                        key_apply: Callable[[any], any] = lambda x: x
                        ) -> dict:
        """
        Applies some action on dictionary items basing on condition.

        Arguments:
            obj:
            check_func: checks condition of value.
            apply_func: applies action on value if condition is True.
            key_check:  checks key of dictionary.
            key_apply:  applies action on key if condition is True.

        Returns:
            Modified dictionary.
        """

        if isinstance(obj, dict):
            for key in obj.keys():
                if key_check(key):
                    obj[key_apply(key)] = apply_func(
                        apply_over_dict(
                            obj[key],
                            check_func=check_func, apply_func=apply_func,
                            key_check=key_check, key_apply=key_apply
                        )
                    )
                else:
                    obj[key] = apply_over_dict(
                        obj[key],
                        check_func=check_func, apply_func=apply_func,
                        key_check=key_check, key_apply=key_apply
                    )
        else:
            if check_func(obj):
                return apply_func(obj)
        return obj


    example = {
        "MSISDN": "9789000007",
        "NETWORK_ID": "41",
        "MHA_PIN": "",
        "ACCOUNT_STATUS": "1",
        "VALIDITY_DATE": "17-04-2019",
        "CURRENT_BALANCE": "1975.0000",
        "LANGUAGE_ID": "10",
        "VMS_PIN": "5646",
        "TRANS_PIN": "541465",
        "PLAN_ID": "33084",
        "SUBSCRIBER_STATUS": "0",
        "SIM_STATUS": "0",
        "LIFE_CYCLE_STATE": "Active",
        "SUBS_TYPE": "1",
        "MAIN_BALANCE": "1975.0000",
        "CBS": "0",
        "PROMO_BALANCE": "0.0000",
        "PROMO_BALANCE_VALIDITY_DATE": "14-10-2017",
        "TOPUP_IND": "1",
        "MNP_IND": "0",
        "ACCOUNT_ID": "10900021",
        "FAMILY_ACCOUNT_ID": "",
        "FAMILY_ACCOUNT_BALANCE": "0.0000",
        "FAMILY_MEMBER_TYPE": "0",
        "FAMILY_STATUS": "0",
        "LTE_EXPIRY_DATE": "",
        "DISCOUNT_CODE_AVAILABLE": "0",
        "DEDICATED_ACCOUNT_BALANCE": "",
        "ACTUAL_CREDIT_LIMIT": "",
        "AVAILABLE_CREDIT_LIMIT": "",
        "BUNDLE_TOPUP_INDICATOR": "1",
        "OBA_BUNDLE_CODE": "0",
        "OBA_DUE_AMOUNT": "0.0000",
        "FIRST_ACTIVATION_DATE": "",
        "LAST_TOPUP_DATE": "25-09-2017",
        "FLH_SUBSCRIPTION_STATUS": "0",
        "IMMEDIATE_EXPIRY_PROMO_BALANCE": "",
        "IMMEDIATE_PROMO_EXPIRY_DATE": "",
        "ICC_ID": "6666666666666611006",
        "PRIMARY_IMSI": "555555555511006",
        "SECONDARY_IMSI": "444444444411006",
        "PCN_STATUS": "1",
        "PDN_STATUS": "1",
        "IS_SUBSCRIBER_REGISTERED": "0",
        "REGISTRATION_DATE": "",
        "RLH_STATUS": "RLH",
        "RLH_STATUS_UPDATED_DATE": "",
        "LOAN_BALANCE": "0.0000",
        "LOAN_EXPIRY_DATE": "",
        "LOAN_OUTSTANDING": "0.0000",
        "LAST_ACTIVITY_DATE": "25-09-2017",
        "SUBS_CATEGORY": "1",
        "ZIPCODE": "600089",
        "RSH": "1",
        "SUBS_SUB_CATEGORIES": {
            "SUB_CATEGORY": {
                "TYPE": "NUS",
                "STATUS": "1",
                "ID": "1514526525",
                "EXPIRY": "26-11-2019",
                "LAST_UPDATED_ON": "26-12-2019",
                "REMAINING_COUNTER": "8"
            }
        },
        "PORTED_OUT_IVR": "1",
        "ATR_ID": "5.1",
        "SIM_CATEGORY": "GO_ONLINE_SIM",
        "OBA_FLAG": "1",
        "SIM_ACTIVATED_DATE": "07-08-2020 23:00:00",
        "PRELOADED_AVAILABLE_FLAG": "1",
        "WHOLESALE_PACKAGE_ID": "LYCA001",
        "VVM_ENABLED": "1",
        "CATEGORY": "GOLD"
    }

    example = apply_over_dict(example, check_func=lambda x: x == '', apply_func=lambda x: None)
    _ = GetAccountDetailsResponseType(**example)
