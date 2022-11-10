import datetime
import urllib.parse
import uuid
import tshared.utils.ipc as ipc


async def lookup_base(request, svc, url, last_updated: datetime.datetime = None):
    params = ''
    if last_updated:
        params = '?' + urllib.parse.urlencode({'last_updated': str(last_updated)})

    url += params

    return await ipc.call(request, svc, 'GET', url)


async def check_person_existance(request, id_person: uuid.UUID):
    return await ipc.call(request, 'bp', 'GET', f'/persons/{id_person}/exists')


async def get_person_data(request, id_person: uuid.UUID):
    return await ipc.call(request, 'bp', 'GET', f'/persons/{id_person}')


async def insert_person_data(request, body):
    return await ipc.call(request, 'bp', 'POST', f'/persons/', body=body)


async def update_person_data(request, id_person, return_person_data=False, body: dict = None, ):
    try:
        if not body:
            body = {}

        body['return_person_data'] = return_person_data
        return await ipc.call(request, 'bp', 'PUT', f'/persons/{id_person}', body=body)
    except Exception as e:
        raise


async def create_company(request, **kwargs):
    return await ipc.call(request, 'bp', 'POST', f'/companies/', body={**kwargs})


async def update_company(request, company_id: uuid.UUID, **kwargs):
    return await ipc.call(request, 'bp', 'PATCH', f'/companies/{company_id}', body={**kwargs})


async def create_company_site(request, company_id: uuid.UUID, **kwargs):
    return await ipc.call(request, 'bp', 'POST', f'/companies/{company_id}/sites', body={**kwargs})


async def get_company(request, id_company, fields=None):
    if fields:
        fields = f'?fields={fields}'
    else:
        fields = ''
    return await ipc.call(request, 'bp', 'GET', f'/companies/{id_company}{fields}')

async def get_company_by_source_id(request, source, id_source, fields=None):
    if fields:
        fields = f'?fields={fields}'
    else:
        fields = ''
    return await ipc.call(request, 'bp', 'GET', f'/companies/by-source/{source}/{id_source}?{fields}')


async def get_company_hq(request, id_company, fields=None):
    if fields:
        fields = f'&fields={str(fields)}'
    else:
        fields = ''
    return await ipc.call(request, 'bp', 'GET', f'/companies/{id_company}/sites?hq_only=true{fields}')


async def get_company_site(request, id_company_site):
    return await ipc.call(request, 'bp', 'GET', f'/sites/{id_company_site}')


async def lookup_companies(request, last_updated: datetime.datetime = None):
    return await lookup_base(request, 'bp', '/lookups/companies', last_updated)


async def lookup_company_sites(request, last_updated: datetime.datetime = None):
    return await lookup_base(request, 'bp', '/lookups/sites', last_updated)


async def lookup_company_types(request, last_updated: datetime.datetime = None):
    return await lookup_base(request, 'bp', '/lookups/company_types', last_updated)


async def lookup_educational_titles(request, last_updated: datetime.datetime = None):
    return await lookup_base(request, 'bp', '/lookups/educational_titles', last_updated)


async def lookup_genders(request, last_updated: datetime.datetime = None):
    return await lookup_base(request, 'bp', '/lookups/genders', last_updated)


async def lookup_nationalities(request, last_updated: datetime.datetime = None):
    return await lookup_base(request, 'bp', '/lookups/nationalities', last_updated)


async def lookup_document_types(request, last_updated: datetime.datetime = None):
    return await lookup_base(request, 'bp', '/lookups/document_types', last_updated)


async def lookup_phone_types(request, last_updated: datetime.datetime = None):
    return await lookup_base(request, 'bp', '/lookups/phone_types', last_updated)


async def lookup_email_types(request, last_updated: datetime.datetime = None):
    return await lookup_base(request, 'bp', '/lookups/email_types', last_updated)


async def lookup_bp_industry_types(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'bp', '/lookups/industry_types', last_updated)


async def lookup_bp_gender_prefix(request, last_updated: datetime.datetime = None):
    return await ipc.lookup_base(request, 'bp', '/lookups/gender_prefix', last_updated)

# {{ ipc_function }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}