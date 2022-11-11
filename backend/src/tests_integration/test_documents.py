# import os
# import base64
#
# from tshared.test import SetupBaseAuthorizedTest
#
# current_file_folder = os.path.dirname(os.path.realpath(__file__))
#
#
# class TestDocumentsAndFiles(SetupBaseAuthorizedTest):
#
#     def setUp(self):
#         self.api_modules = [
#             'svc_tenants.tenants.api',
#             'svc_documents.documents.api',
#             'svc_files.files.api',
#             'svc_flows.flows.api',
#
#         ]
#         super().setUp()
#
#     def test_get_file(self):
#         with open(current_file_folder + '/images/dclogo.png', 'rb') as f:
#             source_binary = f.read()
#         encoded = base64.b64encode(source_binary)
#         self.api(self.token, 'POST', f'/documents/users/{self.id_system_user}',
#                  {'filename': 'test.png', 'bse64encoded': encoded.decode('utf-8')})
#         self.save_last_result(add_request_body=True)
#         with open(self.last_result['file'], 'rb') as f:
#             saved_binary = f.read()
#         self.assertEqual(source_binary, saved_binary)
#         url_without_api_v3 = self.last_result['url'][len('/api/v3'):]
#         self.api(self.token, 'GET', url_without_api_v3, expected_code=None, expected_raw=True, binary=True)
#
#         # self.assertTrue(len(self.last_result), 198328)
#
#         self.api(self.token, 'GET', f'/documents/users/{self.id_system_user}')
#         self.show_last_result()
#
#         url_without_api_v3 = url_without_api_v3.replace('.png', '.thumbnail.png')
#         self.api(self.token, 'GET', url_without_api_v3, expected_code=None, expected_raw=True, binary=True)
#         self.assertLess(len(self.last_result), 198328)
#
#         self.api(None, 'GET', url_without_api_v3, expected_code=None, expected_raw=True, binary=True)
#
#
# class TestDocuments(SetupBaseAuthorizedTest):
#     def setUp(self):
#         self.api_modules = [
#             'svc_tenants.tenants.api',
#             'svc_documents.documents.api',
#             'svc_flows.flows.api',
#         ]
#         super().setUp()
#
#     def test_get_about(self):
#         self.api(self.token, 'GET', '/tenants/about', expected_result_subset={"service": "tenants"})
#         self.api(self.token, 'GET', '/documents/about', expected_result_subset={"service": "documents"})
#
#     def test_mk_thumbnail_aca_proportions(self):
#         with open(current_file_folder + '/images/aca.jpg', 'rb') as f:
#             source_binary = f.read()
#
#         encoded = base64.b64encode(source_binary)
#
#         self.api(self.token, 'POST', f'/documents/users/{self.id_system_user}',
#                  {'filename': 'test.png', 'bse64encoded': encoded.decode('utf-8')})
#
#         with open(self.last_result['file'], 'rb') as f:
#             saved_binary = f.read()
#
#         self.assertEqual(source_binary, saved_binary)
#         self.api(self.token, 'GET', f'/documents/users/{self.id_system_user}')
#         self.show_last_result()
#
#     def test_get_documents_instance(self):
#         with open(current_file_folder + '/images/dclogo.png', 'rb') as f:
#             source_binary = f.read()
#
#         encoded = base64.b64encode(source_binary)
#
#         self.api(self.token, 'POST', f'/documents/users/{self.id_system_user}',
#                  {'filename': 'test.png', 'bse64encoded': encoded.decode('utf-8')})
#         with open(self.last_result['file'], 'rb') as f:
#             saved_binary = f.read()
#         self.assertEqual(source_binary, saved_binary)
#         self.api(self.token, 'GET', f'/documents/users/{self.id_system_user}')
#
#     def test_post_documents_instance(self):
#         with open(current_file_folder + '/images/dclogo.png', 'rb') as f:
#             source_binary = f.read()
#
#         encoded = base64.b64encode(source_binary)
#
#         self.api(self.token, 'POST', f'/documents/users/{self.id_system_user}',
#                  {'filename': 'test.png', 'bse64encoded': encoded.decode('utf-8')})
#         with open(self.last_result['file'], 'rb') as f:
#             saved_binary = f.read()
#         self.assertEqual(source_binary, saved_binary)
#
#     def test_delete_document(self):
#         with open(current_file_folder + '/images/dclogo.png', 'rb') as f:
#             source_binary = f.read()
#
#         encoded = base64.b64encode(source_binary)
#
#         self.api(self.token, 'POST', f'/documents/users/{self.id_system_user}',
#                  {'filename': 'test.png', 'bse64encoded': encoded.decode('utf-8')})
#         with open(self.last_result['file'], 'rb') as f:
#             saved_binary = f.read()
#         self.assertEqual(source_binary, saved_binary)
#         document_id = self.last_result["id"]
#         self.api(self.token, 'DELETE', f'/documents/-/{document_id}')
