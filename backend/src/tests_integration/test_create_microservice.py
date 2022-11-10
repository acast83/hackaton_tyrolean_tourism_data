import pathlib
import platform
import unittest
import subprocess
import json
from scripts.create_microservice.utils import read_yaml_config, create_test_name, from_snake_to_camel_case


def get_python_interpreter_path() -> pathlib.Path:
    venv_path = pathlib.Path(__file__, '../../../.venv/bin').resolve(strict=True)

    list_of_interpreters = [pathlib.Path(x) for x in venv_path.glob('python*')]
    if list_of_interpreters:
        return list_of_interpreters[0]
    else:
        raise FileNotFoundError('Python interpreter not found.')


def get_sed_module():
    if platform.system() == 'Darwin':
        sed = 'gsed'
    elif platform.system() == 'Linux':
        sed = 'sed'
    else:
        raise Exception(f'{platform.system()} OS not supported.')
    try:
        r = subprocess.run([sed, '--help'], stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
        r.check_returncode()
        return sed
    except subprocess.CalledProcessError as e:
        raise Exception(f'{sed} module not found on the system.')


class TestCreateNewService(unittest.TestCase):
    sources = pathlib.Path(pathlib.Path.cwd(), '../..').resolve()
    interpreter = get_python_interpreter_path()
    services = pathlib.Path(sources, 'src').resolve()
    script_location = pathlib.Path(pathlib.Path.cwd().parent,
                                   'scripts/create_microservice/create_microservice.py'
                                   ).resolve(strict=True)
    service_name = 'qwerty'
    with_lookups = True
    config: dict = None
    lookups = None

    def _delete_temp_files(self):
        sed = get_sed_module()

        r = subprocess.run([sed, '-i', f"s/SERVICE_NAME/{self.service_name}/g", 'test_create_microservice.py.test_files'])
        r.check_returncode()
        p1 = subprocess.Popen(["cat", "test_create_microservice.py.test_files"], stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["xargs", "-n", "1", "rm", "-f"], stdin=p1.stdout, stdout=subprocess.PIPE)
        p1.stdout.close()
        _ = p2.communicate()[0]
        p1.wait()
        p2.wait()
        subprocess.run(['rm', 'test_create_microservice.py.test_files'])
        subprocess.run(['rm', '-rf', str(pathlib.Path(self.services, f'svc_{self.service_name}'))])

    def _create_new_service(self):
        script_dir = pathlib.Path(self.services, 'scripts/create_microservice').resolve(strict=True)
        template = pathlib.Path(script_dir, 'templates/mmm.tar.gz').resolve(strict=True)
        lookups = pathlib.Path(script_dir, 'for_tests/lookups_bp.json').resolve(strict=True)
        self.lookups = lookups
        config = pathlib.Path(script_dir, 'config.yaml').resolve(strict=True)

        command = [str(self.interpreter), str(self.script_location),
                   '--name', self.service_name,
                   '--template', str(template),
                   '--config', str(config),
                   '--test_mode']
        if self.with_lookups:
            command.append('--lookups')
            command.append(str(lookups))
        result = subprocess.run(command)
        result.check_returncode()

    @classmethod
    def setUpClass(cls) -> None:
        _ = get_sed_module()

        script_dir = pathlib.Path(cls.services, 'scripts/create_microservice').resolve(strict=True)
        config = pathlib.Path(script_dir, 'config.yaml').resolve(strict=True)
        cls.config = read_yaml_config(config_path=config)

    def setUp(self) -> None:
        self._create_new_service()

    def tearDown(self) -> None:
        self._delete_temp_files()
        pass

    def test_create_service(self):
        svc = pathlib.Path(self.services, f'svc_{self.service_name}')
        self.assertTrue(svc.is_dir())

    def test_db_yaml(self):
        db_yaml_name = str(pathlib.Path(self.services, self.config['directories']['db_yaml']['target']))
        db_yaml_test_name = create_test_name(db_yaml_name)
        db_yaml_test_file = pathlib.Path(db_yaml_test_name).resolve()
        db_yaml_file = pathlib.Path(db_yaml_name).resolve()

        self.assertTrue(db_yaml_test_file.is_file())

        with db_yaml_test_file.open() as tf, db_yaml_file.open() as of:
            test_file = tf.read()
            orig_file = of.read()

            # check db
            self.assertTrue(0 == orig_file.count(f'db_{self.service_name}:'))
            self.assertTrue(1 == test_file.count(f'db_{self.service_name}:'))
            self.assertTrue(1 == test_file.count('# {{ db_env }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}'))

            # check conn
            self.assertTrue(0 == orig_file.count(f'conn_{self.service_name}:'))
            self.assertTrue(1 == test_file.count(f'conn_{self.service_name}:'))
            self.assertTrue(1 == test_file.count('# {{ db_connection }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}'))

            # check models
            self.assertTrue(0 == orig_file.count(f"default_connection: 'conn_{self.service_name}'"))
            self.assertTrue(1 == test_file.count(f"default_connection: 'conn_{self.service_name}'"))
            self.assertTrue(1 == test_file.count('# {{ db_models }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}'))

    def test_services_yaml(self):
        services_yaml_name = str(pathlib.Path(self.services, self.config['directories']['services_yaml']['target']))
        services_yaml_test_name = create_test_name(services_yaml_name)
        services_yaml_test_file = pathlib.Path(services_yaml_test_name).resolve()
        services_yaml_file = pathlib.Path(services_yaml_name).resolve()

        self.assertTrue(services_yaml_test_file.is_file())

        with services_yaml_test_file.open() as tf, services_yaml_file.open() as of:
            test_file = tf.read()
            orig_file = of.read()

            self.assertTrue(0 == orig_file.count(f'prefix: ${{API_PREFIX}}/{self.service_name}'))
            self.assertTrue(1 == test_file.count(f'prefix: ${{API_PREFIX}}/{self.service_name}'))
            self.assertTrue(1 == test_file.count('# {{ new_service }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}'))

    def test_env(self):
        env_name = str(pathlib.Path(self.services, self.config['directories']['env']['target']))
        env_test_name = create_test_name(env_name)
        env_test_file = pathlib.Path(env_test_name).resolve()
        env_file = pathlib.Path(env_name).resolve()

        self.assertTrue(env_test_file.is_file())

        with env_test_file.open() as tf, env_file.open() as of:
            test_file = tf.read()
            orig_file = of.read()

            self.assertTrue(0 == orig_file.count(f'DB_{self.service_name.upper()}="${{installation_name}}_{self.service_name}"'))
            self.assertTrue(1 == orig_file.count('# {{ env_var }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}'))
            self.assertTrue(1 == test_file.count(f'DB_{self.service_name.upper()}="${{installation_name}}_{self.service_name}"'))
            self.assertTrue(1 == test_file.count('# {{ env_var }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}'))

    def test_ipc(self):
        if self.with_lookups:
            ipc_name = str(pathlib.Path(self.services,
                                        self.config['directories']['ipc']['target'].replace('SERVICE_NAME', self.service_name)))
            ipc_file = pathlib.Path(ipc_name).resolve()

            self.assertTrue(ipc_file.is_file())

    def test_cache(self):
        if self.with_lookups:
            cache_name = str(pathlib.Path(self.services, self.config['directories']['cache']['target']))
            cache_test_name = create_test_name(cache_name)
            cache_test_file = pathlib.Path(cache_test_name).resolve()
            cache_file = pathlib.Path(cache_name).resolve()

            self.assertTrue(cache_test_file.is_file())

            with cache_test_file.open() as tf, cache_file.open() as of:
                test_file = tf.read()
                orig_file = of.read()

                self.assertEqual(0, orig_file.count(f'import tshared.ipc.{self.service_name} as ipc_{self.service_name}'))
                self.assertEqual(1, test_file.count(f'import tshared.ipc.{self.service_name} as ipc_{self.service_name}'))
                self.assertEqual(1, test_file.count('# {{ import_ipc }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}'))

    def test_models_lookups(self):
        if self.with_lookups:
            models_name = str(
                pathlib.Path(self.services,
                             self.config['directories']['models_lookups']['target'].replace('SERVICE_NAME', self.service_name)))
            models_file = pathlib.Path(models_name).resolve()

            self.assertTrue(models_file.is_file())

    def test_api_lookups(self):
        if self.with_lookups:
            with (self.lookups.open() as il, pathlib.Path(self.services, f'svc_{self.service_name}', 'init/lookups.json').open() as ol):
                il_json_keys = set(json.load(il))
                ol_json_keys = set(json.load(ol))
                self.assertEqual(il_json_keys, ol_json_keys)

    def test_test_integration(self):
        test_path = pathlib.Path(self.services, 'tests_integration', f'test_{self.service_name}.py')
        self.assertTrue(test_path.is_file())

    def test_shared_test(self):
        shared_test_name = str(pathlib.Path(self.services, self.config['directories']['shared_test']['target']))
        shared_test_test_name = create_test_name(shared_test_name)
        shared_test_test_file = pathlib.Path(shared_test_test_name).resolve()
        shared_test_file = pathlib.Path(shared_test_name).resolve()

        self.assertTrue(shared_test_test_file.is_file())

        with shared_test_test_file.open() as tf, shared_test_file.open() as of:
            test_file = tf.read()
            orig_file = of.read()

            # init func
            func_signature = f'def initialize_lookups_svc_{self.service_name}(self)'
            func_placeholder = '# {{ function_body }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}'
            self.assertTrue(0 == orig_file.count(func_signature))
            self.assertTrue(1 == orig_file.count(func_placeholder))
            self.assertTrue(1 == test_file.count(func_signature))
            self.assertTrue(1 == test_file.count(func_placeholder))

            # init func call
            call_function = f'self.initialize_lookups_svc_{self.service_name}()'
            call_placeholder = '# {{ function_call }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}'
            self.assertTrue(0 == orig_file.count(call_function))
            self.assertTrue(1 == orig_file.count(call_placeholder))
            self.assertTrue(1 == test_file.count(call_function))
            self.assertTrue(1 == test_file.count(call_placeholder))


class TestAddLookupToExitedServiceWithLookups(unittest.TestCase):
    sources = pathlib.Path(pathlib.Path.cwd(), '../..').resolve()
    interpreter = get_python_interpreter_path()
    services = pathlib.Path(sources, 'src').resolve()
    script_location = pathlib.Path(pathlib.Path.cwd().parent,
                                   'scripts/create_microservice/create_microservice.py'
                                   ).resolve(strict=True)
    service_name = 'qwerty'
    with_lookups = True
    config_dict: dict = None
    config = 'config.yaml'
    lookups = None
    lookups_additional = None
    template = None

    @classmethod
    def _delete_temp_files(cls):
        sed = get_sed_module()

        r = subprocess.run([sed, '-i', f"s/SERVICE_NAME/{cls.service_name}/g", 'test_create_microservice.py.test_files'])
        r.check_returncode()
        p1 = subprocess.Popen(["cat", "test_create_microservice.py.test_files"], stdout=subprocess.PIPE)
        p2 = subprocess.Popen(["xargs", "-n", "1", "rm", "-f"], stdin=p1.stdout, stdout=subprocess.PIPE)
        p1.stdout.close()
        _ = p2.communicate()[0]
        p1.wait()
        p2.wait()
        subprocess.run(['rm', 'test_create_microservice.py.test_files'])
        subprocess.run(['rm', '-rf', str(pathlib.Path(cls.services, f'svc_{cls.service_name}'))])

    def __create_new_service(self, lookups):
        script_dir = pathlib.Path(self.services, 'scripts/create_microservice').resolve(strict=True)
        config = pathlib.Path(script_dir, 'config.yaml').resolve(strict=True)
        command = [str(self.interpreter), str(self.script_location),
                   '--name', self.service_name,
                   '--template', str(self.template),
                   '--config', str(config),
                   '--test_mode']
        if self.with_lookups:
            command.append('--lookups')
            command.append(str(lookups))
        result = subprocess.run(command)
        result.check_returncode()

    def _create_new_service(self):
        self.__create_new_service(lookups=self.lookups)

    def _add_lookups(self):
        self.__create_new_service(lookups=self.lookups_additional)

    @classmethod
    def setUpClass(cls) -> None:
        _ = get_sed_module()

        script_dir = pathlib.Path(cls.services, 'scripts/create_microservice').resolve(strict=True)
        config = pathlib.Path(script_dir, 'config.yaml').resolve(strict=True)
        cls.config_dict = read_yaml_config(config_path=config)
        cls.lookups = pathlib.Path(script_dir, 'for_tests/lookups_bp.json').resolve(strict=True)
        cls.lookups_additional = pathlib.Path(script_dir, 'for_tests/lookups_bp_additional.json').resolve(strict=True)
        cls.template = pathlib.Path(cls.services, 'scripts/create_microservice/templates/mmm.tar.gz').resolve(strict=True)

    @staticmethod
    def _get_json_keys(json_file: pathlib.Path) -> set:
        with json_file.open() as f:
            return set(json.load(f))

    def setUp(self) -> None:
        self._create_new_service()

    def tearDown(self) -> None:
        self._delete_temp_files()

    def test_empty(self):
        # print(self._get_json_keys(self.lookups))
        # print(self._get_json_keys(self.lookups_additional))
        pass

    def test_cache(self):
        cache_name = str(pathlib.Path(self.services, self.config_dict['directories']['cache']['target']))
        cache_test_name = create_test_name(cache_name)
        cache_test_file = pathlib.Path(cache_test_name).resolve()

        self.assertTrue(cache_test_file.is_file())

        org_lk = self._get_json_keys(self.lookups)
        add_lk = self._get_json_keys(self.lookups_additional)

        with cache_test_file.open() as tf:
            test_file = tf.read()

            self.assertTrue(1 == test_file.count(f'import tshared.ipc.{self.service_name} as ipc_{self.service_name}'))
            self.assertTrue(1 == test_file.count('# {{ import_ipc }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}'))
            self.assertTrue(1 == test_file.count('# {{ lookup }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}'))

            for key in org_lk:
                s = f'class Lookup{self.service_name.capitalize()}{from_snake_to_camel_case(key)}(Lookup):'
                self.assertTrue(1 == test_file.count(s))
            for key in add_lk:
                s = f'class Lookup{self.service_name.capitalize()}{from_snake_to_camel_case(key)}(Lookup):'
                self.assertTrue(0 == test_file.count(s))    # TEST CASE

        self._add_lookups()

        with cache_test_file.open() as tf:
            test_file = tf.read()

            self.assertTrue(1 == test_file.count(f'import tshared.ipc.{self.service_name} as ipc_{self.service_name}'))
            self.assertTrue(1 == test_file.count('# {{ import_ipc }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}'))
            self.assertTrue(1 == test_file.count('# {{ lookup }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}'))

            for key in org_lk:
                s = f'class Lookup{self.service_name.capitalize()}{from_snake_to_camel_case(key)}(Lookup):'
                self.assertTrue(1 == test_file.count(s))
            for key in add_lk:
                s = f'class Lookup{self.service_name.capitalize()}{from_snake_to_camel_case(key)}(Lookup):'
                self.assertTrue(1 == test_file.count(s))    # TEST CASE

    def test_models_lookups(self):
        models_name = str(
            pathlib.Path(self.services,
                         self.config_dict['directories']['models_lookups']['target'].replace('SERVICE_NAME', self.service_name)))
        models_file = pathlib.Path(models_name).resolve()

        self.assertTrue(models_file.is_file())

        org_lk = self._get_json_keys(self.lookups)
        add_lk = self._get_json_keys(self.lookups_additional)

        with models_file.open() as tf:
            test_file = tf.read()

            self.assertTrue(1 == test_file.count('# {{ lookup_model }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}'))

            for key in org_lk:
                s = f'class Lookup{from_snake_to_camel_case(key)}(Model, base_models.BaseModelLookup):'
                self.assertTrue(1 == test_file.count(s))
            for key in add_lk:
                s = f'class Lookup{from_snake_to_camel_case(key)}(Model, base_models.BaseModelLookup):'
                self.assertTrue(0 == test_file.count(s))    # TEST CASE

        self._add_lookups()

        with models_file.open() as tf:
            test_file = tf.read()

            self.assertTrue(1 == test_file.count('# {{ lookup_model }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}'))

            for key in org_lk:
                s = f'class Lookup{from_snake_to_camel_case(key)}(Model, base_models.BaseModelLookup):'
                self.assertTrue(1 == test_file.count(s))
            for key in add_lk:
                s = f'class Lookup{from_snake_to_camel_case(key)}(Model, base_models.BaseModelLookup):'
                self.assertTrue(1 == test_file.count(s))    # TEST CASE

    def test_api_lookups(self):
        org_lk = self._get_json_keys(self.lookups)
        add_lk = self._get_json_keys(self.lookups_additional)

        with pathlib.Path(self.services, f'svc_{self.service_name}/{self.service_name}/api/lookups.py').open() as ol:
            test_file = ol.read()

            for key in org_lk:
                s = f"'{key}': {{'model': models.Lookup{from_snake_to_camel_case(key)}, 'translations': models.TranslationLookup{from_snake_to_camel_case(key)}}},"
                self.assertTrue(1 == test_file.count(s))
            for key in add_lk:
                s = f"'{key}': {{'model': models.Lookup{from_snake_to_camel_case(key)}, 'translations': models.TranslationLookup{from_snake_to_camel_case(key)}}},"
                self.assertTrue(0 == test_file.count(s))

        self._add_lookups()

        with pathlib.Path(self.services, f'svc_{self.service_name}', 'init/lookups.json').open() as jl:
            ol_json_keys = set(json.load(jl))
            self.assertEqual(ol_json_keys, org_lk | add_lk)

        with pathlib.Path(self.services,
                          f'svc_{self.service_name}/{self.service_name}/api/lookups.py').open() as nl:
            test_file = nl.read()

            for key in org_lk:
                s = f"'{key}': {{'model': models.Lookup{from_snake_to_camel_case(key)}, 'translations': models.TranslationLookup{from_snake_to_camel_case(key)}}},"
                self.assertTrue(1 == test_file.count(s))
            for key in add_lk:
                s = f"'{key}': {{'model': models.Lookup{from_snake_to_camel_case(key)}, 'translations': models.TranslationLookup{from_snake_to_camel_case(key)}}},"
                self.assertTrue(1 == test_file.count(s))

    def test_test_integration(self):
        org_lk = self._get_json_keys(self.lookups)
        add_lk = self._get_json_keys(self.lookups_additional)

        with pathlib.Path(self.services, f'tests_integration/test_{self.service_name}.py').open() as ol:
            test_file = ol.read()

            for key in org_lk:
                s = f'"{key}",'
                self.assertEqual(1, test_file.count(s))
            for key in add_lk:
                s = f'"{key}",'
                self.assertEqual(0, test_file.count(s))

        self._add_lookups()

        with pathlib.Path(self.services, f'tests_integration/test_{self.service_name}.py').open() as nl:
            test_file = nl.read()

            for key in org_lk:
                s = f'"{key}",'
                self.assertEqual(1, test_file.count(s))
            for key in add_lk:
                s = f'"{key}",'
                self.assertEqual(1, test_file.count(s))

    def test_shared_test(self):
        shared_test_name = str(pathlib.Path(self.services, self.config_dict['directories']['shared_test']['target']))
        shared_test_test_name = create_test_name(shared_test_name)
        shared_test_test_file = pathlib.Path(shared_test_test_name).resolve()

        org_lk = self._get_json_keys(self.lookups)
        add_lk = self._get_json_keys(self.lookups_additional)

        self.assertTrue(shared_test_test_file.is_file())

        with shared_test_test_file.open() as tf:
            test_file = tf.read()

            # init func
            func_signature = f'def initialize_lookups_svc_{self.service_name}(self)'
            func_placeholder = '# {{ function_body }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}'
            self.assertTrue(1 == test_file.count(func_signature))
            self.assertTrue(1 == test_file.count(func_placeholder))

            # init func call
            call_function = f'self.initialize_lookups_svc_{self.service_name}()'
            call_placeholder = '# {{ function_call }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}'
            self.assertTrue(1 == test_file.count(call_function))
            self.assertTrue(1 == test_file.count(call_placeholder))

            for key in org_lk:
                s = f"self.api(self.token, 'GET', '/{self.service_name}/lookups/{key}?index_by=code')['items']"
                self.assertEqual(1, test_file.count(s))
            for key in add_lk:
                s = f"self.api(self.token, 'GET', '/{self.service_name}/lookups/{key}?index_by=code')['items']"
                self.assertEqual(0, test_file.count(s))

        self._add_lookups()

        with shared_test_test_file.open() as nf:
            test_file = nf.read()

            # init func
            func_signature = f'def initialize_lookups_svc_{self.service_name}(self)'
            func_placeholder = '# {{ function_body }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}'
            self.assertTrue(1 == test_file.count(func_signature))
            self.assertTrue(1 == test_file.count(func_placeholder))

            # init func call
            call_function = f'self.initialize_lookups_svc_{self.service_name}()'
            call_placeholder = '# {{ function_call }}{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}'
            self.assertTrue(1 == test_file.count(call_function))
            self.assertTrue(1 == test_file.count(call_placeholder))

            for key in org_lk:
                s = f"self.api(self.token, 'GET', '/{self.service_name}/lookups/{key}?index_by=code')['items']"
                self.assertEqual(1, test_file.count(s))
            for key in add_lk:
                s = f"self.api(self.token, 'GET', '/{self.service_name}/lookups/{key}?index_by=code')['items']"
                self.assertEqual(1, test_file.count(s))
