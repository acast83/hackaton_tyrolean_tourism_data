from jinja2 import Environment, FileSystemLoader, select_autoescape
import pathlib

from utils import from_snake_to_camel_case, is_string_in_file, prepare_for_template


def template_lookup_class(service_name: str, lookup_name: str, template_path: pathlib.Path):
    class_env = Environment(
        loader=FileSystemLoader(template_path),
        autoescape=select_autoescape()
    )
    class_template = class_env.get_template('cache_lookup_class.jinja2')
    class_result = class_template.render(service_name=service_name,
                                         lookup_name=lookup_name,
                                         service_name_camel_case=from_snake_to_camel_case(service_name),
                                         lookup_name_camel_case=from_snake_to_camel_case(lookup_name))
    return class_result


def template_ipc_import(service_name: str, target_path: pathlib.Path):
    d = 'DELETE'

    import_string = f'import tshared.ipc.{service_name} as ipc_{service_name}'
    if not is_string_in_file(string=import_string, file=target_path):
        template_sep = 1
    else:
        import_string = ''
        template_sep = 0
    return prepare_for_template(code_string=import_string, var_name='import_ipc',
                                del_placeholder=d, template_sep=template_sep)


def template_cache(service_name: str, lookup_name: str, template_path: pathlib.Path, target_path: pathlib.Path):
    d = 'DELETE'

    string = f'Lookup{from_snake_to_camel_case(service_name)}{from_snake_to_camel_case(lookup_name)}'

    if not is_string_in_file(string=string, file=target_path):
        class_result = template_lookup_class(service_name, lookup_name, template_path)

        result_env = Environment(
            loader=FileSystemLoader(target_path.parent),
            autoescape=select_autoescape()
        )
        result_template = result_env.get_template(target_path.name)
        result_vars = {
            'import_ipc': template_ipc_import(service_name=service_name, target_path=target_path),
            'lookup': prepare_for_template(code_string=class_result, var_name='lookup',
                                           del_placeholder=d, indent=0, template_sep=3)
        }
        result = result_template.render(**result_vars).replace(f'# {d}', '')
        with target_path.open('w') as t:
            t.write(result)
