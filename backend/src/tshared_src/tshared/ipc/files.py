import tshared.utils.ipc as ipc

async def get(request, fname, token, download):

    return await ipc.call(request, 'files', 'GET', f'/static/{fname}?token={token}&download={"true"if download else "false"}')
    

# {{ ipc_function }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
