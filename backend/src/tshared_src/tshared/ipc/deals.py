import json
import uuid
import datetime
import urllib.parse

import tshared.utils.ipc as ipc


async def create_mock_deal(request, body):
    return await ipc.call(request, 'deals', 'POST', '/mock', body=body)


async def create_deal(request, body, _return_type='id'):
    return await ipc.call(request, 'deals', 'POST', f'/?_return_type={_return_type}', body=body)


async def delete_deal(request, id_deal, reason):
    return await ipc.call(request, 'deals', 'DELETE', f'/{id_deal}?reason={reason}')


async def get_single_deal(request, id_deal):
    return await ipc.call(request, 'deals', 'GET', f'/{id_deal}')


async def get_deals4kanban_pipeline(request, id_kanban_pipeline, filters: dict = None, fields: str = None,
                                    order_by: str = '-created',
                                    no_paginate: bool = True, page: int = 1, force_limit: int = None,
                                    per_page: int = 50, include_columns_in_response: bool = True, include_menus_in_response: bool = True,
                                    search: str = None):
    import urllib.parse
    p = {
        'no_paginate': 'true' if no_paginate else 'false',
        'fields': fields,
    }
    if filters:
        p['filters'] = json.dumps(filters)

    p = urllib.parse.urlencode(p)

    return await ipc.call(request, 'deals', 'GET', f'/kanban-pipelines/{id_kanban_pipeline}/deals?{p}')


async def patch_deal(request, id_deal, body, origin):
    return await ipc.call(request, 'deals', 'PATCH', f'/{id_deal}?origin={origin}', body=body)
    # return await ipc.call(request, 'deals', 'PATCH', f'/igor-tmp-deal-patch/{id_deal}', body=body)


async def get_deal_cache4kanban(request, id_deal):
    return await ipc.call(request, 'deals', 'GET', f'/{id_deal}/cache/kanban')


async def mk_cache(request, id_deal, section=None):
    return await ipc.call(request, 'deals', 'PATCH', f'/{id_deal}/mk-cache', body={
        'section': section
    })


async def lookup_deals_deal_stages(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'deals', '/lookups/deal_stages', last_updated)


async def lookup_deals_deal_classifications(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'deals', '/lookups/deal_classifications', last_updated)


async def lookup_deals_deal_sources(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'deals', '/lookups/deal_sources', last_updated)


async def lookup_deals_deal_statuses(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'deals', '/lookups/deal_statuses', last_updated)

# {{ ipc_function }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}