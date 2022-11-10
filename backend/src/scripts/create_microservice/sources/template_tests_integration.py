from jinja2 import Environment, FileSystemLoader, select_autoescape
import pathlib

from utils import is_string_in_file, prepare_for_template, get_template_variable_indent, from_snake_to_camel_case


def add_lookup(lookup_name: str, target_file: pathlib.Path):
    d = "DELETE"

    env = Environment(
        loader=FileSystemLoader(target_file.parent),
        autoescape=select_autoescape()
    )
    template = env.get_template(target_file.name)
    result = prepare_for_template(code_string=f'"{lookup_name}",', var_name='lookup_name',
                                  del_placeholder=d,
                                  indent=get_template_variable_indent('lookup_name', target_file),
                                  template_sep=1)
    with target_file.open('w') as f:
        f.write(template.render(lookup_name=result).replace(f'# {d}', ''))


def add_lookup_method(service_name: str, template_path: pathlib.Path, target_file: pathlib.Path):
    d = "DELETE"

    temp_env = Environment(
        loader=FileSystemLoader(template_path),
        autoescape=select_autoescape()
    )
    temp_template = temp_env.get_template('test_tenants_service_name_method.py.jinja2')
    lookup_method = temp_template.render(service_name=service_name,
                                         lookup_name=prepare_for_template(code_string='', var_name='lookup_name',
                                                                          del_placeholder=d,
                                                                          indent=get_template_variable_indent('lookup_name', target_file),
                                                                          template_sep=0),
                                         ).replace(f'# {d}', '')

    env = Environment(
        loader=FileSystemLoader(target_file.parent),
        autoescape=select_autoescape()
    )
    template = env.get_template(target_file.name)
    result_method = prepare_for_template(code_string=lookup_method, var_name='lookup_method',
                                         del_placeholder=d,
                                         indent=get_template_variable_indent('lookup_method', target_file),
                                         template_sep=2)
    result = template.render(lookup_method=result_method).replace(f'# {d}', '')

    with target_file.open('w') as f:
        f.write('\n'.join([x
                           for x in result.split('\n')
                           if -1 == x.find('lookup_method')]))


def add_test_file(service_name: str,
                  template_path: pathlib.Path,
                  target_file: pathlib.Path):
    d = 'DELETE'

    env = Environment(
        loader=FileSystemLoader(template_path),
        autoescape=select_autoescape()
    )
    template = env.get_template('test_tenants_service_name.py.jinja2')

    with target_file.open('w') as f:
        result = template.render(service_name=service_name,
                                 service_name_camel_case=from_snake_to_camel_case(service_name),
                                 lookup_method=prepare_for_template(code_string='',
                                                                    var_name='lookup_method',
                                                                    del_placeholder=d,
                                                                    indent=get_template_variable_indent('lookup_method', target_file),
                                                                    template_sep=0
                                                                    ),
                                 ).replace(f'# {d}', '')
        f.write(result)


def template_test_integration(service_name: str, lookup_name: str,
                              template_path: pathlib.Path, target_file: pathlib.Path):
    if not target_file.is_file():
        add_test_file(service_name=service_name, template_path=template_path, target_file=target_file)
    if lookup_name and not is_string_in_file(f'{lookup_name}', target_file):
        if not is_string_in_file('test_lookup_all_lookups', target_file):
            add_lookup_method(service_name=service_name, template_path=template_path, target_file=target_file)
        add_lookup(lookup_name=lookup_name, target_file=target_file)
