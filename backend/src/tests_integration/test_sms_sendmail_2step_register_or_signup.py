import os
from tshared.test import SetupBaseAuthorizedTest

# import dotenv
# dotenv.load_dotenv()


current_file_folder = os.path.dirname(os.path.realpath(__file__))


class TestSMSWithTenants(SetupBaseAuthorizedTest):

    def setUp(self):
        self.api_modules = [
            'svc_tenants.tenants.api',
            'svc_sms.sms.api',
            'svc_sendmail.sendmail.api',
        ]
        super().setUp()

    def test_about(self):
        self.api(self.token, 'GET', '/tenants/about', expected_result_subset={"service": "tenants"})
        self.api(self.token, 'GET', '/sms/about', expected_result_subset={"service": "sms"})
        self.api(self.token, 'GET', '/sendmail/about', expected_result_subset={"service": "sendmail"})

    def test_first_time_register_using_email(self):
        self.api(None, 'POST', f'/tenants/{self.id_tenant}/users/signup', {'value': 'igor@digitalcube.rs'},
                 expected_result_subset={'required': 'pin'}, expected_result_contain_keys={'id'})
        signup_id = self.last_result['id']

        self.api(self.token, 'GET', f'/sendmail/tests/last-enqueued')
        pin = self.last_result['subject'].split('activation PIN: ')[-1]

        self.api(None, 'POST', f'/tenants/{self.id_tenant}/users/signup/step2/{signup_id}', {'value': pin},
                 expected_result_contain_keys={'token'})

    def test_first_time_register_using_phonenumber(self):
        self.api(None, 'POST', f'/tenants/{self.id_tenant}/users/signup', {'value': '+381 69 697 76 76'},
                 expected_result_subset={'required': 'pin'}, expected_result_contain_keys={'id'}
                 )
        signup_id = self.last_result['id']
        self.api(self.token, 'GET', f'/sms/tests/last-enqueued')
        pin = self.last_result['message'].split('activation PIN: ')[-1]

        self.api(None, 'POST', f'/tenants/{self.id_tenant}/users/signup/step2/{signup_id}', {'value': pin},
                 expected_result_contain_keys={'token'})

    def _test_login_already_registerd_user_using_email(self):
        self.api(None, 'POST', f'/tenants/{self.id_tenant}/users/signup', {'value': 'system'}, expected_code=None)
        signup_id = self.last_result['id']
        self.api(None, 'POST', f'/tenants/{self.id_tenant}/users/signup/step2/{signup_id}', {'value': 'system123'},
                 expected_result_contain_keys={'token'})

    def test_login_already_registerd_user_using_sms(self):
        pass
        # TODO

    def test_login_already_registerd_user_using_username_and_password(self):
        pass
        # TODO

    def test_setup_username_and_password_for_user_registered_with_email(self):
        pass
        # TODO

    def test_setup_username_and_password_for_user_registered_with_phone(self):
        pass
        # TODO
