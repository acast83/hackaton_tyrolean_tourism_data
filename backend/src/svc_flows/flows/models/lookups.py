from tortoise import fields, Model
import tshared.models.base as base_models


class LookupFlowType(Model, base_models.BaseModelLookup):
    class Meta:
        table = "flows_lookup_flow_types"
        unique_together = (('id_tenant', 'code'),)
        app = 'flows'


class TranslationFlowType(Model):
    class Meta:
        table = "flows_translation_lookup_flow_types"
        app = 'flows'

    lookup = fields.ForeignKeyField('flows.LookupFlowType', null=False, index=True, related_name='translations')
    language = fields.CharField(max_length=32, null=False)
    value = fields.TextField(null=False)


class LookupFlowVisibility(Model, base_models.BaseModelLookup):
    class Meta:
        table = "flows_lookups_flow_visibility"
        unique_together = (('id_tenant', 'code'),)
        app = 'flows'


class TranslationLookupFlowVisibility(Model):
    class Meta:
        table = "flows_translation_lookups_flow_visibility"
        app = 'flows'

    lookup = fields.ForeignKeyField('flows.LookupFlowVisibility', null=False, index=True, related_name='translations')
    language = fields.CharField(max_length=32, null=False)
    value = fields.TextField(null=False)


class LookupFlowPriorities(Model, base_models.BaseModelLookup):
    class Meta:
        table = "flows_lookups_flow_priorities"
        unique_together = (('id_tenant', 'code'),)
        app = 'flows'


class TranslationLookupFlowPriorities(Model):
    class Meta:
        table = "flows_translation_lookups_flow_priorities"
        app = 'flows'

    lookup = fields.ForeignKeyField('flows.LookupFlowPriorities', null=False, index=True, related_name='translations')
    language = fields.CharField(max_length=32, null=False)
    value = fields.TextField(null=False)

# {{ lookup_model }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
