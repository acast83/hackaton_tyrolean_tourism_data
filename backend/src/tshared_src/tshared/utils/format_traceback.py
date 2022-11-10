import functools
import inspect
import pathlib
import traceback
from runpy import run_path
import runpy
import string
import keyword
import types

from base3.http import BaseHttpException
from base3.core import Base


class FormatTracebackError(Exception):
    pass


def get_variables_from_line(line: str) -> list:
    """Splits line by punctuation chars excluding keywords."""

    t = {**{ord(x): ' ' for x in list("'\"_")}, ord('.'): ' .'}
    p = {char: ' ' for char in string.punctuation.translate(t)}
    r = line.translate(str.maketrans(p))

    return [x for x in r.split() if not keyword.iskeyword(x)]


def get_file_as_lines(file: str):
    file = pathlib.Path(file)
    result = []

    if file.is_file():
        with open(file) as f:
            result = f.readlines()
    return result


def format_signature(traceback_object: types.TracebackType):
    # def fp(pi: inspect.Parameter, pvalue): return f'{pi.name}: {type(pvalue).__name__} = {pvalue}'

    path = traceback_object.tb_frame.f_code.co_filename

    func_name = traceback_object.tb_frame.f_code.co_name
    line_number = traceback_object.tb_lineno
    file = get_file_as_lines(path)
    if -1 != func_name.find('module'):
        return f"module {path.split('/')[-1]}"
    signature_index_begin_list = [i
                                  for i in range(len(file))
                                  if -1 != file[i].find(f"def {func_name}") and i <= line_number]
    signature = ''
    if signature_index_begin_list:
        signature_index_begin = signature_index_begin_list[-1]
        for line in file[signature_index_begin:]:
            if -1 == line.find('):'):
                break
            else:
                signature += line

    return f"{signature.strip()}:"


def format_line(traceback_object, raw_line: str):
    result = raw_line.strip()

    line_number = traceback_object.tb_lineno
    local_vars = traceback_object.tb_frame.f_locals
    line_vars = get_variables_from_line(raw_line)

    for var in line_vars:
        if var in local_vars:
            if (not inspect.isfunction(local_vars[var])
                    and not inspect.ismethod(local_vars[var])
                    and not inspect.isclass(local_vars[var])
                    and not inspect.ismodule(local_vars[var])
            ):
                max_len = 40
                if len(str(local_vars[var])) < max_len:
                    result = result.replace(var, f'{var}<{type(local_vars[var]).__name__}({local_vars[var]})>')
                else:
                    v = str(local_vars[var])
                    result = result.replace(var, f'{var}<{type(local_vars[var]).__name__}({v[:max_len]} ... {v[-max_len:None]})>')

    return f'{result}'


def format_traceback(traceback_object: types.TracebackType, file: list):
    path = traceback_object.tb_frame.f_code.co_filename
    signature = format_signature(traceback_object)
    line_number = traceback_object.tb_lineno
    if len(file) > line_number and file:
        line = format_line(traceback_object, raw_line=file[line_number - 1])
    else:
        line = ''
    return f'{path}, line {line_number}, in {signature} {line}'


def process_traceback(traceback_object):
    exc_traceback = traceback_object
    result = []
    files = dict()

    while exc_traceback:
        filename = exc_traceback.tb_frame.f_code.co_filename

        if not files.get(filename):
            files[filename] = get_file_as_lines(filename)

        result.append(format_traceback(exc_traceback, file=files[filename]))
        exc_traceback = exc_traceback.tb_next

    return result


def traceback_as_message(e: Exception) -> str:
    traceback_object: types.TracebackType = e.__traceback__
    exception_type = str(type(e).__name__)

    if isinstance(e, BaseHttpException):
        r = e._dict()
        r['message'] = r.get('id', 'no message')
    else:
        # Exception
        r = {'message': e.args[0] if e.args else '', 'type': str(type(e).__name__)}

    try:
        formatted_tb = process_traceback(traceback_object=traceback_object)
    except Exception as e:
        p = traceback.format_tb(tb=e.__traceback__)
        t = [x.replace('\n', ' ') for x in p]
        return f"{exception_type}({r['message']}) => LOGGER FAIL: {e}: {', '.join(reversed(t))}"
    formatted_tb.reverse()
    return f"{exception_type}({r['message']}) => " + " | ".join(formatted_tb)


def log(_func=None, *, arg: str = '+++'):
    _ = arg

    def _wrapper(func):
        @functools.wraps(func)
        def _log(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                exc_traceback = e.__traceback__

                tresult = process_traceback(exc_traceback)
                print(*tresult, sep='\n')
                raise
            return result
        return _log

    if _func is None:
        return _wrapper
    else:
        return _wrapper(_func)
