'''
            "text": "Created OLO Request {'uid': 'O6ENXJUPVC7C6VU',
            'iccid': '1234567890', 'id_tenant': '6ce5ba2e-1d55-47ef-9111-b8ee748efd39',
            'created_by': '9538ea17-691c-4f2c-a465-5b1846105f67',
            'id_customer': '419913ac-feb2-4012-8f1d-06a01e5806b5',
            'operation_id': 'c253845d-2465-4eea-89a9-30757175af66',
            'phone_number': '+381695967576', 'portin_iccid': '0987654321', 'account_balance': 100.0, 'last_updated_by': '9538ea17-691c-4f2c-a465-5b1846105f67', 'portin_datetime': '2022-05-07 00:00:00+02:00', 'portin_phone_number': '+386012345678', 'id_contact_subscriber': '59651d8e-883c-4709-81f3-a2e3a437b420'}"

'''


async def compile_attributes(data, pattern):
    lst = []
    for key in data:
        if key not in pattern:
            continue

        if pattern[key] == 'text':
            lst.append(f'{key}: {data[key]}')
            continue

        if type(pattern[key])==tuple and pattern[key][0]=='lookup':
            lookup = pattern[key][1]


    return '<ul>' + '<li>'.join(lst) + '</ul>'


async def CREATE_OLO_REQUEST(handler, data, lang):
    import tshared.lookups.cache as lookups

    lkps = {
        'l_operations': await lookups.LookupOloOloOperationType.create(handler)
    }

    d = data['data']
    return f"Created OLO Request {d['uid']} with the following attributes: " + \
           await compile_attributes(d, pattern={'iccid': 'text',
                                                'phone_number': 'text',
                                                'operation_id': ('lookup', lkps['l_operations'])
                                                })


supported_actions = 'CREATE_OLO_REQUEST',


async def messages(handler, data, lang='en'):
    if 'action' not in data:
        return "TODO / missing action in flow"

    a = data['action']
    if data['action'] not in supported_actions:
        return f"TODO / action {data['action']} is not implemented"

    if a == 'CREATE_OLO_REQUEST': return await CREATE_OLO_REQUEST(handler, data, lang)
    # return str(data['action'])
    return "TODO"
