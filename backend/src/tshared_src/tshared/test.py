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
            user = self.api(self.token, 'POST', f'/tenants/{self.id_tenant}/users', x,
                            expected_code=http.status.CREATED)

            self.users[x['username']] = {'id': user['id'], 'token': user['token']}

    def register_initial_users(self):
        return self.register_testing_users(user_list=[
            {'username': 'aca', 'password': '123', 'first_name': 'Aleksandar', 'last_name': 'Stojkovic'},
            {'username': 'bane', 'password': '123', 'first_name': 'Branislav', 'last_name': 'Cavic'},
            {'username': 'tina', 'password': '123', 'first_name': 'Tina', 'last_name': 'Popovic'},
            {'username': 'mitar', 'password': '123', 'first_name': 'Mitar', 'last_name': 'Spasic'},
        ])

    def create_master_user_single_tenant_and_tenant_system_user(self, tenant_code=None):
        self.api(None, 'POST', '/tenants/users',
                 {'username': 'master', 'password': 'admin123', 'first_name': 'master', 'last_name': 'user'},
                 expected_code=http.status.CREATED)

        self.master_token = self.last_result['token']

        tenant_code = 'DCUBE'
        self.tenant_name = "dcube"

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
            with open(current_file_folder + f'/../../svc_{svc}/init/lookups.json', 'rt') as f:
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

    # {{ function_body }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}

    def initialize_lookups(self):
        api_modules = [a.split('.')[1] for a in self.api_modules]
        if 'tenants' in api_modules:
            self.initialize_lookups_svc_tenants()

        if 'flows' in api_modules:
            self.initialize_lookups_svc_flows()

        # {{ function_call }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}

    def setUp(self, tenant_code=None):
        super().setUp()
        self.create_master_user_single_tenant_and_tenant_system_user(tenant_code=tenant_code)
        self.initialize_lookups()
