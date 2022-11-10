from jinja2 import Environment, FileSystemLoader, select_autoescape
import pathlib

from utils import prepare_for_template, is_string_in_file, get_template_variable_indent


def template_shared_test_function(templates_dir, service_name):
    lookup = f'# {{{{ lookup_get_{service_name} }}}}{{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}}'
    template_path = pathlib.Path(templates_dir, 'test_init_function.jinja2')

    env = Environment(
        loader=FileSystemLoader(template_path.parent),
        autoescape=select_autoescape()
    )
    template = env.get_template(template_path.name)
    return template.render(lookup=lookup, service_name=service_name)


def template_shared_test_function_call(templates_dir, service_name):
    template_path = pathlib.Path(templates_dir, 'test_init_function_call.jinja2')

    env = Environment(
        loader=FileSystemLoader(template_path.parent),
        autoescape=select_autoescape()
    )
    template = env.get_template(template_path.name)
    return template.render(service_name=service_name)


def add_init_function(service_name: str, template_file: pathlib.Path, target_file: pathlib.Path = None):
    d = 'DELETE'

    function_body = template_shared_test_function(templates_dir=template_file.parent,
                                                  service_name=service_name)
    function_body = prepare_for_template(code_string=function_body,
                                         var_name='function_body',
                                         del_placeholder=d,
                                         indent=get_template_variable_indent('function_body', target_file))
    function_call = template_shared_test_function_call(templates_dir=template_file.parent,
                                                       service_name=service_name)
    function_call = prepare_for_template(code_string=function_call,
                                         var_name='function_call',
                                         del_placeholder=d,
                                         indent=get_template_variable_indent('function_call', target_file),
                                         template_sep=1)

    with target_file.open() as c:
        init_functions_get_vars = {x.strip().split()[2]: d + x.strip()
                                   for x in c.readlines() if x.find('lookup_get_') != -1}

    env = Environment(
        loader=FileSystemLoader(target_file.parent),
        autoescape=select_autoescape()
    )
    template = env.get_template(target_file.name)
    result = template.render(function_call=function_call,
                             function_body=function_body,
                             **init_functions_get_vars).replace(f'# {d}', '')

    with target_file.open('w') as f:
        f.write(result)


def add_lookup_get(service_name: str, lookup_name: str, template_path: pathlib.Path, target_file: pathlib.Path):
    lookup_template = pathlib.Path(template_path, 'test_init_function_lookup_get.jinja2')
    d = 'DELETE'

    with target_file.open() as c:
        template_variables = {line.strip().split()[2]: line.strip().lstrip('# ')
                              for line in c.readlines() if line.find('}}{') != -1}

    env = Environment(
        loader=FileSystemLoader(lookup_template.parent),
        autoescape=select_autoescape()
    )
    template = env.get_template(lookup_template.name)
    lookup_get_line = template.render(service_name=service_name, lookup_name=lookup_name)
    template_variables[f'lookup_get_{service_name}'] = prepare_for_template(code_string=lookup_get_line,
                                                                            var_name=f'lookup_get_{service_name}',
                                                                            del_placeholder=d,
                                                                            indent=8,
                                                                            template_sep=1
                                                                            )
    env = Environment(
        loader=FileSystemLoader(target_file.parent),
        autoescape=select_autoescape()
    )
    template = env.get_template(target_file.name)
    result = template.render(**template_variables).replace(f'# {d}', '')
    with target_file.open('w') as f:
        f.write(result)


def template_shared_test(service_name: str, lookup_name: str,
                         template_path: pathlib.Path, target_file: pathlib.Path):
    if not is_string_in_file(f'initialize_lookups_svc_{service_name}', target_file):
        add_init_function(service_name=service_name,
                          template_file=pathlib.Path(template_path, 'test_init_function.jinja2'),
                          target_file=target_file)
    if not is_string_in_file(f'self.lookup_{service_name}_{lookup_name}', target_file):
        add_lookup_get(service_name=service_name,
                       lookup_name=lookup_name,
                       template_path=template_path,
                       target_file=target_file)
