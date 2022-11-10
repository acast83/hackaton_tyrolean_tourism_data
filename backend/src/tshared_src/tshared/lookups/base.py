import uuid
from base3 import http
from base3.core import Base
from tortoise.transactions import in_transaction
import tortoise.timezone
import datetime
import copy

import dateutil.parser


class BaseInitAllLookupsHandler(Base):

    async def post(self, lookups: dict, db_connection: str, tbl2model: dict, tml2model_order: list = None):

        try:
            async with in_transaction(db_connection):

                self.log.debug(f'updating lookups for tenant {self.id_tenant}')

                added, updated, skipped = 0, 0, 0
                tr_added, tr_updated, tr_skipped = 0, 0, 0

                if not tml2model_order:
                    tml2model_order = tbl2model.keys()

                for key in tml2model_order:

                    self.log.debug(' '*4+f'{key}')

                    if key in lookups:
                        default_order = 0
                        for item in lookups[key]:

                            self.log.debug(' ' * 8 + f'{item}')

                            model, translations_model = tbl2model[key]['model'], tbl2model[key]['translations']

                            code = item['code']

                            order = item['order'] if 'order' in item else default_order
                            default_order = order + 1

                            _id = item['id'] if 'id' in item else uuid.uuid4()

                            filters = {
                                'id_tenant': self.id_tenant,
                                'code': code}
                            if 'group_code' in item:
                                filters['group_code'] = item['group_code']

                            lkp = await model.filter(**filters).get_or_none()

                            self.log.debug(' ' * 8 + f'lkp: {lkp}')

                            if not lkp:
                                self.log.debug('  '* 8 + 'creating new lookup item')
                                kwa = copy.copy(item)
                                kwa['id_tenant'] = self.id_tenant
                                kwa['created_by'] = self.id_user
                                kwa['last_updated_by'] = self.id_user
                                if 'id' not in kwa:
                                    kwa['id'] = _id

                                if 'translations' in kwa:
                                    del kwa['translations']

                                try:
                                    lkp = model(**kwa)
                                    # lkp = model(id_tenant=self.id_tenant, created_by=self.id_user, last_updated_by=self.id_user, code=code, id=_id, order=order)

                                    added += 1
                                    await lkp.save()
                                except Exception as e:
                                    raise
                            else:

                                self.log.debug('  '* 8 + 'updateing or skipping')

                                _updated = False
                                if order != lkp.order:
                                    lkp.order = order
                                    _updated = True
                                    self.log.debug('  '* 12 + f'update because order: {order}!={lkp.order}')

                                # TODO: ?what about content?

                                if _updated:
                                    updated += 1
                                    await lkp.save()
                                else:
                                    self.log.debug('  '* 12 + f'skipping')
                                    skipped += 1

                            tr = {t.language: t for t in await translations_model.filter(lookup=lkp).all()}

                            if 'translations' in item:
                                for l in item['translations']:
                                    if l in tr:
                                        if tr[l].value != item['translations'][l]:
                                            tr[l].value = item['translations'][l]
                                            tr_updated += 1
                                            await tr[l].save()
                                        else:
                                            tr_skipped += 1
                                    else:
                                        tr[l] = translations_model(lookup=lkp, language=l,
                                                                   value=item['translations'][l])
                                        await tr[l].save()
                                        tr_added += 1

                            if 'parent' in item:
                                parent_lookup_model = tbl2model[item['parent']['lookup']]['model']
                                parent_lookup_key = item['parent']['key']
                                parent_lookup_relation = item['parent']['relation']
                                parent_value = item['parent']['value']

                                if not hasattr(lkp, parent_lookup_relation):
                                    raise http.HttpNotAcceptable(id_message='LOOKUP_PARENT_RELATION_NOT_DEFINED',
                                                                 message=f'Parent relation {parent_lookup_relation} is not defined for lookup {key}')

                                all_by_key = {getattr(l, parent_lookup_key): l for l in
                                              await parent_lookup_model.filter(id_tenant=self.id_tenant).all()}

                                if parent_value not in all_by_key:
                                    raise http.HttpNotAcceptable(id_message='UNKNOWN_LOOKUP_RELATION',
                                                                 message=f'relation {parent_value} is not defined for lookup {key}')

                                await lkp.fetch_related(parent_lookup_relation)

                                setattr(lkp, parent_lookup_relation, all_by_key[parent_value])
                                await lkp.save()

                            if 'connections' in item:
                                for connection in item['connections']:
                                    conn_lookup_model = tbl2model[item['connections'][connection]['lookup']]['model']
                                    conn_lookup_key = item['connections'][connection]['key']
                                    conn_lookup_list = item['connections'][connection]['list']
                                    conn_lookup_relation = item['connections'][connection]['relation']

                                    if not hasattr(lkp, conn_lookup_relation):
                                        raise http.HttpNotAcceptable(id_message='LOOKUP_MANY2MANY_RELATION_NOT_DEFINED',
                                                                     message=f'Many2Many relation {conn_lookup_relation} is not defined for lookup {key}')

                                    all_by_key = {getattr(l, conn_lookup_key): l for l in
                                                  await conn_lookup_model.filter(id_tenant=self.id_tenant).all()}

                                    await lkp.fetch_related(conn_lookup_relation)

                                    for rel in getattr(lkp, conn_lookup_relation):
                                        await getattr(lkp, conn_lookup_relation).remove(rel)

                                    for citem in conn_lookup_list:
                                        if citem not in all_by_key:
                                            raise http.HttpNotAcceptable(id_message='UNKNOWN_LOOKUP_RELATION',
                                                                         message=f'relation {citem} is not defined for lookup {key}')

                                        await getattr(lkp, conn_lookup_relation).add(all_by_key[citem])

            return {'lookups': {'added': added, 'updated': updated, 'skipped': skipped},
                    'translations': {'added': tr_added, 'updated': tr_updated, 'skipped': tr_skipped}}
        except Exception as e:
            raise


class BaseAllLookupsHandler(Base):
    async def get(self, db_connection: str, tbl2model: dict, format: str = 'default', lang: str = 'default',
                  format_frontend_key: str = 'code', frontend_format: str = 'list'):
        # async with in_transaction(db_connection):
        if format == 'frontend':
            async def f(tbl):
                model = tbl2model[tbl]['model']

                if frontend_format == 'list':
                    return [{'id': l.id, 'code': l.code} for l in await model.all().order_by('created')]
                if format_frontend_key == 'code':
                    return {str(l.code): {'id': l.id} for l in await model.all()}
                if format_frontend_key == 'id':
                    return {str(l.id): {'code': l.code} for l in await model.all()}

            return {t: await f(t) for t in tbl2model.keys()}

        # default format

        return [t for t in tbl2model.keys()]


class BaseSingleLookupHandler(Base):

    async def get(self, table: str, db_connection: str, tbl2model: dict, last_updated: datetime.datetime = None,
                  index_by='id', filters={},
                  fields=['id', 'order', 'code']

                  ):

        if last_updated:
            # last_updated = dateutil.parser.parse(last_updated) if type(last_updated)==str else last_updated

            if tortoise.timezone.is_naive(last_updated):
                last_updated = tortoise.timezone.make_aware(last_updated)

        if table not in tbl2model:
            raise http.HttpErrorNotFound(id_message='LOOKUP_NOT_FOUND', message='Lookup is not found')

        try:
            if True:
            # async with in_transaction(db_connection):
                try:
                    filters['id_tenant'] = self.id_tenant

                    if last_updated:
                        filters['last_updated__gt'] = last_updated

                    res = {}
                    max_last_updated = None
                    for v in await tbl2model[table]['model'].filter(**filters).all().prefetch_related('translations'):

                        val = {}
                        for f in fields:
                            val[f] = getattr(v, f)

                        val['translations'] = {t.language: t.value for t in v.translations}

                        # val = {'id': v.id, 'order': v.order, 'code': v.code, 'translations': {t.language: t.value for t in v.translations}}

                        if index_by == 'code':
                            res[v.code] = val

                        elif index_by == 'id':
                            res[str(v.id)] = val

                        v_lu = tortoise.timezone.make_naive(v.last_updated)
                        if not max_last_updated or max_last_updated < v_lu:
                            max_last_updated = v_lu

                    return {'last_updated': max_last_updated,
                            'items': res}
                except Exception as e:
                    raise

        except Exception as e:
            raise
