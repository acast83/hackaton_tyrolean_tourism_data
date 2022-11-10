from tortoise import fields, timezone, Model
import tshared.models.base as base_models


class LookupMessageSendingStatus(Model, base_models.BaseModelLookup):
    class Meta:
        table = "telegram_lookups_message_sending_status"
        unique_together = (('id_tenant', 'code'),)
        app = 'telegram'


class TranslationLookupMessageSendingStatus(Model):
    class Meta:
        table = "telegram_translation_lookups_message_sending_status"
        app = 'telegram'

    lookup = fields.ForeignKeyField('telegram.LookupMessageSendingStatus', null=False, index=True, related_name='translations')
    language = fields.CharField(max_length=32, null=False)
    value = fields.TextField(null=False)


# {{ lookup_model }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
