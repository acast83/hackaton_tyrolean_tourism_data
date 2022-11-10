import os
import json
import importlib
import tortoise
from tortoise import Tortoise
from tornado.httpclient import AsyncHTTPClient
from tortoise.backends.asyncpg import AsyncpgDBClient
from base3.utils import load_config
from base3 import app, test, http
from tshared.utils.setup_logger import setup_logging
from tshared.utils.register_db_signal import register_db_signal_for_models_in_module
from scripts.load_env_variables import load_env_variables

current_file_folder = os.path.dirname(os.path.realpath(__file__))


class SetUpTest(test.BaseTest):

    def setUp(self):

        AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")

        # load_dotenv()  # dotenv_path='/../../.env')
        load_env_variables(from_config_file='../environments/environment.yaml',
                           config_file_sections=['testing'],
                           )

        self.config = load_config('/', [current_file_folder + '/../../config/services.yaml',
                                        current_file_folder + '/../../config/db.yaml'
                                        ])

        if hasattr(self, 'api_modules'):
            for module in self.api_modules:
                try:
                    importlib.import_module(module)
                    register_db_signal_for_models_in_module(module.replace('.api', '.models'))  # fixme delete

                except Exception as e:
                    print('exception e', e)
                    raise
        else:
            print('no self.api_modules defined')

        # self.get_new_ioloop().run_sync(self.initialize_database)
        tortoise.run_async(self.initialize_database())

        self.my_app = app.make_app(print_routes=False, debug=True)

        setup_logging(settings=self.config,
                      services=[x.split('.')[1] for x in self.api_modules],
                      for_testing=True)

        super().setUp()

    def tearDown(self):

        # self.get_new_ioloop().run_sync(self.close_database)
        tortoise.run_async(self.close_database())
        super().tearDown()

    async def close_database(self):

        await Tortoise.close_connections()

    async def initialize_database(self):

        db_config = self.config['db_test']

        client = AsyncpgDBClient(user=db_config['user'],
                                 password=db_config['password'],
                                 database=db_config['database'],
                                 host=db_config['host'],
                                 port=db_config['port'],
                                 connection_name='default'
                                 )

        dbb = db_config['database']
        # print("DELETE THIS",dbb)

        await client.db_delete()
        await client.db_create()
        await client.close()

        try:

            models = []
            for svc in self.config['services']:
                for am in self.api_modules:
                    if f'svc_{svc}.' in am:
                        models.append(f'svc_{svc}.{svc}.models')
                        break

            # db_url = f"postgres://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['database']}"

            import copy
            tcfg = copy.deepcopy(self.config['tortoise'])

            if 'aerich' in tcfg['apps']:
                del tcfg['apps']['aerich']

            used_apps = set([x.split('.')[1] for x in self.api_modules])

            tcfg_app = {}

            for app in tcfg['apps']:
                if app in used_apps:
                    tcfg_app[app] = {'default_connection': 'conn_test',
                                     'models': tcfg['apps'][app]['models']}
            tcfg['apps'] = tcfg_app

            await Tortoise.init(
                config=tcfg,
                modules={"models": models})

            await Tortoise.generate_schemas()

        except Exception as e:
            raise

        # print('db initialized')


class SetupBaseAuthorizedTest(SetUpTest):

    def register_testing_users(self,
                               user_list=[
                                   {'username': 'igor', 'password': '123', 'first_name': 'Igor', 'last_name': 'Jeremic',
                                    "vacation_groups": ['ORTHODOX'],
                                    "department_groups": ['DEV', 'PD', 'SUP'], 'wiki_groups': ['SALES']},
                                   {'username': 'aca', 'password': '123', 'first_name': 'Aleksandar',
                                    'last_name': 'Stojkovic',
                                    "vacation_groups": ['ORTHODOX'],
                                    "department_groups": ['DEV'], 'wiki_groups': ['DEV']},
                               ]
                               ):

        if not hasattr(self, 'users'):
            self.users = {}

        for x in user_list:

            user_groups = []
            if 'department_groups' in x:
                user_groups += [self.tenants_lookup_user_groups_departments[g]['id'] for g in x['department_groups']]
                del x['department_groups']

            if 'vacation_groups' in x:
                user_groups += [self.tenants_lookup_user_groups_vacation[g]['id'] for g in x['vacation_groups']]
                del x['vacation_groups']

            if 'wiki_groups' in x:
                user_groups += [self.tenants_lookup_user_groups_wiki[g]['id'] for g in x['wiki_groups']]
                del x['wiki_groups']

            x['user_groups'] = user_groups

            user = self.api(self.token, 'POST', f'/tenants/{self.id_tenant}/users', x,
                            expected_code=http.status.CREATED)

            self.users[x['username']] = {'id': user['id'], 'token': user['token']}

    def register_initial_users(self):
        return self.register_testing_users(user_list=
        [
            {'username': 'aca', 'password': '123', 'first_name': 'Aleksandar', 'last_name': 'Stojkovic',
             "vacation_groups": ['ORTHODOX'],
             "department_groups": ['DEV'], 'wiki_groups': ['DEV']},
            {'username': 'mikhail', 'password': '123', 'first_name': 'Mikhail', 'last_name': 'Zotochev',
             "vacation_groups": ['ORTHODOX'],
             "department_groups": ['DEV'], 'wiki_groups': ['DEV']},
            {'username': 'ivo', 'password': '123', 'first_name': 'Ivo', 'last_name': 'Kovacevic',
             "vacation_groups": ['ORTHODOX'],
             "department_groups": ['DEV', 'PD', 'SUP'], 'wiki_groups': ['SALES', 'SUP']},
            {'username': 'slobodan', 'password': '123', 'first_name': 'Slobodan', 'last_name': 'Dolinic',
             "vacation_groups": ['ORTHODOX'],
             "department_groups": ['DEV', 'PD', 'SUP']},
            {'username': 'igor', 'password': '123', 'first_name': 'Igor', 'last_name': 'Jeremic',
             "vacation_groups": ['ORTHODOX'],
             "department_groups": ['DEV', 'PD', 'SUP'], 'wiki_groups': ['SALES']},
            {'username': 'fabio', 'password': '123', 'first_name': 'Fabio', 'last_name': 'Panaioli',
             "vacation_groups": ['CATHOLIC'],
             "department_groups": ['DEV', 'QA'], 'wiki_groups': ['SUP']},
            {'username': 'mustafa', 'password': '123', 'first_name': 'Mustafa', 'last_name': 'Redžepović',
             "vacation_groups": ['MUSLIM'],
             "department_groups": ['QA'], 'wiki_groups': ['SALES']},
        ])

    def create_master_user_single_tenant_and_tenant_system_user(self, tenant_code=None):
        self.api(None, 'POST', '/tenants/users',
                 {'username': 'master', 'password': 'admin123', 'first_name': 'master', 'last_name': 'user'},
                 expected_code=http.status.CREATED)

        self.master_token = self.last_result['token']

        if not tenant_code:
            tenant_code = 'DCUBE'
            self.tenant_name = "dcube"

        else:
            self.tenant_name = tenant_code.lower()

        self.api(self.master_token, 'POST', '/tenants/', {'code': tenant_code, 'name': self.tenant_name})
        self.id_tenant = self.last_result['id']

        self.api(self.master_token, 'POST', f'/tenants/{self.id_tenant}/users',
                 {'username': 'system', 'password': 'system123', 'first_name': 'system', 'last_name': 'user'},
                 expected_code=http.status.CREATED)

        self.id_system_user = self.last_result['id']
        self.token = self.last_result['token']

    def _load_lookups(self, svc):
        tenant_name = getattr(self, 'tenant_name') if hasattr(self, 'tenant_name') else 'dcube'

        try:
            with open(current_file_folder + f'/../../svc_{svc}/init/lookups.{tenant_name}.json', 'rt') as f:
                self.api(self.token, 'POST', f'/{svc}/lookups/init', body={'lookups': json.load(f)})
        except Exception as e:
            try:
                fname = current_file_folder + f'/../../svc_{svc}/init/lookups.json'

                if svc == 'messenger':
                    print('stop')

                with open(current_file_folder + f'/../../svc_{svc}/init/lookups.json', 'rt') as f:
                    lkps = json.load(f)
                    self.api(self.token, 'POST', f'/{svc}/lookups/init', body={'lookups': lkps})
            except Exception as e:
                print("SVC", svc)
                raise NameError("NO LOOKUPS FILE FOR SVC")

    def initialize_lookups_svc_tenants(self):

        self._load_lookups('tenants')

        self.tenants_lookup_user_groups_departments = \
            self.api(self.token, 'GET', '/tenants/lookups/user_groups?group=DEPARTMENTS&index_by=code')['items']
        self.tenants_lookup_user_groups_vacation = \
            self.api(self.token, 'GET', '/tenants/lookups/user_groups?group=VACATION&index_by=code')['items']
        self.tenants_lookup_user_groups_wiki = \
            self.api(self.token, 'GET', '/tenants/lookups/user_groups?group=WIKI&index_by=code')['items']

        self.tenants_lookup_user_roles = \
            self.api(self.token, 'GET', '/tenants/lookups/roles?index_by=code')['items']

        self.lookup_tenants_prefered_language = \
            self.api(self.token, 'GET', '/tenants/lookups/prefered_language?index_by=code')['items']
        # {{ lookup_get_tenants }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}

    def initialize_lookups_svc_flows(self):

        self._load_lookups('flows')

        self.flow_types = self.api(self.token, 'GET', '/flows/lookups/flow_types?index_by=code')['items']
        self.lookup_flows_flow_visibility = self.api(self.token, 'GET', '/flows/lookups/flow_visibility?index_by=code')[
            'items']
        self.lookup_flows_flow_priorities = self.api(self.token, 'GET', '/flows/lookups/flow_priorities?index_by=code')[
            'items']
        # {{ lookup_get_flows }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}

    def initialize_lookups_svc_sla(self):

        self._load_lookups('sla')

        self.lookup_sla_groups = self.api(self.token, 'GET', '/sla/lookups/groups?index_by=code')['items']
        self.lookup_sla_additional = self.api(self.token, 'GET', '/sla/lookups/additional?index_by=code')['items']
        self.lookup_sla_business_component_groups = \
            self.api(self.token, 'GET', '/sla/lookups/business_component_groups?index_by=code')['items']

        self.lookup_sla_business_components = \
            self.api(self.token, 'GET', '/sla/lookups/business_components?index_by=code')['items']

        self.lookup_sla_main = self.api(self.token, 'GET', '/sla/lookups/main?index_by=code')['items']

        self.lookup_billing_period = self.api(self.token, 'GET', '/sla/lookups/billing_period?index_by=code')['items']
        self.lookup_sla_status = self.api(self.token, 'GET', '/sla/lookups/status?index_by=code')['items']
        # {{ lookup_get_sla }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}

    def initialize_lookups_svc_wiki(self):

        self._load_lookups('wiki')

        self.wiki_statuses = self.api(self.token, 'GET', '/wiki/lookups/statuses?index_by=code')['items']
        # {{ lookup_get_wiki }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}

    def initialize_lookups_svc_bp(self):
        self._load_lookups('bp')

        self.lookup_bp_educational_titles = self.api(self.token, 'GET', '/bp/lookups/educational_titles?index_by=code')[
            'items']
        self.lookup_bp_company_types = self.api(self.token, 'GET', '/bp/lookups/company_types?index_by=code')['items']
        self.lookup_bp_gender = self.api(self.token, 'GET', '/bp/lookups/genders?index_by=code')['items']
        self.lookup_bp_nationalities = self.api(self.token, 'GET', '/bp/lookups/nationalities?index_by=code')['items']
        self.lookup_bp_document_types = self.api(self.token, 'GET', '/bp/lookups/document_types?index_by=code')['items']
        self.lookup_bp_phone_types = self.api(self.token, 'GET', '/bp/lookups/phone_types?index_by=code')['items']
        self.lookup_bp_email_types = self.api(self.token, 'GET', '/bp/lookups/email_types?index_by=code')['items']
        self.lookup_bp_industry_types = self.api(self.token, 'GET', '/bp/lookups/industry_types?index_by=code')['items']
        self.lookup_bp_gender_prefix = self.api(self.token, 'GET', '/bp/lookups/gender_prefix?index_by=code')['items']
        # {{ lookup_get_bp }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}

    def initialize_lookups_svc_tickets(self):
        self._load_lookups('tickets')

        self.api(self.token, 'GET', '/tickets/lookups', expected_result=[
            "types", "priorities", 'status_types', 'statuses'
        ])
        self.tickets_lookup_ticket_types = self.api(self.token, 'GET', '/tickets/lookups/types?index_by=code')['items']
        self.tickets_lookup_ticket_priorities = \
            self.api(self.token, 'GET', '/tickets/lookups/priorities?index_by=code')['items']
        self.tickets_lookup_ticket_statuses = self.api(self.token, 'GET', '/tickets/lookups/statuses?index_by=code')[
            'items']
        # {{ lookup_get_tickets }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}

    def initialize_lookups_svc_contacts(self):
        self._load_lookups('contacts')

        self.contacts_lookup_phone_number_types = \
            self.api(self.token, 'GET', '/contacts/lookups/phone_number_types?index_by=code')['items']

        self.contacts_lookup_email_types = \
            self.api(self.token, 'GET', '/contacts/lookups/email_types?index_by=code')['items']
        # {{ lookup_get_contacts }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}

    def initialize_lookups_svc_open_messenger(self):

        self._load_lookups('open_messenger')

        self.lookup_open_messenger_type = self.api(self.token, 'GET', '/open_messenger/lookups/type?index_by=code')[
            'items']
        self.lookup_open_messenger_statuses = \
            self.api(self.token, 'GET', '/open_messenger/lookups/statuses?index_by=code')['items']
        # {{ lookup_get_open_messenger }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}

    def initialize_lookups_svc_pdfgen(self):
        self._load_lookups('pdfgen')
        self.lookup_pdfgen_document_types = self.api(self.token, 'GET', '/pdfgen/lookups/document_types?index_by=code')[
            'items']
        # {{ lookup_get_pdfgen }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}

    def initialize_lookups_svc_services(self):
        self._load_lookups('services')

        self.lookup_services_service_groups = \
            self.api(self.token, 'GET', '/services/lookups/service_groups?index_by=code')['items']
        self.lookup_services_service_types = \
            self.api(self.token, 'GET', '/services/lookups/service_types?index_by=code')['items']
        self.lookup_services_phone_number_origins = \
            self.api(self.token, 'GET', '/services/lookups/phone_number_origins?index_by=code')['items']
        self.lookup_services_service_status = \
            self.api(self.token, 'GET', '/services/lookups/service_status?index_by=code')['items']
        self.lookup_services_sim_status = self.api(self.token, 'GET', '/services/lookups/sim_status?index_by=code')[
            'items']
        self.lookup_services_service_template_item_type = \
            self.api(self.token, 'GET', '/services/lookups/service_template_item_type?index_by=code')['items']
        self.lookup_services_plintron_call_type = \
            self.api(self.token, 'GET', '/services/lookups/plintron_call_type?index_by=code')['items']
        # {{ lookup_get_services }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}

    def initialize_lookups_svc_pdf_generator(self):
        self._load_lookups('pdf_generator')

        self.lookup_pdf_generator_document_types = \
            self.api(self.token, 'GET', '/pdf_generator/lookups/document_types?index_by=code')['items']
        # {{ lookup_get_pdf_generator }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}

    def initialize_lookups_svc_wallet(self):
        self._load_lookups('wallet')

        self.lookup_wallet_transaction_type = \
            self.api(self.token, 'GET', '/wallet/lookups/transaction_type?index_by=code')['items']
        self.lookup_wallet_exchange_operation = \
            self.api(self.token, 'GET', '/wallet/lookups/exchange_operation?index_by=code')['items']
        # {{ lookup_get_wallet }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}

    def initialize_lookups_svc_kanban(self):
        self._load_lookups('kanban')

        self.lookup_kanban_kanban_application = \
            self.api(self.token, 'GET', '/kanban/lookups/kanban_application?index_by=code')['items']

        self.lookup_kanban_application = \
            self.api(self.token, 'GET', '/kanban/lookups/kanban_application?index_by=code')['items']
        # {{ lookup_get_kanban }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}

    def initialize_lookups_svc_deals(self):
        self._load_lookups('deals')

        self.lookup_deals_deal_stages = self.api(self.token, 'GET', '/deals/lookups/deal_stages?index_by=code')['items']
        self.lookup_deals_deal_classifications = \
            self.api(self.token, 'GET', '/deals/lookups/deal_classifications?index_by=code')['items']
        self.lookup_deals_deal_sources = self.api(self.token, 'GET', '/deals/lookups/deal_sources?index_by=code')[
            'items']
        self.lookup_deals_deal_statuses = self.api(self.token, 'GET', '/deals/lookups/deal_statuses?index_by=code')[
            'items']
        # {{ lookup_get_deals }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}

    def initialize_lookups_svc_messenger(self):
        self._load_lookups('messenger')

        self.lookup_messenger_chat_notification_channel = \
            self.api(self.token, 'GET', '/messenger/lookups/chat_notification_channel?index_by=code')['items']
        # {{ lookup_get_messenger }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}

    def initialize_lookups_svc_olo(self):
        self._load_lookups('olo')

        self.lookup_olo_olo_process = self.api(self.token, 'GET', '/olo/lookups/olo_process?index_by=code')['items']
        self.lookup_olo_olo_operator = self.api(self.token, 'GET', '/olo/lookups/olo_operator?index_by=code')['items']
        self.lookup_olo_olo_operation_group = \
            self.api(self.token, 'GET', '/olo/lookups/olo_operation_group?index_by=code')['items']
        self.lookup_olo_olo_operation_type = \
            self.api(self.token, 'GET', '/olo/lookups/olo_operation_type?index_by=code')['items']
        self.lookup_olo_olo_operation_status = \
            self.api(self.token, 'GET', '/olo/lookups/olo_operation_status?index_by=code')['items']
        self.lookup_olo_olo_operation_steps = \
            self.api(self.token, 'GET', '/olo/lookups/olo_operation_steps?index_by=code')['items']
        self.lookup_olo_olo_direction = self.api(self.token, 'GET', '/olo/lookups/olo_direction?index_by=code')['items']
        self.lookup_olo_olo_interface = self.api(self.token, 'GET', '/olo/lookups/olo_interface?index_by=code')['items']
        # {{ lookup_get_olo }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}

    def initialize_lookups_svc_conferences(self):

        self._load_lookups('conferences')

        self.lookup_conferences_conf_session_status = \
            self.api(self.token, 'GET', '/conferences/lookups/conf_session_status?index_by=code')['items']
        # {{ lookup_get_conferences }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}

    def initialize_lookups_svc_telegram(self):
        with open(current_file_folder + '/../../svc_telegram/init/lookups.json', 'rt') as f:
            lookups = json.load(f)

        self.api(self.token, 'POST', '/telegram/lookups/init', body={'lookups': lookups}, expected_code=None)

        self.lookup_telegram_message_sending_status = \
            self.api(self.token, 'GET', '/telegram/lookups/message_sending_status?index_by=code')['items']
        # {{ lookup_get_telegram }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}

    # {{ function_body }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}

    def initialize_lookups(self):
        api_modules = [a.split('.')[1] for a in self.api_modules]
        if 'tenants' in api_modules:
            self.initialize_lookups_svc_tenants()
        if 'bp' in api_modules:
            self.initialize_lookups_svc_bp()
        if 'flows' in api_modules:
            self.initialize_lookups_svc_flows()
        if 'tickets' in api_modules:
            self.initialize_lookups_svc_tickets()
        if 'wiki' in api_modules:
            self.initialize_lookups_svc_wiki()
        if 'contacts' in api_modules:
            self.initialize_lookups_svc_contacts()
        if 'sla' in api_modules:
            self.initialize_lookups_svc_sla()
        if 'open_messenger' in api_modules:
            self.initialize_lookups_svc_open_messenger()
        if 'pdfgen' in api_modules:
            self.initialize_lookups_svc_pdfgen()
        if 'services' in api_modules:
            self.initialize_lookups_svc_services()
        if 'pdf_generator' in api_modules:
            self.initialize_lookups_svc_pdf_generator()
        if 'wallet' in api_modules:
            self.initialize_lookups_svc_wallet()
        if 'kanban' in api_modules:
            self.initialize_lookups_svc_kanban()
        if 'deals' in api_modules:
            self.initialize_lookups_svc_deals()
        if 'messenger' in api_modules:
            self.initialize_lookups_svc_messenger()
        if 'olo' in api_modules:
            self.initialize_lookups_svc_olo()
        if 'conferences' in api_modules:
            self.initialize_lookups_svc_conferences()
        if 'telegram' in api_modules:
            self.initialize_lookups_svc_telegram()
        # {{ function_call }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}

    def setUp(self, tenant_code=None):
        super().setUp()
        self.create_master_user_single_tenant_and_tenant_system_user(tenant_code=tenant_code)
        self.initialize_lookups()
