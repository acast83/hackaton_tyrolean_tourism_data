import os
from tshared.test import SetupBaseAuthorizedTest

# import dotenv
# dotenv.load_dotenv()


current_file_folder = os.path.dirname(os.path.realpath(__file__))


class TestFlows(SetupBaseAuthorizedTest):

    def setUp(self):
        self.api_modules = [
            'svc_tenants.tenants.api',
            'svc_flows.flows.api',
          
        ]
        super().setUp()

    def test_about(self):
        self.api(self.token, 'GET', '/tenants/about', expected_result_subset={"service": "tenants"})
        self.api(self.token, 'GET', '/flows/about', expected_result_subset={"service": "flows"})

    def test_custom_flow_message_on_user_instance(self):
        self.api(self.token, 'POST', f'/flows/users/{self.id_system_user}', {
            'type_id': self.flow_types['FLOW_TYPE_MESSAGE']['id'],
            'html': '<p>Test</p>',
            'text': 'Test',
            'data': {'a': 'b'}
        }, expected_result_contain_keys={'id'})

    # TODO:Test
    def test_flow_on_user_change_own_properties(self):
        self.api(self.token, 'GET', f'/tenants/me')

        self.api(None, 'POST', f'/tenants/{self.id_tenant}/sessions', {'username': 'system', 'password': 'system123'})

        self.api(self.token, 'GET', f'/flows/users/{self.id_system_user}?fields=html&order_by=-created',
                 expected_result=[{'html': 'user logged in'}])

        self.api(self.token, 'PATCH', f'/tenants/me', {'first_name': 'Test'})
        self.api(self.token, 'GET', f'/flows/users/{self.id_system_user}?fields=html&order_by=-created',
                 expected_result=[{"html": "user changes his first_name to Test"},
                                  {'html': 'user logged in'}])

        # there is no change, last name was user too
        self.api(self.token, 'PATCH', f'/tenants/me', {'last_name': 'user'})
        self.api(self.token, 'GET', f'/flows/users/{self.id_system_user}?fields=html&order_by=-created',
                 expected_result=[{"html": "user changes his first_name to Test"},
                                  {'html': 'user logged in'}])

        # user -> User
        self.api(self.token, 'PATCH', f'/tenants/me', {'last_name': 'User'})
        self.api(self.token, 'GET', f'/flows/users/{self.id_system_user}?fields=html&order_by=-created',
                 expected_result=[{"html": "user changes his last_name to User"},
                                  {"html": "user changes his first_name to Test"},
                                  {'html': 'user logged in'}])

        self.api(self.token, 'PATCH', f'/tenants/me', {'old_password': 'system123', 'password': '1234'})
        self.api(self.token, 'GET', f'/flows/users/{self.id_system_user}?fields=html&order_by=-created',
                 expected_result=[{"html": "user changes his password by providing old password"},
                                  {"html": "user changes his last_name to User"},
                                  {"html": "user changes his first_name to Test"},
                                  {'html': 'user logged in'}])
