from tortoise import fields, timezone, Model
import tshared.models.base as base_models
import jwt
from tortoise.transactions import in_transaction


class Option(Model, base_models.BaseModelOptions):
    class Meta:
        table = "tenants_options"
        unique_together = (('id_tenant', 'key'),)
        app = 'tenants'


class Tenant(Model, base_models.BaseModelNoTenant):
    class Meta:
        table = "tenants"
        app = 'tenants'

    code = fields.CharField(max_length=64, unique=True)
    name = fields.TextField()

    allowed_ordering = {
        'code': 'code',
        'name': 'name',
    }

    protected_fields = None
    default_fields = None
    mandatory_fields_for_visibility = ('code', 'name')
    serialization_fields_order = (
        'id', 'code', 'name', 'touched', 'created', 'last_updated', 'created_by', 'last_updated_by')

    search_term = fields.TextField(null=True)


class RegisterUserQueue(Model, base_models.BaseModel):
    class Meta:
        table = 'tenants_register_users_queue'
        app = 'tenants'

    first_name = fields.CharField(max_length=128, null=True)
    last_name = fields.CharField(max_length=128, null=True)
    username = fields.CharField(max_length=64, null=True)
    password = fields.CharField(max_length=128, null=True)
    email = fields.CharField(max_length=128, null=True)
    mobile_phone = fields.CharField(max_length=128, null=True)

    pin = fields.CharField(max_length=8)


class Captcha(Model):
    class Meta:
        table = 'tenants_captcha'
        app = 'tenants'

    id = fields.UUIDField(pk=True)
    created = fields.DatetimeField(default=timezone.now)
    value = fields.CharField(max_length=32)


class UserSettings(Model, base_models.BaseModel):
    class Meta:
        table = "tenants_user_settings"
        app = 'tenants'
        unique_together = (('user_id', 'key'),)

    user = fields.ForeignKeyField('tenants.User', index=True)
    key = fields.CharField(128)

    # TODO: promeniti u JsonField, ali tako da moze da podrzi json tipa "en" tj string
    # TODO: trenutno imamo problem, python3.10 dekoridranje puca, prolazi broj, dict, verovatno
    # TODO: i list, ali string puca cak i ako je opkoljen navodnicima

    value = fields.TextField(null=False)


class User(Model, base_models.BaseModel):
    class Meta:
        table = "tenants_users"
        unique_together = (('id_tenant', 'uid'), ('id_tenant', 'username'),
                           ('id_tenant', 'email', 'active'),
                           ('id_tenant', 'mobile_phone', 'active'))
        app = 'tenants'

    uid = fields.CharField(max_length=7)
    username = fields.CharField(max_length=255, null=True)
    password = fields.CharField(max_length=128, null=True)
    first_name = fields.CharField(max_length=128, null=True)
    last_name = fields.CharField(max_length=128, null=True)

    profile_picture = fields.CharField(max_length=128, null=True)

    email = fields.CharField(max_length=128, null=True)
    mobile_phone = fields.CharField(max_length=128, null=True)

    mobile_phone_is_verified = fields.BooleanField(default=False)
    email_is_verified = fields.BooleanField(default=False)

    account_verified = fields.BooleanField(default=False)

    uid_prefix = 'U'
    uid_total_size = 6
    uid_alphabet = base_models.uid_alphabet

    reset_password_uuid = fields.UUIDField(null=True, unique=True)
    reset_password_uuid_expiration_timestamp = fields.DatetimeField(null=True)

    pin_login_uuid = fields.UUIDField(null=True, unique=True)
    pin_login_pin = fields.CharField(max_length=32, null=True, unique=False)

    delete_account_key = fields.UUIDField(null=True, unique=True)
    delete_account_pin = fields.CharField(max_length=32, null=True)
    delete_account_key_expired_after = fields.DatetimeField(null=True)
    delete_account_timestamp = fields.DatetimeField(null=True)

    no_search = fields.BooleanField(default=None, null=True)

    data = fields.JSONField(default=None, null=True)

    role = fields.ForeignKeyField('tenants.LookupUserRole', default=None, null=True)

    name_case_fields = {'first_name', 'last_name'}

    connected_fields = {
        'display_name': 'cache11.display_name',
        'groups': 'groups.id'
    }

    allowed_ordering = {
        'uid': 'uid',
        'username': 'username',
        'first_name': 'cache11__display_name_lc',
        'last_name': 'cache11__last_name_lc',
        'display_name': 'cache11__display_name_lc'
    }

    protected_fields = ('password', 'touched', 'merged_with')
    default_fields = ('id', 'uid', 'username', 'first_name', 'last_name', 'cache11.display_name', 'role_id')
    mandatory_fields_for_visibility = ('username', 'first_name')
    serialization_fields_order = (
        'id', 'id_tenant', 'uid', 'active', 'username', 'first_name', 'last_name', 'email', 'mobile_phone')

    patchable_by_user = ('first_name', 'last_name', 'email', 'mobile_phone', 'password', 'profile_picture', 'data')
    patchable_by_admin = ('first_name', 'last_name', 'email', 'mobile_phone', 'username', 'password', 'profile_picture', 'data')

    async def mk_cache(self, handler):

        async with in_transaction('conn_tenants'):
            display_name = ' '.join([n.strip().capitalize() for n in [self.first_name, self.last_name] if n])
            if not display_name:
                display_name = self.username if self.username else ''

            search = ' '.join([str(x).capitalize()
                               for x in [self.username, self.first_name if self.first_name else "",
                                         self.last_name if self.last_name else "",
                                         self.email if self.email else ""]])
            search = search.lower()
            args = {
                'display_name': display_name,
                'display_name_lc': display_name.lower(),
                'last_name_lc': self.last_name.lower() if self.last_name else None,
                'search': search
            }

            commit = False
            cache = await C11Users.filter(user=self).get_or_none()
            if not cache:
                commit = True
                cache = C11Users(user=self)

            for arg in args:
                if hasattr(cache, arg) and args[arg] != getattr(cache, arg):
                    setattr(cache, arg, args[arg])
                    commit = True

            if commit:
                await cache.save()

        return commit


class C11Users(Model):
    class Meta:
        table = "tenants_c11_users"
        app = 'tenants'

    user = fields.OneToOneField('tenants.User', related_name='cache11')

    display_name = fields.CharField(max_length=255, null=True)

    display_name_lc = fields.CharField(max_length=255, null=True)
    last_name_lc = fields.CharField(max_length=255, null=True)

    created_by_display_name = fields.CharField(max_length=255, null=True)
    last_updated_by_display_name = fields.CharField(max_length=255, null=True)

    created_by_display_profile_picture = fields.CharField(max_length=255, null=True)
    last_updated_by_display_profile_picture = fields.CharField(max_length=255, null=True)
    search = fields.TextField(null=True)


class DBChangeLog(Model):
    class Meta:
        table = 'tenants_changelogs'
        app = 'tenants'

    created = fields.DatetimeField(auto_now=True)
    id_tenant = fields.UUIDField()
    model = fields.CharField(max_length=64)


class Session(Model, base_models.BaseModel):
    class Meta:
        table = "tenants_sessions"
        app = 'tenants'

    user = fields.ForeignKeyField('tenants.User', on_delete='RESTRICT')

    ttl = fields.IntField(null=True, default=3600 * 24 * 7)
    expires_on = fields.DatetimeField(null=True)

    def token(self):
        payload = {
            'id': str(self.id),
            'created': int(self.created.timestamp()),
            'expires': int(self.expires_on.timestamp()) if self.expires_on else None,
            'id_user': str(self.created_by),
            'id_tenant': str(self.id_tenant) if self.id_tenant else None
        }

        v2_payload = {
            'id': str(self.id),
            'id_session': str(self.id),
            'created': int(self.created.timestamp()),
            'expires': int(self.expires_on.timestamp()) if self.expires_on else None,
            'id_user': str(self.user_id),
            'permissions': 0,
            'id_groups': [],
            'id_tenant': str(self.id_tenant)
        }

        from base3.config_keys import _private_key
        j = jwt.encode(v2_payload, _private_key, algorithm='RS256')

        return j.decode('ascii') if type(j) != str else j
