import zeep
from typing import Optional, Union, Callable


__all__ = [
    "get_type",
    "PlintronTypeConstructor"
]


def filter_dict(obj: dict, condition: Callable[[any], bool]) -> dict:
    if not isinstance(obj, dict):
        raise TypeError(f'filter_dict() supports only dict objects, '
                        f'but {type(obj)} supplied.')
    result = dict()

    for k, v in obj.items():
        if isinstance(v, dict):
            result[k] = filter_dict(obj=v, condition=condition)
        elif condition(v):
            result[k] = v
    return result


def rm_nones(obj: dict) -> dict:
    """Deletes keys from dictionary if value is None."""

    if not isinstance(obj, dict):
        raise TypeError(f'rm_nones accepts only dicts objects, '
                        f'but {type(obj)} is supplied.')

    return filter_dict(obj=obj, condition=lambda x: x is not None)


def get_type(plintron_client, plintron_type_name: str,
             body: dict, to_rmnones: bool = True
             ) -> zeep.xsd.CompoundValue:
    if to_rmnones:
        body = rm_nones(body)
    compound_type = plintron_client.get_type(plintron_type_name)
    return compound_type(**body)


class PlintronTypeConstructor:

    def __init__(self, client: Union[zeep.Client, zeep.AsyncClient]):
        self._client = client

    def enable_bundle_auto_renewal_type(self, *,
                                        imsi, msisdn, icc_id, bundle_code,
                                        renewal_mode, card_number, card_id):
        body = {
            'IMSI': imsi, 'MSISDN': msisdn, 'ICCID': icc_id,
        }
        body = rm_nones(body)
        body_2 = {
            'BUNDLE_CODE': bundle_code, 'RENEWAL_MODE': renewal_mode,
            'CARD_NUMBER': card_number, 'CARD_ID': card_id
        }
        body_2 = rm_nones(body_2)

        ftype = self._client.get_type('EnableBundleAutoRenewalType')
        return ftype(**body, **body_2)

    def cancel_bundle_type(self, *,
                           bundle_code,
                           msisdn, imsi, icc_id,
                           cancel_date, reason):
        """
        CancelBundleType(BUNDLE_CODE: StringTypeM,
                         ({MSISDN: MSISDNType} | {IMSI: IMSIType} | {ICC_ID: ICCIDType}),
                         CANCEL_DATE: DATE,
                         REASON: StringTypeO
                         )
        """
        body = {
            'IMSI': imsi, 'MSISDN': msisdn, 'ICC_ID': icc_id,
        }
        body = rm_nones(body)
        body_2 = {
            'BUNDLE_CODE': bundle_code, 'CANCEL_DATE': cancel_date,
            'REASON': reason
        }
        body_2 = rm_nones(body_2)

        ftype = self._client.get_type('CancelBundleType')
        return ftype(**body, **body_2)

    # noinspection PyShadowingNames
    def get_type(self, type: str, to_rmnones: bool = True, **arguments):
        if to_rmnones:
            arguments = rm_nones(arguments)
        ftype = self._client.get_type(type)
        return ftype(**arguments)

    def register_subscriber_italy_type(self, **arguments):
        return self.get_type(type='RegisterSubscriberITALYType', **arguments)

    def update_subscriber_italy_type(self, **arguments):
        return self.get_type(type='REQUESTUPDATESUBSCRIBERITALY', **arguments)

    def get_transaction_det_type(self, **arguments):
        return self.get_type(type='GetTransactionDetType', **arguments)

    def portin_request_details_type(self, **arguments):
        return self.get_type(type='PortinRequestDetailsType', **arguments)

    def portout_request_details_type(self, **arguments):
        return self.get_type(type='PortoutRequestDetailsType', **arguments)

    def do_auto_top_up_type(self, **arguments):
        return self.get_type(type='DoAutoTopUpType', **arguments)

    def do_schedule_top_up_type(self, **arguments):
        return self.get_type(type='DoScheduleTopUpType', **arguments)

    def do_bundle_top_up_type(self, **arguments):
        return self.get_type(type='DoBundleTopUpType', **arguments)

