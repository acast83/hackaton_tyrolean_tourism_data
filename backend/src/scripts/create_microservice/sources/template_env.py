from jinja2 import Environment, FileSystemLoader, select_autoescape
import pathlib

from utils import is_string_in_file, prepare_for_template, get_template_variable_indent


def prepare_new_env(service_name: str, target_file: pathlib.Path):
    d = "DELETE"

    result = f'DB_{service_name.upper()}="${{installation_name}}_{service_name}"'

    return prepare_for_template(result, 'env_var', del_placeholder=d,
                                indent=get_template_variable_indent('env_var', target_file),
                                template_sep=1
                                )


def template_env(service_name: str, target_file: pathlib.Path):
    d = "DELETE"

    env_var = prepare_new_env(service_name, target_file)

    env = Environment(loader=FileSystemLoader(target_file.parent), autoescape=select_autoescape())
    template = env.get_template(target_file.name)

    if not is_string_in_file(string=service_name, file=target_file):
        result = template.render(env_var=env_var).replace(f'# {d}', '')

        with target_file.open('w') as f:
            f.write(result)
