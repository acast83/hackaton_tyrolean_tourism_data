import sys
import pathlib
import string
from itertools import cycle


__all__ = ["define_order_of_import"]


"""
    Linux shell variables can contain only
        letters (a to z or A to Z),
        numbers (0 to 9) or
        the underscore character (_)
"""
ALPHA = string.ascii_letters + string.digits + '_'


def get_key_value(line: str) -> tuple:
    eq_index = line.find('=')
    if eq_index == -1:
        eq_index = None

    key = line[:eq_index]
    if eq_index:
        value = line[eq_index + 1:]
    else:
        value = ''

    return key, value


def find_usages(source: dict, target: dict) -> list:
    result = list()

    for var in source.keys():
        for key, value in target.items():
            i = value.find(var)
            if (i > 0 and value[i - 1] == '$') or (i > 1 and value[i - 2] == '$'):
                result.append(key)
    return result


def find_all_usages(paths: tuple = None) -> dict:
    files_and_variables = {}
    result = {}

    for path in paths:
        files_and_variables = {**files_and_variables, **get_variables(path=path)}

    for source_name, source_vars in files_and_variables.items():
        for target_name, target_vars in files_and_variables.items():
            result[target_name] = result.get(target_name, {})
            if source_name == target_name:
                continue
            result[target_name][source_name] = find_usages(source_vars, target_vars)

    return result


def get_variables_from_file(file: pathlib.Path) -> dict:
    # todo multiline variables
    result = {}

    with file.open() as f:
        for line in f:
            key, value = get_key_value(line.strip())
            result[key] = value
    return result


def get_variables(path: str):
    p = pathlib.Path(path).resolve(strict=True)
    if p.is_file() or p.is_dir():
        envs = pathlib.Path(path).resolve(strict=True)
    else:
        raise FileNotFoundError(path)

    files = {}
    if envs.is_dir():
        for e in envs.glob("*.env*"):
            files[str(e)] = get_variables_from_file(e)
    elif envs.is_file():
        files[str(envs)] = get_variables_from_file(envs)
    else:
        raise Exception('Unexpected.')

    return files


def define_order_of_import(paths: tuple) -> list:
    usages: dict = find_all_usages(paths=paths)
    result = {k: [k for k, v in v.items() if v] for k, v in usages.items()}

    order = []

    # todo is range(len(result) ** 3) enough to resolve all references?
    for _, file in zip(range(len(result) ** 3), cycle(sorted(result.keys()))):
        if file in result:
            if not result[file]:
                order.append(file)
                result.pop(file)
            else:
                temp = []
                for d in result[file]:
                    if d not in order:
                        temp.append(d)
                result[file] = temp
        if not result:
            break
    if result:
        raise Exception(f'You have circular dependencies in your env files:\n'
                        f'{f"{chr(10)}".join([chr(9) + str(k) + ": " + str(v) for k, v in result.items()])}')

    return order


def main(*args):
    o = define_order_of_import(paths=args)
    print(" ".join(o))


if __name__ == "__main__":
    # todo multiline env variables

    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            file_path = pathlib.Path(arg).resolve()
            if not file_path.is_file() and not file_path.is_dir():
                print(f"File {file_path} does not exists.", file=sys.stderr)
                exit(1)
        main(*sys.argv[1:])
    else:
        print(f"Please supply env files.", file=sys.stderr)
        exit(2)
