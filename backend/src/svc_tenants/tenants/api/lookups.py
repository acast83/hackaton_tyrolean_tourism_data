import tshared.lookups.base
import datetime
import tortoise.timezone
import dateutil.parser
from .. import models
from base3.decorators import route, api

db_connection = 'conn_tenants'

tbl2model = {
    'permissions': {'model': models.LookupUserPermission, 'translations': models.TranslationLookupUserPermission},
    'roles': {'model': models.LookupUserRole, 'translations': models.TranslationLookupUserRole},
    'user_groups': {'model': models.LookupUserGroup, 'translations': models.TranslationLookupUserGroup},
    'org_units': {'model': models.LookupOrgUnit, 'translations': models.TranslationLookupOrgUnit},
    'prefered_language': {'model': models.LookupPreferedLanguage, 'translations': models.TranslationLookupPreferedLanguage},
    # {{ tbl2model }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
}


@route('/lookups/init')
class TenantsInitLookupsHandler(tshared.lookups.base.BaseInitAllLookupsHandler):

    @api()
    async def post(self, lookups: dict):
        return await super().post(lookups, db_connection, tbl2model)


@route('/lookups')
class TenantsAllLookupsHandler(tshared.lookups.base.BaseAllLookupsHandler):

    @api()
    async def get(self, format: str = 'default', lang: str = 'default', format_frontend_key: str = 'code',
                  frontend_format: str = 'list'):
        return await super().get(db_connection, tbl2model, format=format, lang=lang,
                                 format_frontend_key=format_frontend_key, frontend_format=frontend_format)


@route('/lookups/:table')
class TenantsSingleLookupHandler(tshared.lookups.base.BaseSingleLookupHandler):

    async def get_tenants(self, last_updated: datetime.datetime):

        filters = {}
        if last_updated:
            if tortoise.timezone.is_naive(last_updated):
                last_updated = tortoise.timezone.make_aware(last_updated)

            filters['last_updated__gt'] = last_updated

        all_tenants = await models.Tenant.filter(**filters).prefetch_related().all()

        max_last_updated = None

        res = {}

        for t in all_tenants:

            # ?
            t_lu = tortoise.timezone.make_naive(t.last_updated)
            if not max_last_updated or max_last_updated < t_lu:
                max_last_updated = t_lu

            res[str(t.id)] = {'id': str(t.id), 'code': t.code, 'name': t.name}

        return {'last_updated': max_last_updated, 'items': res}

    async def get_users(self, last_updated: datetime.datetime):

        filters = {'id_tenant': self.id_tenant}
        if last_updated:
            if tortoise.timezone.is_naive(last_updated):
                last_updated = tortoise.timezone.make_aware(last_updated)

            filters['last_updated__gt'] = last_updated

        all_users = await models.User.filter(**filters).prefetch_related('cache11', 'groups').all()

        # all_users = await models.User.filter(id_tenant=self.id_tenant).all() #, last_updated__gt=last_updated).all()
        max_last_updated = last_updated  # None

        res = {}

        def user_groups(user):
            group_by_group_code = {}
            for g in user.groups:
                if g.group_code not in group_by_group_code:
                    group_by_group_code[g.group_code] = []

                group_by_group_code[g.group_code].append(g.id)

            return group_by_group_code

        for u in all_users:

            # u_lu = tortoise.timezone.make_naive(u.last_updated)
            u_lu = u.last_updated
            if not max_last_updated or max_last_updated < u_lu:
                max_last_updated = u_lu

            try:
                res[str(u.id)] = {'id': str(u.id), 'username': u.username,
                                  'display_name': u.cache11.display_name if u.cache11 else u.username,
                                  'unique_id': u.uid,
                                  'profile_picture': u.profile_picture, 'groups': user_groups(u)
                                  }
            except Exception as e:
                raise

        return {'last_updated': max_last_updated,
                'items': res}

    @api()
    async def get(self, table: str, last_updated: datetime.datetime = None, index_by: str = 'id', group: str = None):

        # TODO: dodati tipove u base-u  i tamo zavrsiti ovo
        if last_updated and type(last_updated) == str:
            last_updated = dateutil.parser.parse(last_updated)

        if last_updated and tortoise.timezone.is_naive(last_updated):
            last_updated = tortoise.timezone.make_aware(last_updated)

        if table == 'tenants':
            return await self.get_tenants(last_updated=last_updated)

        if table == 'users':
            return await self.get_users(last_updated=last_updated)

        try:
            filters = {}

            if group:
                filters['group_code'] = group

            fields = ['id', 'order', 'code']
            if table == 'user_groups':
                fields = ['id', 'order', 'code', 'group_code']

            res = await super().get(table, db_connection, tbl2model,
                                    last_updated=last_updated if last_updated else None, index_by=index_by,
                                    filters=filters, fields=fields)

            return res

        except Exception as e:
            raise