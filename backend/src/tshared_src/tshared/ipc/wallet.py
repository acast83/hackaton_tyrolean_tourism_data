import datetime
import tshared.utils.ipc as ipc


async def lookup_wallet_transaction_type(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'wallet', '/lookups/transaction_type', last_updated)


async def lookup_wallet_exchange_operation(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'wallet', '/lookups/exchange_operation', last_updated)

# {{ ipc_function }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
