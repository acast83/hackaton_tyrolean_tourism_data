import uuid
import base3.handlers
from .. import models
from base3 import http
from base3.core import Base
from base3.decorators import route, api
import tshared.ipc.deals as ipc_deals
import tshared.ipc.documents as ipc_documents
import tshared.ipc.tickets as ipc_tickets
import tshared.ipc.tenants as ipc_tenants

import tshared.lookups.cache as lookups

db_connection = 'conn_flows'
from ..messages.deals import messages as deal_messages
from ..messages.olo import messages as olo_messages


@route('/about')
class HandlerFlowsAbout(Base):
    @api(auth=False)
    async def get(self):
        """
        Get about information

        Responses:
            @flows/GET_200_documentation_get_about.json
        """
        return {'service': 'flows'}


@route('/options')
class HandlerFlowsOptions(base3.handlers.BaseOptionsHandler):
    model_Option = models.Option
    db_connection = db_connection


@route('/multiply')
class HandlerMultiplyFlows(Base):
    """
    Parameters:
        instance (path):    # TODO
        id_instance (path):
    """

    @api()
    async def post(self,
                   list_of_new_flow_messages: list,
                   expected_count_in_result=False
                   ):
        """
        Post multiply TODO tests

        Parameters:
            list_of_new_flow_messages (body):
            expected_count_in_result (body):

        RequestBody:
            @flows/POST_200_documentation_post_multiply.request_body.json TODO

        Responses:
            @flows/POST_200_documentation_post_multiply.json
        """

        results = []

        from tortoise.transactions import in_transaction
        async with in_transaction(connection_name='conn_flows'):

            for fm in list_of_new_flow_messages:

                instance = fm['instance']
                id_instance = fm['id_instance']
                type_id = fm['type_id'] if 'type_id' in fm else None
                if not type_id and 'type_code' in fm:
                    from tshared.lookups.cache import LookupFlowTypes
                    lft = await LookupFlowTypes.create(handler=self)
                    type_id = lft.get(key=fm['type_code'], index='code', default=None, dkey='id')

                if type_id is None:
                    raise http.HttpInternalServerError(id_message='UNKNOWN_TYPE_ID')

                html = fm['html'] if 'html' in fm else None
                text = fm['text'] if 'text' in fm else None
                data = fm['data'] if 'data' in fm else None

                body = {'html': html,
                        'text': text,
                        'data': data,
                        'type_id': type_id,
                        'instance': instance,
                        'id_instance': id_instance,
                        'created_by': self.id_user,
                        'last_updated_by': self.id_user,
                        'id_tenant': self.id_tenant
                        }
                try:
                    flow = await models.Flow.safe_create(body)
                    await flow.save()
                except Exception as e:
                    raise

                if expected_count_in_result:
                    filters = {'id_tenant': self.id_tenant,
                               'instance': instance, 'id_instance': id_instance, 'type_id': type_id}

                    count = await models.Flow.filter(**filters).count()

                    results.append({'id': flow.id,
                                    'count': count})
                    continue

                results.append({'id': flow.id})

        return results


@route('/:instance/parent/:level/:id_parent')
class GetFlowsByParentOnLevel(Base):

    @api()
    async def get(self, instance: str, level: int, id_parent: uuid.UUID, no_paginate: bool = True, page=1, per_page=100, fields=None,
                  include_menus_in_response=True,
                  order_by='-created', search=None, flow_types: str = None, activity_mode=True):
        lang = "en"
        try:
            me = await ipc_tenants.me(self.request)
            lang = me["language"]  # this will fail, We need to get somehow language from v2
        except:
            pass
        json_filters = {'id_tenant': self.id_tenant, 'active': True, 'instance': instance}

        level2key = {
            1: 'parent_1st_level',
            2: 'parent_2nd_level',
            3: 'parent_3rd_level'
        }

        if level not in level2key:
            raise http.HttpNotAcceptable(id_message='INVALID_PARENT_LEVEL')

        json_filters[f'{level2key[level]}'] = id_parent

        if flow_types:
            json_filters['type__in'] = [uuid.UUID(x) for x in flow_types.split(',')]

        if search:
            json_filters["cache1n__language"] = lang
        res = await models.Flow.base_get(request=self.request, json_filters=json_filters,
                                         no_paginate=no_paginate, page=page, per_page=per_page,
                                         include_menus_in_response=(table_menus, instance) if
                                         include_menus_in_response else False,
                                         lowercased_search_field="cache1n__search",
                                         search=search,
                                         fields=fields, order_by=order_by, prefetched=['cache11', 'cache1n'])

        flow_data = res if no_paginate else res["items"]
        flow_messages = []
        if flow_data:
            flow_messages = await generate_messages(self, lang=lang, instance=instance, res=flow_data, activity_mode=activity_mode)

        if not no_paginate:
            res["items"] = flow_messages
        return res
        #
        # if instance == 'olo86':
        #     for f in res:
        #         if 'data' in f:
        #             f['html'] = await olo_messages.messages(f['data'], lang='en')
        #             del f['data']
        #
        # if instance == 'deals':
        #
        #     for f in res:
        #         if 'data' in f:
        #             f['html'] = await deal_messages.messages(f['data'], lang='en')
        #             del f['data']


async def generate_messages(handler, lang, instance, res, activity_mode=False):
    flow_types_lookups = await lookups.LookupFlowTypes.create(handler=handler, force_key_value=['code', 'id'])

    if instance == 'olo86':
        for f in res:
            if 'data' in f:
                msg = await olo_messages.messages(handler, f['data'], lang=lang)
                if msg[:4] == 'TODO':
                    f['html'] = 'DEFAULT: ' + f['html']
                else:
                    f['html'] = msg

                del f['data']

    if instance == 'sales':

        for f in res:
            if str(f['type_id']) == flow_types_lookups['FLOW_TYPE_MESSAGE']:
                continue

            if 'data' in f:
                f['html'] = await deal_messages.messages(handler, data=f['data'], lang=lang, activity_mode=activity_mode, created_by_display_name=f["created_by_display_name"])
                del f['data']
    return res


async def table_menus(request, table):
    if table not in ("flows"):
        return []
    if table == "flows":
        res = {
            'action_menus': {
                '37bfa239-0cf3-4440-9d2b-7f75a10f3ce0': [
                    {
                        "command": "PRIORITY",
                        "icon": "waiting for data from frontend",
                        "code": "CHANGE_PRIORITY",
                        "name": "Change priority",
                        "method": "PATCH",
                        "url": "/flows/deals/:id",

                    },
                    {
                        "command": "DELETE",
                        "icon": "waiting for data from frontend",
                        "code": "DELETE",
                        "name": "Delete",
                        "method": "DELETE",
                        "url": "/flows/deals/:id",

                    },
                    {
                        "command": "COPYTOCLIPBOARD",
                        "icon": "copy",
                        "code": "COPY",
                        "name": "Copy link",
                        "url": "/flows/deals/:id"
                    }
                ]
            },

        }

    return res


@route('/:instance/:id_instance')
class HandlerFlows(Base):
    """
    Parameters:
        instance (path):    # TODO
        id_instance (path):
    """

    @api()
    async def post(self, instance: str, id_instance: uuid.UUID, type_id: uuid.UUID = None, html: str = None, text: str = None,
                   data: dict = None, attached_documents: dict = None, expected_count_in_result: bool = False,
                   parents: dict = None):
        """
        Post single flow instance   TODO parameters

        Parameters:
            type_id (body): Flow type
            html (body):    TODO
            text (body):    TODO
            data (body):    TODO
            attached_documents (body):   TODO
            expected_count_in_result (body): Bool value. If true, response body will return number of all flow instances.

        RequestBody:
            @flows/POST_200_documentation_post_single_flow_instance.request_body.json

        Responses:
            @flows/POST_200_documentation_post_single_flow_instance.json
        """
        lookup_flow_visibility = await lookups.LookupFlowVisibility.create(self, force_key_value=['code', 'id'])
        lookup_flow_priority = await lookups.LookupFlowPriorities.create(self, force_key_value=['code', 'id'])

        try:
            if not type_id:
                flow_types_lookups = await lookups.LookupFlowTypes.create(handler=self)
                type_id = flow_types_lookups.get('FLOW_TYPE_MESSAGE', index='code')["id"]
        except Exception as e:
            raise

        if not parents:
            parents = {
                'parent_1st_level': None,
                'parent_2nd_level': None,
                'parent_3rd_level': None
            }

        body = self.request_body()

        body['instance'] = instance
        body['id_instance'] = id_instance
        body["type_id"] = type_id
        # body["visibility_id"] = lookup_flow_visibility["VISIBLE"]
        # body["priority_id"] = lookup_flow_priority["REGULAR"]  # change if there are cases when we create important flow

        for p in parents:
            body[p] = parents[p]

        try:
            flow = await models.Flow.safe_create(body)
            await flow.save()

            await flow.mk_cache(handler=self, data=data)

        except Exception as e:
            raise

        if expected_count_in_result:
            filters = {'id_tenant': self.id_tenant,
                       'instance': instance, 'id_instance': id_instance, 'type_id': type_id}

            # if data and 'command' in data:
            #     TODO : check this
            # filters['data__contains'] = [{"command": data['command']}]

            count = await models.Flow.filter(**filters).count()

            return {'id': flow.id,
                    'count': count}

        return {'id': flow.id,
                # "attachments": [],
                "instance": instance,
                "id_instance": id_instance,
                "post_type": "message",  # hardcoded
                "saved_message": flow.html,
                "html": flow.html,
                }

    @api()
    async def get(self, instance: str, id_instance: uuid.UUID, no_paginate: bool = True, page=1, per_page=100, fields=None,
                  order_by='-created', search=None, flow_types: str = None, include_header: bool = False,
                  include_menus_in_response=True,
                  id_type_csv=None, priority=None, visibility=None):
        """
        Get single flow instance TODO parameters

        Parameters:
            page (query): Current page
            per_page (query): Number of items per page
            search (query): General search
            fields (query): CSV string of fields (by default it is null, and in this case will be used from personal user setting)
               enum: @Flow.default_fields
            order_by (query): Order
               enum: @Flow.allowed_ordering
            no_paginate (query): If true, pagination will not be provided. By default, it is True
            flow_types (query):  TODO

        Responses:
            @flows/GET_200_documentation_get_single_flow_instance.json
        """
        lang = "en"
        try:
            me = await ipc_tenants.me(self.request)
            lang = me["language"]  # this will fail, We need to get somehow language from v2
        except:
            pass
        lookup_flow_types = await lookups.LookupFlowTypes.create(self, force_key_value=['code', 'id'])
        lookup_flow_visibility = await lookups.LookupFlowVisibility.create(self, force_key_value=['code', 'id'])
        lookup_flow_priority = await lookups.LookupFlowPriorities.create(self, force_key_value=['code', 'id'])

        json_filters = {'id_tenant': self.id_tenant, 'touched': True, 'active': True, 'instance': instance,
                        'id_instance': id_instance, }
        if id_type_csv:
            frontend_type_codes = id_type_csv.split(",")
            flow_types_dict = {"1": lookup_flow_types["FLOW_TYPE_MESSAGE"],
                               "2": lookup_flow_types["FLOW_TYPE_SYSTEM_ACTION"],
                               "3": lookup_flow_types["FLOW_TYPE_USER_ACTION"],
                               "5": lookup_flow_types["FLOW_TYPE_USER_ACTION"]}
            json_filters["type_id__in"] = [flow_types_dict[key] for key in flow_types_dict if key in frontend_type_codes]
        if visibility:
            frontend_visibility_codes = visibility.split(",")
            visibility_dict = {'visible': False,
                               'deleted': True
                               }
            # if 'visible' in frontend_visibility_codes:
            #     visibility_filter = [False, None]
            # if 'deleted' in frontend_visibility_codes:
            #     visibility_filter.append(True)
            # json_filters["archived__in"] = visibility_filter
            json_filters["archived__in"] = [visibility_dict[key] for key in visibility_dict if key in frontend_visibility_codes]

            # if "deleted" in frontend_visibility_codes:
            #
            #     json_filters["archived__in"] = [True, False]

            # flow_visibility_dict = {"visible": lookup_flow_visibility["VISIBLE"],
            #                         "deleted": lookup_flow_visibility["HIDDEN"]}
            # json_filters["visibility_id__in"] = [flow_visibility_dict[key] for key in flow_visibility_dict if key in frontend_visibility_codes]

        if priority:
            frontend_priority_codes = priority.split(",")
            flow_priority_dict = {"important": True,
                                  "regular": False}
            json_filters["important__in"] = [flow_priority_dict[key] for key in flow_priority_dict if key in frontend_priority_codes]

        if flow_types:  # mislim da je ovo nepotrebno, proveriti
            json_filters['type__in'] = [uuid.UUID(x) for x in flow_types.split(',')]

        if search:
            json_filters["cache1n__language"] = lang

        self.log.info(f"filters: {json_filters}")
        res = await models.Flow.base_get(request=self.request, json_filters=json_filters,
                                         no_paginate=no_paginate, page=page, per_page=per_page,
                                         include_menus_in_response=(table_menus, instance) if
                                         include_menus_in_response else False,
                                         lowercased_search_field="cache1n__search",
                                         search=search,
                                         fields=fields, order_by=order_by, prefetched=['cache11', 'cache1n'])

        flow_data = res if no_paginate else res["items"]
        flow_messages = []
        if flow_data:
            flow_messages = await generate_messages(self, lang=lang, instance=instance, res=flow_data, )

        description, attachments, created, created_by = None, [], None, None

        if not include_header:
            if not no_paginate:
                res["items"] = flow_messages
            return res

        if instance == "deals":
            deal, _ = await ipc_deals.get_single_deal(self.request, id_deal=id_instance)
            description = deal["detailed_description"]
            created = deal["created"]
            created_by = deal["created_by"]

            documents, _ = await ipc_documents.get_all_documents4_id_instance(self.request, instance=instance, id_instance=id_instance)
            attachments = documents["items"]

        elif instance == "tickets":
            ticket, _ = await ipc_tickets.get_single_ticket(self.request, id_ticket=id_instance)
            description = ticket["description"]
            created = ticket["created"]
            created_by = ticket["created_by"]
            documents, _ = await ipc_documents.get_all_documents4_id_instance(self.request, instance=instance, id_instance=id_instance)
            attachments = documents["items"]


        else:
            return res

        return {
            'flow_header': {
                'enabled': True,  # it is enough to be flow_header = None ?!?
                'description': description,
                'attachments': attachments,
                'created': created,  # date time of deal/ticket/... has been created
                'created_by': created_by,  # id of person who created deal/ticket/...
            },
            'flow': res}

        # TODO: prebacei na ovo jer ce ti trebati serializacija, ili provajduj serializaciju, ili je opisi u samom flow objektu sto je i najbolje

        # if not fields:
        #     if hasattr(models.Flow, 'default_fields'):
        #         fields = getattr(models.Flow, 'default_fields')
        # else:
        #     if type(fields) == str:
        #         fields = fields.split(',')
        #
        #
        # return [await f.serialize(fields=fields, prefetched=['cache11'], language='en') for f in await
        # models.Flow.base_get(json_filters=json_filters,
        #                      no_paginate=no_paginate, page=page, per_page=per_page,
        #                      fields=fields, order_by=order_by, prefetched=['cache11'],
        #                      return_awaitable_orm_objects=True)]


@route('/:flow_id')
class HandlerSingleFlowItem(Base):
    @api()
    async def get(self, flow_id: uuid.UUID):
        """
        returns single flow item data
        """
        return await models.Flow.base_fetch_single(id=flow_id, id_tenant=self.id_tenant, fields=None, )

    @api()
    async def patch(self, flow_id: uuid.UUID):
        """
        patch method used to update single flow item. #test when you get body from frontend
        """
        flow = await models.Flow(active=True, id_tenant=self.id_tenant, id=flow_id).get_or_none()
        if not flow:
            raise http.HttpErrorNotFound(id_message="FLOW_ITEM_NOT_FOUND", message=str(flow_id))

        if True:
            flow, updated = await models.Flow.base_patch_single(id=flow_id, handler=self)

            self.log.debug(f'flow updated = {flow}, {updated}')

            if flow and updated:
                self.log.debug("SAVING")
                await flow.save()
                await flow.mk_cache(handler=self)

            self.log.debug(f"RETURN: {updated}")

            return {'updated': updated}


@route('/:flow_id/archived')
class HandlerSingleFlowItemArchive(Base):

    @api()
    async def patch(self, flow_id: uuid.UUID, value: bool):
        """
        patch method used to update single flow item using actions
        """

        flow = await models.Flow.filter(active=True, id_tenant=self.id_tenant, id=flow_id).get_or_none()
        if not flow:
            raise http.HttpErrorNotFound(id_message="FLOW_ITEM_NOT_FOUND", message=str(flow_id))
        if value:
            flow.archived = True
        else:
            flow.archived = False
        await flow.save()

        return await models.Flow.base_fetch_single(id=flow_id, id_tenant=self.id_tenant, fields=None, )


@route('/:flow_id/important')
class HandlerSingleFlowItemPriority(Base):

    @api()
    async def patch(self, flow_id: uuid.UUID, value: bool):
        """
        patch method used to update single flow item using action important
        """

        flow = await models.Flow.filter(active=True, id_tenant=self.id_tenant, id=flow_id).get_or_none()
        if not flow:
            raise http.HttpErrorNotFound(id_message="FLOW_ITEM_NOT_FOUND", message=str(flow_id))
        if value:
            flow.important = True
        else:
            flow.important = False

        await flow.save()

        return await models.Flow.base_fetch_single(id=flow_id, id_tenant=self.id_tenant, fields=None, )


@route('/:instance/:id_instance/count')
class HandlerCountOfFlows(Base):
    """
    Parameters:
        instance (path):  TODO
        id_instance (path): Instance ID
    """

    @api()
    async def get(self, instance: str, id_instance: uuid.UUID, type_id: uuid.UUID = None, command: str = None) -> dict:
        """
        Get the number of ? TODO

        Parameters:
            type_id (query):    TODO
            command (query):    TODO

        Responses:
            @flows/GET_200_documentation_get_instance_count.json
        """
        filters = {'id_tenant': self.id_tenant,
                   'instance': instance,
                   'id_instance': id_instance
                   }

        if type_id:
            filters['type_id'] = type_id

        if command:
            pass
            filters['data__contains'] = [{"command": "user-fetch-link"}]

            # TODO: Check SQL Query

        try:
            count = await models.Flow.filter(**filters).count()
        except Exception as e:
            raise
        return {'count': count}


@route('/:instance/:id_instance/last')
class HandlerLastFlows(Base):
    """
    Parameters:
        instance (path): # TODO
        id_instance (path): Instance ID
    """

    @api()
    async def get(self, instance: str, id_instance: uuid.UUID, fields: str = None):
        """
        Get the last created instance info  TODO parameters

        Parameters:
            fields (query): CSV string of fields (by default it is null, and in this case will be used from personal user setting)
                enum: @Flow.default_fields

        Responses:
            @flows/GET_200_documentation_get_last_instance.json
        """
        json_filters = {'id_tenant': self.id_tenant, 'touched': True, 'active': True, 'instance': instance,
                        'id_instance': id_instance}

        r = await models.Flow.base_get(json_filters=json_filters,
                                       no_paginate=True,
                                       fields=fields, order_by='-created', prefetched=['cache11'])
        if not r:
            raise http.HttpErrorNotFound
        return r[0]


@route('/:flow_id/action_menu')
class SingleFlowActionMenuHandler(Base):
    @api()
    async def get(self, flow_id: uuid.UUID):
        """
        get single flow post action menu
        """

        flow = await models.Flow.filter(id_tenant=self.id_tenant, id=flow_id).get_or_none()
        if not flow:
            raise http.HttpErrorNotFound(id_message="FLOW_POST_NOT_FOUND")
        if flow.instance == "deals":
            flow_action_menu = [{
                "command": "COPYTOCLIPBOARD",
                "icon": "copy",
                "code": "COPY",
                "name": "Copy link",
                "url": f"/flows/{flow_id}"
            }]

            if flow.archived == False:
                flow_action_menu.append({
                    "command": "ARCHIVE",
                    "icon": "todo",
                    "code": "TODO",
                    "name": "Archive Flow item",
                    "url": f"/flows/{flow_id}/archived"
                })
            else:
                flow_action_menu.append({
                    "command": "RESTORE",
                    "icon": "todo",
                    "code": "TODO",
                    "name": "Restore Flow item",
                    "url": f"/flows/{flow_id}/archived"
                })
            if flow.important == False:
                flow_action_menu.append({
                    "command": "IMPORTANT",
                    "icon": "todo",
                    "code": "TODO",
                    "name": "Make flow item important",
                    "url": f"/flows/{flow_id}/important"
                })
            else:
                flow_action_menu.append({
                    "command": "REGULAR",
                    "icon": "todo",
                    "code": "TODO",
                    "name": "Make flow item regular",
                    "url": f"/flows/{flow_id}/important"
                })
            return flow_action_menu
        else:
            raise http.HttpNotAcceptable(id_message="NOT_IMPLEMENTED_YET")