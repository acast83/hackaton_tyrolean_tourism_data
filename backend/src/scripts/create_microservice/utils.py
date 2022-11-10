import typing
import pathlib
import yaml
import shutil


def is_string_in_file(string: str, file: typing.Union[str, pathlib.Path]) -> bool:
    if isinstance(file, str):
        file = pathlib.Path(file)
    elif isinstance(file, pathlib.Path):
        pass
    else:
        raise TypeError(f'is_string_int_file: file '
                        f'should be str or Path but {type(file)} is given.')

    if file.is_file():
        with file.open() as f:
            return f.read().find(string) != -1
    else:
        raise FileNotFoundError(f"is_string_int_file: {file} is not found.")


def create_dir_if_not_exist(path: typing.Union[str, pathlib.Path]):
    if isinstance(path, str):
        path = pathlib.Path(path)

    if not path.is_dir() and path.name.find('.') == -1:
        path.mkdir(parents=True, exist_ok=True)


def from_snake_to_camel_case(string: str):
    return " ".join(["".join([x.capitalize() for x in word.split('_')])
                     for word in string.split()])


def prepare_for_template(code_string,
                         var_name,
                         del_placeholder,
                         indent: int = 0,
                         template_sep: int = 2):
    code_string = '\n'.join([' ' * indent + x if i != 0 else x
                             for i, x in enumerate(code_string.split('\n'))])
    return (del_placeholder
            + code_string
            + '\n' * template_sep
            + f'{" " * indent}# {{{{ {var_name} }}}}{{# TEMPLATE PLACEHOLDER. DO NOT DELETE #}}')


def get_template_variable_indent(variable_name: str, template_file: pathlib.Path) -> int:
    with template_file.open() as f:
        lines = [line
                 for line in f.readlines()
                 if line.find(variable_name) != -1 and line.find('#') != -1]
    if lines:
        return len(lines[0]) - len(lines[0].lstrip())
    return 0


def create_test_name(name: str) -> str:
    split_name = list(pathlib.Path(name).parts)
    file_name = split_name[-1]
    if file_name.find('.') != -1:
        split_name[-1] = (file_name[:file_name.rfind('.')]
                          + '.test'
                          + file_name[file_name.rfind('.'):])
    else:
        split_name[-1] = 'test.' + file_name
    return str(pathlib.Path(*split_name))


def read_yaml_config(config_path: pathlib.Path) -> dict:
    with config_path.open() as y:
        return yaml.load(y, yaml.Loader)


def create_test_files(config: dict):
    dirs = config['directories']
    project_sources = pathlib.Path(
        pathlib.Path(__file__).parent,
        config['services_location']).resolve()
    list_test_files = []

    for template, directories in dirs.items():
        new_name = create_test_name(directories['target'])
        old_path = pathlib.Path(project_sources, directories['target'])
        new_path = pathlib.Path(project_sources, new_name)
        if old_path.is_file():
            if not new_path.is_file():
                shutil.copyfile(old_path, new_path)
            list_test_files.append(str(new_path))
        elif -1 != str(new_path).find('ipc') or -1 != str(new_path).find('tests_integration'):
            list_test_files.append(str(old_path))

        if new_name.find('SERVICE_NAME') == -1:
            directories['target'] = new_name

    with pathlib.Path(project_sources,
                      'tests_integration',
                      'test_create_microservice.py.test_files').open('w') as f:
        f.write("\n".join(list_test_files))

    return dirs


def get_directories(service_name: str, config: dict, is_test_mode: bool):
    if is_test_mode:
        dirs = create_test_files(config=config)
    else:
        dirs = config['directories']

    t = pathlib.Path(pathlib.Path(__file__).parent, config['templates_dir'])
    p = pathlib.Path(__file__).parent.parent
    return {k: {'template': pathlib.Path(p, t, v['template']).resolve(strict=True),
                'target': pathlib.Path(p.parent, v['target'].replace('SERVICE_NAME', service_name)).resolve()}
            for k, v in dirs.items()}


def check_variables_placeholders(dirs: dict, service_name: str, services_location: pathlib.Path) -> bool:
    test = {
        'ipc': {'vars': ['ipc_function']},
        'cache': {'vars': ['import_ipc', 'lookup']},
        'models_lookups': {'vars': ['lookup_model']},
        'api_lookups': {'vars': ['tbl2model']},
        'test_integration': {'vars': ['lookup_name']},
        'shared_test': {'vars': [f'lookup_get_{service_name}', 'function_body', 'function_call']},
    }

    if pathlib.Path(services_location, f'svc_{service_name}').is_dir():
        return True

    for check_item, variables in test.items():
        target_file = pathlib.Path(dirs[check_item]['target'])

        with target_file.open() as c:
            init_functions_get_vars = [x.strip().split()[2]
                                       for x in c.readlines() if x.find('}}{#') != -1]
            test[check_item]['path'] = target_file
            for v in init_functions_get_vars:
                if v in test[check_item]['vars']:
                    _ = test[check_item]['vars'].pop(test[check_item]['vars'].index(v))

    is_not_missing = True
    for key, x in test.items():
        if x['vars']:
            is_not_missing = False
            print('in', x['path'], 'missing: ', x['vars'])

    return is_not_missing


if __name__ == "__main__":
    print(from_snake_to_camel_case('hello_world'))
