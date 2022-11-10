import uuid
import datetime
import urllib.parse

import tshared.utils.ipc as ipc


async def my_coupons(request):
    return await ipc.call(request, 'conferences', 'GET', f'/my-coupons')


async def initialize_coupons(request, acronym, id_user):
    res = await ipc.call(request, 'conferences', 'POST', f'/{acronym}/init-coupons', body={'id_user': str(id_user)})
    return res

async def lookup_conferences_conf_session_status(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'conferences', '/lookups/conf_session_status', last_updated)

# {{ ipc_function }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
