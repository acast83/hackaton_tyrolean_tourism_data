import io
import configparser
import pathlib
import os
import sys
import typing
from typing import Union
import yaml

import dotenv

try:
    from scripts.define_env_export_order import define_order_of_import
except ModuleNotFoundError:
    from define_env_export_order import define_order_of_import


__all__ = [
    "load_env_variables",
    "set_env",
]


def print_env_variables(_vars: list):
    def print_env(name):
        print(f"||{os.getenv(name)}||")
    
    for _var in _vars:
        print_env(_var)
    print('-----')


def read_config(file, sections: Union[tuple, str, None] = tuple()) -> list:
    file = pathlib.Path(file).resolve(strict=True)
    if isinstance(sections, str):
        sections = [sections]
    elif sections is None:
        sections = tuple()
    
    if file.suffix in ['.yml', '.yaml']:
        with file.open() as f:
            config = yaml.load(f, Loader=yaml.FullLoader)

        result: list = config['environment']['common']

        for section in sections:
            try:
                if isinstance(config['environment'][section], list):
                    result += config['environment'][section]
                elif isinstance(config['environment'][section], str):
                    result.append(config['environment'][section])
            except KeyError as ke:
                raise KeyError(f'{ke}. In config file {file}') from ke

        return result

    else:
        raise ValueError(f'Unknown config file extension: <{file.suffix}>.')


def load_env_variables(*,
                       from_config_file: Union[str, pathlib.Path, None] = None,
                       config_file_sections: Union[str, list, tuple, None] = None,
                       from_env_files: Union[str, list, tuple, None] = None) -> None:
    """
    Looks for env files, end exports variables from those files.
    Also function resolves order of loading env variables.

    Arguments:
        from_config_file: formatted as yaml-file, with 'environment' section
        config_file_sections: section in config file where env files stored
        from_env_files: location of env files (with .env in name) or directory

    Raises:
        FileNotFoundError: if any of env file does not exist.
    """

    config_file = from_config_file
    env_files = from_env_files

    if isinstance(env_files, str):
        env_files = (env_files,)
    elif env_files is None:
        env_files = tuple()

    env_files_list = [*env_files]

    if isinstance(config_file, (str, pathlib.Path)) and pathlib.Path(config_file).is_file():
        env_files_config_file = pathlib.Path(config_file).resolve()

        config: list = read_config(from_config_file, config_file_sections)

        if config:
            env_files_list += [pathlib.Path(env_files_config_file.parent, x).resolve(strict=True)
                               for x in config]

    if env_files_list:
        env_files_ordered = define_order_of_import(tuple(set(env_files_list)))
        env_vars = ''

        for env_file in env_files_ordered:
            with open(env_file) as f:
                env_vars += f.read() + '\n'

        variables_stream = io.StringIO(env_vars)
        dotenv.load_dotenv(stream=variables_stream)

    else:
        raise FileNotFoundError(f"Env files not found in: {pathlib.Path(config_file).resolve()}.\n"
                                f"Env files list: {env_files_list}\n"
                                f"CONFIG_FILE: {config_file}\n"
                                f"ENV_FILES: {env_files}\n"
                                f"CONFIG_FILE_SECTIONS: {config_file_sections}\n"
                                f"MAIN: {__name__}\n"
                                f"SECTION: {config_file_sections}"
                                )


def set_env(*, variables: dict):
    for key, value in variables.items():
        os.environ[key] = value


if __name__ == "__main__":
    vars_to_check = ['FA9', 'FK9', 'TELEGRAM_BOT_NAME', 'DB_SMS']
    print_env_variables(vars_to_check)
    load_env_variables(from_env_files=['../.env'])
    print_env_variables(vars_to_check)

    t = {'REC': "TETE", "HI": "WORLD"}
    vars_to_check = [*t.keys()]
    print_env_variables(vars_to_check)
    set_env(variables=t)
    print_env_variables(vars_to_check)

