from jinja2 import Environment, FileSystemLoader, select_autoescape
import pathlib

from utils import is_string_in_file, prepare_for_template


def add_ipc_function(service_name: str, lookup_name: str, template_path: pathlib.Path, target_path: pathlib.Path):
    d = "DELETE"

    function_env = Environment(loader=FileSystemLoader(template_path), autoescape=select_autoescape())
    function_template = function_env.get_template('ipc.service_name.function.jinja2')
    function = function_template.render(service_name=service_name, lookup_name=lookup_name)
    function = prepare_for_template(code_string=function, var_name='ipc_function', del_placeholder=d, template_sep=3)

    target_env = Environment(loader=FileSystemLoader(target_path.parent), autoescape=select_autoescape())
    template = target_env.get_template(target_path.name)
    result = template.render(ipc_function=function).replace(f'# {d}', '')

    with target_path.open('w') as f:
        f.write(result)


def add_ipc_file(service_name: str, template_path: pathlib.Path, target_path: pathlib.Path = None):
    if target_path is None:
        target_path = pathlib.Path(template_path, f'{service_name}.py')

    env = Environment(
        loader=FileSystemLoader(template_path),
        autoescape=select_autoescape()
    )
    template = env.get_template('ipc.service_name.py.jinja2')

    with target_path.open('w') as f:
        result = template.render(ipc_function='{{ ipc_function }}')
        f.write(result)


def template_ipc(service_name: str, lookup_name: str,
                 template_path: pathlib.Path, target_file: pathlib.Path):

    if not target_file.is_file():
        add_ipc_file(service_name=service_name, template_path=template_path, target_path=target_file)

    if not is_string_in_file(string=f'lookup_{service_name}_{lookup_name}', file=target_file):
        add_ipc_function(service_name=service_name, lookup_name=lookup_name,
                         template_path=template_path, target_path=target_file)
