import tshared.utils.ipc as ipc


async def enqueue(request, target, message, scheduled=None):
    return await ipc.call(request, 'sms', 'POST', '/enqueue', body={
        'target_number': target,
        'message': message,
        'scheduled_not_send_before_timestamp': scheduled
    })


async def send_enqueued_sms(request, id_sms):
    return await ipc.call(request, 'sms', 'POST', f'/{id_sms}/send', body={'a': 'b'})


async def send_sms(request, target, message):
    return await ipc.call(request, 'sms', 'POST', '/send', body={
        'target_number': target,
        'message': message,
        'scheduled_not_send_before_timestamp': None
    })

# {{ ipc_function }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
