import inspect
import os
import pathlib
import sys
import typing
import copy
from difflib import SequenceMatcher
import string

import logging
import logging.config

import unittest
import tornado.web

import base3
from tshared.utils.format_traceback import traceback_as_message
from tshared.utils.merge_dicts import merge_dicts


__all__ = [
    "setup_logging",
    "get_logger_for",
    "log_for",
    "log",
]


class SetupLoggerError(Exception):
    pass


def _if_in_debugger_change_console_handlers_to_debug(logging_config: dict) -> dict:
    def check_debug_modules_result() -> tuple:
        get_trace = getattr(sys, 'gettrace', None)
        if get_trace:
            get_trace = get_trace()
        return get_trace, 'pdb' in sys.modules, 'gdb' in sys.modules

    def is_in_tests() -> bool:
        gt, pdb, gdb = check_debug_modules_result()
        return gt is None and (pdb or gdb)

    def is_in_debug() -> bool:
        gt, pdb, gdb = check_debug_modules_result()
        return type(gt).__name__ == "ThreadTracer" and not pdb and not gdb

    handlers = logging_config.get('handlers')

    if handlers and is_in_debug():
        for handler_name in handlers:
            if (handlers[handler_name]
                    and handlers[handler_name].get('class') == 'logging.StreamHandler'):
                handlers[handler_name]['level'] = 'DEBUG'
    return logging_config


def setup_logging(settings: dict, for_testing: bool = False, **kwargs) -> None:
    """
    Args:
        settings: {'logging': dict(), 'services: dict()', ...}
        for_testing: True if setup called in testing

    Raises:
        SetupLoggerError
    """

    def resolve_filename(filename: str):
        app_name = os.getenv('installation_name', 'base3')
        test_name = "test." if for_testing else ""

        if filename and filename[0] != '/':
            # _caller_file = inspect.currentframe().f_back.f_code.co_filename
            _caller_file = inspect.currentframe().f_back.f_code.co_filename
            _caller_dir = pathlib.Path(_caller_file).parent
            filename = str(pathlib.Path(_caller_dir, filename).resolve())
        # return filename.replace('service_name', f'{app_name}.{test_name}{handler_name}')
        return filename

    def make_handler(handler_name: str):
        """
        file:
          class: logging.FileHandler
          filename: /tmp/test_log2.log
          formatter: default
          mode: w
          level: INFO
        """
        h = copy.deepcopy(handlers_template)
        app_name = os.getenv('installation_name', 'base3')
        test_name = "test." if for_testing else ""
        # if h['filename'] and h['filename'][0] != '/':
        #     # _caller_file = inspect.currentframe().f_back.f_code.co_filename
        #     _caller_file = inspect.currentframe().f_back.f_code.co_filename
        #     _caller_dir = pathlib.Path(_caller_file).parent
        #     h['filename'] = str(pathlib.Path(_caller_dir, h['filename']).resolve())
        #     # print(h['filename'])
        #     pass
        h['filename'] = resolve_filename(h['filename'])
        h['filename'] = h['filename'].replace('service_name', f'{app_name}.{test_name}{handler_name}')
        return h

    def make_logger(svc_name):
        """
        service_template:
          handlers: [console]
          propagate: false
        """
        l = copy.deepcopy(logger_template)
        # l['handlers'].append(f'file_{svc_name}')
        l['handlers'].append(f'file_services_{svc_name}')
        return l

    def create_directory(path):
        try:
            dir_path = pathlib.Path(path).parent
            dir_path.mkdir(parents=True, exist_ok=True)
        except PermissionError as e:
            pass

    try:
        if settings.get('logging'):
            #
            # setting app loggers for every service
            # setting app loggers for every service
            # begin
            #
            services_settings = settings.get('services', {})
            logging_settings = settings.get('logging', {})

            logger_template = logging_settings['loggers'].pop('SERVICE_TEMPLATE', None)
            handlers_template = logging_settings['handlers'].pop('FILE_SERVICE_TEMPLATE', None)

            services = [name for name, conf in services_settings.items() if conf.get('active') is True]

            # config root
            if settings['logging'].get('handlers', {}).get('file_root'):
                handler = settings['logging']['handlers']['file_root']
                create_directory(handler['filename'])
            
            # config general services logger
            if logging_settings:
                logging_settings['handlers']['file_services']['filename'] = resolve_filename(logging_settings['handlers']['file_services']['filename'])
                pass
            
            if services:
                if not logger_template or not handlers_template:
                    raise SetupLoggerError("No templates were supplied for services loggers or file handlers.")

                created_handler_names = []

                if not logging_settings['handlers'].get(f'file_services') or True:
                    handler = make_handler(f"services")
                    logging_settings['handlers']['file_services'] = handler
                    create_directory(handler['filename'])
                if not logging_settings['loggers'].get('services'):
                    logging_settings['loggers']['services'] = make_logger("services")
                    logging_settings['loggers']['services']['propagate'] = False

                for service_name in kwargs.get('services', []):
                    logger_name = f"services.{service_name}"
                    filehandler_name = f'file_services_{service_name}'

                    # create filehandler if not exists
                    if not logging_settings['handlers'].get(filehandler_name):
                        created_handler_names.append(logger_name)
                        handler = make_handler(logger_name)
                        logging_settings['handlers'][filehandler_name] = handler
                        create_directory(handler['filename'])

                    # create logger if not exists
                    if not logging_settings['loggers'].get(logger_name):
                        logging_settings['loggers'][logger_name] = make_logger(service_name)
                #
                # end
                #

                # override loggers setting by custom ones from services configuration
                for service_name, service_config in services_settings.items():
                    if 'logging' in service_config:
                        if service_config['logging'] and isinstance(service_config, dict):
                            logging_settings = merge_dicts(logging_settings, service_config['logging'])
                        elif not service_config['logging']:
                            # disable logging == delete filehandlers for this logger
                            logger_name = f"services.{service_name}"
                            filehandler_name = f'file_services_{service_name}'
                            logging_settings['handlers'].pop(filehandler_name)
                            service_handlers = logging_settings['loggers'][logger_name]['handlers']
                            logging_settings['loggers'][logger_name]['handlers'] = [x
                                                                                    for x in service_handlers
                                                                                    if x != filehandler_name]
                        else:
                            # unexpected case
                            raise SetupLoggerError(f'setup_logger: unexpected '
                                                   f'value {service_config["logging"]} '
                                                   f'or type {type(service_config["logging"])} '
                                                   f'for {service_name} service logging configuration.')

            logging_settings = _if_in_debugger_change_console_handlers_to_debug(logging_settings)
            logging.config.dictConfig(logging_settings)
    except ValueError as ve:
        raise SetupLoggerError(ve, 'Config file problem possibly. '
                                   'Check if all file handlers have existing directories in path.')
    except Exception as e:
        raise SetupLoggerError(e)


class RawLog:
    """
    CRITICAL = 50
    ERROR = 40

    WARNING = 30
    INFO = 20

    DEBUG = 10
    NOTSET = 0
    """
    def __init__(self, logger: logging.Logger, obj=None, note=None):
        self._logger = logger
        self._object = obj
        self._note = self._prepare_note(note)

    @staticmethod
    def _prepare_note(note: dict) -> str:
        if note:
            result = ', '.join([f'{name}: {item}' for name, item in note.items() if item])
            return f'{" ++ "}{result}{" ++"}'
        else:
            return ''

    @staticmethod
    def _add_note_to_extra(note: str, kwargs: dict) -> dict:
        extra = kwargs.pop('extra', {})

        return {'extra': {**extra, 'note': note}, **kwargs}

    def critical(self, message: typing.Union[str, Exception], *args, **kwargs):
        self._logger.critical(self._prepare_message(message), *args,
                              **self._add_note_to_extra(self._note, kwargs)
                              )

    def fatal(self, message: typing.Union[str, Exception], *args, **kwargs):
        self._logger.fatal(self._prepare_message(message), *args,
                           **self._add_note_to_extra(self._note, kwargs)
                           )

    def error(self, message: typing.Union[str, Exception], *args, **kwargs):
        self._logger.error(self._prepare_message(message), *args,
                           **self._add_note_to_extra(self._note, kwargs)
                           )

    def warning(self, message: typing.Union[str, Exception], *args, **kwargs):
        self._logger.warning(self._prepare_message(message), *args,
                             **self._add_note_to_extra(self._note, kwargs)
                             )

    def warn(self, message: typing.Union[str, Exception], *args, **kwargs):
        self.warning(message, *args,
                     **self._add_note_to_extra(self._note, kwargs)
                     )

    def info(self, message: typing.Union[str, Exception], *args, **kwargs):
        self._logger.info(self._prepare_message(message), *args,
                          **self._add_note_to_extra(self._note, kwargs)
                          )

    def debug(self, message: typing.Union[str, Exception], *args, **kwargs):
        self._logger.debug(self._prepare_message(message), *args,
                           **self._add_note_to_extra(self._note, kwargs)
                           )

    def exception(self, message: typing.Union[str, Exception], *args, **kwargs):
        self._logger.exception(message, *args,
                               **self._add_note_to_extra(self._note, kwargs)
                               )

    @staticmethod
    def _prepare_message(message: typing.Union[str, Exception]):
        if isinstance(message, Exception):
            message = traceback_as_message(message)
        return " ".join(message.splitlines())


def _get_note_from_object(obj: any) -> dict:
    result = dict()

    if isinstance(obj, str):
        # custom logger object
        # init by name
        # not implemented
        result['note'] = 'note string note'
    elif isinstance(obj, dict):
        return obj
    elif isinstance(obj, tornado.web.RequestHandler):
        # class Base
        # from services method
        # from class api if _origin_self<Base> supplied
        result['remote_ip'] = obj.request.remote_ip
        if hasattr(obj, 'id_user'):
            result['user_id'] = obj.id_user
        result['service_ip'] = obj.request.host
    elif isinstance(obj, base3.decorators.api):
        # class api
        # from decorator
        # not much information
        if obj.auth:
            result['access_type'] = 'authorized'
        else:
            result['access_type'] = 'unauthorized'

    return result


def make_logger(logger_name: str, obj=None) -> RawLog:
    """
    Getting logger by name.

    Here we can:
        * change format of logging (by creating new formatter)
          for example add new placeholders depending on supplied information.
        * change file name of logfile (by creating new file handler)

    """

    logger = logging.getLogger(logger_name)

    note = _get_note_from_object(obj)

    return RawLog(logger, obj=obj, note=note)


class bc:
    magenta = '\033[95m'
    blue = '\033[94m'
    cyan = '\033[96m'
    green = '\033[92m'
    yellow = '\033[93m'
    red = '\033[91m'
    gray = '\033[90m'
    white = '\033[37m'
    end = '\033[0m'
    bold = '\033[1m'
    underline = '\033[4m'


def hl_text(text: str, substring: str = None, color: str = bc.green) -> str:
    if not substring:
        return f'{color}{text}{bc.end}'
    elif isinstance(substring, list):
        for s in substring:
            text = text.replace(s, f'{color}{substring}{bc.end}')
        return text
    elif isinstance(substring, dict):
        for s, color in substring.items():
            text = text.replace(s, f'{color}{substring}{bc.end}')
        return text
    else:
        return text.replace(substring, f'{color}{substring}{bc.end}')


class CustomFilter(logging.Filter):
    def __init__(self, **kwargs):
        super().__init__()
        self.kwargs = kwargs

    def filter(self, record: logging.LogRecord) -> bool:
        def format_a_trace(tr: str) -> str:
            if not tr or ("DEBUG" in tr
                          or "INFO" in tr or "WARNING" in tr
                          or "ERROR" in tr or "CRITICAL" in tr):
                return tr

            colors = [bc.gray, bc.white, bc.white]

            temp = tr.strip()
            temp = temp.replace(', in ', '\n')
            temp = temp.replace('::', ':\n')
            temp = [x for x in temp.split('\n')]

            for i in range(len(temp)):
                temp[i] = '\t' * i + hl_text(temp[i], color=colors[i % len(colors)])
            return "\n".join(temp)

        try:
            if record.msg.find('=>') != -1:
                header_end = record.msg.find('=>')
                header_end = header_end + 2 if header_end != -1 else None
                footer_begin = record.msg.find('++')
                footer_begin = footer_begin if footer_begin != -1 else None
                header = record.msg[:header_end].strip('=> ')
                traces = [format_a_trace(x) if i > 0 else format_a_trace(x) + f'\t<=\t{hl_text(header, color=bc.red)}'
                          for i, x in enumerate(record.msg[header_end:footer_begin].split(' | '))
                          if x.strip()]
                footer = record.msg[footer_begin:] if footer_begin else ''
                result = header + '\n' + "\n".join(traces) + footer

                record.msg = result
        except Exception as e:
            record.msg = "\n".join([f"{i}. {hl_text(x, color=bc.gray)}" if i % 2 else f"{i}. {hl_text(x, color=bc.white)}"
                                    for i, x in enumerate(record.msg.split(' | '))])
            _ = e
        return True


def filter_factory():
    def filter_instance(record):
        print("Hello from function filter!")
        return True
    return filter_instance


def _get_service_name_from(obj: any) -> str:
    if isinstance(obj, str):
        return obj
    elif isinstance(obj, tornado.web.RequestHandler):
        prefix = os.environ.get('API_PREFIX', '___')
        return obj._uri.replace(prefix, '').split('/')[1]
    elif isinstance(obj, base3.decorators.api):
        return obj.service_name
    elif isinstance(obj, unittest.TestCase):
        services_list = obj.api_modules if hasattr(obj, 'api_modules') else None
        object_location = pathlib.Path(inspect.getmodule(object=obj).__file__).name

        if services_list:
            #
            # Comparing test filename with api_modules names
            # looking for common substrings
            # longest found common substring returned as the logger name
            #
            guess_list: list[str] = []

            for svc in services_list:
                # getting longest substring
                match = SequenceMatcher(a=svc, b=object_location).find_longest_match()
                guess_list.append(svc[match.a:match.a + match.size])

            # stripping lines of punctuation begin
            table = {char: None for char in string.punctuation}
            guess_list = [x.translate(str.maketrans(table)) for x in guess_list]
            # stripping lines of punctuation end

            # getting longest substring
            result = max(guess_list, key=len)
            if result:
                return result

        # test_base.py > test_[base].py
        return object_location[5:-3]

    return ''


def get_logger_for(obj: any) -> RawLog:
    """Get logger by type of object or by name.

    Args:
        obj:
            if obj is type of str than logger(obj) returned
            if obj is tornado.web.RequestHandler func called from service method
            or from api decorator with `_origin_self` as argument.

    Returns:
        RawLog object that has same methods for logging as python
        Logger class (critical(), error(), etc)
    """

    if isinstance(obj, str):
        return make_logger(obj)
    elif isinstance(obj, (tornado.web.RequestHandler,
                          base3.decorators.api,
                          unittest.TestCase,
                          )):
        service_name = _get_service_name_from(obj)
        return make_logger(f'services.{service_name}', obj)

    # root logger
    return make_logger('', obj)


log_for = get_logger_for
log = get_logger_for
