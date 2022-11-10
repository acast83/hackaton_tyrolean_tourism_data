import datetime

import tshared.utils.ipc as ipc


# lookups

async def lookup_phone_number_types(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'contacts', '/lookups/phone_number_types', last_updated)


async def lookup_email_types(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'contacts', '/lookups/email_types', last_updated)

# {{ ipc_function }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
