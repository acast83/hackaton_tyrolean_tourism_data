from tortoise import fields, Model
import tshared.models.base as base_models


class LookupUserPermission(Model, base_models.BaseModelLookup):
    class Meta:
        table = "tenants_lookup_user_permissions"
        unique_together = (('id_tenant', 'code'),)
        app = 'tenants'


class TranslationLookupUserPermission(Model):
    class Meta:
        table = "tenants_translation_lookup_user_permissions"
        app = 'tenants'

    lookup = fields.ForeignKeyField('tenants.LookupUserPermission', null=False, index=True, related_name='translations')
    language = fields.CharField(max_length=32, null=False)
    value = fields.TextField(null=False)


class LookupUserRole(Model, base_models.BaseModelLookup):
    class Meta:
        table = "tenants_lookup_user_roles"
        unique_together = (('id_tenant', 'code'),)
        app = 'tenants'

    permissions: fields.ManyToManyRelation['LookupUserPermission'] = fields.ManyToManyField('tenants.LookupUserPermission', related_name='in_roles')


class TranslationLookupUserRole(Model):
    class Meta:
        table = "tenants_translation_lookup_user_roles"
        app = 'tenants'

    lookup = fields.ForeignKeyField('tenants.LookupUserRole', null=False, index=True, related_name='translations')
    language = fields.CharField(max_length=32, null=False)
    value = fields.TextField(null=False)


class LookupUserGroup(Model, base_models.BaseModelLookup):
    class Meta:
        table = "tenants_lookup_user_groups"
        unique_together = (('id_tenant', 'code', 'group_code'),)
        app = 'tenants'

    group_code = fields.CharField(max_length=32)

    users = fields.ManyToManyField('tenants.User', related_name='groups')


class LookupPreferedLanguage(Model, base_models.BaseModelLookup):
    class Meta:
        table = "tenants_lookups_prefered_language"
        unique_together = (('id_tenant', 'code'),)
        app = 'tenants'


class TranslationLookupPreferedLanguage(Model):
    class Meta:
        table = "tenants_translation_lookups_prefered_language"
        app = 'tenants'

    lookup = fields.ForeignKeyField('tenants.LookupPreferedLanguage', null=False, index=True, related_name='translations')
    language = fields.CharField(max_length=32, null=False)
    value = fields.TextField(null=False)


# TODO: rename this into user-group instead user_group
class TranslationLookupUserGroup(Model):
    class Meta:
        table = "tenants_translation_lookup_user_groups"
        app = 'tenants'

    lookup = fields.ForeignKeyField('tenants.LookupUserGroup', null=False, index=True, related_name='translations')
    language = fields.CharField(max_length=32, null=False)
    value = fields.TextField(null=False)


class LookupOrgUnit(Model, base_models.BaseModelLookup):
    class Meta:
        table = "tenants_lookup_org_units"
        unique_together = (('id_tenant', 'code'),)
        app = 'tenants'


class TranslationLookupOrgUnit(Model):
    class Meta:
        table = "tenants_translation_lookup_org_units"
        app = 'tenants'

    lookup = fields.ForeignKeyField('tenants.LookupOrgUnit', null=False, index=True, related_name='translations')
    language = fields.CharField(max_length=32, null=False)
    value = fields.TextField(null=False)

# {{ lookup_model }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
