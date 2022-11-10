from jinja2 import Environment, FileSystemLoader, select_autoescape
import pathlib

from utils import prepare_for_template, get_template_variable_indent, is_string_in_file


def get_db_variable(variable_name: str, service_name: str,
                    template_path: pathlib.Path, target_file: pathlib.Path):
    d = 'DELETE'

    env = Environment(
        loader=FileSystemLoader(template_path),
        autoescape=select_autoescape()
    )
    template = env.get_template(f'{variable_name}.jinja2')

    result = template.render(service_name=service_name)
    result = prepare_for_template(code_string=result, var_name=variable_name, del_placeholder=d,
                                  indent=get_template_variable_indent(variable_name, template_file=target_file))
    return result


def get_db_env(service_name: str, template_path: pathlib.Path, target_file: pathlib.Path):
    return get_db_variable('db_env', service_name, template_path, target_file)


def get_db_conn(service_name: str, template_path: pathlib.Path, target_file: pathlib.Path):
    return get_db_variable('db_connection', service_name, template_path, target_file)


def get_db_model(service_name: str, template_path: pathlib.Path, target_file: pathlib.Path):
    return get_db_variable('db_models', service_name, template_path, target_file)


def template_db_yaml(service_name: str, template_path: pathlib.Path, target_file: pathlib.Path):
    d = 'DELETE'

    env = Environment(
        loader=FileSystemLoader(target_file.parent),
        autoescape=select_autoescape()
    )
    template = env.get_template(target_file.name)

    result = template.render(
                 db_env=get_db_env(service_name, template_path, target_file),
                 db_connection=get_db_conn(service_name, template_path, target_file),
                 db_models=get_db_model(service_name, template_path, target_file),
             ).replace(f'# {d}', '')

    if not is_string_in_file(f'conn_{service_name}', target_file):
        with target_file.open('w') as f:
            f.write(result)
