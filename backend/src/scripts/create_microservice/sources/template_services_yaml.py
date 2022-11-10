from jinja2 import Environment, FileSystemLoader, select_autoescape
import pathlib

from utils import is_string_in_file, prepare_for_template, get_template_variable_indent


def calculate_next_port(target_file: pathlib.Path):
    with target_file.open() as f:
        ports = [int(x.split(':')[-1])
                 for x in f.readlines()
                 if x.find('port:') != -1 and x.split(':')[1].strip().isnumeric()]
    return max(ports) + 1


def prepare_new_service(service_name: str, template_path: pathlib.Path, target_file: pathlib.Path):
    d = "DELETE"

    env = Environment(
        loader=FileSystemLoader(template_path),
        autoescape=select_autoescape()
    )
    template = env.get_template('services.jinja2')
    result = template.render(service_name=service_name)
    new_port = calculate_next_port(target_file)
    result = result.replace('PORT_PLACEHOLDER', str(new_port))
    return prepare_for_template(result, 'new_service', del_placeholder=d,
                                indent=get_template_variable_indent('new_service', target_file),
                                )


def template_services_yaml(service_name: str, template_path: pathlib.Path, target_file: pathlib.Path):
    d = "DELETE"

    new_service = prepare_new_service(service_name, template_path, target_file)

    env = Environment(loader=FileSystemLoader(target_file.parent), autoescape=select_autoescape())
    template = env.get_template(target_file.name)

    if not is_string_in_file(string=service_name, file=target_file):
        result = template.render(new_service=new_service).replace(f'# {d}', '')

        with target_file.open('w') as f:
            f.write(result)
