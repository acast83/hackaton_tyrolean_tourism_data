import pathlib
import json
from jinja2 import Environment, FileSystemLoader, select_autoescape

from sources.template_ipc import template_ipc
from sources.template_cache import template_cache
from sources.template_shared_test import template_shared_test
from sources.template_models_lookup import template_models_lookups
from sources.template_api_lookups import template_api_lookups
from sources.template_tests_integration import template_test_integration
from utils import is_string_in_file


def add_lookup_import_to_init(service_name: str, services_location: pathlib.Path):
    init_file = pathlib.Path(services_location,
                             f'svc_{service_name}/{service_name}/api/__init__.py'
                             ).resolve(strict=True)
    d = 'DELETE'

    if not is_string_in_file(string='.lookups',
                             file=init_file):
        env = Environment(
            loader=FileSystemLoader(init_file.parent),
            autoescape=select_autoescape()
        )
        template = env.get_template(init_file.name)
        result = template.render(lookup_import=f'{d}from .lookups import *').replace(f'# {d}', '')
        with init_file.open('w') as f:
            f.write(result)


def process_lookups(service_name: str, lookups: pathlib.Path, dirs: dict, services_location: pathlib.Path):
    add_lookup_import_to_init(service_name=service_name, services_location=services_location)

    with lookups.open() as j:
        lookups = json.load(j)

    exists_lookups = pathlib.Path(services_location, f'svc_{service_name}/init/lookups.json')
    with exists_lookups.open() as lj:
        plookups = json.load(lj)
        lookups = {k: v for k, v in lookups.items() if k not in plookups}

    with exists_lookups.open('w') as nl:
        nl.write(json.dumps({**plookups, **lookups}, indent=2))

    for lookup_name, lookup in lookups.items():
        template_ipc(service_name=service_name, lookup_name=lookup_name,
                     template_path=dirs['ipc']['template'],
                     target_file=dirs['ipc']['target'])
        template_cache(service_name=service_name, lookup_name=lookup_name,
                       template_path=dirs['cache']['template'],
                       target_path=dirs['cache']['target'])
        template_shared_test(service_name=service_name, lookup_name=lookup_name,
                             template_path=dirs['shared_test']['template'],
                             target_file=dirs['shared_test']['target'])
        template_models_lookups(service_name=service_name,
                                lookup_name=lookup_name, lookup=lookup,
                                template_path=dirs['models_lookups']['template'],
                                target_file=dirs['models_lookups']['target'])
        template_api_lookups(service_name=service_name, lookup_name=lookup_name,
                             template_path=dirs['api_lookups']['template'],
                             target_file=dirs['api_lookups']['target'])
        template_test_integration(service_name=service_name, lookup_name=lookup_name,
                                  template_path=dirs['test_integration']['template'],
                                  target_file=dirs['test_integration']['target'])

