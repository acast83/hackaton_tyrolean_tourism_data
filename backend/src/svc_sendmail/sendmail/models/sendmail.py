import tshared.models.base as base_models
from tortoise import fields, Model


class Option(Model, base_models.BaseModelOptions):
    class Meta:
        table = "sendmail_options"
        unique_together = (('id_tenant', 'key'),)
        app = 'sendmail'


class MailQueue(Model, base_models.BaseModel):
    class Meta:
        table = "sendmail_mail_queue"
        app = 'sendmail'

    sender_email = fields.CharField(max_length=128, null=False)
    sender_display_name = fields.CharField(max_length=255, null=True)

    receiver_email = fields.CharField(max_length=128, null=False)
    receiver_display_name = fields.CharField(max_length=255, null=True)

    cc_receivers_list = fields.JSONField(null=True)
    bcc_receivers_list = fields.JSONField(null=True)

    subject = fields.TextField(null=True)
    body = fields.TextField(null=True)
    html_body = fields.TextField(null=True)

    status = fields.JSONField(null=True)

    sent_to_gateway = fields.DatetimeField(null=True)
    read_by_user = fields.DatetimeField(null=True)

    attachments = fields.JSONField(null=True)