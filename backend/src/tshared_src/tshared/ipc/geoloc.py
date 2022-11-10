import datetime
import urllib.parse
import uuid
import tshared.utils.ipc as ipc
from base3 import http


async def lookup_base(request, svc, url, last_updated: datetime.datetime = None):
    params = ''
    if last_updated:
        params = '?' + urllib.parse.urlencode({'last_updated': str(last_updated)})

    url += params

    return await ipc.call(request, svc, 'GET', url)


async def lookup_countries(request, last_updated: datetime.datetime = None):
    return await lookup_base(request, 'geoloc', '/lookups/countries', last_updated)


async def lookup_provinces(request, last_updated: datetime.datetime = None, id_country=None):
    return await lookup_base(request, 'geoloc', '/lookups/provinces', last_updated)


async def lookup_municipalities(request, last_updated: datetime.datetime = None, id_country=None, id_province=None):
    return await lookup_base(request, 'geoloc', '/lookups/municipalities', last_updated)


async def get_country_data_by_code(request, code: str, language='default'):
    return await ipc.call(request, 'geoloc', 'GET', f'/countries/code/{code}')


async def get_province_data_by_country_and_province_code(request, country_code: str, province_code: str, language: str = 'default'):
    return await ipc.call(request, 'geoloc', 'GET', f'/countries/code/{country_code}/provinces/{province_code}')


async def get_city_data(request, id_municipality: uuid.UUID, language='default'):
    return await ipc.call(request, 'geoloc', 'GET', f'/municipalities/{id_municipality}?language={language}')


async def get_country_data(request, id_country: uuid.UUID, language='default'):
    return await ipc.call(request, 'geoloc', 'GET', f'/countries/{id_country}?language={language}')


async def get_municipality_by_country_code_and_province_code_and_search_term(request, country_code: str,
                                                                             province_code: str,
                                                                             municipality_term: str,
                                                                             language='default',
                                                                             search_policy='__istartswith'):
    return await ipc.call(request, 'geoloc', 'GET',
                          f'/countries/code/{country_code}/provinces/code/{province_code}/municipalities/?municipality_term={municipality_term}&language={language}&search_policy={search_policy}')

# {{ ipc_function }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
