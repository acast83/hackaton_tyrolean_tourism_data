import tshared.utils.ipc as ipc


async def enqueue(request, receiver_display_name, receiver_email, subject, html_body, sender_display_name=None, sender_email=None, attachments=None, body=None):
    b = {
        # 'sender_email': sender_email,
        # 'sender_display_name': sender_display_name,
        'receiver_email': receiver_email,
        'receiver_display_name': receiver_display_name,
        'subject': subject,
        'html_body': html_body,
        'body': body
    }
    if sender_display_name:
        b['sender_display_name'] = sender_display_name
    if sender_email:
        b['sender_email'] = sender_email
    if attachments:
        b['attachments'] = attachments

    return await ipc.call(request, 'sendmail', 'POST', '/enqueue', body=b)


async def send_enqueued_email(request, id_email, body=None):
    if not body:
        body = {'_void': True}
    return await ipc.call(request, 'sendmail', 'POST', f'/{id_email}/send', body=body)


async def sendmail(request, sender_display_name, sender_email, receiver_display_name, receiver_email, subject, html_body, body=None):
    return await ipc.call(request, 'sendmail', 'POST', '/send', body={
        'sender_email': sender_email,
        'sender_display_name': sender_display_name,
        'receiver_email': receiver_email,
        'receiver_display_name': receiver_display_name,
        'subject': subject,
        'html_body': html_body,
        'body': body
    })

# {{ ipc_function }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
