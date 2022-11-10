import uuid
import json
import datetime
import base3.handlers
import tortoise.timezone
from .. import models
from base3.core import Base
from base3.decorators import route, api
from tortoise.transactions import in_transaction
from tortoise.query_utils import Prefetch
from tortoise.queryset import Q

from base3 import http

db_connection = 'conn_geoloc'


@route('/about')
class GeoLocAboutHandler(Base):

    @api(auth=False)
    async def get(self):
        """
        Get about information

        Responses:
            @geoloc/GET_200_documentation_get_about.json
        """

        return {'service': 'geoloc'}


@route('/options')
class GeoLocOptionsHandler(base3.handlers.BaseOptionsHandler):
    model_Option = models.Option
    db_connection = db_connection


@route('/countries/:id_country/import')
class HandlerImportDataForCountry(Base):
    """
    Parameters:
        id_country (path): Country ID
    """

    @api()
    async def patch(self, id_country: uuid.UUID, data: dict):
        """
        Import specific country

        Parameters:
            data (body): JSON file containing all information about a country

        RequestBody:
            @geoloc/PATCH_200_documentation_patch_import_specific_country.request_body.json

        Responses:
            @geoloc/PATCH_200_documentation_patch_import_specific_country.json
        """

        _db_regions = {}
        _db_provinces = {}

        res = {'regions': {'added': 0, 'updated': 0, 'skipped': 0},
               'provinces': {'added': 0, 'updated': 0, 'skipped': 0},
               'municipalities': {'added': 0, 'updated': 0, 'skipped': 0}, }

        # async with in_transaction('conn_geoloc'):
        if True:
            country = await models.Country.filter(id=id_country).get_or_none()

            for region in data['regions']:
                r = await models.Region.filter(id=region['id']).get_or_none()
                if not r:
                    r = models.Region(
                        id=region['id'],
                        created_by=self.id_user,
                        last_updated_by=self.id_user,
                        en_value=region['en_value'] if 'en_value' in region else region['local_value'],
                        created=tortoise.timezone.make_aware(datetime.datetime.now()),
                        last_updated=tortoise.timezone.make_aware(datetime.datetime.now()),
                        country=country,
                        local_value=region['local_value']
                    )
                    await r.save()
                    res['regions']['added'] += 1
                else:
                    res['regions']['skipped'] += 1

                if 'translations' in region:
                    for language in region['translations']:
                        db_trans = models.TranslationRegion(created_by=self.id_user, last_updated_by=self.id_user,
                                                            region=r, language=language,
                                                            value=region['translations'][language].lower(),
                                                            cs_value=region['translations'][language])
                        await db_trans.save()

                _db_regions[str(r.id)] = r

            for province in data['provinces']:
                p = await models.Province.filter(id=province['id']).get_or_none()
                if not p:
                    p = models.Province(
                        id=province['id'],
                        region=_db_regions[province['id_region']],
                        created_by=self.id_user,
                        last_updated_by=self.id_user,
                        created=tortoise.timezone.make_aware(datetime.datetime.now()),
                        last_updated=tortoise.timezone.make_aware(datetime.datetime.now()),
                        country=country,
                        code=province['code'].upper(),
                        local_value=province['local_value'],
                        en_value=province['en_value'] if 'en_value' in province else province['local_value']
                    )

                    await p.save()
                    res['provinces']['added'] += 1
                else:
                    res['provinces']['skipped'] += 1

                if 'translations' in province:
                    for language in province['translations']:
                        db_trans = models.TranslationProvince(created_by=self.id_user, last_updated_by=self.id_user,
                                                              province=p, language=language,
                                                              value=province['translations'][language].lower(),
                                                              cs_value=province['translations'][language])
                        await db_trans.save()

                _db_provinces[str(p.id)] = p

            for municipality in data['municipalities']:
                m = await models.Municipality.filter(id=municipality['id']).get_or_none()
                if not m:
                    m = models.Municipality(
                        id=municipality['id'],
                        province=_db_provinces[municipality['id_province']],
                        region_id=_db_provinces[municipality['id_province']].region_id,
                        created_by=self.id_user,
                        last_updated_by=self.id_user,
                        created=tortoise.timezone.make_aware(datetime.datetime.now()),
                        last_updated=tortoise.timezone.make_aware(datetime.datetime.now()),
                        country=country,
                        local_value=municipality['local_value'],
                        en_value=municipality['en_value'] if 'en_value' in municipality else municipality['local_value'],

                        zip=municipality['zip'] if 'zip' in municipality else None,
                        istat_code=municipality['istat_code'] if 'istat_code' in municipality else None,
                    )

                    await m.save()
                    res['municipalities']['added'] += 1

                    name_as_list_of_splited_words = municipality['local_value'].split(' ')
                    for w in name_as_list_of_splited_words:
                        mw = models.MunicipalitySearch(municipality=m,
                                                       created_by=self.id_user,
                                                       last_updated_by=self.id_user,
                                                       language='local',
                                                       value=w.lower().strip())
                        await mw.save()

                    if 'translations' in municipality:
                        for language in municipality['translations']:
                            db_trans = models.TranslationMunicipality(created_by=self.id_user, last_updated_by=self.id_user,
                                                                      municipality=m, language=language,
                                                                      value=municipality['translations'][language].lower(),
                                                                      cs_value=municipality['translations'][language])
                            await db_trans.save()

                            name_as_list_of_splited_words = municipality['translations'][language].split(' ')
                            for w in name_as_list_of_splited_words:
                                mw = models.MunicipalitySearch(municipality=m,
                                                               created_by=self.id_user,
                                                               last_updated_by=self.id_user,
                                                               language=language,
                                                               value=w.lower().strip())
                                await mw.save()



                else:
                    res['municipalities']['skipped'] += 1

        return res


@route('/countries/import')
class HandlerImportCountries(Base):

    @api()
    async def patch(self, data: json):
        """
        Import all countries

        Parameters:
            data (body): JSON file containing all information about a country

        RequestBody:
            @geoloc/PATCH_200_documentation_patch_import_all_countries.request_body.json

        Responses:
            @geoloc/PATCH_200_documentation_patch_import_all_countries.json
        """
        existing_by_code = {c.code: c for c in await models.Country.all()}

        added, updated, skipped = 0, 0, 0

        async with in_transaction(connection_name=db_connection):

            for country in data:

                try:

                    if not country['value_local'] and country['value_en']:
                        country['value_local'] = country['value_en']

                    # print('c', country['code'], country['value_en'], country['value_local'])
                    if country['code'] not in existing_by_code:
                        _id = country['id'] if 'id' in country else str(uuid.uuid4())
                        db_country = models.Country(id=_id, created_by=self.id_user, last_updated_by=self.id_user,
                                                    code=country['code'],
                                                    eu_country=country['eu_country'] if 'eu_country' in country and country['eu_country'] else False,
                                                    en_value=country['value_en'].lower() if 'value_en' in country else country['value_local'],
                                                    local_value=country['value_local'].lower())

                        await db_country.save()

                        if 'translations' in country:
                            for language in country['translations']:
                                db_trans = models.TranslationCountry(created_by=self.id_user,
                                                                     last_updated_by=self.id_user,
                                                                     country=db_country, language=language,
                                                                     value=country['translations'][language].lower(),
                                                                     cs_value=country['translations'][language])
                                await db_trans.save()

                        added += 1
                        existing_by_code[country['code']] = db_country

                except Exception as e:
                    raise

        return {'added': added, 'updated': updated, 'skipped': skipped}


@route('/countries')
class HandlerCountries(Base):

    @api()
    async def get(self, no_paginate=True, page=1, per_page=100, fields=None, order_by='en_value',
                  search=None, language: str = 'default'):
        """
        Get all countries

        Parameters:
            page (query): Current page
            per_page (query): Number of items per page
            search (query): General search
            language (query): Language of response
            fields (query): CSV string of fields (by default it is null, and this case will be used from personal user setting)
                enum: @Country.default_fields
            order_by (query): Order
                enum: @Country.allowed_ordering
            no_paginate (query): If true, pagination will not be provided. By default, it is True

        Responses:
            @geoloc/GET_200_documentation_get_all_countries.json
        """

        return await models.Country.base_get(
            no_paginate=no_paginate, page=page, per_page=per_page, fields=fields, order_by=order_by, search=search, force_limit=50,
            language=language,
            lowercased_search_field='en_value',
            prefetched=['translations'])


@route('/countries/:id_country')
class HandlerSingleCountries(Base):

    @api()
    async def get(self, id_country: uuid.UUID, language: str = 'default', fields=None, ):
        """
        Get single country
        TODO
        """

        return await models.Country.base_get(
            json_filters={"id": id_country},
            fields=fields,
            language=language,
            expected_one_item=True,
            prefetched=['translations'])


@route('/countries/code/:code')
class HandlerSingleCountryByCode(Base):

    @api()
    async def get(self, code: str, language: str = 'default', fields=None, ):
        """
        TODO
        """

        return await models.Country.base_get(
            json_filters={"code": code},
            fields=fields,
            language=language,
            expected_one_item=True,
            prefetched=['translations'])


@route('/countries/code/:country_code/provinces/:province_code')
class HandlerSingleProvinceInCountryByCode(Base):

    @api()
    async def get(self, country_code: str, province_code: str, language: str = 'default', fields=None, ):
        """
        TODO
        """

        raise http.HttpInternalServerError(id_message='NOT_IMPLEMENTED')

        country = await models.Country.base_get(
            json_filters={"code": country_code},
            fields=fields,
            language=language,
            expected_one_item=True,
            return_awaitable_orm_objects=True,
            prefetched=['translations'])

        # if not country:
        #     raise http.HttpErrorNotFound(id_message='COUNTRY_NOT_FOUND', message=country_code)
        #
        # province = await models.Province.base_get(
        #     json_filters={'country': country,
        #
        #                   }
        # )


@route('/countries/code/:country_code/provinces/code/:province_code/municipalities')
class HandlerSingleMunicipalityInProvinceByCodeInCountryByCode(Base):

    @api(auth=False)
    async def get(self, country_code: str, province_code: str,
                  municipality_term: str,
                  language: str = 'default',
                  search_policy: str = '__istartswith',
                  fields=None, ):

        if language == 'default':
            language = 'local'
        self.log.info(f'searching for country by country code {country_code.upper()}')
        country = await models.Country.base_get(
            json_filters={"code": country_code.upper()},
            fields=fields,
            language=language,
            expected_one_item=True,
            # return_awaitable_orm_objects=True,
            prefetched=['translations'])

        if not country:
            raise http.HttpErrorNotFound(id_message='COUNTRY_NOT_FOUND', message=country_code)

        try:
            province = await models.Province.base_get(
                json_filters={"code": province_code.upper()},
                fields=fields,
                language=language,
                expected_one_item=True,
                # return_awaitable_orm_objects=True,
                prefetched=['translations'],

                #               debug_return_query=True
            )

        #            return {"query": province}

        except BaseException as e:

            return {"debug": True, "exception": str(type(e))}

        if not province:
            raise http.HttpErrorNotFound(id_message='PROVINCE_NOT_FOUND', message=province_code)

        filters = {"country__code": country_code.upper(),
                   "province__code": province_code.upper(),
                   "search__language": language}

        if search_policy == "exact":
            search_policy = ""
        filters[f"search__value{search_policy}"] = municipality_term

        try:
            self.log.info(f'searching for municipality by municipality term {municipality_term}')
            municipality_data = await models.Municipality.base_get(
                json_filters=filters,
                fields=fields,
                language=language,
                no_paginate=True,
                distinct=True,
                expected_one_item=True if not search_policy else False,
                prefetched=['translations', 'province', 'country', 'search'])



        except Exception as e:
            raise http.HttpErrorNotFound(id_message='MUNICIPALITY_NOT_FOUND')

        if not municipality_data:
            raise http.HttpErrorNotFound(id_message='MUNICIPALITY_NOT_FOUND', message=municipality_term)

        province = province["translation"] if 'translation' in province and province["translation"] else province["en_value"]
        country = country["translation"] if 'translation' in country and country["translation"] else country["en_value"]

        def parse_municipality_data(m):
            id = m["id"]
            name = m["translation"] if m["translation"] else m["en_value"]

            zip = m["zip"]

            res = {
                "id": id,
                "municipality": name,
                "zip": zip,
                "province": province,
                "country": country
            }
            return res

        if not search_policy:
            result = parse_municipality_data(municipality_data)
        else:
            result = []
            for municipality in municipality_data:
                result.append(parse_municipality_data(municipality))
        return result


@route('/countries/:id_country/regions')
class HandlerRegionsInCountry(Base):
    """
    Parameters:
        id_country (path): Country ID
    """

    @api()
    async def get(self, id_country: uuid.UUID, no_paginate=True, page=1, per_page=100, fields=None,
                  order_by='local_value', search=None, language='default'):
        """
        Get all country regions

        Parameters:
            page (query): Current page
            per_page (query): Number of items per page
            search (query): General search
            language (query): Language of response
            fields (query): CSV string of fields (by default it is null, and this case will be used from personal user setting)
                enum: @Region.default_fields
            order_by (query): Order
                enum: @Region.allowed_ordering
            no_paginate (query): If true, pagination will not be provided. By default, it is True

        Responses:
            @geoloc/GET_200_documentation_get_all_country_regions.json
        """
        json_filters = {
            'country_id': id_country
        }

        return await models.Region.base_get(
            json_filters=json_filters, no_paginate=no_paginate, page=page, per_page=per_page, fields=fields,
            order_by=order_by, search=search, language=language, lowercased_search_field='local_value',
            prefetched=['translations'])


@route('/countries/:id_country/provinces')
class HandlerProvincesInCountry(Base):
    """
    Parameters:
        id_country (path): Country ID
    """

    @api()
    async def get(self, id_country: uuid.UUID, no_paginate=True, page=1, per_page=100, fields=None, force_limit=50,
                  order_by='local_value', search=None, language='default'):
        """
        Get all country provinces

        Parameters:
            page (query): Current page
            per_page (query): Number of items per page
            search (query): General search
            language (query): Language of response
            fields (query): CSV string of fields (by default it is null, and this case will be used from personal user setting)
                enum: @Province.default_fields
            order_by (query): Order
                enum: @Province.allowed_ordering
            no_paginate (query): If true, pagination will not be provided. By default, it is True

        Responses:
            @geoloc/GET_200_documentation_get_all_country_provinces.json
        """
        json_filters = {
            'country_id': id_country
        }

        return await models.Province.base_get(
            json_filters=json_filters, no_paginate=no_paginate, page=page, per_page=per_page, fields=fields,
            order_by=order_by, search=search, language=language, lowercased_search_field='local_value',
            prefetched=['translations'])

    @api()
    async def post(self, id_country: uuid.UUID, local_value: str, en_value: str = None, ):
        country = await models.Country.get(id=id_country).prefetch_related().get_or_none()
        if not country:
            raise http.HttpErrorNotFound

        province = models.Province(country=country, region=None, created_by=self.id_user, last_updated_by=self.id_user,
                                   local_value=local_value.lower(), en_value=en_value, cs_value=local_value)
        await province.save()
        return {'id': province.id}


@route('/regions/:id_region/provinces')
class HandlerProvincesInRegion(Base):
    """
    Parameters:
        id_region (path): Region ID
    """

    @api()
    async def get(self, id_region: uuid.UUID, no_paginate=True, page=1, per_page=100, fields=None,
                  order_by='local_value', search=None, language='default'):
        """
        Get all region provinces

        Parameters:
            page (query): Current page
            per_page (query): Number of items per page
            search (query): General search
            language (query): Language of response
            fields (query): CSV string of fields (by default it is null, and this case will be used from personal user setting)
                enum: @Province.default_fields
            order_by (query): Order
                enum: @Province.allowed_ordering
            no_paginate (query): If true, pagination will not be provided. By default, it is True

        Responses:
            @geoloc/GET_200_documentation_get_all_regions_provinces.json
        """
        json_filters = {
            'region_id': id_region
        }

        return await models.Province.base_get(
            json_filters=json_filters, no_paginate=no_paginate, page=page, per_page=per_page, fields=fields,
            order_by=order_by, search=search, language=language, lowercased_search_field='local_value',
            prefetched=['translations'])


@route('/countries/:id_country/municipalities')
class HandlerMunicipalitiesInCountry(Base):
    """
    Parameters:
        id_country (path): Country ID
    """

    @api()
    async def get(self, id_country: uuid.UUID, no_paginate=True, page=1, per_page=100, fields=None,
                  order_by='local_value', search=None, language='default'):
        """
        Get all provinces municipalities.

        Parameters:
            page (query): Current page
            per_page (query): Number of items per page
            search (query): General search
            language (query): Language of response
            fields (query): CSV string of fields (by default it is null, and this case will be used from personal user setting)
                enum: @Municipality.default_fields
            order_by (query): Order
                enum: @Municipality.allowed_ordering
            no_paginate (query): If true, pagination will not be provided. By default, it is True

        Responses:
            @geoloc/GET_200_documentation_get_municipalities_from_province.json
        """
        json_filters = {
            'country_id': id_country
        }

        return await models.Municipality.base_get(
            json_filters=json_filters, no_paginate=no_paginate, page=page, per_page=per_page, fields=fields,
            order_by=order_by, search=search, language=language, lowercased_search_field='local_value',
            prefetched=['translations'])


@route('/countries/code/:country_code/municipalities')
class HandlerMunicipalitiesSearchInCountryByCode(Base):

    @api(deprecated=True, deprecated_work_till='2022-09-30', deprecated_replace_with="")  # Arguments not used, not implemented yet
    async def get(self, country_code: str, search: str, fields=None,
                  order_by='local_value', language='default'):

        search = search.lower().strip()
        if language == 'default':
            language = 'en'
        municipalies = await models.Municipality.filter(country__code=country_code.upper(),
                                                        search__value__istartswith=search, ). \
            prefetch_related(Prefetch('translations',
                                      queryset=models.TranslationMunicipality.filter(language=language), ),
                             Prefetch('province__translations',
                                      queryset=models.TranslationProvince.filter(language=language), ),
                             Prefetch('country__translations',
                                      queryset=models.TranslationCountry.filter(
                                          language__in=[language, 'it']), )).limit(50).distinct().all()
        if not municipalies:
            return []

        result = []
        for municipality in municipalies:

            municipality_name = municipality.translations[0].value if municipality.translations else municipality.en_value
            municipality_zip = municipality.zip
            province = municipality.province.translations[0].value if municipality.province.translations else municipality.province.en_value
            country_name = None
            country_name_italian = None
            if municipality.country.translations:
                for translation in municipality.country.translations:
                    if translation.language == language:
                        country_name = translation.value
                    if translation.language == 'it':
                        country_name_italian = translation.value
            if not country_name:
                country_name = municipality.country.en_value

            m_res = {
                "id": municipality.id,
                "municipality": municipality_name,
                "zip": municipality_zip,
                "istat_code": municipality.istat_code,
                "province": province,
                "country": country_name,
                "country_italian": country_name_italian,
                "eu_country": municipality.country.eu_country,
                "mpc_with_zip": f"{municipality_name.lower().capitalize()}, {municipality_zip if municipality_zip else ''}, {province.capitalize()}, {country_name.capitalize()}",
                "mpc": f"{municipality_name.lower().capitalize()}, {province.capitalize()}, {country_name.capitalize()}"

            }
            result.append(m_res)

        return result


@route('/provinces/:id_province/municipalities')
class HandlerMunicipalitiesInProvince(Base):
    """
    Parameters:
        id_province (path): Province ID
    """

    @api()
    async def get(self, id_province: uuid.UUID, no_paginate=True, page=1, per_page=100, fields=None,
                  order_by='local_value', search=None, language='default'):
        """
        Get all provinces municipalities

        Parameters:
            page (query): Current page
            per_page (query): Number of items per page
            search (query): General search
            language (query): Language of response
            fields (query): CSV string of fields (by default it is null, and this case will be used from personal user setting)
                enum: @Municipality.default_fields
            order_by (query): Order
                enum: @Municipality.allowed_ordering
            no_paginate (query): If true, pagination will not be provided. By default, it is True

        Responses:
            @geoloc/GET_200_documentation_get_all_municipalities_from_province.json
        """
        json_filters = {
            'province_id': id_province
        }

        return await models.Municipality.base_get(
            json_filters=json_filters, no_paginate=no_paginate, page=page, per_page=per_page, fields=fields,
            order_by=order_by, search=search, language=language, lowercased_search_field='local_value',
            prefetched=['translations'])

    @api()
    async def post(self, id_province: uuid.UUID, local_value: str, en_value: str = None, zip: str = None):
        province = await models.Province.get(id=id_province).prefetch_related('country', 'region').get_or_none()
        if not province:
            raise http.HttpErrorNotFound

        city = models.Municipality(province=province, country=province.country, region=province.region, created_by=self.id_user, last_updated_by=self.id_user, zip=zip,
                                   local_value=local_value.lower(), en_value=en_value, cs_value=local_value)
        await city.save()
        return {'id': city.id}


@route('/lookup-test/:tbl')
class HandlerGeoLocLookupTest(Base):
    """
    Parameters:
        tbl (path): Table
    """

    @api()
    async def get(self, tbl):
        """
        Get all lookups from table.

        Responses:
            @geoloc/GET_200_documentation_get_lookup_tests.json
        """
        from tshared.lookups.cache import LookupCountries
        if tbl == 'countries':
            lookup_countries = await LookupCountries.create(self)
            res = len(lookup_countries['LookupCountries'].cache_by_id)

            return {'len': res}


@route('/municipalities-search')
class HandlerMunicipalitiesSearchInTheWorld(Base):

    @api()
    async def get(self, search: str, fields=None,
                  order_by='local_value', language='default'):
        # alway is no paginate
        # limit 50
        # don't use base-get
        # fields=None - odnose se na city

        search = search.lower().strip()
        if language == 'default':
            language = 'en'
        municipalies = await models.Municipality.filter(search__value__istartswith=search, ).prefetch_related(Prefetch('translations',
                                                                                                                       queryset=models.TranslationMunicipality.filter(language=language),
                                                                                                                       ),
                                                                                                              Prefetch('province__translations',
                                                                                                                       queryset=models.TranslationProvince.filter(language=language),
                                                                                                                       ),
                                                                                                              Prefetch('country__translations',
                                                                                                                       queryset=models.TranslationCountry.filter(language__in=[language, 'it']),
                                                                                                                       )).limit(50).distinct().all()
        if not municipalies:
            return []

        result = []
        for municipality in municipalies:

            municipality_name = municipality.translations[0].value if municipality.translations else municipality.en_value
            municipality_zip = municipality.zip
            province = municipality.province.translations[0].value if municipality.province.translations else municipality.province.en_value
            country_name = None
            country_name_italian = None
            if municipality.country.translations:
                for translation in municipality.country.translations:
                    if translation.language == language:
                        country_name = translation.value
                    if translation.language == 'it':
                        country_name_italian = translation.value
            if not country_name:
                country_name = municipality.country.en_value

            m_res = {
                "municipality": municipality_name,
                "zip": municipality_zip,
                "istat_code": municipality.istat_code,
                "province": province,
                "country": country_name,
                "country_italian": country_name_italian,
                "eu_country": municipality.country.eu_country

            }
            result.append(m_res)

        return result


@route('/municipalities')
class HandlerMunicipalitiesInTheWorld(Base):

    @api()
    async def get(self, search: str = None, fields=None,
                  order_by='local_value', language='default', country_codes: str = None):
        # alway is no paginate
        # limit 50
        # don't use base-get
        # fields=None - odnose se na city

        if search == '':
            return []
        filters = []
        if search:
            filters = [Q(search__value__istartswith=search.lower().strip())]
        if country_codes:
            filters.append(Q(country__code__in=[c.upper() for c in country_codes.split(",")]))

        if language == 'default':
            language = 'en'
        municipalies = await models.Municipality.filter(*filters).prefetch_related(Prefetch('translations',
                                                                                            queryset=models.TranslationMunicipality.filter(
                                                                                                language=language),
                                                                                            ),
                                                                                   Prefetch('province__translations',
                                                                                            queryset=models.TranslationProvince.filter(
                                                                                                language=language),
                                                                                            ),
                                                                                   Prefetch('country__translations',
                                                                                            queryset=models.TranslationCountry.filter(
                                                                                                language__in=[language, 'it']),
                                                                                            )).limit(50).distinct().all()
        if not municipalies:
            return []

        result = []
        for municipality in municipalies:

            municipality_name = municipality.translations[0].value if municipality.translations else municipality.en_value
            municipality_zip = municipality.zip
            province = None
            if municipality.province:
                province = municipality.province.translations[0].value.capitalize() if municipality.province.translations else municipality.province.en_value.capitalize()
            country_name = None
            country_name_italian = None
            if municipality.country.translations:
                for translation in municipality.country.translations:
                    if translation.language == language:
                        country_name = translation.value.capitalize()
                    if translation.language == 'it':
                        country_name_italian = translation.value.capitalize()
            if not country_name:
                country_name = municipality.country.en_value.capitalize()

            if province:
                mpc_with_zip = f"{municipality_name}, {municipality_zip}, {province}, {country_name}"
                mpc = f"{municipality_name}, {province}, {country_name}"
            else:
                mpc_with_zip = f"{municipality_name}, {municipality_zip}, {country_name}"
                mpc = f"{municipality_name}, {country_name}"

            m_res = {
                "municipality": municipality_name,
                "zip": municipality_zip,
                "istat_code": municipality.istat_code,
                "province": province,
                "country": country_name,
                "country_italian": country_name_italian,
                "eu_country": municipality.country.eu_country,
                "id": municipality.id,
                "mpc_with_zip": mpc_with_zip,
                "mpc": mpc
            }

            result.append(m_res)

        return result

    # TODO: Remove this method ?!

    # @api()
    # async def _get(self, no_paginate=True, page=1, per_page=100, fields=None,
    #                order_by='local_value', search=None, language='default'):
    #     """
    #     Get all provinces municipalities.
    #
    #     Parameters:
    #         page (query): Current page
    #         per_page (query): Number of items per page
    #         search (query): General search
    #         language (query): Language of response
    #         fields (query): CSV string of fields (by default it is null, and this case will be used from personal user setting)
    #             enum: @Municipality.default_fields
    #         order_by (query): Order
    #             enum: @Municipality.allowed_ordering
    #         no_paginate (query): If true, pagination will not be provided. By default, it is True
    #
    #     Responses:
    #         @geoloc/GET_200_documentation_get_municipalities_from_province.json
    #     """
    #     if language == 'default':
    #         language = 'en'
    #     json_filters = {}
    #     self.log.info("getting all countries with base get method")
    #     municipalities = await models.Municipality.base_get(
    #         json_filters=json_filters, no_paginate=no_paginate, page=page, per_page=per_page, fields=fields, force_limit=50,
    #         order_by=order_by, search=search, language=language, lowercased_search_field='local_value', return_awaitable_orm_objects=True,
    #         prefetched=['translations', 'province__translations', 'country__translations'])
    #     self.log.info("successfully got all countries orm objects with base get method")
    #
    #     result = []
    #     if not municipalities:
    #         return []
    #
    #     if no_paginate:
    #         data = await municipalities
    #     else:
    #         data = await municipalities["items"]
    #
    #     self.log.info("parsing data for each municipality")
    #     for municipality in data:
    #         m_data = {}
    #         m_data["id"] = municipality.id
    #         m_data["zip"] = municipality.zip
    #
    #         m_data["municipality"] = None
    #         m_data["province"] = None
    #         m_data["country"] = None
    #
    #         self.log.info(f"parsing municipality data for municipality {municipality.id} {municipality.en_value}")
    #
    #         for p in municipality.translations:
    #             if p.language == language:
    #                 m_data["municipality"] = p.value
    #         if not m_data["municipality"]:
    #             m_data["municipality"] = municipality.en_value
    #
    #         self.log.info(f"parsing province data for municipality {municipality.id} {municipality.en_value}")
    #         if municipality.province and municipality.province.translations:
    #             for p in municipality.province.translations:
    #                 if p.language == language:
    #                     m_data["province"] = p.value
    #             if not m_data["province"]:
    #                 m_data["province"] = municipality.province.en_value
    #
    #         self.log.info(f"parsing country data for municipality {municipality.id} {municipality.en_value}")
    #         if municipality.country and municipality.country.translations:
    #             for p in municipality.country.translations:
    #                 if p.language == language:
    #                     m_data["country"] = p.value
    #             if not m_data["country"]:
    #                 m_data["country"] = municipality.country.en_value
    #         if m_data["province"]:
    #             m_data["mpc_with_zip"] = f'{m_data["municipality"].lower().capitalize()}, {m_data["zip"]}, {m_data["province"].capitalize()}, {m_data["country"]}'
    #             m_data["mpc"] = f'{m_data["municipality"].lower().capitalize()}, {m_data["province"].capitalize() if m_data["province"] else ""}, {m_data["country"]}'
    #
    #         else:
    #             m_data["mpc_with_zip"] = f'{m_data["municipality"].lower().capitalize()}, {m_data["zip"]}, {m_data["country"]}'
    #             m_data["mpc"] = f'{m_data["municipality"].lower().capitalize()}, {m_data["country"]}'
    #
    #         result.append(m_data)
    #     return result

    @api()
    async def post(self,
                   country_id: uuid.UUID,
                   city_name: str,
                   city_zip: str,
                   province_id_or_name: str = None,
                   language: str = 'default'
                   ):

        # async with in_transaction(connection_name=db_connection):
        if True:
            self.log.info(f'querying for a country, country id {country_id}')
            country = await models.Country.filter(id=country_id).get_or_none()
            if not country:
                self.log.critical(f'country not found, country id {country_id}')
                raise http.HttpErrorNotFound(id_message='COUNTRY_NOT_FOUND')

            if country.code == "IT":
                raise http.HttpForbiden(id_message="CREATING_CITIES_FOR_ITALY_IS_FORBIDDEN")

            province = None
            if province_id_or_name:
                province_id = None
                try:
                    province_id = uuid.UUID(province_id_or_name)
                except:
                    pass

                if not province_id:
                    self.log.info(f'creating province input for db')
                    if country.en_value.lower() == 'italy':
                        raise http.HttpNotAcceptable(id_message='PROVINCE_FOR_ITALY_CANNOT_BE_CREATED')

                    province = models.Province(country=country,
                                               created_by=self.id_user,
                                               last_updated_by=self.id_user,
                                               local_value=province_id_or_name.lower(),
                                               cs_value=province_id_or_name,
                                               en_value=province_id_or_name.lower())
                    try:
                        await province.save()
                    except Exception as e:
                        self.log.critical(f'error creating province {province_id_or_name}, error: {e}')
                        raise http.HttpNotAcceptable(id_message='ERROR_CREATING_PROVINCE', message=f'error creating province, error {e}')

                else:
                    try:
                        province = await models.Province.filter(country=country, id=province_id).get_or_none()
                    except Exception as e:
                        self.log.critical(f' province not found, province id {province_id}')
                        raise http.HttpErrorNotFound(id_message='PROVINCE_IN_COUNTRY_NOT_FOUND')

            city = models.Municipality(
                created_by=self.id_user,
                last_updated_by=self.id_user,
                local_value=city_name,
                en_value=city_name,
                zip=city_zip,
                country=country,
                province=province,

            )

            try:

                await city.save()

            except Exception as e:
                self.log.critical(f'error creating city {city_name}, error: {e}')
                raise http.HttpNotAcceptable(id_message='ERROR_CREATING_CITY', message=f'name: {city_name}, error {e}')
            self.log.info("city successfully created")
            name_as_list_of_splited_words = city.en_value.split(' ')
            for w in name_as_list_of_splited_words:
                self.log.info(f"inserting search for city, term {w}")

                mw = models.MunicipalitySearch(municipality=city,
                                               created_by=self.id_user,
                                               last_updated_by=self.id_user,
                                               language=language,
                                               value=w.lower().strip())
                await mw.save()
                self.log.info(f" successfully saved search term {w} in the database, search object id {mw.id}")

        if province:
            mpc_with_zip = f"{city.en_value}, {city.zip}, {province.en_value}, {country.en_value.capitalize()}"
            mpc = f"{city.en_value}, {province.en_value}, {country.en_value.capitalize()}"
        else:
            mpc_with_zip = f"{city.en_value}, {city.zip}, {country.en_value.capitalize()}"
            mpc = f"{city.en_value}, {country.en_value.capitalize()}"

        return {
            "id": city.id,
            "zip": city.zip,
            "municipality": city.en_value,
            "province": province.en_value if province else None,
            "country": country.en_value,
            "mpc_with_zip": mpc_with_zip,
            "mpc": mpc
        }


@route('/provinces')
class HandlerProvincesInTheWorld(Base):

    @api()
    async def get(self, no_paginate=True, page=1, per_page=100, fields=None,
                  order_by='local_value', search=None, language='default'):
        """
        Get all provinces.

        Parameters:
            page (query): Current page
            per_page (query): Number of items per page
            search (query): General search
            language (query): Language of response
            fields (query): CSV string of fields (by default it is null, and this case will be used from personal user setting)
                enum: @Municipality.default_fields
            order_by (query): Order
                enum: @Municipality.allowed_ordering
            no_paginate (query): If true, pagination will not be provided. By default, it is True

        Responses:
            @geoloc/
        """
        json_filters = {}

        return await models.Province.base_get(
            json_filters=json_filters, no_paginate=no_paginate, page=page, per_page=per_page, fields=fields,
            order_by=order_by, search=search, language=language, lowercased_search_field='local_value',
            prefetched=['translations'])


@route('/municipalities/:id_municipality')
class MunicipalitiesHandler(Base):

    @api()
    async def get(self, id_municipality: uuid.UUID, no_paginate=True, page=1, per_page=100, fields=None,
                  order_by='local_value', search=None, language='default'):
        if language == 'default':
            language = 'en'
        municipality = await models.Municipality.filter(id=id_municipality, ).prefetch_related(Prefetch('translations',
                                                                                                        queryset=models.TranslationMunicipality.filter(language=language),
                                                                                                        ),
                                                                                               Prefetch('province__translations', queryset=models.TranslationProvince.filter(language=language),
                                                                                                        ),
                                                                                               Prefetch('country__translations',
                                                                                                        queryset=models.TranslationCountry.filter(language__in=[language, 'it']),
                                                                                                        )).get_or_none()
        if not municipality:
            raise http.HttpErrorNotFound(id_message='MUNICIPALITY_NOT_FOUND')

        municipality_name = municipality.translations[0].value if municipality.translations else municipality.en_value
        municipality_zip = municipality.zip
        if municipality.province:
            province = municipality.province.translations[0].value if municipality.province and municipality.province.translations else municipality.province.en_value
        else:
            province = None
        country_name = None
        country_name_italian = None
        if municipality.country.translations:
            for translation in municipality.country.translations:
                if translation.language == language:
                    country_name = translation.value
                if translation.language == 'it':
                    country_name_italian = translation.value
        if not country_name:
            country_name = municipality.country.en_value

        if province:
            mpc_with_zip = f"{municipality_name}, {municipality_zip}, {province}, {country_name}"
            mpc = f"{municipality_name}, {province}, {country_name}"
        else:
            mpc_with_zip = f"{municipality_name}, {municipality_zip}, {country_name}"
            mpc = f"{municipality_name}, {country_name}"

        return {
            "municipality": municipality_name,
            "zip": municipality_zip,
            "istat_code": municipality.istat_code,
            "province_id": str(municipality.province.id) if province else None,
            "country_id": str(municipality.country.id),
            "province": province,
            "country": country_name,
            "country_italian": country_name_italian,
            "eu_country": municipality.country.eu_country,
            "mpc_with_zip": mpc_with_zip,
            "mpc": mpc

        }