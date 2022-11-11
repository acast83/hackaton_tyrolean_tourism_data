import urllib.parse
import json
import os
import pytest
from base3 import http
from tshared.test import SetupBaseAuthorizedTest

# import dotenv
# dotenv.load_dotenv()

current_file_folder = os.path.dirname(os.path.realpath(__file__))


class TestTenantsInitializeLookup2Times(SetupBaseAuthorizedTest):
    def setUp(self):
        self.api_modules = [
            'svc_tenants.tenants.api',
            'svc_documents.documents.api',
        ]
        super().setUp()


class TestTenants(SetupBaseAuthorizedTest):
    def setUp(self):
        self.api_modules = [
            'svc_tenants.tenants.api',
        ]
        super().setUp()

    def test_about(self):
        self.api(self.token, 'GET', '/tenants/about', expected_result_subset={"service": "tenants"})

    def test_lookup_all_lookups(self):
        result = self.api(self.token, 'GET', '/tenants/lookups', expected_code=200)
        expected_result = {
            'permissions',
            'roles',
            'user_groups',
            'org_units',
            "prefered_language"
            # {{ lookup_name }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
        }
        self.assertEqual(first=set(result), second=expected_result)


class TestUserSettings(SetupBaseAuthorizedTest):

    def setUp(self):
        self.api_modules = [
            'svc_tenants.tenants.api',
        ]
        try:
            super().setUp()
        except Exception as e:
            raise

    # TODO: Aca, mozda malo da unapredis ove testove, tjs skloni showlast result i stavi asserte tj expecetd_alues
    def test_user_settings(self):
        self.register_testing_users([{'username': 'igor'},
                                     {'username': 'aca'}])

        print(self.users['igor']['token'])
        print(self.users['aca']['token'])

        self.api(self.users['igor']['token'], 'GET', '/tenants/my-settings', expected_code=http.status.OK)
        self.api(self.users['igor']['token'], 'POST', '/tenants/my-settings/lang',
                 {"value": True},
                 expected_code=http.status.OK)

        self.api(self.users['igor']['token'], 'POST', '/tenants/my-settings/master',
                 {"value": False},
                 expected_code=http.status.OK)

        self.api(self.users['igor']['token'], 'POST', '/tenants/my-settings/null',
                 {"value": None},
                 expected_code=http.status.OK)

        self.api(self.users['igor']['token'], 'POST', '/tenants/my-settings/number',
                 {"value": 24},
                 expected_code=http.status.OK)
        self.api(self.users['igor']['token'], 'POST', '/tenants/my-settings/name',
                 {"value": 'igor'},
                 expected_code=http.status.OK)

        self.api(self.users['igor']['token'], 'GET', '/tenants/my-settings', expected_code=http.status.OK)
        self.api(self.users['igor']['token'], 'GET', '/tenants/my-settings/lang', expected_code=http.status.OK)

        self.api(self.users['aca']['token'], 'GET', '/tenants/my-settings', expected_code=http.status.OK)
        # Mi ovako primenjujemo na SLA
        self.api(self.users['aca']['token'], 'POST', '/tenants/my-settings/sla_applied',
                 {"value": [{"name": "id", "hidden": False, },
                            {"name": "uid", "hidden": False, },
                            {"name": "status_id", "hidden": True}]},
                 expected_code=http.status.OK)
        # self.api(self.users['aca']['token'], 'GET', '/tenants/my-settings/sla_applied', expected_code=http.status.OK)

    def test_user_settings_dict_update(self):
        self.register_testing_users([{'username': 'igor'},
                                     {'username': 'aca'}])
        self.api(self.users['aca']['token'], 'POST', '/tenants/my-settings/kanban-settings',
                 {"value": {
                     "key_1": 10,
                     "key_2": "Belgrade",
                     "key_3": True
                 }}, expected_code=http.status.OK)
        self.api(self.users['aca']['token'], 'PATCH', '/tenants/my-settings/kanban-settings',
                 {"value": {
                     "key_1": 20,
                     "key_2": "Belgrade",
                     "key_4": False

                 }}, expected_code=http.status.OK)

        self.api(self.users['aca']['token'], 'GET', '/tenants/my-settings/kanban-settings',
                 expected_code=http.status.OK)
        self.show_last_result()


class TestUsers(SetupBaseAuthorizedTest):

    def setUp(self):
        self.api_modules = [
            'svc_tenants.tenants.api',
        ]
        try:
            super().setUp()
        except Exception as e:
            raise

        self.register_initial_users()

    def test_get_user(self):
        self.api(self.token, 'POST', f'/tenants/{self.id_tenant}/users',
                 body={'username': 'ivan', 'password': '123', 'first_name': 'ivan', 'last_name': 'ivanovic'},
                 expected_code=http.status.CREATED)
        id_user = self.last_result['id']
        self.api(self.token, 'GET', f'/tenants/users/{id_user}', expected_code=http.status.OK, ignore_uuid_values=True,
                 expected_result_subset={'username': 'ivan'})

    def test_patch_user(self):
        self.api(self.token, 'POST', f'/tenants/{self.id_tenant}/users',
                 body={'username': 'ivan', 'password': '123', 'first_name': 'ivan', 'last_name': 'ivanovic'},
                 expected_code=http.status.CREATED)
        id_user = self.last_result['id']
        self.api(self.token, 'PATCH', f'/tenants/users/{id_user}', body={'first_name': 'Ivan', 'last_name': 'Ivic'},
                 expected_code=http.status.OK)
        self.api(self.token, 'GET', f'/tenants/users/{id_user}', expected_code=http.status.OK, ignore_uuid_values=True,
                 expected_result_subset={'username': 'ivan', 'first_name': 'Ivan', 'last_name': 'Ivic'})

    def test_get_tenant_by_code(self):
        self.api(None, 'GET', f'/tenants/code/DCUBE', expected_code=http.status.OK,
                 expected_result={'id': self.id_tenant})

    def test_force_users(self):
        for i in range(1, 100):
            self.register_testing_users([{'username': f'user{i}'}])
        user_70_id = self.api(self.token, 'GET', f'/tenants/users?no_paginate=true&search=user70')[0]["id"]
        user_80_id = self.api(self.token, 'GET', f'/tenants/users?no_paginate=true&search=user80')[0]["id"]
        user_90_id = self.api(self.token, 'GET', f'/tenants/users?no_paginate=true&search=user90')[0]["id"]
        ids_csv = f"{user_70_id},{user_80_id},{user_90_id}"
        self.api(self.token, 'GET', f'/tenants/users?ids_csv={ids_csv}')

    def test_get_users_ordered_by_last_name(self):
        self.api(self.token, 'GET',
                 f'/tenants/users?fields=username,first_name,last_name&order_by=last_name&no_paginate=true',
                 )

    def test_search_tenant(self):
        self.api(None, 'GET', f'/tenants?search=cube', expected_code=None,
                 expected_result=[
                     {
                         "id": "d70da177-9762-4e57-905c-588a1a112b0d",
                         "code": "DCUBE",
                         "name": "dcube"
                     }], ignore_uuid_values=True)

    def test_captcha(self):
        self.api(None, 'GET', f'/tenants/captcha', expected_code=None)

    def test_get_registration(self):
        self.api(None, 'GET', f'/tenants/{self.id_tenant}/users/register')


if __name__ == '__main__':
    pytest.main()
