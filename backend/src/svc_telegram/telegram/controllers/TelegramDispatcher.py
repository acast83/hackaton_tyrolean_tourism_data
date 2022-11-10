import inspect
import typing
from dataclasses import dataclass

from ..models.TelegramModelsTypes import *
from ..models.TelegramModelsMethods import *


def _get_spec(func: callable):
    while hasattr(func, '__wrapped__'):  # Try to resolve decorated callbacks
        func = func.__wrapped__
    return inspect.getfullargspec(func)


def _check_spec(spec: inspect.FullArgSpec, kwargs: dict):
    if spec.varkw:
        return kwargs

    return {k: v for k, v in kwargs.items() if k in set(spec.args + spec.kwonlyargs)}


class Handler:
    def __init__(self, dispatcher, middleware_key=None):
        self.dispatcher = dispatcher
        self.middleware_key = middleware_key
        self.handlers: list = []

    async def notify(self, message: Message):
        """Use handlers."""
        results = []

        for handler_obj in self.handlers:
            for handler_obj_filter in handler_obj.filters:
                if handler_obj_filter(message):
                    results.append(await handler_obj.handler(message))
                    break
        return results

    def register(self, handler_obj):
        """Add handler."""
        self.handlers.append(handler_obj)

    @dataclass
    class HandlerObject:
        handler: callable
        filters: list[callable] = None


class Dispatcher:
    """
    Updates handler.
    """

    def __init__(self):
        self.message_handlers = Handler(self, middleware_key='message')
        self.route = None

    async def process_update(self, update: Update, route=None):
        self.route = route

        try:
            if update.message:
                return await self.message_handlers.notify(update.message)

        except Exception as e:
            print(e)

    def message_handler(self, *custom_filters, commands=None):
        def decorator(callback):
            self.register_message_handler(callback, *custom_filters, commands=commands)
            return callback
        return decorator

    def register_message_handler(self, callback, *custom_filters, commands=None):
        def create_command_filter(_commands):
            if isinstance(_commands, str):
                _commands = [_commands]
            elif isinstance(_commands, list):
                _commands = _commands
            elif commands is None:
                _commands = []
            else:
                raise ValueError('Commands should be list or str, got {type(_commands)}.')

            _result = []

            for _command in _commands:
                _result.append(lambda message: message.text.startswith(f'/{_command}'))

            return _result

        record = Handler.HandlerObject(handler=callback, filters=[*custom_filters,
                                                                  *create_command_filter(commands)])
        self.message_handlers.register(record)


dp = Dispatcher()
