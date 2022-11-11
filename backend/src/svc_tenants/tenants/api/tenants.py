import copy
import os
import uuid
import yaml
import json
import bcrypt
import base3.handlers
import tortoise.timezone
import datetime
import tshared.ipc.tenants
import tshared.lookups
import random
import tshared.lookups.cache as lookups
import tshared.ipc.sms as ipc_sms
import tshared.ipc.sendmail as ipc_sendmail
import tshared.ipc.flows as ipc_flows
import tshared.utils.common as common
from base3.test import test_mode
from base3 import http
from base3.core import Base
from tshared.utils.setup_logger import log
from base3.decorators import route, api
from tortoise.transactions import in_transaction
from .. import models
from . import config, app_config
import tshared.ipc.documents as ipc_documents

db_connection = 'conn_tenants'
null_uid = uuid.UUID('00000000-0000-0000-0000-000000000000')

current_file_folder = os.path.dirname(os.path.realpath(__file__))


def bcrypt_pass(passwd: str):
    passwd = passwd.strip()

    from base3.test import test_mode
    if test_mode:
        return passwd

    return bcrypt.hashpw(passwd.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def bcrypt_check(plain_test: str, encoded: str):
    plain_test = plain_test.strip()

    from base3.test import test_mode
    if test_mode:
        return plain_test == encoded

    return bcrypt.checkpw(plain_test.encode('utf-8') if type(plain_test) == str else plain_test, encoded.encode() if type(encoded) == str else encoded)


async def create_user(handler, force_tenant=None):
    body = json.loads(handler.request.body) if handler.request.body else {}

    handler.log.debug(f"CREATE USER {body}")

    global null_uid

    allow_create_user_without_tenant = False

    # only allow create first user, if there is no tenants on system and if there is no any user registered
    # this is special user with permissions to open tenants and other system users
    tenants_count = await models.Tenant.all().count()
    if not tenants_count:
        users_count = await models.User.all().count()
        if not users_count:
            handler.id_tenant = null_uid
            handler.id_user = null_uid
            allow_create_user_without_tenant = True

    if handler.id_tenant == null_uid and force_tenant:
        allow_create_user_without_tenant = True

    if not allow_create_user_without_tenant and handler.id_tenant in (None, null_uid):
        raise http.HttpErrorUnauthorized(id_message='UNAUTHORIZED',
                                         message="User can't be created without authorization")

    body['id_tenant'] = force_tenant if force_tenant else handler.id_tenant
    body['created_by'] = handler.id_user
    body['last_updated_by'] = handler.id_user

    if 'uid' not in body:
        body['uid'] = await models.User.gen_uid(handler.id_tenant)

    try:
        # async with in_transaction(connection_name=db_connection):
        if True:

            handler.log.debug('-' * 100)
            handler.log.debug('creating user')

            handler.log.debug('-' * 20 + ' /-0')

            try:
                user = await models.User.safe_create(body)
            except Exception as e:

                handler.log.debug(str(e))
                raise

            if 'password' in body:
                user.password = bcrypt_pass(body['password'])

            await user.save()

            if 'user_groups' in body:
                for id_group in body['user_groups']:
                    group = await models.LookupUserGroup.filter(id=id_group).get_or_none()
                    if group:
                        await user.groups.add(group)

                # await user.fetch_related('groups')

            await user.mk_cache(handler=handler)

            session = await models.Session.safe_create({
                'id_tenant': force_tenant if force_tenant else handler.id_tenant,
                'created_by': user.id,
                'last_updated_by': user.id,
                'user_id': user.id
            })

            handler.log.debug('-' * 20 + ' /4')

            await session.save()
            handler.log.debug('-' * 20 + ' /5')


    except Exception as e:
        # TODO: LOG e
        handler.log.debug('-' * 20 + ' /e1')

        raise http.HttpInternalServerError(id_message='CREATE_USER_ERROR', message=f'Error creating user {e}')

    res = await user.serialize()
    try:
        res['token'] = session.token()
    except Exception as e:
        raise

    return res, http.status.CREATED


@route('/about')
class TenantsAboutHandler(Base):

    @api(auth=False)
    async def get(self):
        """
        Get about information

        Responses:
           @tenants/GET_200_documentation_get_about.json
        """
        log(self).warn('about has been triggered')

        return {'service': 'tenants', 'config': config, 'app_config': app_config}


@route('/options')
class TenantsOptionsHandler(base3.handlers.BaseOptionsHandler):
    model_Option = models.Option
    db_connection = db_connection


@route('/test')
class XTenantsHandler(base3.handlers.Base):
    @api(auth=False)
    async def get(self,
                  fields='id,code,name'
                  ):
        fields = tuple(fields.split(','))
        return [await t.bulk_serialize(fields=fields) for t in await models.Tenant.all().order_by('created')]


import logging


@route('/log/level')
class TenantsLogLevelHandler(Base):

    @api(auth=False)
    async def get(self):

        from . import svc_name

        l = logging.getLogger(f'services.{svc_name}')
        try:
            return {'level': logging._levelToName[l.level]}
        except Exception as e:
            raise http.HttpInternalServerError(id_message='INTERNAL', message=str(e))

    @api(auth=False)
    async def post(self, level: str):

        from . import svc_name

        l = logging.getLogger(f'services.{svc_name}')
        try:
            l.setLevel(logging._nameToLevel[level.upper()])
        except Exception as e:
            raise http.HttpInternalServerError(id_message='INTERNAL', message=str(e))

        self.log.critical(f'lot level for logger {l} changed to {logging._nameToLevel[level.upper()]}')


@route('/')
class TenantsHandler(base3.handlers.BaseOptionsHandler):

    @api(auth=False)
    async def get(self, fields='id,code,name', no_paginate: bool = True, page: int = 1, per_page: int = 100,
                  order_by: str = 'code', search: str = None):
        """
        Get all tenants

        Parameters:
            fields (query): CSV string of fields (by default it is null, and in this case will be used from personal user setting)
                enum: @Tenant.default_fields
            no_paginate (query): If true, pagination will not be provided. By default, it is True
            page (query): Current page
            per_page (query): Number of items per page
            order_by (query): Order
                enum: @Tenant.allowed_ordering
            search (query): General search

        Responses:
            @tenants/GET_200_documentation_get_tenants.json
        """

        return await models.Tenant.base_get(
            no_paginate=no_paginate, page=page, per_page=per_page, fields=fields, order_by=order_by, search=search,
            lowercased_search_field='search_term')

        # fields = tuple(fields.split(','))
        # return [await t.bulk_serialize(fields=fields) for t in await models.Tenant.all().order_by('created')]

    @api(auth=True)
    async def post(self):
        """
        Post tenant TODO request.body

        RequestBody:
            @tenants/POST_201_documentation_post_tenant.request_body.json

        Responses:
            @tenants/POST_201_documentation_post_tenant.json
        """

        body = json.loads(self.request.body) if self.request.body else {}
        body['created_by'] = self.id_user
        body['last_updated_by'] = self.id_user

        body['search_term'] = ' '.join([body[i] for i in ('code', 'name') if i in body and body[i]]).lower()

        tenant = await models.Tenant.safe_create(body)
        await tenant.save()
        try:
            r = await tenant.serialize()
        except Exception as e:
            raise
        return r, http.status.CREATED


@route('/code/:code')
class TenantsByCodeHandler(base3.handlers.BaseOptionsHandler):
    """
    Parameters:
        code (path): Code
    """

    @api(auth=False)
    async def get(self, code: str):
        """
        Get tenant from code

        Responses:
            @tenants/GET_200_documentation_get_tenant_from_code.json
        """
        tenant = await models.Tenant.filter(code=code).get_or_none()
        if not tenant:
            raise http.HttpErrorNotFound(id_message='TENANT_NOT_FOUND')

        return {'id': tenant.id}


@route('/user_id_by_tenant_code_and_username')
class UserIdByTenantCodeAndUsernameHandler(base3.handlers.BaseOptionsHandler):

    # TODO: implement loxL
    @api(auth=False)  # local=True)
    async def get(self, code: str, username: str):
        """
        Get user ID from code and username TODO test

        Parameters:
            code (query): Code
            username (query): Username

        Responses:
            @tenants/GET_200_documentation_get_id_from_code_and_username.json
        """
        tenant = await models.Tenant.filter(code=code).get_or_none()
        if not tenant:
            raise http.HttpErrorNotFound(id_message='TENANT_NOT_FOUND')

        user = await models.User.filter(id_tenant=tenant.id, username=username, active=True).get_or_none()
        if not user:
            raise http.HttpErrorNotFound(id_message='USER_NOT_FOUND_OR_IT_IS_INACTIVE')

        # TODO: set timeout for this session (probably short one)

        session = models.Session(
            created_by=user.id, last_updated_by=user.id,
            id_tenant=tenant.id, user=user, ttl=None, expires_on=None)

        await session.save()
        token = session.token()

        return {'id_user': user.id, 'id_tenant': tenant.id, 'token': token}


@route('/mk-cache/:table')
class TenantsMkCacheHandler(base3.handlers.BaseOptionsHandler):
    """
    Parameters:
        table (path): Table
    """

    @api()
    async def patch(self, table: str):
        """
        Patch table TODO

        RequestBody:
           @TODO/PATCH_200_documentation_patch.request_body.json

        Responses:
           @TODO/PATCH_200_documentation_patch.json
        """

        table2model = {
            'users': models.User
        }

        if table not in table2model:
            raise http.HttpNotAcceptable(id_message='CACHE_FOR_TABLE_NOT_SUPPORTED', message=table)

        model = table2model[table]

        updated = 0
        async with in_transaction(connection_name=db_connection):
            for item in await model.filter(id_tenant=self.id_tenant).all():
                await item.mk_cache(handler=self)
                updated += 1

        return {'updated': updated}


@route('/users/:id_user')
class TenantsSingleUserHandler(base3.handlers.Base):
    """
    Parameters:
        id_user (path): User ID
    """

    @api(auth=True)
    async def get(self, id_user: uuid.UUID, filters: dict = None, fields: str = None):
        """
        Get specific user

        Parameters:
            filters (query): Filter for allowed columns
            fields (query): CSV string of fields (by default it is null, and in this case will be used from personal user setting)
                enum: @User.default_fields

        Responses:
           @tenants/GET_200_documentation_get_user.json
        """

        if not filters:
            filters = {}

        filters['id_tenant'] = self.id_tenant
        filters['id'] = id_user

        user = await models.User.base_get(expected_one_item=True,  # debug_return_query=True,
                                          json_filters=filters, fields=fields,
                                          prefetched=['cache11', 'groups'])

        return user

    @api(auth=True)
    async def patch(self, id_user: uuid.UUID):
        """
        Patch user

        RequestBody:
           @tenants/PATCH_200_documentation_patch_user.request_body.json

        Responses:
           @tenants/PATCH_200_documentation_patch_user.json
        """

        user, updated = await models.User.base_update(id_user, self)
        if updated:
            await user.save()

        return {'updated': updated}


@route('/users')
class TenantsUserHandler(base3.handlers.Base):

    async def grouped(self, users, group, distinct_user_grouping, filtered_groups=None):

        if filtered_groups and type(filtered_groups) == str:
            filtered_groups = filtered_groups.split(',')

        groups = await lookups.LookupUserGroups.create(self)

        by_groups = {}

        added_users = set()

        all = groups.all_by_index(('group_code', 'code'), )
        for gcode_gname in all:
            gcode, gname = gcode_gname.split(':')
            if gcode != group:
                continue

            g = groups.get(all[gcode_gname])

            if filtered_groups and g['id'] not in filtered_groups:
                continue

            by_groups[g['id']] = {'name': g['translations']['en'], 'users': []}

            pass

        for user in users:
            for group_id in user['groups']:
                if group_id not in by_groups:
                    continue

                if distinct_user_grouping:
                    if user['id'] in added_users:
                        continue

                added_users.add(user['id'])
                by_groups[group_id]['users'].append(user)

        return by_groups

    @api()
    async def get(self, no_paginate=False, page:int=1, per_page:int=50, fields=None,
                  order_by='username', search=None, filters: dict = None,
                  group_by_user_group_code=None,
                  distinct_user_grouping=True,
                  departments=None,
                  force_limit=None,
                  ids_csv: str = None
                  ):
        """
        Get all users # TODO

        Parameters:
            page (query): Current page
            per_page (query): Number of items per page
            search (query): General search
            filters (query): Filter for allowed columns
            fields (query): CSV string of fields (by default it is null, and in this case will be used from personal user setting)
               enum: @User.default_fields
            order_by (query): Order
               enum: @User.allowed_ordering
            no_paginate (query): If true, pagination will not be provided. By default, it is True
            force_limit (query): Limits response item number
            group_by_user_group_code (query):
            distinct_user_grouping (query):
            departments (query):
            ids_csv (query):

        Responses:
           @tenants/GET_200_documentation_get_all_users.json
        """

        if not filters:
            filters = {}

        #        if search:
        filters['no_search__not'] = True

        distinct_user_grouping = (distinct_user_grouping in (True, 'none', 'null', 'True', 'true', '1', 'yes', 'T'))

        if ids_csv and ids_csv not in ('null', 'undefined'):
            res_forced = await models.User.base_get(
                json_filters={'id__in': ids_csv.split(','), "id_tenant": self.id_tenant},
                force_limit=force_limit,
                no_paginate=True,
                fields=fields,
                prefetched=['cache11', 'groups'])

        if departments and distinct_user_grouping:
            raise http.HttpInvalidParam(id_message='DEPARTMENTS_CAN_NOT_BE_COMBINED_WITH_DISTINCT_USER_GROUPING')

        if not fields:
            if hasattr(models.User, 'default_fields'):
                fields = getattr(models.User, 'default_fields')
        else:
            if type(fields) == str:
                fields = fields.split(',')

        if group_by_user_group_code:
            if not no_paginate:
                raise http.HttpNotAcceptable(id_message='INVALID_PARAMS_COMBINATION',
                                             message='group_by_user_group_code and no_paginate=False is not acceptable')

            if 'groups' not in fields:
                fields.append('groups')

        if type(filters) == str:
            filters = json.loads(filters)

        filters['id_tenant'] = self.id_tenant

        if departments:
            filters['groups__in'] = departments.split(',')

        try:
            result = await models.User.base_get(request=self.request, json_filters=filters, force_limit=force_limit,
                                                no_paginate=no_paginate, page=page, per_page=per_page, fields=fields,
                                                order_by=order_by, search=search,
                                                lowercased_search_field='cache11__search',
                                                prefetched=['cache11', 'groups'])
            if not no_paginate and ids_csv and res_forced:
                result["items"].extend(res_forced)
            if no_paginate and ids_csv and res_forced:
                result.extend(res_forced)

            if group_by_user_group_code:
                return await self.grouped(result, group_by_user_group_code, distinct_user_grouping, departments)

            return result

        except Exception as e:
            raise

    @api(auth=True, weak=True, permissions='CREATE_USER')
    async def post(self):
        """
        Post a user   TODO

        RequestBody:
           @tenants/POST_201_documentation_post_user.request_body.json

        Responses:
           @tenants/POST_201_documentation_post_user.json
        """

#        import pdb
#        pdb.set_trace()
        
        return await create_user(self)


@route('/captcha')
class CaptchaHandler(base3.handlers.Base):

    @api(auth=False)
    async def get(self):
        """
        Get Captcha

        Responses:
           @tenants/GET_200_documentation_get_captcha.json
        """

        value = str(random.randint(1111, 9999)).upper()
        captcha = models.Captcha(value=value)
        await captcha.save()
        res = {'id': captcha.id}
        from base3.test import test_mode

        if test_mode:
            res['value'] = value

        return res

    @api(auth=False)
    async def post(self, id: uuid.UUID, value: str):
        """
        Post Captcha    TODO parameters

        Parameters:
            id (body): TODO
            value (body): Value

        RequestBody:
           @tenants/POST_204_documentation_post_captcha.request_body.json

        Responses:
           @tenants/POST_204_documentation_post_captcha.json
        """

        value = value.upper()
        existing = models.Captcha(id=id, value=value).get_or_none()

        if not existing:
            raise http.HttpNotAcceptable(id='INVALID_CAPTCHA')

        return None


@route('/:id_tenant/users')
class TenantsTenantUserHandler(base3.handlers.Base):
    """
    Parameters:
        id_tenant (path): Tenant ID
    """

    @api(permissions='CREATE_USER')
    async def post(self, id_tenant: uuid.UUID):
        """
        Post user

        RequestBody:
           @tenants/POST_201_documentation_post_user_from_tenant.request_body.json

        Responses:
           @tenants/POST_201_documentation_post_user_from_tenant.json
        """

        global null_uid

        if self.id_tenant != null_uid and id_tenant != self.id_tenant:
            raise http.HttpErrorUnauthorized(id_message='UNAUTHORIZED', message="tenant_id not match users tenant_id")

        return await create_user(handler=self, force_tenant=id_tenant)


@route('/redirect/:instance/:id_instance', PREFIX='')
class Redirect(base3.handlers.Base):

    @api(auth=False)  # TODO ?
    async def get(self, instance: str, id_instance: uuid.UUID):
        """
        TODO
        """
        if instance not in ('forgot-password', 'activate'):
            raise http.HttpNotAcceptable(id_message='REDIRECT_INSTANCE_NOT_SUPPORTED')

        if instance == 'forgot-password':
            user = models.User.filter(reset_password_uuid=id_instance).get_or_none()
            if not user:
                raise http.HttpErrorNotFound(id_message='NOT_FOUND')

            return await tshared.ipc.tenants.forgot_password(self.request, id_tenant=user.id_tenant,
                                                             id_instance=id_instance)

        if instance == 'activate':
            registrant = models.RegisterUserQueue.filter(id=id_instance, active=False).get_or_none()
            if not registrant:
                raise http.HttpErrorNotFound(id_message='NOT_FOUND')

            return await tshared.ipc.tenants.activate_account(self.request, id_tenant=registrant.id_tenant,
                                                              id_instance=id_instance)


@route('/delete-user-account')
class DeleteUserAccountStep1(base3.handlers.Base):
    @api()
    async def post(self, password: str = None):

        user = await models.User.filter(id_tenant=self.id_tenant, id=self.id_user, active=True).get_or_none()

        if not user:
            raise http.HttpErrorNotFound

        try:
            uuid.UUID(user.password)
            # password is valid - initial uuid
            # user did not set his password, so we can delete this user without comparing passwords and 2FA

            user.username = f'deleted-{user.id}:{user.username}'
            user.active = None
            user.delete_account_timestamp = tortoise.timezone.now()

            await user.save()

            return {'status_code': 'DELETED'}

        except Exception as e:
            if not password:
                raise http.HttpNotAcceptable(id_message='CURRENT_PASSWORD_MUST_BE_PROVIDED')
            # password is not uuid, try to check with bcrypt

        if not bcrypt_check(password.encode(), user.password.encode()):
            raise http.HttpErrorUnauthorized(id_message='PASSWORD_NOT_MATCH')

        user.delete_account_key = uuid.uuid4()
        user.delete_account_key_expired_after = \
            tortoise.timezone.make_aware(datetime.datetime.now() + datetime.timedelta(seconds=300))

        user.delete_account_pin = str(random.randint(1000, 9999))
        await user.save()

        action = None

        if '@' in user.username:
            result, code = await ipc_sendmail.enqueue(self.request,
                                                      sender_display_name=app_config['reset_password']['from'][
                                                          'display_name'],
                                                      sender_email=app_config['reset_password']['from']['email'],
                                                      receiver_email=user.username,
                                                      receiver_display_name=None,
                                                      subject=f'delete account PIN: {user.delete_account_pin}',
                                                      html_body=f'<p>PIN: {user.delete_account_pin}')

            result, code = await ipc_sendmail.send_enqueued_email(self.request, result['id'])

            if code in (200, 201, 204):
                action = 'email_sent'

        else:
            res, code = await ipc_sms.send_sms(self.request, target=user.username,
                                               message=f'delete account PIN: {user.delete_account_pin}')
            if code in (200, 201, 204):
                action = 'sms_sent'

        return {
            'action': action,
            'status_code': 'WAITING_FOR_CONFIRMATION',
            'confirmation_key': user.delete_account_key,
            'expires_on': str(user.delete_account_key_expired_after),
            'pin_sent_to': user.username,
        }

    @api()
    async def delete(self, delete_account_key: uuid.UUID, pin: str):

        q = models.User.filter(id_tenant=self.id_tenant,
                               id=self.id_user,
                               delete_account_key=delete_account_key,
                               delete_account_key_expired_after__lt=tortoise.timezone.now(),
                               delete_account_pin=pin,
                               delete_account_timestamp__isnull=True
                               )

        user = await q.get_or_none()

        if not user:
            raise http.HttpNotAcceptable(id_message='INVALID_DELETE_ACCOUNT_PARAMS_COMBINATION')

        user.username = f'deleted-{user.id}:{user.username}'
        user.active = None
        user.delete_account_timestamp = tortoise.timezone.now()

        await user.save()


@route('/:id_tenant/sessions')
class TenantSessionHandler(base3.handlers.Base):
    """
    Parameters:
        id_tenant (path): Tenant ID
    """

    @api()
    async def get(self):
        """
        Get tenants session     # TODO

        Responses:
           @tenants/GET_200_documentation_get_session_from_tenacnt.json
        """

        return {'ok': True}

    @api(auth=False)
    async def post(self, id_tenant: uuid.UUID, username: str, password: str, show_user_id: bool = False):
        """
        Post tenants session

        Parameters:
            username (body): Username
            password (body): Password
            show_user_id (body): Boolean value, if True, response will include User ID

        RequestBody:
           @tenants/POST_200_documentation_post_session_from_tenant.request_body.json

        Responses:
           @tenants/POST_200_documentation_post_session_from_tenant.json
        """

        try:
            user = await models.User.filter(id_tenant=id_tenant, username=username, active=True).get_or_none()
        except Exception as e:
            raise

        # TODO: verifikup lozinku !

        if not user:
            raise http.HttpErrorUnauthorized(id_message='UNAUTHORIZED', code='Error logging user')

        if not bcrypt_check(password.encode(), user.password.encode()):
            raise http.HttpErrorUnauthorized(id_message='UNAUTHORIZED', code='Error logging user')

        ttl = 3600 * 24 * 7
        expires_on = datetime.datetime.now() + datetime.timedelta(seconds=ttl)

        session = models.Session(
            created_by=user.id, last_updated_by=user.id,
            id_tenant=id_tenant, user=user, ttl=ttl, expires_on=tortoise.timezone.make_aware(expires_on))

        await session.save()

        token = session.token()

        try:
            self.request.headers.add('Authorization', f'Bearer {token}')
            await ipc_flows.flow(self, instance='users', id_instance=user.id,
                                 type_code='FLOW_TYPE_USER_ACTION', message=f'user logged in',
                                 data={'action': 'USER_LOGGED_IN', 'id_session': str(session.id),
                                       'expires_on': str(expires_on)})
        except Exception as e:
            print("flow not in use")
            pass

        if not show_user_id:
            return {'token': token}

        return {'token': token, 'id': user.id}


@route('/:id_tenant/users/signup')
class TenantsRegisterSignUp(base3.handlers.Base):
    """
    Parameters:
        id_tenant (path): Tenant ID
    """

    @api(auth=False)
    async def post(self, id_tenant: uuid.UUID, value: str):
        """
        Post tenants signup     # TODO explain, add RequestBody for other value types

        Parameters:
            value (body): Value used for signup (username, email, phone number)

        RequestBody:
           @tenants/POST_200_documentation_post_signup_from_tenant.request_body.json

        Responses:
           @tenants/POST_200_documentation_post_signup_from_tenant.json
        """

        value = value.lower().replace(' ', '')

        existing_user = await models.User.filter(id_tenant=id_tenant, username=value).get_or_none()
        if existing_user:
            return {'id': existing_user.id,
                    'required': 'password'}

        elif '@' in value and '.' in value:
            cnt_users_by_email = await models.User.filter(id_tenant=id_tenant, email=value, active=True).count()
            if cnt_users_by_email > 0:
                raise http.HttpNotAcceptable(id_message='GIVEN_EMAIL_IS_NOT_UNIQUE_IN_SYSTEM')

            elif cnt_users_by_email == 0:
                try:
                    registrant = models.RegisterUserQueue(
                        id_tenant=id_tenant,
                        first_name=None,
                        last_name=None,
                        username=value,  # str(uuid.uuid4()),
                        password=str(uuid.uuid4()),  # bcrypt_pass(str(uuid.uuid4())),
                        email=value,
                        mobile_phone=None,
                        created_by=null_uid,
                        last_updated_by=null_uid,
                        active=False,
                        pin=str(random.randint(1000, 9999))
                    )

                    await registrant.save()
                except Exception as e:
                    raise

                result, code = await ipc_sendmail.enqueue(self.request,
                                                          sender_display_name=app_config['reset_password']['from'][
                                                              'display_name'],
                                                          sender_email=app_config['reset_password']['from']['email'],
                                                          receiver_email=value,
                                                          receiver_display_name=value,
                                                          subject=f'activation PIN: {registrant.pin}',
                                                          html_body=f'<p>PIN: {registrant.pin}')

                await ipc_sendmail.send_enqueued_email(self.request, result['id'])

                if test_mode:
                    return {'id': registrant.id, 'pin': registrant.pin, 'required': 'pin'}

                return {'id': registrant.id,
                        'required': 'pin'}

            else:

                user = models.User.filter(id_tenant=id_tenant, email=value).get_or_none()

                user.pin_login_uuid = uuid.uuid4()
                user.pin_login_pin = str(random.randint(1000, 9999))

                await user.save()

                if test_mode:
                    return {'id': user.pin_login_uid,
                            'pin': user.pin_login_pin,
                            'required': 'pin'}

                return {'id': user.pin_login_uid,
                        'required': 'pin'}

        elif common.is_phone_number(value):

            value = common.normalize_phone_number(value)

            cnt_users_by_phone_number = await models.User.filter(id_tenant=id_tenant,
                                                                 active=True,
                                                                 mobile_phone__startswith=value).count()

            if cnt_users_by_phone_number > 1:
                raise http.HttpNotAcceptable(
                    id_message='GIVEN_PHONE_NUMBER_IS_NOT_UNIQUE_IN_SYSTEM_OR_IT_IS_PREFIX_TO_ALREADY_ADDED_PHONE')

            elif cnt_users_by_phone_number == 0:
                registrant = models.RegisterUserQueue(
                    id_tenant=id_tenant,
                    first_name=None,
                    last_name=None,
                    username=value, #str(uuid.uuid4()),
                    password=str(uuid.uuid4()), #bcrypt_pass(str(uuid.uuid4())),
                    email=None,
                    mobile_phone=value,
                    created_by=null_uid,
                    last_updated_by=null_uid,
                    active=False,
                    pin=str(random.randint(1000, 9999))
                )

                await registrant.save()

                try:
                    res, code = await ipc_sms.send_sms(self.request, target=value,
                                                       message=f'activation PIN: {registrant.pin}')
                except Exception as e:
                    raise

                if test_mode:
                    return {'id': registrant.id,
                            'required': 'pin',
                            'pin': registrant.pin}

                return {'id': registrant.id, 'required': 'pin', }

            pass


@route('/:id_tenant/users/signup/step2/:id_user_or_pin_or_id_registrant')
class TenantsRegisterSignUpStep2(base3.handlers.Base):
    """
    Parameters:
        id_tenant (path): Tenant ID
        id_user_or_pin_or_id_registrant (path): TODO
    """

    async def login_existing_user(self, id_tenant, user, value):

        if bcrypt_check(value, user.password):
            session = await models.Session.safe_create({
                'id_tenant': id_tenant,
                'created_by': user.id,
                'last_updated_by': user.id,
                'user_id': user.id
            })
            await session.save()

            self.log.debug(f"Session has been created: {session.id}")

            return {'token': session.token()}, http.status.CREATED
        else:
            self.log.error(f"User tries to login with invalid password")
            raise http.HttpErrorUnauthorized(id_message='INVALID_PASSWORD')

    async def login_existing_user_without_password(self, id_tenant, user):
        session = await models.Session.safe_create({
            'id_tenant': id_tenant,
            'created_by': user.id,
            'last_updated_by': user.id,
            'user_id': user.id
        })
        await session.save()

        return {'token': session.token()}, http.status.CREATED

    @api(auth=False)
    async def post(self, id_tenant: uuid.UUID, id_user_or_pin_or_id_registrant: uuid.UUID, value: str):
        """
        Post 2nd step for signup    # TODO tests, parameters

        Parameters:
            value (body):

        RequestBody:
           @TODO/POST_201_documentation_post.request_body.json

        Responses:
           @TODO/POST_201_documentation_post.json
        """

        # scenario 1: login by username / password

        self.log.debug('Login or Register / step 2')

        user = await models.User.filter(id_tenant=id_tenant, id=id_user_or_pin_or_id_registrant).get_or_none()

        if user:
            self.log.debug(f"User found in database, will try to login {user.username} with provided password")
            return await self.login_existing_user(id_tenant, user, value)

        # # scenario 2: login by already registered user pin
        #
        # user = await models.User.filter(id_tenant=id_tenant, pin_login_uuid=id_user_or_pin_or_id_registrant,
        #                                 pin_login_pin=value)
        #
        # if user:
        #     return self.login_existing_user_without_password(id_tenant, user)

        # scenario 3: login by non existing userq

        registrant = await models.RegisterUserQueue.filter(id_tenant=id_tenant, id=id_user_or_pin_or_id_registrant,
                                                           pin=value).get_or_none()

        if registrant:
            self.log.debug(f"Registrant has been found in database id:{registrant.id} email:{registrant.email} phone:{registrant.mobile_phone}")
            id_user = uuid.uuid4()

            try_user = await models.User.filter(username=registrant.username).get_or_none()
            if try_user:
                self.log.error('User with same username already exists, can not register new one, try reset password')
                raise http.HttpNotAcceptable(id_message="USER_ALREADY_EXISTS", message='User with same username already exists, can not register new one, try reset password')

            try:
                self.log.debug(f"Creating user with id={id_user}")
                user = models.User(
                    uid=await models.User.gen_uid(id_tenant),
                    id=id_user, id_tenant=id_tenant, username=registrant.username, password=registrant.password,
                    first_name=registrant.first_name, last_name=registrant.last_name,
                    email=registrant.email, mobile_phone=registrant.mobile_phone,
                    created_by=id_user, last_updated_by=id_user,

                    email_is_verified=True if registrant.email else False,
                    mobile_phone_is_verified=True if registrant.mobile_phone else False

                )

                installation = os.getenv('INSTALLATION', None)
                if installation and installation == 'opencon':
                    user.role_id = '16c81487-bc95-46e6-99c7-119ade942955'

                # PHONE or email is automticaly verified because this step requires PIN received on phone or email

                await user.save()
                self.log.debug(f"User {id_user} has been saved to database")
            except Exception as e:
                self.log.debug(f"Exception occurred while saving user {e}")
                raise

            session = await models.Session.safe_create({
                'id_tenant': id_tenant,
                'created_by': user.id,
                'last_updated_by': user.id,
                'user_id': user.id
            })
            self.log.debug(f'Creating session {session.id} for the user {id_user}')
            await session.save()

            try:
                import tshared.ipc.conferences as ipc_conferences
            except Exception as e:
                pass

            return {'token': session.token()}, http.status.CREATED

        raise http.HttpNotAcceptable(id_message='INVALID_PIN_OR_PASSWORD', message=value)


@route('/:id_tenant/users/register')
class TenantsRegisterUserHandler(base3.handlers.Base):
    """
    Parameters:
        id_tenant: Tenant ID
    """

    @api(auth=False)
    async def get(self):
        """
        Get registered tenant

        Responses:
           @tenants/GET_200_documentation_get_user_register_from_tenant.json
        """

        with open(current_file_folder + '/../../config/registration.yaml') as f:
            return yaml.safe_load(f)

    @api(auth=False)
    async def post(self, id_tenant: uuid.UUID, username: str, password: str, first_name: str = None,
                   last_name: str = None, email: str = None, mobile_phone: str = None, ttl: int = 300):
        """
        Post registered user    # TODO tests, parameter

        Parameters:
            username (body): Username
            password (body): Password
            first_name (body): First name
            last_name (body): Last name
            email (body): Email
            mobile_phone (body): Mobile phone
            ttl (body): TODO ?

        RequestBody:
           @TODO/POST_201_documentation_post.request_body.json

        Responses:
           @TODO/POST_201_documentation_post.json
        """
        username = username.strip()
        password = password.strip()

        tenant = await models.Tenant.filter(id=id_tenant).get_or_none()
        if not tenant:
            raise http.HttpErrorNotFound(id_message='TENANT_NOT_FOUND')

        if not username:
            raise http.HttpErrorNotFound(id_message='MISSING_USERNAME')

        username = username.lower()
        existing_user = await models.User.filter(id_tenant=id_tenant, username=username).get_or_none()

        if existing_user:
            raise http.HttpErrorNotFound(id_message='USERNAME_CAN_NOT_BE_USED',
                                         message=f'username {username} is not allowed for a new account')

        existing_registrant = await models.RegisterUserQueue.filter(
            id_tenant=id_tenant, username=username, created__gt=tortoise.timezone.make_aware(
                datetime.datetime.now() - datetime.timedelta(seconds=ttl))).count()

        if existing_registrant > 0:
            raise http.HttpErrorNotFound(id_message='USERNAME_CAN_NOT_BE_USED',
                                         message=f'username {username} is not allowed for a new account.')

        try:

            registrant = models.RegisterUserQueue(
                id_tenant=id_tenant,
                first_name=first_name,
                last_name=last_name,
                username=username,
                password=bcrypt_pass(password),
                email=email,
                mobile_phone=mobile_phone,
                created_by=null_uid,
                last_updated_by=null_uid,
                active=False,
                pin=str(random.randint(1000, 9999))
            )

            await registrant.save()

            if email:
                result, code = await ipc_sendmail.enqueue(self.request,
                                                          sender_display_name=app_config['reset_password']['from'][
                                                              'display_name'],
                                                          sender_email=app_config['reset_password']['from']['email'],
                                                          receiver_email=email,
                                                          receiver_display_name=first_name,
                                                          subject=f'activation PIN: {registrant.pin}',
                                                          html_body=f'<p>PIN: {registrant.pin}'
                                                          )

                id_email = result['id']
                result = await ipc_sendmail.send_enqueued_email(self.request, id_email)


        except Exception as e:
            raise

        res = {'id': registrant.id}

        # must be included from here !
        from base3.test import test_mode

        if test_mode:
            res['pin'] = registrant.pin

        res['pin'] = registrant.pin

        return res


@route('/:id_tenant/users/forgot-password')
class TenantsUserForgotPasswordHandler(base3.handlers.Base):
    """
    Parameters:
        id_tenant (path): Tenant ID
    """

    @api(auth=False)
    async def post(self, id_tenant: uuid.UUID, username: str, expire_in=300, uri: str = None):
        """
        Post user forgot password   # TODO tests

        Parameters:
            username (body): Username
            expire_in (body): Seconds til expiration TODO ?

        RequestBody:
           @TODO/POST_201_documentation_post.request_body.json

        Responses:
           @TODO/POST_201_documentation_post.json
        """

        self.log.debug(f'forgot password requested for {username}')

        user = await models.User.filter(id_tenant=id_tenant, username=username).get_or_none()

        # always return successful result
        res = {'id_message': 'EMAIL_SEND',
               'message': 'Email with reset password link has been send to your email address'}

        if not user:
            self.log.debug(f'user not found ')
            return res

        try:

            if not user.email:
                self.log.debug('USER_EMAIL_NOT_PROVIDED')
                raise http.HttpNotAcceptable(id_message='USER_EMAIL_NOT_PROVIDED')

            # must be included from here !
            from base3.test import test_mode

            if not test_mode:
                expire_in = 300 if expire_in > 300 else expire_in

            user.reset_password_uuid = uuid.uuid4()
            user.reset_password_uuid_expiration_timestamp = tortoise.timezone.make_aware(
                datetime.datetime.now() + datetime.timedelta(seconds=expire_in))

            self.log.debug(f'reset_password_uuid {user.reset_password_uuid} has been created')
            await user.save()

            _uri = f'{app_config["base_url"]}redirect' if not uri else uri

            self.log.debug(f"SENDING MAIL TO app_config['reset_password']['from']['email'] : pwd uid:{user.reset_password_uuid}")
            result, code = await ipc_sendmail.enqueue(self.request,
                                                      sender_display_name=app_config['reset_password']['from'][
                                                          'display_name'],
                                                      sender_email=app_config['reset_password']['from']['email'],
                                                      receiver_email=user.email,
                                                      receiver_display_name=user.first_name,
                                                      subject='reset password link',
                                                      html_body=f'<p>{_uri}/{user.reset_password_uuid}'
                                                                f'<p>link will expire {user.reset_password_uuid_expiration_timestamp}\n\nreset password code is:{user.reset_password_uuid}',
                                                      # html_body=f'<p>use id: f{user.reset_password_uuid} before {user.reset_password_uudocid_expiration_timestamp}'
                                                      )

            id_email = result['id']
            self.log.debug(f"ID_EMAIL {id_email}")

            result = await ipc_sendmail.send_enqueued_email(self.request, id_email)

            self.log.debug(f'email sent successfully')

        except Exception as e:
            self.log.critical(f'Exception occurred {e}')
            raise

        # must be included from here !
        from base3.test import test_mode

        if test_mode:
            res['test_mode'] = {
                'user.reset_password_uuid': str(user.reset_password_uuid),
                'user.reset_password_uuid_expiration_timestamp': str(
                    tortoise.timezone.make_naive(user.reset_password_uuid_expiration_timestamp))}

        return res


@route('/:id_tenant/users/reset-password/:reset_password_uuid')
class TenantsUserResetPasswordHandler(base3.handlers.Base):
    """
    Parameters:
        id_tenant (path): Tenant ID
        reset_password_uuid (body): Password reset ID
    """

    @api(auth=False)
    async def post(self, id_tenant: uuid.UUID, reset_password_uuid: uuid.UUID, password: str):
        """
        Post user reset password

        Parameters:
            password (body): New password

        RequestBody:
           @TODO/POST_201_documentation_post.request_body.json

        Responses:
           @TODO/POST_201_documentation_post.json
        """

        user = await models.User.filter(id_tenant=id_tenant, reset_password_uuid=reset_password_uuid).get_or_none()

        if not user:
            raise http.HttpNotAcceptable(id_message='INVALID_RESET_PASSWORD_ID_OR_ID_EXPIRED')

        if tortoise.timezone.make_naive(user.reset_password_uuid_expiration_timestamp) < datetime.datetime.now():
            raise http.HttpNotAcceptable(id_message='INVALID_RESET_PASSWORD_ID_OR_ID_EXPIRED')

        user.password = bcrypt_pass(password)
        user.reset_password_uuid = None
        user.reset_password_uuid_expiration_timestamp = None
        await user.save()

        return {'updated': True}


@route('/:id_tenant/users/register/:id_registrant/activate')
class TenantsActivateRegisterUserHandler(base3.handlers.Base):
    """
    Parameters:
       id_tenant (path): Tenant ID
       id_registrant (path): Registrant ID
    """

    @api(auth=False)
    async def patch(self, id_tenant: uuid.UUID, id_registrant: uuid.UUID, pin: str):
        """
        Patch activate user TODO

        Parameters:
           pin (body): PIN

        RequestBody:
           @TODO/PATCH_200_documentation_patch.request_body.json

        Responses:
           @TODO/PATCH_200_documentation_patch.json
        """

        try:
            registrant = await models.RegisterUserQueue.filter(id_tenant=id_tenant, id=id_registrant, pin=pin,
                                                               active=False).get_or_none()
            if not registrant:
                raise http.HttpErrorNotFound(id_message='REGISTRANT_NOT_FOUND')

            id_user = uuid.uuid4()
            user = models.User(
                uid=await models.User.gen_uid(id_tenant),
                id_user=id_user, id_tenant=id_tenant, username=registrant.username, password=registrant.password,
                first_name=registrant.first_name, last_name=registrant.last_name,
                email=registrant.email, mobile_phone=registrant.mobile_phone,
                created_by=id_user, last_updated_by=id_user)

            await user.save()

            session = await models.Session.safe_create({
                'id_tenant': id_tenant,
                'created_by': user.id,
                'last_updated_by': user.id,
                'user_id': user.id
            })
            await session.save()

            return {'token': session.token()}, http.status.CREATED

        except Exception as e:
            raise


@route('/my-settings')
class TenantsMySettings(base3.handlers.Base):

    @api()
    async def get(self):
        """
        Get user settings TODO documentation

        Responses:
           @TODO/GET_200_documentation_get.json
        """

        filter = {'id_tenant': self.id_tenant, 'user_id': self.id_user}
        res = await models.UserSettings.base_get(json_filters=filter, no_paginate=True, fields='key,value')
        return {r['key']: json.loads(r['value']) for r in res}


@route("/my-settings/:key")
class TenantMySingleSetting(base3.handlers.Base):

    @api()
    async def get(self, key):
        """
        Get user settings from key  TODO

        Parameters:
            key (path): Key # TODO

        Responses:
           @TODO/GET_200_documentation_get.json
        """

        filter = {'id_tenant': self.id_tenant, 'user_id': self.id_user, 'key': key}
        res = await models.UserSettings.base_get(json_filters=filter,
                                                 expected_one_item=True,
                                                 fields='value',
                                                 return_none_if_single_object_not_exits=True)

        if not res:
            return None

        return json.loads(res['value'])

    @api()
    async def post(self, key: str, value: str):
        """
        Post .

        Parameters:
            key (path): Key # TODO
            value (body): Value

        RequestBody:
           @TODO/POST_201_documentation_post.request_body.json

        Responses:
           @TODO/POST_201_documentation_post.json
        """

        # TODO iz nekog razologa value je dict, ako se posalje json, sredit to jer ovde zelimo manuelno da
        #  podrzimo da lang: bude str npr

        if type(value) in (dict, list):
            value = json.dumps(value)
        elif type(value) in (int, float, bool, type(None)):
            value = json.dumps(value)
        elif type(value) == str:
            # ako slucajno je dosao dict kao string, probacu da ga dekodiram i ako to radi
            # to upusjem, u suprtnom upisivanjemo string pod navodniima jer je to validan json
            try:
                json.loads(value)
            except Exception as e:
                # namerno dodajemo navodnike da bi kasnije mogli da predjemo na JSONField
                value = f'"{value}"'

        filter = {'id_tenant': self.id_tenant, 'user_id': self.id_user, 'key': key}
        setting = await models.UserSettings.base_get(json_filters=filter,
                                                     expected_one_item=True,
                                                     return_awaitable_orm_objects=True,
                                                     return_none_if_single_object_not_exits=True)
        if not setting:
            try:

                # value = json.dumps(value) # f'"{value}"'
                setting = models.UserSettings(id_tenant=self.id_tenant,
                                              created_by=self.id_user,
                                              last_updated_by=self.id_user,
                                              user_id=self.id_user,
                                              key=key,
                                              value=value
                                              )
                await setting.save()
            except Exception as e:
                raise

        else:
            if setting.value != value:
                setting.last_updated_by = self.id_user
                setting.last_updated = tortoise.timezone.now()
                setting.value = value
                await setting.save()

        return {'id': setting.id}

    @api()
    async def patch(self, key: str, value: str):
        """
        Post .

        Parameters:
            key (path): Key # TODO
            value (body): Value

        RequestBody:
           @TODO/

        Responses:
           @TODO/
        """

        # TODO iz nekog razologa value je dict, ako se posalje json, sredit to jer ovde zelimo manuelno da
        #  podrzimo da lang: bude str npr

        if type(value) in (dict, list):
            value = json.dumps(value)
        elif type(value) in (int, float, bool, type(None)):
            value = json.dumps(value)
        elif type(value) == str:
            # ako slucajno je dosao dict kao string, probacu da ga dekodiram i ako to radi
            # to upusjem, u suprtnom upisivanjemo string pod navodniima jer je to validan json
            try:
                json.loads(value)
            except Exception as e:
                # namerno dodajemo navodnike da bi kasnije mogli da predjemo na JSONField
                value = f'"{value}"'

        filter = {'id_tenant': self.id_tenant, 'user_id': self.id_user, 'key': key}
        setting = await models.UserSettings.base_get(json_filters=filter,
                                                     expected_one_item=True,
                                                     return_awaitable_orm_objects=True,
                                                     return_none_if_single_object_not_exits=True)
        if not setting:
            try:

                # value = json.dumps(value) # f'"{value}"'
                setting = models.UserSettings(id_tenant=self.id_tenant,
                                              created_by=self.id_user,
                                              last_updated_by=self.id_user,
                                              user_id=self.id_user,
                                              key=key,
                                              value=value
                                              )
                await setting.save()
            except Exception as e:
                raise

        else:
            try:
                old_value = json.loads(setting.value)
                new_settings_value = copy.deepcopy(old_value)
                new_values = json.loads(value)
            except:
                raise http.HttpNotAcceptable(id_message="NOT_IMPLEMENTED")
            if type(old_value) not in (dict,) and type(new_values) not in (dict,):
                raise http.HttpNotAcceptable(id_message="NOT_IMPLEMENTED")

            for key in new_values:
                new_settings_value[key] = new_values[key]

            if new_settings_value != old_value:
                setting.value = json.dumps(new_settings_value)
                setting.last_updated_by = self.id_user
                setting.last_updated = tortoise.timezone.now()
                await setting.save()

        return {'id': setting.id}


@route('/me')
class TenantsMeHandler(base3.handlers.Base):

    @api()
    async def get(self, fields: str = None):
        """
        Get user info

        Parameters:
            fields (query): CSV string of fields (by default it is null, and in this case will be used from personal user setting)
                enum: @User.default_fields

        Responses:
           @tenants/GET_200_documentation_get_me.json
        """

        user = await models.User.base_fetch_single(id=self.id_user, id_tenant=self.id_tenant, return_orm_object=True, to_prefetch=['role', 'role__permissions'])
        if not user:
            raise http.HttpInternalServerError(id_message='NOT_ABLE_TO_FETCH_USER_INFO')

        res = await user.serialize(fields=fields.split(',') if fields else None)

        try:
            if not fields or 'permissions' in fields:
                res['permissions'] = []
                res['permissions_codes'] = []
                if user.role:
                    res['permissions'] = [p.id for p in user.role.permissions]
                    res['permissions_codes'] = [p.code for p in user.role.permissions]
        except Exception as e:
            return {'e': str(e)}
        if not fields or 'have_password' in fields:
            # try to check if password is uuid that means it is not set.
            try:
                uuid.UUID(user.password)
                res['have_password'] = False
            except Exception as e:
                res['have_password'] = True

        try:
            x = await ipc_documents.get_by_instance_and_id_instance_no_paginate(self.request, 'users', self.id_user,
                                                                                filter={"document_type_code": "USER_PROFILE_PICTURE"},
                                                                                order_by='-created', limit=1)
        except Exception as e:
            pass

        return res, http.status.OK

    @api()
    async def patch(self):
        """
        Patch user info

        RequestBody:
           @TODO/PATCH_200_documentation_patch.request_body.json

        Responses:
           @TODO/PATCH_200_documentation_patch.json
        """

        self.log.critical('Patching user')
        self.log.critical(f'self.request.body = {self.request.body}')

        user = await models.User.base_fetch_single(id=self.id_user, id_tenant=self.id_tenant, return_orm_object=True)
        if not user:
            self.log.error('NOT_ABLE_TO_FETCH_USER_INFO, user not found')
            raise http.HttpInternalServerError(id_message='NOT_ABLE_TO_FETCH_USER_INFO')

        body = json.loads(self.request.body) if self.request.body else {}
        self.log.critical(f'{body} | {models.User.patchable_by_user}')

        old_password = body['old_password'] if 'old_password' in body else None
        if old_password:
            try:
                if not bcrypt_check(old_password.encode(), user.password.encode()):
                    raise http.HttpNotAcceptable(id_message='OLD_PASSWORD_NOT_MATCH')
            except Exception as e:
                raise http.HttpNotAcceptable(id_message='OLD_PASSWORD_NOT_MATCH')

            del body['old_password']

        updated_fields = []

        if 'password' in body and not old_password:

            try:
                # Initially password is set as uuid, if password is not bcrypted hash, and if it is uuid then
                # allow user to set password, otherwise ask for old password

                self.log.debug('old password not provided')
                if not user.password or uuid.UUID(user.password):
                    user.password = bcrypt_pass(body['password'])
                    del body['password']

                    await user.save()
                    self.log.debug('password has been changed')
                    await ipc_flows.flow(self, instance='users', id_instance=user.id, type_code='FLOW_TYPE_USER_ACTION',
                                         message=f'user set his password for a first time',
                                         data={'action': 'USER_SET_PASSWORD'}
                                         )

                    updated_fields.append('password')

            except Exception as e:
                self.log.error('PASSWORD_CANT_BE_CHANGED_WITHOUT_CURRENT_PASSWORD_PROVIDED, user can change password without old password just first time')
                raise http.HttpNotAcceptable(id_message='PASSWORD_CANT_BE_CHANGED_WITHOUT_CURRENT_PASSWORD_PROVIDED')

        if 'password' in body and old_password:
            setattr(user, 'password', bcrypt_pass(body['password']))
            del body['password']
            await user.save()
            await ipc_flows.flow(self, instance='users', id_instance=user.id, type_code='FLOW_TYPE_USER_ACTION',
                                 message=f'user changes his password by providing old password',
                                 data={'action': 'USER_CHANGE_PASSWORD'}
                                 )

            updated_fields.append('password')

        updated = updated_fields != []

        # if len(body) != 1:
        #     raise http.HttpNotAcceptable(id_message='ONLY_ONE_FIELD_CAN_BE_CHANGED_AT_THE_TIME')

        if True:

            if 'profile_picture_base64_encoded' in body:
                if ',' in body['profile_picture_base64_encoded']:
                    _hdr, _b64 = body['profile_picture_base64_encoded'].split(',')
                    if 'image/png' in _hdr:
                        _type = 'png'
                    elif 'image/jpg' in _hdr or 'image/jpeg' in _hdr:
                        _type = 'jpg'
                    else:
                        raise http.HttpNotAcceptable(id_message='INVALID_IMAGE_TYPE')
                else:
                    _type = 'png'
                    _hdr, _b64 = None, body['profile_picture_base64_encoded']

                _res, _code = await ipc_documents.send_base64_content(self.request, 'users', self.id_user, fname=f'profile_picture.{_type}', document_type_code='USER_PROFILE_PICTURE',
                                                                      data=_b64)

                del body['profile_picture_base64_encoded']
                body['profile_picture'] = _res['thumbnail_url']

            if 'organization' in body:
                if 'data' not in body:
                    body['data'] = {}
                body['data']['organization'] = body['organization']
                del body['organization']

            self.log.critical(f'{body} | {models.User.patchable_by_user}')
            for key in body.keys():
                if key not in models.User.patchable_by_user:
                    raise http.HttpForbiden(id_message='NOT_CHANGEABLE_BY_USER')

                if getattr(user, key) != body[key]:
                    old_value = getattr(user, key)
                    setattr(user, key, body[key])
                    updated_fields.append(key)
                    await user.save()
                    await ipc_flows.flow(self, instance='users', id_instance=user.id, type_code='FLOW_TYPE_USER_ACTION',
                                         message=f'user changes his {key} to {body[key]}',
                                         data={'action': 'USER_CHANGE_PROPERTY',
                                               'property': key,
                                               'from': old_value,
                                               'to': body[key]
                                               })
                    updated = True

            if updated:
                await user.mk_cache(self)

        # This is not place where this should be called, it should be called from external service for update
        # import tshared.ipc.tickets as ipc_tickets
        # try:
        #     await ipc_tickets.service_cache(self.request,
        #                                     self.id_tenant, 'tenants', 'User',
        #                                     user.id, updated_fields, await user.serialize())
        #
        # except Exception as e:
        #     raise

        return {'updated': updated}


@route('/find_user_by_uuid_and_tenant_code/:unique_id_and_tenant_code')
class FindUserByCodeAndTenantHandler(base3.handlers.Base):

    @api(auth=False)
    async def get(self, unique_id_and_tenant_code: str):
        """
        Get user by uuid and code

        Parameters:
            unique_id_and_tenant_code (path): UUID and tenant code to search for user

        Responses:
           @TODO/GET_200_documentation_get.json
        """

        unique_id, tenant_code = unique_id_and_tenant_code.split('--')

        tenant = await models.Tenant.filter(code=tenant_code).get_or_none()
        if not tenant:
            raise http.HttpErrorNotFound(id_message='TENANT_NOT_FOUND', message=tenant_code)

        user = await models.User.filter(id_tenant=tenant.id, uid=unique_id).get_or_none()
        if not user:
            raise http.HttpErrorNotFound(id_message='USER_NOT_FOUND', message=unique_id)

        return {'id': user.id, 'id_tenant': tenant.id}