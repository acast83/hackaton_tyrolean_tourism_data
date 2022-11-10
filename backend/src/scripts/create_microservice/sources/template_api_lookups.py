from jinja2 import Environment, FileSystemLoader, select_autoescape
import pathlib

from utils import from_snake_to_camel_case, prepare_for_template, is_string_in_file


def create_tbl2model(lookup_name: str, template_path: pathlib.Path):
    env = Environment(
        loader=FileSystemLoader(template_path),
        autoescape=select_autoescape()
    )
    template = env.get_template('tbl2model.jinja2')
    return template.render(lookup_name=lookup_name,
                           lookup_name_camel_case=from_snake_to_camel_case(lookup_name),
                           )


def add_model(service_name, lookup_name, target_file: pathlib.Path, template_path: pathlib.Path):
    d = 'DELETE'

    if not target_file.is_file():
        env = Environment(
            loader=FileSystemLoader(template_path),
            autoescape=select_autoescape())
        template = env.get_template('lookups.py.jinja2')
    else:
        env = Environment(
            loader=FileSystemLoader(target_file.parent),
            autoescape=select_autoescape())
        template = env.get_template(target_file.name)

        if is_string_in_file(string=lookup_name, file=target_file):
            return

    tbl2model = prepare_for_template(code_string=create_tbl2model(lookup_name=lookup_name, template_path=template_path),
                                     var_name='tbl2model', del_placeholder=d, indent=4, template_sep=1)

    result = template.render(tbl2model=tbl2model.strip(),
                             service_name=service_name,
                             service_name_camel_case=from_snake_to_camel_case(service_name)
                             ).replace(f'# {d}', '')
    with target_file.open('w') as f:
        f.write(result)


def template_api_lookups(service_name, lookup_name,
                         template_path: pathlib.Path, target_file: pathlib.Path):

    add_model(service_name=service_name,
              lookup_name=lookup_name,
              target_file=target_file,
              template_path=template_path
              )
