import pathlib
import shutil
from utils import from_snake_to_camel_case


def count_lead_spaces(line_):
    return len(line_) - len(line_.lstrip(' '))


#
# PROCESS TEMPLATE BEGIN
#

def rename_files_and_directories(template_name, new_svc_name, script_location: pathlib.Path):
    old_name = f'svc_{template_name}'
    template_path = pathlib.Path(script_location, old_name)

    paths_to_rename = [x for x in template_path.rglob('*') if str(x).find('__pycache__') == -1]
    for i in paths_to_rename:
        if not i.is_dir() and i.is_file() and i.name.find(template_name) != -1:
            new_name = i.name.replace(template_name, new_svc_name)
            i.rename(pathlib.Path(i.parent, new_name))

    for i in paths_to_rename:
        if i.is_dir() and not i.is_file() and i.name.find(template_name) != -1:
            new_name = i.name.replace(template_name, new_svc_name)
            i.rename(pathlib.Path(i.parent, new_name))

    if template_path.is_dir():
        new_path = pathlib.Path(script_location, f'svc_{new_svc_name}')
        template_path.rename(new_path)


def rename_variables_in_string(string, old_name, new_name: str):
    new_names = {
        'var': new_name.lower(),
        'cls': from_snake_to_camel_case(new_name),
        'glb': new_name.upper(),
    }

    template_names = {
        'var': old_name.lower(),
        'cls': from_snake_to_camel_case(old_name),
        'glb': old_name.upper(),
    }

    string = string.replace(template_names['var'], new_names['var'])
    string = string.replace(template_names['cls'], new_names['cls'])
    string = string.replace(template_names['glb'], new_names['glb'])
    return string


def rename_variables_inside_a_file(path, old_name, new_name: str):
    if not path.is_dir() and path.is_file():
        with path.open('r+') as f:
            temp = f.read()

            temp = rename_variables_in_string(temp, old_name, new_name)

            f.seek(0)
            f.write(temp)
            f.truncate()


def rename_variables_inside_files(template_name, new_svc_name: str, script_location: pathlib.Path):
    old_name = f'svc_{template_name}'
    template_path = pathlib.Path(script_location, old_name)

    paths_to_rename = [x for x in template_path.rglob('*') if str(x).find('__pycache__') == -1]
    for path in paths_to_rename:
        rename_variables_inside_a_file(path=path, old_name=template_name, new_name=new_svc_name)


def move_new_service(new_svc_name, script_location: pathlib.Path, services_location: pathlib.Path):
    shutil.move(pathlib.Path(script_location, f'svc_{new_svc_name}'), services_location)


def get_file_name_wo_extension(path: pathlib.Path):
    if isinstance(path, str):
        path = pathlib.Path(path)

    n = path.name
    ext_index = path.name.find('.')
    return n[:ext_index if ext_index != -1 else None]


def process_template(template: pathlib.Path, new_svc_name,
                     services_location: pathlib.Path, script_location: pathlib.Path):

    services_list = [x.name.replace('svc_', '') for x in services_location.glob('svc_*')]

    if new_svc_name not in services_list:
        if template.is_file():
            template_path = template
        else:
            raise FileNotFoundError(f'Template {template} not found.')

        template_name = get_file_name_wo_extension(template_path)

        shutil.unpack_archive(template_path, extract_dir=script_location)

        rename_variables_inside_files(template_name=template_name,
                                      new_svc_name=new_svc_name,
                                      script_location=script_location)
        rename_files_and_directories(template_name=template_name,
                                     new_svc_name=new_svc_name,
                                     script_location=script_location)
        move_new_service(new_svc_name=new_svc_name,
                         script_location=script_location,
                         services_location=services_location)

#
# PROCESS TEMPLATE END
#
