import tshared.utils.ipc as ipc


# lookups

async def update_cache_count(request, id_shortener, number_of_accesses):
    return await ipc.call(request, 'shortener', 'PATCH',
                          f'/update-cache-count', body={'id': str(id_shortener),
                                                        'number_of_accesses': number_of_accesses})

# {{ ipc_function }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
