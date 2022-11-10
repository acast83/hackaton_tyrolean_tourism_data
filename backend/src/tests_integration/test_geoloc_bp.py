import os
import json
from base3 import http
from tshared.test import SetupBaseAuthorizedTest

# import dotenv
# dotenv.load_dotenv()

current_file_folder = os.path.dirname(os.path.realpath(__file__))


class TestTenantsAndBusinessPartners(SetupBaseAuthorizedTest):

    def setUp(self):
        self.api_modules = [
            'svc_tenants.tenants.api',
        ]
        super().setUp()

    def test_about(self):
        self.api(self.token, 'GET', '/tenants/about', expected_code=http.status.OK,
                 expected_result_subset={"service": "tenants"})


class TestTenantsGeoLocAndBusinessPartners(SetupBaseAuthorizedTest):

    def setUp(self):
        self.api_modules = [
            'svc_tenants.tenants.api',
            'svc_geoloc.geoloc.api'
        ]
        super().setUp()

    def test_about(self):
        self.api(self.token, 'GET', '/tenants/about', expected_code=http.status.OK,
                 expected_result_subset={"service": "tenants"})
        self.api(self.token, 'GET', '/geoloc/about', expected_code=http.status.OK,
                 expected_result_subset={"service": "geoloc"})

    def test_aca(self):
        with open(current_file_folder + '/../svc_geoloc/init/my_countries.json') as f:
            countries = json.load(f)

        self.api(self.token, 'PATCH', '/geoloc/countries/import', {'data': countries}, expected_result={
            "added": 4,
            "updated": 0,
            "skipped": 0
        })

        self.api(self.token, 'GET', '/geoloc/countries?fields=id,en_value&search=italy&no_paginate=true',
                 expected_length=1)

        id_italy = self.last_result[0]['id']

        with open(current_file_folder + '/../svc_geoloc/init/my_italy.json') as f:
            italy = json.load(f)

        self.api(self.token, 'PATCH', f'/geoloc/countries/{id_italy}/import', body={'data': italy})

        self.api(self.token, 'GET', f'/geoloc/countries/{id_italy}/provinces?search=trento')

        id_trento_province = self.last_result[0]['id']

        self.api(self.token, 'GET', f'/geoloc/provinces/{id_trento_province}/municipalities', expected_length=2)

        self.api(self.token, 'POST', f'/geoloc/provinces/{id_trento_province}/municipalities', body={
            'local_value': 'Dro',
        })
        self.show_last_result()

        self.api(self.token, 'GET', f'/geoloc/provinces/{id_trento_province}/municipalities', expected_length=3)
        self.show_last_result()

        self.api(self.token, 'GET', f'/geoloc/countries/{id_italy}/provinces', expected_length=3)
        self.show_last_result()

        self.api(self.token, 'POST', f'/geoloc/countries/{id_italy}/provinces', body={'local_value': 'Lazio'})
        id_lazio = self.last_result['id']

        self.api(self.token, 'GET', f'/geoloc/countries/{id_italy}/provinces', expected_length=4)
        self.show_last_result()

        self.api(self.token, 'POST', f'/geoloc/provinces/{id_lazio}/municipalities', body={
            'local_value': 'Roma',
        })

    def test_get_municipalities_all(self):
        with open(current_file_folder + '/../svc_geoloc/init/my_countries.json') as f:
            countries = json.load(f)

        self.api(self.token, 'PATCH', '/geoloc/countries/import', {'data': countries}, expected_result={
            "added": 4,
            "updated": 0,
            "skipped": 0
        })

        self.api(self.token, 'GET', '/geoloc/countries?fields=id,en_value&search=italy&no_paginate=true',
                 expected_length=1)

        id_italy = self.last_result[0]['id']

        with open(current_file_folder + '/../svc_geoloc/init/my_italy.json') as f:
            italy = json.load(f)

        self.api(self.token, 'PATCH', f'/geoloc/countries/{id_italy}/import', body={'data': italy})

        self.api(self.token, 'GET', '/geoloc/municipalities')
        self.assertEqual(len(self.last_result), 8)
        self.api(self.token, 'GET', '/geoloc/municipalities?search=')
        self.assertEqual(len(self.last_result), 0)
        self.api(self.token, 'GET', '/geoloc/municipalities?search=mer')
        self.assertEqual(len(self.last_result), 2)

    def test_get_municipalities_from_specific_country(self):
        with open(current_file_folder + '/../svc_geoloc/init/my_countries.json') as f:
            countries = json.load(f)

        self.api(self.token, 'PATCH', '/geoloc/countries/import', {'data': countries}, expected_result={
            "added": 4,
            "updated": 0,
            "skipped": 0
        })

        self.api(self.token, 'GET', '/geoloc/countries?fields=id,en_value&search=italy&no_paginate=true',
                 expected_length=1)

        id_italy = self.last_result[0]['id']

        with open(current_file_folder + '/../svc_geoloc/init/my_italy.json') as f:
            italy = json.load(f)

        self.api(self.token, 'PATCH', f'/geoloc/countries/{id_italy}/import', body={'data': italy})
        self.api(self.token, 'GET', f'/geoloc/countries/{id_italy}/municipalities')
        self.assertEqual(len(self.last_result), 8)
        self.api(self.token, 'GET', f'/geoloc/countries/{id_italy}/municipalities?search=mer')
        self.assertEqual(len(self.last_result), 2)

    def _test_import_whole_italy(self):  # TODO Test takes too long?
        with open(current_file_folder + '/../svc_geoloc/init/my_countries.json') as f:
            countries = json.load(f)

        self.api(self.token, 'PATCH', '/geoloc/countries/import', {'data': countries}, expected_result={
            "added": 4,
            "updated": 0,
            "skipped": 0
        })

        self.api(self.token, 'GET', '/geoloc/countries?fields=id,en_value&search=italy&no_paginate=true',
                 expected_length=1)

        id_italy = self.last_result[0]['id']

        with open(current_file_folder + '/../svc_geoloc/init/italy.json') as f:
            italy = json.load(f)

        self.api(self.token, 'PATCH', f'/geoloc/countries/{id_italy}/import', body={'data': italy})

    def test_get_specific_country_data(self):  #
        with open(current_file_folder + '/../svc_geoloc/init/my_countries.json') as f:
            countries = json.load(f)

        self.api(self.token, 'PATCH', '/geoloc/countries/import', {'data': countries}, expected_result={
            "added": 4,
            "updated": 0,
            "skipped": 0
        })

        self.api(self.token, 'GET', '/geoloc/countries?no_paginate=true',
                 expected_length=4)

        id_italy = self.last_result[1]['id']

        self.api(self.token, 'GET', f'/geoloc/countries/{id_italy}?language=de')
        self.show_last_result()

    def test_get_specific_municipality_data(self):
        with open(current_file_folder + '/../svc_geoloc/init/my_countries.json') as f:
            countries = json.load(f)

        self.api(self.token, 'PATCH', '/geoloc/countries/import', {'data': countries}, expected_result={
            "added": 4,
            "updated": 0,
            "skipped": 0
        })

        self.api(self.token, 'GET', '/geoloc/countries?no_paginate=true',
                 expected_length=4)

        id_austria = self.last_result[0]['id']
        id_italy = self.last_result[1]['id']

        with open(current_file_folder + '/../svc_geoloc/init/my_italy.json') as f:
            italy = json.load(f)

        self.api(self.token, 'PATCH', f'/geoloc/countries/{id_italy}/import', body={'data': italy})

        self.api(self.token, 'GET', f'/geoloc/countries/{id_italy}/municipalities?search=mer')
        # self.show_last_result()
        # return

        merano_id = self.last_result[0]["id"]
        self.api(self.token, 'GET', f'/geoloc/municipalities/{merano_id}?language=de')
        self.show_last_result()

    def test_get_all_provinces(self):
        with open(current_file_folder + '/../svc_geoloc/init/my_countries.json') as f:
            countries = json.load(f)

        self.api(self.token, 'PATCH', '/geoloc/countries/import', {'data': countries}, expected_result={
            "added": 4,
            "updated": 0,
            "skipped": 0
        })

        self.api(self.token, 'GET', '/geoloc/countries?fields=id,en_value&search=italy&no_paginate=true',
                 expected_length=1)

        id_italy = self.last_result[0]['id']

        with open(current_file_folder + '/../svc_geoloc/init/my_italy.json') as f:
            italy = json.load(f)

        self.api(self.token, 'PATCH', f'/geoloc/countries/{id_italy}/import', body={'data': italy})
        self.api(self.token, 'GET', '/geoloc/provinces?search=')

    def test_create_new_city(self):
        with open(current_file_folder + '/../svc_geoloc/init/my_countries.json') as f:
            countries = json.load(f)

        self.api(self.token, 'PATCH', '/geoloc/countries/import', {'data': countries}, expected_result={
            "added": 4,
            "updated": 0,
            "skipped": 0
        })

        self.api(self.token, 'GET', '/geoloc/countries?fields=id,en_value&no_paginate=true',
                 expected_length=4)

        id_italy = self.last_result[1]['id']
        id_serbia = self.last_result[2]['id']

        with open(current_file_folder + '/../svc_geoloc/init/my_italy.json') as f:
            italy = json.load(f)

        self.api(self.token, 'PATCH', f'/geoloc/countries/{id_italy}/import', body={'data': italy})

        # self.api(self.token, 'POST', '/geoloc/municipalities', body={"country_id": id_serbia, "province_id_or_name": "timocka krajina",
        #                                                              "city_name": "negotin", "city_zip": "19300"})

        self.api(self.token, 'POST', '/geoloc/municipalities',
                 body={"country_id": id_serbia, "city_name": "DEspotovac", "city_zip": "35213"})

        self.api(self.token, 'GET', f'/geoloc/countries/{id_italy}/provinces')
        bolzano_province_id = self.last_result[0]["id"]

        self.api(self.token, 'POST', '/geoloc/municipalities',
                 body={"country_id": id_italy, "province_id_or_name": str(bolzano_province_id),
                       "city_name": "new city", "city_zip": "12345"}, expected_code=403)
        self.api(self.token, 'GET', '/geoloc/municipalities', expected_code=200)
        self.show_last_result()

    def test_get_provinces_for_specific_country_test_search(self):
        with open(current_file_folder + '/../svc_geoloc/init/my_countries.json') as f:
            countries = json.load(f)

        self.api(self.token, 'PATCH', '/geoloc/countries/import', {'data': countries}, expected_result={
            "added": 4,
            "updated": 0,
            "skipped": 0
        })

        self.api(self.token, 'GET', '/geoloc/countries?no_paginate=true',
                 expected_length=4)

        id_italy = self.last_result[1]['id']

        with open(current_file_folder + '/../svc_geoloc/init/my_italy.json') as f:
            italy = json.load(f)

        self.api(self.token, 'PATCH', f'/geoloc/countries/{id_italy}/import', body={'data': italy})

        self.api(self.token, 'GET', f'/geoloc/countries/{id_italy}/provinces?search=bol', expected_code=200)
        self.assertEqual(self.last_result[0]["en_value"], "Bolzano")

    def test_get_municipality_by_country_code_province_code_and_municipality_term(self):  # popadali
        with open(current_file_folder + '/../svc_geoloc/init/my_countries.json') as f:
            countries = json.load(f)

        self.api(self.token, 'PATCH', '/geoloc/countries/import', {'data': countries}, expected_result={
            "added": 4,
            "updated": 0,
            "skipped": 0
        })

        self.api(self.token, 'GET', '/geoloc/countries?no_paginate=true',
                 expected_length=4)

        id_italy = self.last_result[1]['id']

        with open(current_file_folder + '/../svc_geoloc/init/my_italy.json') as f:
            italy = json.load(f)
        italy_code = "it"
        self.api(self.token, 'PATCH', f'/geoloc/countries/{id_italy}/import', body={'data': italy})

        self.api(self.token, 'GET',
                 f'/geoloc/countries/code/it/provinces/code/bz/municipalities?search_policy=exact&language=it&municipality_term=merano',
                 expected_code=200,
                 expected_result={
                     "id": "5a5fc63d-5c12-4892-b72b-b349e78409bd",
                     "municipality": "Merano",
                     "zip": "39012",
                     "province": "Bolzano",
                     "country": "Italia"
                 }, ignore_uuid_values=True)

        self.api(self.token, 'GET',
                 f'/geoloc/countries/code/it/provinces/code/bz/municipalities?municipality_term=mera')
        self.assertEqual(len(self.last_result), 2)

    def test_get_municipality_by_search_term(self):
        with open(current_file_folder + '/../svc_geoloc/init/my_countries.json') as f:
            countries = json.load(f)

        self.api(self.token, 'PATCH', '/geoloc/countries/import', {'data': countries}, expected_result={
            "added": 4,
            "updated": 0,
            "skipped": 0
        })

        self.api(self.token, 'GET', '/geoloc/countries?no_paginate=true',
                 expected_length=4)

        id_italy = self.last_result[1]['id']

        with open(current_file_folder + '/../svc_geoloc/init/my_italy.json') as f:
            italy = json.load(f)
        italy_code = "it"
        self.api(self.token, 'PATCH', f'/geoloc/countries/{id_italy}/import', body={'data': italy})

        self.api(self.token, 'GET', f'/geoloc/municipalities-search?search=mera')
        self.show_last_result()

        self.api(self.token, 'PATCH', f'/geoloc/countries/{id_italy}/import', body={'data': italy})
        self.api(self.token, 'GET', '/geoloc/municipalities?search=mer')
        self.assertEqual(len(self.last_result), 2)
        self.api(self.token, 'GET', '/geoloc/municipalities?country_codes=rs&search=mer')
        self.assertEqual(len(self.last_result), 0)
        self.api(self.token, 'GET', '/geoloc/municipalities?country_codes=rs,it&search=mer')
        self.assertEqual(len(self.last_result), 2)
        self.api(self.token, 'GET', '/geoloc/municipalities?country_codes=it&search=mer')
        self.assertEqual(len(self.last_result), 2)

        self.api(self.token, 'GET', '/geoloc/municipalities?country_codes=it&search=')

    def test_get_municipality_by_search_term_for_country_by_country_code(self):
        with open(current_file_folder + '/../svc_geoloc/init/my_countries.json') as f:
            countries = json.load(f)

        self.api(self.token, 'PATCH', '/geoloc/countries/import', {'data': countries}, expected_result={
            "added": 4,
            "updated": 0,
            "skipped": 0
        })

        self.api(self.token, 'GET', '/geoloc/countries?no_paginate=true',
                 expected_length=4)

        id_italy = self.last_result[1]['id']

        with open(current_file_folder + '/../svc_geoloc/init/my_italy.json') as f:
            italy = json.load(f)
        italy_code = "it"
        self.api(self.token, 'PATCH', f'/geoloc/countries/{id_italy}/import', body={'data': italy})

        self.api(self.token, 'GET', f'/geoloc/countries/code/it/municipalities?search=mera')
        self.assertEqual(len(self.last_result), 2)


class BaseTestWithAllCountries(SetupBaseAuthorizedTest):
    def setUp(self):
        self.api_modules = [
            'svc_tenants.tenants.api',
            'svc_geoloc.geoloc.api'
        ]
        super().setUp()

    def test(self):
        with open(current_file_folder + '/../svc_geoloc/init/countries.json') as f:
            countries = json.load(f)
        self.api(self.token, 'PATCH', '/geoloc/countries/import', {'data': countries}, expected_result={
            "added": 249,
            "updated": 0,
            "skipped": 0
        })

        self.api(self.token, 'GET', '/geoloc/countries?search=italy&fields=id,en_value,code')
        self.show_last_result()


class BaseTestOnAFewItalianCities(SetupBaseAuthorizedTest):

    def setUp(self):
        self.api_modules = [
            'svc_tenants.tenants.api',
            'svc_geoloc.geoloc.api'
        ]
        super().setUp()
        self.import_a_few_countries()

        self.api(self.token, 'GET', '/geoloc/countries?fields=id,en_value&search=italy&no_paginate=true',
                 expected_length=1)
        self.id_italy = self.last_result[0]['id']

        self.import_my_italy()

    def test_import_all_countries(self):
        with open(current_file_folder + '/../svc_geoloc/init/countries.json') as f:
            countries = json.load(f)

        self.api(self.token, 'PATCH', '/geoloc/countries/import', {'data': countries}, expected_result={
            "added": 245,
            "updated": 0,
            "skipped": 0
        })

    def import_a_few_countries(self):
        with open(current_file_folder + '/../svc_geoloc/init/my_countries.json') as f:
            countries = json.load(f)

        self.api(self.token, 'PATCH', '/geoloc/countries/import', {'data': countries}, expected_result={
            "added": 4,
            "updated": 0,
            "skipped": 0
        })

    def import_my_italy(self):
        with open(current_file_folder + '/../svc_geoloc/init/my_italy.json') as f:
            italy = json.load(f)

        self.api(self.token, 'PATCH', f'/geoloc/countries/{self.id_italy}/import', body={'data': italy},
                 expected_result={'municipalities': {'added': 8, 'skipped': 0, 'updated': 0},
                                  'provinces': {'added': 3, 'skipped': 0, 'updated': 0},
                                  'regions': {'added': 2, 'skipped': 0, 'updated': 0}})


class TestDocumentationGeoloc(BaseTestOnAFewItalianCities):

    def setUp(self):
        self.api_modules = [
            'svc_tenants.tenants.api',
            'svc_bp.bp.api',
            'svc_geoloc.geoloc.api'
        ]
        super().setUp()


class TestOnAFewItalianCities(BaseTestOnAFewItalianCities):

    def test_fetch_all_countries(self):
        self.api(self.token, 'GET', '/geoloc/countries?fields=en_value', expected_result=[
            {"en_value": "Austria"},
            {"en_value": "Italy"},
            {"en_value": "Serbia"},
            {"en_value": "Switzerland"}])

    def test_lookup_countries(self):
        self.api(self.token, 'GET', '/geoloc/lookup-test/countries')
        self.show_last_result()

    def test_fetch_all_countries_translated(self):
        self.api(self.token, 'GET', '/geoloc/countries?fields=translation&language=de',
                 expected_result=[{"translation": "Österreich"},
                                  {"translation": "Italien"},
                                  {"translation": "Serbien"},
                                  {"translation": "Schweiz"}])

        self.api(self.token, 'GET', '/geoloc/countries?fields=translation&language=sr',
                 expected_result=[{"translation": "Austrija"},
                                  {"translation": "Italija"},
                                  {"translation": "Srbija"},
                                  {"translation": "Švajcarska"}])

        self.api(self.token, 'GET', '/geoloc/countries?fields=translation&language=it',
                 expected_result=[{"translation": "Austria"},
                                  {"translation": "Italia"},
                                  {"translation": "Serbia"},
                                  {"translation": "Svizzera"}])

        self.api(self.token, 'GET', '/geoloc/countries?fields=translation&language=en',
                 expected_result=[{"translation": "Austria"},
                                  {"translation": "Italy"},
                                  {"translation": "Serbia"},
                                  {"translation": "Switzerland"}])

    def test_fetch_all_italian_regions(self):
        self.api(self.token, 'GET', f'/geoloc/countries/{self.id_italy}/regions?fields=local_value',
                 expected_result=[{"local_value": "Lombardia"},
                                  {"local_value": "Trentino-alto adige"}])

    def test_fetch_all_italian_regions_translated(self):
        self.api(self.token, 'GET', f'/geoloc/countries/{self.id_italy}/regions?fields=translation&language=de',
                 expected_result=[{"translation": "Lombardei"},
                                  {"translation": "Trentino-südtirol"}])
        self.api(self.token, 'GET', f'/geoloc/countries/{self.id_italy}/regions?fields=translation&language=it',
                 expected_result=[{"translation": "Lombardia"},
                                  {"translation": "Trentino-alto adige"}])
        self.api(self.token, 'GET', f'/geoloc/countries/{self.id_italy}/regions?fields=translation&language=sr',
                 expected_result=[{"translation": "Lombardija"},
                                  {"translation": "Trentino-južni tirol"}])
        self.api(self.token, 'GET', f'/geoloc/countries/{self.id_italy}/regions?fields=translation&language=en',
                 expected_result=[{"translation": "Lombardy"},
                                  {"translation": "Trentino-south tyrol"}])

    def test_fetch_all_italian_provinces(self):
        self.api(self.token, 'GET', f'/geoloc/countries/{self.id_italy}/provinces?fields=local_value',
                 expected_result=[{"local_value": "Bolzano"},
                                  {"local_value": "Milano"},
                                  {"local_value": "Trento"}])

    def test_fetch_all_italian_provinces_translated(self):
        self.api(self.token, 'GET', f'/geoloc/countries/{self.id_italy}/provinces?fields=translation&language=de',
                 expected_result=[{"translation": "Bozen - südtirol"},
                                  {"translation": "Mailan"},
                                  {"translation": "Trient"}])
        self.api(self.token, 'GET', f'/geoloc/countries/{self.id_italy}/provinces?fields=translation&language=it',
                 expected_result=[{"translation": "Bolzano"},
                                  {"translation": "Milano"},
                                  {"translation": "Trento"}])
        self.api(self.token, 'GET', f'/geoloc/countries/{self.id_italy}/provinces?fields=translation&language=en',
                 expected_result=[{"translation": "South tyrol"},
                                  {"translation": "Milan"},
                                  {"translation": "Trento"}])

    def test_fetch_all_provinces_in_chosen_region(self):
        self.api(self.token, 'GET', f'/geoloc/countries/{self.id_italy}/regions?fields=id,local_value&search=Trentino',
                 expected_result=[{"id": "9ee6efea-38bc-4858-9513-499f6088a951",
                                   "local_value": "Trentino-alto adige"}], ignore_uuid_values=True)

        id_trentino = self.last_result[0]['id']

        self.api(self.token, 'GET', f'/geoloc/regions/{id_trentino}/provinces?fields=local_value',
                 [{"local_value": "Bolzano"},
                  {"local_value": "Trento"}])

    def test_fetch_all_municipalities_in_province(self):
        self.api(self.token, 'GET', f'/geoloc/countries/{self.id_italy}/provinces?fields=id,local_value&search=bolzano',
                 expected_result=[{"id": "82b6344e-72a4-4a34-ad36-794487a84792", "local_value": "Bolzano"}],
                 ignore_uuid_values=True)
        id_bolzano = self.last_result[0]['id']

        self.api(self.token, 'GET', f'/geoloc/provinces/{id_bolzano}/municipalities?fields=local_value',
                 expected_result=[{'local_value': 'Bolzano'},
                                  {'local_value': 'Lana'},
                                  {'local_value': 'Merano'},
                                  {'local_value': 'Merano2'},
                                  {'local_value': 'Scena'}])

        self.api(self.token, 'GET', f'/geoloc/provinces/{id_bolzano}/municipalities?fields=local_value&language=de')

    def test_fetch_all_municipalities_in_province_translated(self):
        self.api(self.token, 'GET', f'/geoloc/countries/{self.id_italy}/provinces?fields=id,local_value&search=bolzano',
                 expected_result=[{"id": "82b6344e-72a4-4a34-ad36-794487a84792", "local_value": "Bolzano"}],
                 ignore_uuid_values=True)
        id_bolzano = self.last_result[0]['id']

        self.api(self.token, 'GET', f'/geoloc/provinces/{id_bolzano}/municipalities?fields=translation&language=it',
                 expected_result=[{'translation': 'Bolzano'},
                                  {'translation': 'Lana'},
                                  {'translation': 'Merano'},
                                  {'translation': None},
                                  {'translation': 'Scena'}])

        self.api(self.token, 'GET', f'/geoloc/provinces/{id_bolzano}/municipalities?fields=translation&language=de',
                 expected_result=[{'translation': 'Bozen'},
                                  {'translation': 'Lana'},
                                  {'translation': 'Meran'},
                                  {'translation': None},
                                  {'translation': 'Schenna'}])

    def test_fetch_all_countries_on_a_few_languages_languages(self):
        self.api(self.token, 'GET', '/geoloc/countries?fields=en_value,translation&language=de',
                 expected_result=[{"en_value": "Austria", "translation": "Österreich"},
                                  {"en_value": "Italy", "translation": "Italien"},
                                  {"en_value": "Serbia", "translation": "Serbien"},
                                  {"en_value": "Switzerland", "translation": "Schweiz"}])

        self.api(self.token, 'GET', '/geoloc/countries?fields=translation&language=it',
                 expected_result=[{"translation": "Austria"},
                                  {"translation": "Italia"},
                                  {"translation": "Serbia"},
                                  {"translation": "Svizzera"}])

        self.api(self.token, 'GET', '/geoloc/countries?fields=translation&language=sr',
                 expected_result=[{"translation": "Austrija"},
                                  {"translation": "Italija"},
                                  {"translation": "Srbija"},
                                  {"translation": "Švajcarska"}])

    def test_search_countries(self):
        self.api(self.token, 'GET', '/geoloc/countries?fields=en_value&search=iTAlY', expected_result=[
            {"en_value": "Italy"}
        ])
