import tshared.models.base as base_models
from tortoise import fields, Model


class Option(Model, base_models.BaseModelOptions):
    class Meta:
        table = "sms_options"
        unique_together = (('id_tenant', 'key'),)
        app = 'sms'


class ReceivedSMS(Model, base_models.BaseModel):
    class Meta:
        table = "sms_received"
        app = 'sms'

    from_number = fields.CharField(max_length=32)
    to_number = fields.CharField(max_length=32)
    message = fields.TextField(null=True)
    raw = fields.JSONField(null=True)

    polled = fields.DatetimeField(null=True, default=None)


class SMSQueue(Model, base_models.BaseModel):
    class Meta:
        table = "sms_queue"
        app = 'sms'
        
        unique_together = (('id_tenant', 'external_id'),)

    target_number = fields.CharField(max_length=64, null=False)
    message = fields.TextField(null=False)
    scheduled_not_send_before_timestamp = fields.DatetimeField(null=True)
    sent_to_gateway = fields.DatetimeField(null=True)
    external_id = fields.CharField(64, index=True, null=True)
    price = fields.DecimalField(10,4,null=True)
    initial_response = fields.JSONField(null=True)
    status = fields.JSONField(null=True)
    delivery_confirmed_timestamp = fields.DatetimeField(null=True)
    delivery_report_response=fields.JSONField(null=True)