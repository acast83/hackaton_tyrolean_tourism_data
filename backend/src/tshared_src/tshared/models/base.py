from tortoise import fields, timezone
import nanoid
import tortoise.fields.relational
from base3 import http
from tortoise.queryset import Q
import uuid
import json
from tortoise.transactions import in_transaction
import asyncpg.pgproto.pgproto
import inspect
import urllib.parse
import time
import tshared.ipc.tenants as ipc_tenants

uid_alphabet = 'WERTYUPAFGHJKLXCVBNM346789'
uid_generator_max_attempts = 10
from tortoise.functions import Count
from tshared.lookups import LookupUsers
import base3.test as b3t
from tshared.utils.setup_logger import get_logger_for


async def mk_cache(handler, model, connection_name, json_filters=None, LOOKUPS=None, log_progress=False):
    if not json_filters:
        json_filters = {}

    json_filters['id_tenant'] = handler.id_tenant

    updated = 0
    start = time.time()
    if log_progress:
        log = get_logger_for(handler)
        log.critical(f'mk_cache model={model}; json_filters={json_filters}, LOOKUPS={LOOKUPS.keys() if LOOKUPS else None}')

    async with in_transaction(connection_name=connection_name):
        for item in await model.filter(**json_filters).all():
            if log_progress:
                _s = time.time()
            await item.mk_cache(handler=handler, prefetched=False, LOOKUPS=LOOKUPS)
            updated += 1

            if log_progress:
                t = time.time()
                log.critical(f'mk_cache  id={item.id} i={updated} item={item} time={round(t - _s, 6)} total_time={round(t - start, 4)}')

    if log_progress:
        log.critical(f'mk_cache model={model} finished; total_time={round(t - start, 4)}')

    return {'updated': updated, 'time': round(time.time() - start, 4)}


async def translate(translation_models, item_model_name, item_model, handler, conn_name, terms_by_language):
    current_translation_by_language = {t.language: t for t in
                                       await translation_models.filter(**{item_model_name: item_model}).all()}

    for term in terms_by_language:

        for lang in terms_by_language[term]:

            if lang not in current_translation_by_language:
                kwa = {
                    item_model_name: item_model,
                    'language': lang,
                    'created_by': handler.id_user,
                    'last_updated_by': handler.id_user,
                    term: terms_by_language[term][lang].lower(),
                    f'cs_{term}': terms_by_language[term][lang]
                }
                current_translation_by_language[lang] = translation_models(**kwa)
                await current_translation_by_language[lang].save()
            else:
                # TODO: ispitaj da li je bilo promene i samo u slucaju promene uradi save

                setattr(current_translation_by_language[lang], term, terms_by_language[term][lang].lower())
                setattr(current_translation_by_language[lang], f'cs_{term}', terms_by_language[term][lang])
                setattr(current_translation_by_language[lang], f'last_updated_by', handler.id_user)
                await current_translation_by_language[lang].save()

    pass


async def mk_cache_lookups_code_and_names(itm_model_name,
                                          itm_model,
                                          handler,
                                          conn_name,
                                          prefetched: bool,
                                          C11,
                                          C1N=None,
                                          languages=('en', 'it', 'de', 'sr'),
                                          default_language='en',
                                          svc_lookups_info: list = None,

                                          c11_cache_dict=None,
                                          c1n_cache_dict=None,

                                          LOOKUPS=None

                                          ):
    try:

        if not svc_lookups_info:
            svc_lookups_info = []
        if not c11_cache_dict:
            c11_cache_dict = {}
        if not c1n_cache_dict:
            c1n_cache_dict = {}
        if not LOOKUPS:
            LOOKUPS = {}

        if 'lookup_users' not in LOOKUPS:
            try:
                lookup_users = await LookupUsers.create(handler)
            except Exception as e:
                raise
        else:
            lookup_users = LOOKUPS['lookup_users']

        if True:
            # async with in_transaction(conn_name):
            # if True:
            c11 = {}
            c1n = {}
            for l in languages:
                c1n[l] = {}

            try:
                c11['created_by_display_name'] = lookup_users.get(itm_model.created_by)['display_name']
            except Exception as e:
                raise http.HttpInternalServerError(id_message='USER_ID_NOT_FOUND_IN_LOOKUP',
                                                   message=itm_model.created_by)

            try:
                c11['last_updated_by_display_name'] = lookup_users.get(itm_model.last_updated_by)['display_name']
            except Exception as e:
                raise http.HttpInternalServerError(id_message='USER_ID_NOT_FOUND_IN_LOOKUP',
                                                   message=itm_model.last_updated_by)

            for f in svc_lookups_info:
                f_code = f[0]
                f_name = f[1]
                f_id = f[2]
                lookup_class = f[3]

                if f_id:
                    try:
                        the_lookup = await lookup_class.create(handler)
                        _f = the_lookup.get(f_id)
                    except Exception as e:
                        raise

                    if _f:
                        order = int(_f['order']) if _f['order'] else 0
                        order = f'{order:04}'
                        c11[f_code] = f"{order}:{_f['code']}"

                        for l in languages:
                            c1n[l][f_name] = _f['translations'][l] if l in _f['translations'] else \
                                _f['translations'][default_language]

            if not prefetched:
                if C11 and C1N:
                    await itm_model.fetch_related('cache11', 'cache1n')
                elif C11 and not C1N:
                    await itm_model.fetch_related('cache11')

            if not itm_model.cache11:
                c11[itm_model_name] = itm_model
                _c11t = C11(**c11)

                for k in c11_cache_dict:
                    setattr(_c11t, k, c11_cache_dict[k])

                await _c11t.save()
            else:
                try:
                    for k in c11:
                        setattr(itm_model.cache11, k, c11[k])

                    for k in c11_cache_dict:
                        setattr(itm_model.cache11, k, c11_cache_dict[k])

                    await itm_model.cache11.save()
                except Exception as e:
                    raise

            if C1N:
                map_c1n = {k.language: k for k in itm_model.cache1n}
                for l in languages:
                    if l not in map_c1n:
                        c1n[l][itm_model_name] = itm_model
                        map_c1n[l] = C1N(language=l, **c1n[l])
                        if c11_cache_dict:
                            for k in c1n_cache_dict:
                                if hasattr(map_c1n[l], k):
                                    setattr(map_c1n[l], k, f"{c11['created_by_display_name'].lower()} {c1n_cache_dict[k][l].lower()}")
                        await map_c1n[l].save()
                    else:
                        to_upd = False
                        for key in c1n[l]:
                            if hasattr(map_c1n[l], key):
                                cv = getattr(map_c1n[l], key)
                                if cv != c1n[l][key]:
                                    setattr(map_c1n[l], key, c1n[l][key])
                                    to_upd = True
                        if to_upd:
                            await map_c1n[l].save()

    except Exception as e:
        raise


class BaseModelNoTenant:
    id = fields.UUIDField(pk=True)
    created = fields.DatetimeField(auto_now_add=True)
    created_by = fields.UUIDField(null=False)
    last_updated = fields.DatetimeField(auto_now=True)
    last_updated_by = fields.UUIDField(null=False)

    touched = fields.BooleanField(null=False, default=False, index=True)
    active = fields.BooleanField(null=True, default=True, index=True)
    merged_with = fields.UUIDField(default=None, null=True, index=True)

    name_case_fields = {}

    @staticmethod
    def name_case(s: str):
        if s is None:
            return None

        return s.capitalize()

    @classmethod
    def all_fields(cls):
        t = cls()
        res = t._all_fields()
        if hasattr(cls, 'connected_fields'):
            for f in cls.connected_fields:
                res.append(f)

        return res

    def _all_fields(self):
        return [i for i in self.__dict__.keys() if i[:1] != '_']

    def mutable_fields(self):
        read_only_fields = getattr(self, 'read_only_fields') if hasattr(self, 'read_only_fields') else {}
        protected_fields = getattr(self, 'protected_fields') if hasattr(self, 'protected_fields') else {}

        return set([f for f in self._all_fields() if f not in read_only_fields and f not in protected_fields])

    @classmethod
    async def safe_create(cls, args: dict, attach_list_items: list = None):

        instance = cls()

        protected_fields = []
        if hasattr(cls, 'protected_fields') and cls.protected_fields:
            protected_fields = cls.protected_fields

        for arg in instance.all_fields():
            if arg in args and arg not in protected_fields:
                setattr(instance, arg, args[arg])

        touched = True
        if hasattr(cls, 'mandatory_fields_for_visibility') and cls.mandatory_fields_for_visibility:
            untouched = False
            for mk in cls.mandatory_fields_for_visibility:
                if hasattr(instance, mk):
                    v = getattr(instance, mk)
                    if not v:
                        untouched = True
                        break

            touched = not untouched
        try:
            await instance.save()
        except Exception as e:
            raise
        if attach_list_items:

            async def fn_attach_list_items(instance, model, connection_key, items: list):
                for item in items:
                    item[connection_key] = instance.id
                    db_item = model(**item)
                    await db_item.save()

            for r in attach_list_items:
                if r[1]:
                    try:
                        await fn_attach_list_items(instance, model=r[0], connection_key=r[1], items=r[2])
                    except Exception as e:
                        raise

        setattr(instance, 'touched', touched)

        return instance

    async def bulk_serialize(self, fields=None):

        protected_fields = []
        if (hasattr(self, 'protected_fields') and self.protected_fields
                and isinstance(fields, (list, tuple, set, dict))
                and [f for f in fields if f in self.protected_fields]):
            protected_fields = self.protected_fields

        if not fields:
            if hasattr(self, 'default_fields') and self.default_fields:
                fields = [f for f in self.default_fields if f not in protected_fields]
            else:
                fields = [f for f in self.all_fields() if f not in protected_fields]
        else:
            fields = [f for f in self.all_fields() if f not in protected_fields]

        return await self.serialize(fields)

    async def serialize(self, fields=None, prefetched=[], language='en'):

        # if 'Country' in str(self):
        #     print("BREAK POINT")

        res = {}
        if not fields:
            fields = self.all_fields()

        protected_fields = []
        if hasattr(self, 'protected_fields') and self.protected_fields:
            protected_fields = self.protected_fields

        o2m_connections = self.o2m_connections if hasattr(self, 'o2m_connections') else {}
        if o2m_connections:
            prefetched = set(prefetched)
            to_fetch = set()
            for f in fields:
                if f in o2m_connections:
                    to_fetch.add(o2m_connections[f])

            for fr in to_fetch:
                if fr not in prefetched:
                    await self.fetch_related(fr)

        connected_fields = self.connected_fields if hasattr(self, 'connected_fields') else {}
        if connected_fields:
            prefetched = set(prefetched)
            to_fetch = set()
            for f in fields:
                if f in connected_fields:
                    tv = connected_fields[f].split('.')
                    if len(tv) == 2:
                        to_fetch.add(tv[0])

            for fr in to_fetch:
                if fr not in prefetched:
                    await self.fetch_related(fr)

        for f in fields:
            if f in protected_fields:
                continue

            if hasattr(self, f):

                attr = getattr(self, f)

                if hasattr(attr, '__self__') and attr.__self__ == self:
                    if inspect.iscoroutinefunction(attr):
                        res[f] = await attr()
                    else:
                        res[f] = attr()

                    continue

                def try_serialize_or_return_id(x):
                    if hasattr(x, 'serialize'):
                        return x.serialize()

                    return x.id

                if type(getattr(self, f)) == tortoise.fields.relational.ManyToManyRelation:
                    res[f] = [str(x.id) for x in await getattr(self, f).all()]
                elif type(getattr(self, f)) == tortoise.fields.relational.ReverseRelation:
                    res[f] = [try_serialize_or_return_id(x) for x in await getattr(self, f).all()]
                else:
                    res[f] = getattr(self, f)

                if hasattr(self, 'name_case_fields') and self.name_case_fields and f in self.name_case_fields:
                    res[f] = self.name_case(res[f])

                continue

            if f in o2m_connections:
                value = getattr(self, f)
                res[f] = {'id': value.id}

            # if field is not simple attr, then it can be fk relation or m2m relation
            if f in connected_fields:
                tv = connected_fields[f].split('.')
                if len(tv) == 2:
                    ct = getattr(self, tv[0])

                    if ct:
                        if tortoise.fields.relational.ReverseRelation == type(ct):
                            # in many2many relation depends on target language, serialize will setup result for the language or default_language(en)

                            if language == 'all':
                                # if language is 'all' result will be map of all values by language
                                if f in self.name_case_fields:
                                    v = {r.language: self.name_case(getattr(r, tv[1])) for r in ct}
                                else:
                                    v = {r.language: getattr(r, tv[1]) for r in ct}
                            else:
                                # if language != 'all' value will be given on target language, if there is not value on target language english will be used
                                # othervise value will be None

                                en = None
                                v = None
                                for r in ct:
                                    if hasattr(r, 'language'):

                                        if r.language == language:
                                            v = getattr(r, tv[1])

                                            if f in self.name_case_fields:
                                                v = self.name_case(v)

                                            break
                                        if r.language == 'en':
                                            en = getattr(r, tv[1])

                                            if f in self.name_case_fields:
                                                en = self.name_case(en)

                                            continue
                                    else:
                                        v = getattr(r, tv[1])

                                        if f in self.name_case_fields:
                                            v = self.name_case(v)

                                        break

                                if en and not v:
                                    v = en

                        else:
                            # if ct is field in 1-1 relation, result is simple value of this field

                            v = getattr(ct, tv[1])
                            if f in self.name_case_fields:
                                v = self.name_case(f)

                        res[f] = v

        if hasattr(self, 'serialization_fields_order') and self.serialization_fields_order:
            ordered_fields = self.serialization_fields_order
            ordered_res = {}

            # first add ordered_fields
            for field in ordered_fields:
                if field in res:
                    ordered_res[field] = res[field]

            # add other fields
            for field in res:
                if field not in ordered_res:
                    ordered_res[field] = res[field]

            return ordered_res

        return res

    @classmethod
    async def base_update(cls, id: uuid.UUID, handler, body: dict = None, attach_list_items: list = None, _voids=False):
        instance = cls()
        request_body = body if body else json.loads(handler.request.body)
        id_tenant = handler.id_tenant

        item = await cls.filter(id_tenant=id_tenant, id=id).get_or_none()

        if not item:
            raise http.HttpErrorNotFound(id_message=f'{cls.__name__.upper()}_NOT_FOUND',
                                         message=f'{cls.__name__} not found')
        if _voids:
            return item, ['_']

        fields = {}
        for _field in item.mutable_fields():
            if _field in request_body:
                fields[_field] = request_body[_field]

        if not fields:
            raise http.HttpNotAcceptable(id_message='FIELDS_NOT_MATCH_MUTABLE_FIELDS')

        def test_is_equal(a, b):
            if type(a) in (uuid.UUID, asyncpg.pgproto.pgproto.UUID):
                a = str(a)
            if type(b) in (uuid.UUID,):
                b = str(b)

            return a == b

        updated = []

        for field in fields:
            current_value = getattr(item, field)
            value = fields[field]

            if not test_is_equal(current_value, value):
                setattr(item, field, value)
                updated.append(field)
        if updated:
            item.last_updated_by = handler.id_user

            if hasattr(item, 'mk_cache'):
                await item.mk_cache(handler)

        if attach_list_items:
            pass

            # async def fn_attach_list_items(instance, model, connection_key, items: list):
            #     for item in items:
            #         # db_item = await model.filter(id_tenant=id_tenant, id=id).get_or_none()
            #         item[connection_key] = instance.id
            #         db_item = model(**item)
            #         await db_item.save()
            #
            # for r in attach_list_items:
            #     if r[1]:
            #         try:
            #             await fn_attach_list_items(instance, model=r[0], connection_key=r[1], items=r[2])
            #         except Exception as e:
            #             raise

        # if updated:
        #     await item.save(sorted(updated))

        return item, sorted(updated)

    @classmethod
    async def base_patch_single(cls, id: uuid.UUID, handler, _voids=None):

        # TODO: consider that this function should just call base_update

        request_body = json.loads(handler.request.body)
        id_tenant = handler.id_tenant

        item = await cls.filter(id_tenant=id_tenant, id=id).get_or_none()

        if not item:
            raise http.HttpErrorNotFound(id_message=f'{cls.__name__.upper()}_NOT_FOUND',
                                         message=f'{cls.__name__} not found')
        if _voids:
            return item, ['_']

        field = None
        for _field in item.mutable_fields():
            if _field in request_body:
                if field:
                    raise http.HttpNotAcceptable(id_message='ONLY_ONE_FIELD_PROPERTY_CAN_BE_CHANGED_AT_THE_TIME')
                field = _field
                value = request_body[field]

        if not field:
            raise http.HttpNotAcceptable(id_message='FIELD_NOT_PROVIDED')

        updated = False

        current_value = getattr(item, field)

        def test_is_equal(a, b):
            if type(a) in (uuid.UUID, asyncpg.pgproto.pgproto.UUID):
                a = str(a)
            if type(b) in (uuid.UUID,):
                b = str(b)

            if a == b:
                return True

            return False

        if not test_is_equal(current_value, value):
            setattr(item, field, value)
            updated = True

        return item, updated

    @classmethod
    async def base_create(cls, handler, body=None, skip_uid: bool = False, attach_list_items: list = None):

        if not body:
            body = json.loads(handler.request.body) if handler.request.body else {}

        body['id_tenant'] = handler.id_tenant
        body['created_by'] = handler.id_user
        body['last_updated_by'] = handler.id_user

        if not skip_uid:
            body['uid'] = await cls.gen_uid(handler.id_tenant)

        item = await cls.safe_create(body, attach_list_items)

        return item

    @classmethod
    async def base_fetch_single(cls,
                                id: uuid.UUID,
                                id_tenant: uuid.UUID,
                                fields: str = None,
                                language: str = 'default',
                                return_orm_object=False,

                                to_prefetch: list = [],
                                ):

        try:
            if language == 'default':
                language = 'en'

            if not fields:
                if hasattr(cls, 'default_fields'):
                    fields = cls.default_fields
                else:
                    fields = cls.all_fields()

            if type(fields) == str:
                fields = fields.split(',')

            to_prefetch = set(to_prefetch)

            o2m_connections = cls.o2m_connections if hasattr(cls, 'o2m_connections') else {}
            if o2m_connections:
                for f in fields:
                    if f in o2m_connections:
                        to_prefetch.add(o2m_connections[f])

            connected_fields = cls.connected_fields if hasattr(cls, 'connected_fields') else {}
            if connected_fields:
                for f in fields:
                    if f in connected_fields:
                        tv = connected_fields[f].split('.')
                        if len(tv) == 2:
                            to_prefetch.add(tv[0])

            query = cls.filter(id_tenant=id_tenant, id=id).prefetch_related(*to_prefetch)

            result = await query.get_or_none()

            if return_orm_object:
                return result

            if not result:
                raise http.HttpErrorNotFound(id_message=f'{cls.__name__.upper()}_NOT_FOUND',
                                             message=f'{cls.__name__} not found')

            return await result.serialize(fields=fields, prefetched=to_prefetch, language=language)

        except Exception as e:
            raise

    @classmethod
    async def base_update_or_create(cls, connection_name,
                                    handler, data: dict,
                                    json_filters: dict = None,
                                    q_filters: list = None,
                                    return_orm_object=False,
                                    ):

        if not json_filters:
            json_filters = {}
        if not q_filters:
            q_filters = []

        async with in_transaction(connection_name):
            item = await cls.base_get(json_filters, q_filters,
                                      expected_one_item=True,
                                      return_awaitable_orm_objects=True,
                                      return_none_if_single_object_not_exits=True)

            if not item:
                created = True
                data['id_tenant'] = handler.id_tenant
                data['created_by'] = handler.id_user
                data['last_updated_by'] = handler.id_user

                item = cls(**data)
                await item.save()

            else:
                created = False
                updated = []
                for key in data:
                    if hasattr(item, key) and str(getattr(item, key)) != str(data[key]):
                        setattr(item, key, data[key])
                        updated.append(key)

                if updated:
                    await item.save()

        if return_orm_object:
            return item

        if created:
            return {'id': item.id, 'created': True}

        return {'id': item.id, 'updated': updated}

    @classmethod
    async def fetch_by_id(cls,
                          handler,
                          id: uuid.UUID):

        filters = {'id': id, 'active': True}
        if hasattr(handler, 'id_tenant'):
            filters['id_tenant'] = handler.id_tenant

        item = await cls.filter(**filters).get_or_none()
        if not item:
            raise http.HttpErrorNotFound

        return item

    @classmethod
    async def base_get(cls,
                       json_filters: dict = None,
                       q_filters: list = None,
                       no_paginate: bool = False,
                       page: int = 1, per_page: int = 100,
                       fields=None,
                       fields_template=None,
                       order_by: str = 'created',
                       force_limit: int = None,
                       search: str = None,
                       language: str = 'default',
                       lowercased_search_field=None,
                       prefetched: list = None,
                       return_awaitable_orm_objects=False,
                       distinct=False,
                       search_policy='contains',

                       expected_one_item=False,
                       return_none_if_single_object_not_exits=False,

                       # my_uri='/',
                       # my_params='',
                       request=None,
                       only_summary=False,
                       debug_return_query=False,
                       customizable_fields_property_name=None,
                       include_columns_in_response=False,
                       include_menus_in_response=False,

                       force_connection='conn_test',
                       force_ids=None,
                       row_post_processor=None,

                       ):
        """

        lowercased_search_field: field that stores searchable data with all characters lowercased

        """

        if b3t.test_mode:
            force_connection = 'conn_test'

        # if q_filters:
        #     print("BREAKPOINT")

        if customizable_fields_property_name and not fields:
            try:
                fields = await ipc_tenants.get_property(request, customizable_fields_property_name)
                fields = [f['name'] for f in fields] if fields else []
            except Exception as e:
                raise

        if not prefetched:
            prefetched = []

        if not json_filters:
            json_filters = {}

        if 'active' not in json_filters:
            json_filters['active'] = True

        if not q_filters:
            q_filters = []

        if language == 'default':
            language = 'en'

        if not fields:

            if hasattr(cls, 'default_fields_templates') and fields_template:
                fields = getattr(cls, 'default_fields_templates')[fields_template]

            else:
                if hasattr(cls, 'default_fields'):
                    fields = getattr(cls, 'default_fields')
        else:
            if type(fields) == str:
                fields = fields.split(',')

        if not fields and not return_awaitable_orm_objects:
            raise http.HttpNotAcceptable(id_message='FIELDS_NOT_PROVIDED_OR_THERE_ARE_NO_DEFAULT_FIELDS')

        # ! snimi sta je korisnik hteo da ima, pa obrisi kasnije, ili ovo vrati na drugom mestu !?!
        # ! fields = list(fields)
        # ! fields.append('created_by')
        # ! fields.append('last_updated_by')

        filters = []
        if search:
            if not lowercased_search_field:
                raise http.HttpNotAcceptable(
                    id_message='CAN_NOT_USE_SEARCH_FEATURE_WITHOUT_LOWERCASEDSEARCHFIELD_PROVIDED')

            search = search.lower()
            filters.append(Q(**{f'{lowercased_search_field}__{search_policy}': search}))

        if json_filters:
            for key in json_filters:
                filters.append(Q(**{key: json_filters[key]}))

        if q_filters:
            for qf in q_filters:
                filters.append(qf)

        if order_by:
            direction = '-' if order_by[0] == '-' else ''
            order_by_without_direction = order_by if not direction else order_by[1:]

            if not hasattr(cls, 'allowed_ordering'):
                allowed_ordering = {'created': 'created'}
            else:
                allowed_ordering = getattr(cls, 'allowed_ordering')
                if 'created' not in allowed_ordering:
                    allowed_ordering['created'] = 'created'

            if order_by_without_direction not in allowed_ordering:
                raise http.HttpNotAcceptable(id_message='ORDER_NOT_ALLOWED',
                                             message=f'{order_by} field is not allowed, allowed fields are {allowed_ordering.keys()}')

            order_by = f'{direction}{allowed_ordering[order_by_without_direction]}'

        have_active_filter = False
        for f in filters:
            if hasattr(f, 'filters') and 'active' in getattr(f, 'filters'):
                have_active_filter = True
                break

        if not have_active_filter:
            filters.append(Q(active=True))

        # if force_ids:
        #     force_ids = force_ids.split(',')
        #     ff = [Q(
        #         Q(Q(id__in=force_ids),
        #           Q(*filters, join_type='AND'), join_type='OR'
        #           ))]
        #
        #     filters = ff

        query = cls.filter(*filters)

        if prefetched:
            query = query.prefetch_related(*prefetched)
        if order_by:
            try:
                query = query.order_by(order_by)
            except Exception as e:
                raise

        if force_limit:
            if not no_paginate:
                raise http.HttpNotAcceptable(id_message='FORCE_LIMIT_NOT_ACCEPTABLE_WITH_PAGINATION')
            query = query.limit(force_limit)

        if debug_return_query:
            return {'sql': query.sql()}

        if expected_one_item:
            try:
                item = await query.get_or_none()
                if not item:
                    if return_none_if_single_object_not_exits:
                        return None
                    raise http.HttpErrorNotFound

            except http.HttpErrorNotFound:
                raise
            except Exception as e:
                raise http.HttpInternalServerError(id_message='NOT_FOUND_OR_FOUND_MORE_THEN_ONE_ITEM')

            if return_awaitable_orm_objects:
                return item

            if row_post_processor:
                return row_post_processor(item.serialize(fields=fields, prefetched=prefetched, language=language))
            return await item.serialize(fields=fields, prefetched=prefetched, language=language)

        # print('-'*100)
        # print(query.sql())
        # print('-'*100)

        if no_paginate:
            if distinct:
                query = query.distinct()
            if return_awaitable_orm_objects:
                return query.all()

            if row_post_processor:
                return [
                    row_post_processor(await item.serialize(fields=fields, prefetched=prefetched, language=language))
                    for item in
                    await query.all()]

            return [await item.serialize(fields=fields, prefetched=prefetched, language=language) for item in
                    await query.all()]

        if return_awaitable_orm_objects:
            return query.offset((page - 1) * per_page).limit(per_page).all()

        if not request:
            raise http.HttpNotAcceptable(id_message='FOR_PAGINATE_REQUEST_OBJECT_MUST_BE_PROVIDED')
        try:
            # print('-SQL- '*20)
            # print(query.sql())
            # print('/' + '-SQL- '*20)

            return await paginate(page, per_page, query, fields, prefetched, language, request=request,
                                  only_summary=only_summary, distinct=distinct,
                                  include_columns_in_response=include_columns_in_response,
                                  include_menus_in_response=include_menus_in_response,
                                  force_connection=force_connection, row_post_processor=row_post_processor)
        except Exception as e:
            raise


async def paginate(page, per_page, query, fields, prefetched, language, request, only_summary=False,
                   items_name='items', distinct=False, include_columns_in_response=False,
                   include_menus_in_response=False,
                   row_post_processor=None,
                   force_connection='conn_test'):
    try:
        qcount = query.annotate(count=Count('id', distinct=True)).values('count')
        # print(qcount.sql())
        sql = qcount.sql()
        # print("SQL",sql)
        # print( sql.split('GROUP BY') )
        # count = (await qcount)[0]['count']
        # count = (await query.annotate(count=Count('id')).values('count'))[0]['count']

        from tortoise import Tortoise
        # TODO: sredi ovo da to bude default !!!
        conn = Tortoise.get_connection(force_connection)
        raw_query = sql.split('GROUP BY')[0]

        # print("\n\n",raw_query,"\n\n")
        count = (await conn.execute_query(raw_query))[1][0]['count']
        # count = x[1][0]['count']
    except  Exception as e:
        count = 0

    # count = query.annotate(count=Count("id", distinct=True)).values('count').sql()[0]['count']

    if distinct:
        query = query.distinct()

    # if distinct:
    #     for i in await query.all().values('id_site','cache11__customer_site_number'):
    #         print(i)

    # cquery = query.order_by('id').values('id')
    # try:
    #     count = len(await cquery)
    # except Exception as e:
    #     raise

    total_pages = (count // per_page) + (1 if count % per_page > 0 else 0)

    # TODO: parsiraj testiraj da li treba +1 za next

    uri = request.uri.split('?')[0]
    params = request.arguments

    for p in params:
        for i in range(len(params[p])):
            params[p][i] = params[p][i].decode('utf-8')
        if len(params[p]) == 1:
            params[p] = params[p][0]

    previous_page = page - 1 if page > 1 else None
    next_page = page + 1 if page < total_pages else None

    if 'page' in params:
        params['page'] = str(previous_page) if previous_page else '1'
    prev_params = urllib.parse.urlencode(params)

    if 'page' in params:
        params['page'] = str(next_page) if next_page else str(total_pages)
    next_params = urllib.parse.urlencode(params)

    summary = {
        'total_items': count,
        # 'total_pages': (count // per_page)+1 if int(count / per_page) == count / per_page else (count // per_page),
        'total_pages': total_pages,
        'page': page,
        'per_page': per_page,

        'previous_page': previous_page,
        'next_page': next_page,
        'previous_uri': f'{uri}?{prev_params}' if previous_page else None,
        'next_uri': f'{uri}?{next_params}' if next_page else None

    }

    if only_summary:
        return {'summary': summary}

    items = await query.offset((page - 1) * per_page).limit(per_page).all()

    res = {
        'summary': summary,
    }

    if include_menus_in_response:
        menus_function, table_property_name = include_menus_in_response
        menus = await menus_function(request, table_property_name)

        res['menus'] = menus

    if include_columns_in_response:
        columns_function, table_property_name = include_columns_in_response

        columns = await columns_function(request, table_property_name)

        def f(c):
            if 'hidden' in c:
                del c['hidden']
            if 'locked' in c:
                del c['locked']
            return c

        res['columns'] = [f(c) for c in columns if 'hidden' not in c or not c['hidden']]

    if row_post_processor:
        # for item in items:
        #     # sitem = await item.serialize(fields=fields, prefetched=prefetched, language=language)
        #     # print("SITEM",sitem)
        #     # print("RITEM",row_post_processor(sitem))
        #     #

        res[items_name] = [
            row_post_processor(await item.serialize(fields=fields, prefetched=prefetched, language=language)) for item
            in
            items]
        return res

    res[items_name] = [await item.serialize(fields=fields, prefetched=prefetched, language=language) for item in items]
    return res


class BaseModel(BaseModelNoTenant):
    # TODO: inherit Model and make it abstracet (change on all project)
    #
    # class Meta:
    #     abstract = True

    id_tenant = fields.UUIDField(index=True)

    async def mk_cache(self, *args, **kwargs):
        pass

    @classmethod
    async def gen_uid(cls, id_tenant, prefix=None, size=None, alphabet=None):

        # if not hasattr(cls, 'uid'):
        #     raise NameError('NO_UID_FIELD_DEFINED')

        if not prefix:
            prefix = cls.uid_prefix if hasattr(cls, 'uid_prefix') else 'X'

        if not size:
            size = cls.uid_total_size if hasattr(cls, 'uid_total_size') else 5

        if not alphabet:
            alphabet = cls.uid_alphabet if hasattr(cls, 'uid_alphabet') else uid_alphabet

        for attempt in range(0, uid_generator_max_attempts):
            uid = prefix + nanoid.generate(alphabet=alphabet, size=size - 1)

            # u slucaju da je id_tenant None, samo se generise nema provera
            if not id_tenant:
                return uid

            try:
                exists = await cls.filter(uid=uid, id_tenant=id_tenant).get_or_none()
            except Exception as e:
                raise NameError('ERROR_FETCHING_OBJECT_BY_UID')

            if not exists:
                return uid

        raise NameError('TOO_MANY_ATTEMPS_FOR_UID_GENERATION')

    @classmethod
    def cvt_filters(cls, filters):
        qfilters = []

        def kw(f):
            if cls.filters[f]['type'] is None:
                return {cls.filters[f]['target']: filters[f]}

            return {cls.filters[f]['target']: cls.filters[f]['type'](filters[f])}

        if hasattr(cls, 'filters'):
            for filter in getattr(cls, 'filters'):
                if filter in filters:
                    qfilters.append(Q(**kw(filter)))
                    del filters[filter]

        return qfilters

    class BaseModelCache(BaseModelNoTenant):
        pass


class C11Base:
    created_by_display_name = fields.CharField(max_length=255, null=True)
    last_updated_by_display_name = fields.CharField(max_length=255, null=True)

    created_by_display_profile_picture = fields.CharField(max_length=255, null=True)
    last_updated_by_display_profile_picture = fields.CharField(max_length=255, null=True)


class BaseModelOptions(BaseModel):
    key = fields.CharField(max_length=128)
    value = fields.TextField(null=True)


class BaseModelLookup(BaseModelNoTenant):
    id_tenant = fields.UUIDField(index=True)
    code = fields.CharField(max_length=128, null=False)
    order = fields.IntField(null=True)
    active = fields.BooleanField(null=False, default=True)


async def fix_name_case_fields(instance):
    if hasattr(instance, 'name_case_fields'):
        for field in getattr(instance, 'name_case_fields'):
            if hasattr(instance, field):
                f = getattr(instance, field)
                if f:
                    setattr(instance, field, f.lower())