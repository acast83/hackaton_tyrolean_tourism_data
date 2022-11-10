import os
import uuid
from unittest.mock import patch as patch
from tshared.test import SetupBaseAuthorizedTest
import unittest.mock

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
        self.api(self.token, 'GET', '/flows/about', expected_result_subset={"service": "flows"})

    def test_lookup_all_lookups(self):
        result = self.api(self.token, 'GET', '/flows/lookups', expected_code=200)
        expected_result = {
            'flow_types',
            "flow_visibility",
            "flow_priorities",
            # {{ lookup_name }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}
        }
        self.assertEqual(first=set(result), second=expected_result)

    def test_create_flow(self):
        id_instance = uuid.uuid4()
        self.api(self.token, 'POST', f'/flows/sales/{id_instance}', body={"html": "Nii did something"})

        self.api(self.token, 'GET', f'/flows/sales/{id_instance}')
        self.assertEqual(self.last_result[0]["html"], "Nii did something")

    def test_flow_filters(self):
        deal_id = uuid.uuid4()
        self.api(self.token, 'POST', f'/flows/sales/{deal_id}',
                 body={"html": "some text", "type_id": self.flow_types["FLOW_TYPE_USER_ACTION"]["id"]})
        self.api(self.token, 'POST', f'/flows/sales/{deal_id}',
                 body={"html": "some text", "type_id": self.flow_types["FLOW_TYPE_USER_ACTION"]["id"]})
        self.api(self.token, 'POST', f'/flows/sales/{deal_id}', body={"html": "some text"})

        self.api(self.token, 'GET', f'/flows/sales/{deal_id}?id_type_csv=1')
        self.assertEqual(self.last_result[0]["html"], "some text")
        self.assertEqual(len(self.last_result), 1)
        self.api(self.token, 'GET', f'/flows/sales/{deal_id}?id_type_csv=1,3')
        self.assertEqual(len(self.last_result), 3)
        self.api(self.token, 'GET', f'/flows/sales/{deal_id}?id_type_csv=1,2,3,5')
        self.assertEqual(len(self.last_result), 3)
        self.api(self.token, 'GET', f'/flows/sales/{deal_id}?visibility=visible,deleted')
        self.assertEqual(len(self.last_result), 3)
        self.api(self.token, 'GET', f'/flows/sales/{deal_id}?visibility=deleted')
        self.assertEqual(len(self.last_result), 0)
        self.api(self.token, 'GET', f'/flows/sales/{deal_id}?priority=regular,important')
        self.assertEqual(len(self.last_result), 3)
        self.api(self.token, 'GET', f'/flows/sales/{deal_id}?priority=important')
        self.assertEqual(len(self.last_result), 0)

    def test_update_flow(self):
        deal_id = uuid.uuid4()
        self.api(self.token, 'POST', f'/flows/sales/{deal_id}',
                 body={"html": "some text", "type_id": self.flow_types["FLOW_TYPE_USER_ACTION"]["id"]})
        flow_id = self.last_result["id"]
        self.api(self.token, 'GET', f'/flows/{flow_id}')
        self.assertEqual(self.last_result["type_id"], self.flow_types["FLOW_TYPE_USER_ACTION"]["id"])
        self.api(self.token, 'PATCH', f'/flows/{flow_id}',
                 body={"type_id": self.flow_types["FLOW_TYPE_SYSTEM_ACTION"]["id"]})
        self.api(self.token, 'GET', f'/flows/{flow_id}')
        self.assertEqual(self.last_result["type_id"], self.flow_types["FLOW_TYPE_SYSTEM_ACTION"]["id"])
        self.api(self.token, 'PATCH', f'/flows/{flow_id}',
                 body={"visibility_id": self.lookup_flows_flow_visibility["HIDDEN"]["id"]})
        self.api(self.token, 'GET', f'/flows/{flow_id}')
        self.assertEqual(self.last_result["visibility_id"], self.lookup_flows_flow_visibility["HIDDEN"]["id"])
        self.api(self.token, 'PATCH', f'/flows/{flow_id}',
                 body={"priority_id": self.lookup_flows_flow_priorities["IMPORTANT"]["id"]})
        self.api(self.token, 'GET', f'/flows/{flow_id}')
        self.assertEqual(self.last_result["priority_id"], self.lookup_flows_flow_priorities["IMPORTANT"]["id"])

    def test_update_flow_archive(self):
        deal_id = uuid.uuid4()
        self.api(self.token, 'POST', f'/flows/sales/{deal_id}',
                 body={"html": "some text", "type_id": self.flow_types["FLOW_TYPE_USER_ACTION"]["id"]})
        flow_id = self.last_result["id"]
        self.api(self.token, 'POST', f'/flows/sales/{deal_id}', body={"html": "some new text", })

        self.api(self.token, 'GET', f'/flows/{flow_id}')
        self.assertEqual(self.last_result["active"], True)
        self.api(self.token, 'GET', f'/flows/sales/{deal_id}?visibility=visible')
        self.assertEqual(len(self.last_result), 2)
        self.api(self.token, 'PATCH', f'/flows/{flow_id}/archived', body={"value": True})
        self.api(self.token, 'GET', f'/flows/{flow_id}')
        self.assertEqual(self.last_result["archived"], True)
        self.api(self.token, 'GET', f'/flows/sales/{deal_id}?visibility=visible')
        self.assertEqual(len(self.last_result), 1)
        self.api(self.token, 'GET', f'/flows/sales/{deal_id}?visibility=deleted')
        self.assertEqual(len(self.last_result), 1)

    def test_update_flow_important(self):
        deal_id = uuid.uuid4()
        self.api(self.token, 'POST', f'/flows/sales/{deal_id}',
                 body={"html": "some text", "type_id": self.flow_types["FLOW_TYPE_USER_ACTION"]["id"]})
        flow_id = self.last_result["id"]
        self.api(self.token, 'GET', f'/flows/{flow_id}')
        self.assertEqual(self.last_result["important"], False)
        self.api(self.token, 'GET', f'/flows/sales/{deal_id}')
        self.assertEqual(len(self.last_result), 1)
        self.api(self.token, 'PATCH', f'/flows/{flow_id}/important', body={"value": True})
        self.api(self.token, 'GET', f'/flows/{flow_id}')
        self.assertEqual(self.last_result["important"], True)
        self.api(self.token, 'GET', f'/flows/sales/{deal_id}?priority=regular,important')
        self.assertEqual(len(self.last_result), 1)
        self.api(self.token, 'GET', f'/flows/sales/{deal_id}?priority=regular')
        self.assertEqual(len(self.last_result), 0)

    def test_create_external_impresa_flow_post(self):
        deal_id = uuid.uuid4()
        self.api(self.token, 'POST', f'/flows/sales/{deal_id}', body={"html": "some text",
                                                                      "type_id": self.flow_types[
                                                                          "FLOW_EXTERNAL_IMPRESA_ACTION"]["id"],
                                                                      "data": {
                                                                          "action": "ADD_EXTERNAL_POST_FROM_IMPRESA",
                                                                          "key1": "value1",
                                                                          "key2": "value2", }})
        self.api(self.token, 'GET', f'/flows/sales/{deal_id}')
        self.assertEqual(self.last_result[0]["html"], '<div>key1: value1\nkey2: value2\n </div>')
        self.api(self.token, 'GET', f'/flows/sales/{deal_id}?no_paginate=false')
        self.show_last_result()

    def test_translate_flow_messages_for_deals(self, *args):
        deal_id = uuid.uuid4()
        self.api(self.token, 'POST', f'/flows/sales/{deal_id}',
                 body={"data": {"action": "CREATE_DEAL", "deal": {"company": {"name": "Digital"}}},
                       "type_id": self.flow_types["FLOW_TYPE_USER_ACTION"]["id"]})

        with unittest.mock.patch('svc_flows.flows.api.flows.ipc_tenants.me', return_value={"language": "it"}):
            self.api(self.token, 'GET', f'/flows/sales/{deal_id}')
            # self.show_last_result()

        with unittest.mock.patch('svc_flows.flows.api.flows.ipc_tenants.me', return_value={"language": "de"}):
            self.api(self.token, 'GET', f'/flows/sales/{deal_id}')
            # self.show_last_result()

        self.api(self.token, 'GET', f'/flows/sales/{deal_id}?no_paginate=true&search=system')
        self.assertEqual(len(self.last_result), 1)

        with unittest.mock.patch('svc_flows.flows.api.flows.ipc_tenants.me', return_value={"language": "de"}):
            self.api(self.token, 'GET', f'/flows/sales/{deal_id}?no_paginate=true&search=erstellt')
            # self.assertEqual(len(self.last_result), 1)
            self.show_last_result()
        self.show_last_result()
