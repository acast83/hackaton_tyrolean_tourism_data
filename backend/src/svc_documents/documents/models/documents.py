import tshared.models.base as base_models
from tortoise import fields, Model


class Option(Model, base_models.BaseModelOptions):
    class Meta:
        table = "documents_options"
        unique_together = (('id_tenant', 'key'),)
        app = 'documents'


class Document(Model, base_models.BaseModel):
    class Meta:
        table = 'documents'
        app = 'documents'
        indexes = (('instance', 'id_instance'),)

    instance = fields.CharField(max_length=128, null=True)
    id_instance = fields.CharField(max_length=128, index=True)

    order_on_instance = fields.IntField(null=True)

    path_on_instance = fields.CharField(max_length=255, default='/')
    order_on_instance_path = fields.IntField(null=True)

    filename = fields.CharField(max_length=255, null=True)
    filesize = fields.IntField(null=True)
    filetype = fields.CharField(max_length=32, null=True)

    document_type_code = fields.CharField(max_length=128, null=True)
    document_description = fields.TextField(null=True)

    # storage_location = fields.CharField(max_length=255, null=True)
    hash256 = fields.CharField(max_length=255, null=True)

    owner_rwd_policy = fields.JSONField(null=False, default={'read': True, 'write': True, 'delete': True})
    default_user_groups_rwd_policy = fields.JSONField(null=False,
                                                      default={'read': True, 'write': False, 'delete': False})
    default_users_rwd_policy = fields.JSONField(null=False, default={'read': True, 'write': False, 'delete': False})
    default_all_unauthorized_rwd_policy = fields.JSONField(null=False,
                                                           default={'read': False, 'write': False, 'delete': False})

    default_fields = ('id', 'created', 'filename', 'filesize', 'thumbnail', 'location', 'instance', 'id_instance', 'document_type_code', 'document_description', 'filetype')
    serialization_fields_order = (
        'id', 'id_tenant', 'instance', 'id_instance', 'filename', 'filesize', 'location', 'thumbnail')

    location = fields.CharField(max_length=255, null=True)
    thumbnail = fields.CharField(max_length=255, null=True)

    metadata = fields.JSONField(null=True)

    allowed_ordering = {
        'created': 'created',
        'filename': 'filename',
    }

    async def mk_cache(self, handler):
        pass


class DocumentSharing:
    can_read = fields.BooleanField(default=True)
    can_modify = fields.BooleanField(default=False)
    can_delete = fields.BooleanField(default=False)


class DocumentSharedWithUserGroup(Model, DocumentSharing):
    class Meta:
        table = 'documents_shared_user_groups'
        app = 'documents'
        unique_together = (('document', 'id_user_group'),)

    document = fields.ForeignKeyField('documents.Document', related_name='shared_user_groups')
    id_user_group = fields.UUIDField(null=False)


class DocumentSharedWithUsers(Model, DocumentSharing):
    class Meta:
        table = 'documents_shared_users'
        app = 'documents'
        unique_together = (('document', 'id_user'),)

    document = fields.ForeignKeyField('documents.Document', related_name='shared_users')
    id_user = fields.UUIDField(null=False)


class C11Document(Model):
    class Meta:
        table = "documents_cache_11"
        app = 'documents'

    document = fields.OneToOneField('documents.Document', related_name='cache11')

    created_by_display_name = fields.CharField(max_length=255, null=True)
    last_updated_by_display_name = fields.CharField(max_length=255, null=True)
    created_by_display_profile_picture = fields.CharField(max_length=255, null=True)
    last_updated_by_display_profile_picture = fields.CharField(max_length=255, null=True)

    shared_with_list_of_users_with_profile_pictures = fields.JSONField(null=True)
    shared_with_list_of_user_groups = fields.JSONField(null=True)