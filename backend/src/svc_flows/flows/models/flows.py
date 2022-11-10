import tshared.models.base as base_models
from tortoise import fields, Model
from .messages import flow_message


class Option(Model, base_models.BaseModelOptions):
    class Meta:
        table = "flows_options"
        unique_together = (('id_tenant', 'key'),)
        app = 'flows'


class Flow(Model, base_models.BaseModel):
    class Meta:
        table = "flows"
        app = 'flows'

    instance = fields.CharField(max_length=32, null=False, index=True)
    id_instance = fields.UUIDField(null=False, index=True)

    important = fields.BooleanField(default=False, null=True)
    archived = fields.BooleanField(default=False)

    type = fields.ForeignKeyField('flows.LookupFlowType', null=False, index=True)
    visibility = fields.ForeignKeyField('flows.LookupFlowVisibility', null=True, index=True)
    priority = fields.ForeignKeyField('flows.LookupFlowPriorities', null=True, index=True)

    html = fields.TextField(null=True)
    text = fields.TextField(null=True)
    data = fields.JSONField(null=True)

    attached_documents = fields.JSONField(null=True)
    mentioned_persons = fields.JSONField(null=True)

    email_sent_to = fields.JSONField(null=True)
    timesheet_logged = fields.JSONField(null=True)

    automatically_merged_with = fields.ForeignKeyField('flows.Flow', null=True)
    last_created_timestamp_for_auto_merged_flows = fields.DatetimeField(null=True)

    parent_1st_level = fields.UUIDField(index=True, null=True)
    parent_2nd_level = fields.UUIDField(index=True, null=True)
    parent_3rd_level = fields.UUIDField(index=True, null=True)

    default_fields = ('id', 'created', 'created_by', 'type_id', 'visibility_id', 'priority_id', 'html', 'data', 'active',
                      'archived', 'important', 'created_by_display_name', 'created_by_profile_picture')

    connected_fields = {
        'attached_documents_info': 'cache11.attached_documents_info',
        'mentioned_persons_info': 'cache11.mentioned_persons_info',
        'created_by_display_name': 'cache11.created_by_display_name',
        'created_by_profile_picture': 'cache11.created_by_profile_picture',
    }

    allowed_ordering = {
        'created': 'created',
    }

    async def generated_message(self):
        return await flow_message(self)

    async def mk_cache(self, handler, data: dict = None, prefetched=False, ):
        await self.fetch_related('cache11')
        translations_dict = {}
        c1n_cache_dict = {'item': self}
        if self.instance == "sales":
            from ..messages.deals.messages import messages as generate_deal_message
            data = self.data
            for lang in ("en", "it", "de", "sr"):
                try:
                    message = await generate_deal_message(handler=handler, data=data, lang=lang)
                except Exception as e:
                    raise
                translations_dict[lang] = message
                c1n_cache_dict["search"] = translations_dict

        try:
            c11_cache_dict = {'item': self}

            if data:
                c11_cache_dict.update(data)

            await base_models. \
                mk_cache_lookups_code_and_names(itm_model_name='flow',
                                                itm_model=self,
                                                handler=handler,
                                                conn_name='conn_flows',
                                                prefetched=prefetched,
                                                C11=C11Flow,
                                                C1N=C1NFlows,
                                                c11_cache_dict=c11_cache_dict,
                                                c1n_cache_dict=c1n_cache_dict,
                                                svc_lookups_info=[])
        except Exception as e:
            raise
        await self.fetch_related('cache11')
        return self


class C11Flow(Model):
    class Meta:
        table = "flows_cache_11_flows"
        app = 'flows'

    flow = fields.OneToOneField('flows.Flow', related_name='cache11')

    attached_documents_info = fields.JSONField(null=True)
    mentioned_persons_info = fields.JSONField(null=True)

    created_by_display_name = fields.CharField(max_length=255, null=True)
    created_by_profile_picture = fields.CharField(max_length=255, null=True)


class C1NFlows(Model):
    class Meta:
        table = "flows_cache_1n"
        app = 'flows'

    flow = fields.ForeignKeyField('flows.Flow', related_name='cache1n')

    language = fields.CharField(max_length=32, null=False)

    search = fields.TextField(null=True)