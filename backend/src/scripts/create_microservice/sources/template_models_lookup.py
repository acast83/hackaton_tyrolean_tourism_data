from jinja2 import Environment, FileSystemLoader, select_autoescape
import pathlib

from utils import from_snake_to_camel_case, prepare_for_template, is_string_in_file


def template_parent(service_name, lookup_name, lookup, templates_dir):
    """
    {{ service_name }}
    {{ service_name_camel_case }}
    {{ lookup_name }}

    {{ relation }}
    {{ parent_lookup }}
    """
    if lookup and isinstance(lookup, list) and lookup[0].get('parent'):
        lookup_item = lookup[0]['parent']
        relation = lookup_item['relation']
        parent_lookup = lookup_item['lookup']

        template_file = pathlib.Path(templates_dir, 'lookup_parent.py.jinja2')

        env = Environment(
            loader=FileSystemLoader(template_file.parent),
            autoescape=select_autoescape()
        )
        template = env.get_template(template_file.name)
        return '\n    ' + template.render(
            service_name=service_name,
            lookup_name=lookup_name,
            relation=relation,
            parent_lookup=from_snake_to_camel_case(parent_lookup),
        )
    else:
        return ''


def template_models_lookups_model(service_name, lookup_name, lookup, templates_dir):
    template_file = pathlib.Path(templates_dir, 'lookup_model.jinja2')

    env = Environment(
        loader=FileSystemLoader(template_file.parent),
        autoescape=select_autoescape()
    )
    template = env.get_template(template_file.name)
    return template.render(lookup_name=lookup_name,
                           lookup_name_camel_case=from_snake_to_camel_case(lookup_name),
                           service_name=service_name,
                           parent=template_parent(service_name=service_name,
                                                  lookup_name=lookup_name,
                                                  lookup=lookup,
                                                  templates_dir=templates_dir,
                                                  ),
                           )


def template_models_lookups(service_name,
                            lookup_name,
                            lookup,
                            template_path: pathlib.Path,
                            target_file: pathlib.Path
                            ):
    d = 'DELETE'

    model = template_models_lookups_model(service_name=service_name,
                                          lookup_name=lookup_name,
                                          lookup=lookup,
                                          templates_dir=template_path)

    env = Environment(
        loader=FileSystemLoader(target_file.parent),
        autoescape=select_autoescape()
    )
    template = env.get_template(target_file.name)
    model = prepare_for_template(code_string=model, var_name='lookup_model',
                                 del_placeholder=d, indent=0, template_sep=3)
    result = template.render(lookup_model=model).replace(f'# {d}', '')

    if is_string_in_file(lookup_name, target_file):
        return

    with target_file.open('w') as f:
        f.write(result)
