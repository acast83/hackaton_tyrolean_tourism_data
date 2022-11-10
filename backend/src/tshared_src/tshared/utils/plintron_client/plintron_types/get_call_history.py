import json
from typing import Literal, Union, Optional
from pydantic import validator
from datetime import date, datetime
from decimal import Decimal

# from svc_services import BasePlintronModel
from tshared.utils.plintron_client.plintron_types.base_plintron_model import BasePlintronModel


__all__ = [
    "GetCallHistoryResponse",
    "BillingHistoryResponse",
]


Balance = Union[int, float, Decimal]


class BillingHistoryResponse(BasePlintronModel):
    """
    <xs:complexType name="BillingHistoryResponseType">
        <xs:sequence>
            <xs:element name="CALL_TYPE" type="NameType" minOccurs="0" />
            <xs:element name="CALLED_NUMBER" type="StringType" minOccurs="0" />
            <xs:element name="DATE" type="StringType" minOccurs="0" />
            <xs:element name="TIME" type="StringType" minOccurs="0" />
            <xs:element name="DURATION" type="StringType" minOccurs="0" />
            <xs:element name="COST" type="Balance_CostType" minOccurs="0" />
            <xs:element name="TARIFF_PLAN" type="NameType" minOccurs="0" />
            <xs:element name="BUNDLE_NAME" type="StringType" minOccurs="0" />
            <xs:element name="BUNDLE_CODE" type="Bundle_CodeTypeO" minOccurs="0" />
            <xs:element name="INITIAL_FREE_UNITS" type="StringTypesO" minOccurs="0" />
            <xs:element name="FINAL_FREE_UNITS" type="StringTypesO" minOccurs="0" />
            <xs:element name="TOTAL_USED_UNITS" type="StringTypesO" minOccurs="0" />
            <xs:element name="TOTAL_USED_BYTES" type="StringTypesO" minOccurs="0" />
            <xs:element name="REMAINING_MAIN_BALANCE" type="StringTypesO" minOccurs="0" />
            <xs:element name="REASON" type="StringTypesO" minOccurs="0" />
            <xs:element name="SUB_TYPE" type="StringTypesO" minOccurs="0" />
            <xs:element name="MODE_OF_DEDUCTION" type="StringTypesO" minOccurs="0" />
            <xs:element name="USED_ROAMING_ALLOWANCE" type="StringTypesO" minOccurs="0" />
            <xs:element name="USED_HOME_ALLOWANCE" type="StringTypesO" minOccurs="0" />
            <xs:element name="OVERAGE_CHARGES" type="StringTypesO" minOccurs="1" />
            <xs:any namespace="##any" processContents="skip" minOccurs="0" maxOccurs="unbounded" />
        </xs:sequence>
    </xs:complexType>
    """

    call_type: Optional[str]
    called_number: Optional[str]
    date: Optional[str]
    time: Optional[str]
    duration: Optional[str]
    cost: Optional[Balance]
    tariff_plan: Optional[str]
    bundle_name: Optional[str]
    bundle_code: Optional[str]
    initial_free_units: Optional[Balance]
    final_free_units: Optional[Balance]
    total_used_units: Optional[Balance]
    total_used_bytes: Optional[Balance]
    remaining_main_balance: Optional[Balance]
    reason: Optional[str]
    sub_type: Optional[str]
    mode_of_deduction: Optional[str]
    used_roaming_allowance: Optional[Balance]
    used_home_allowance: Optional[str]
    overage_charges: Optional[Balance]
    bundle_charge: Optional[Balance]


class GetCallHistoryResponse(BasePlintronModel):
    """
    <xs:element name="GET_CALL_HISTORY_RESPONSE">
        <xs:complexType>
            <xs:sequence minOccurs="0">
                <xs:element minOccurs="0" name="DETAIL" type="BillingHistoryResponseType" maxOccurs="unbounded" />
            </xs:sequence>
        </xs:complexType>
    </xs:element>
    """

    detail: Optional[
        Union[
            list[BillingHistoryResponse],
            BillingHistoryResponse
        ]
    ]

    def len(self):
        if self.detail:
            if isinstance(self.detail, list):
                return len(self.detail)
            return 1
        return 0

    def __len__(self):
        return self.len()


if __name__ == "__main__":
    from typing import Callable
    from pathlib import Path

    # asset_path = Path('../../../../../tests_integration/assets/sim_manager/'
    #                   'plintron/plintron_GET_CALL_HISTORY.json').resolve()
    asset_path = Path('../../../../../tests_integration/assets/sim_manager/'
                      'plintron/plintron_GET_CALL_HISTORY_one.json').resolve()
    with asset_path.open() as f:
        response = json.load(f)

    a = GetCallHistoryResponse(**response)
    print(a.len())
    print(len(a))
