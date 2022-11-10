import typing
import importlib
import types

import tortoise
from tortoise import Tortoise, Model
from tortoise.signals import Signals


async def signal_post_save(sender: typing.Type[Model],
                           instance: Model,
                           created: bool,
                           using_db: typing.Optional[tortoise.BaseDBAsyncClient],
                           update_fields: typing.List[str],
                           *args, **kwargs
                           ) -> None:
    print('*' * 25)
    print('sender       ', sender)
    print('instance     ', instance.__dict__)
    print('created      ', created)
    print('using_db     ', using_db)
    print('update_fields', update_fields)
    print('args', args)
    print('kwargs', kwargs)
    pass


async def signal_pre_save(sender: typing.Type[Model],
                          instance: Model,
                          using_db: typing.Optional[tortoise.BaseDBAsyncClient],
                          update_fields: typing.List[str],
                          *args, **kwargs
                          ) -> None:
    print('+' * 25)
    print('sender       ', sender)
    print('instance     ', instance.__dict__)
    print('using_db     ', using_db)
    print('update_fields', update_fields)
    print('args', args)
    print('kwargs', kwargs)
    pass


def register_db_signal_for_models_in_module(models_module: typing.Union[str, types.ModuleType],
                                            signal_type: Signals = Signals.post_save):
    """
    Parameters:
        models_module:
            example: svc_tickets.tickets.models
        signal_type: type from tortoise.signals.Signals
            enum: pre_save, post_save, pre_delete, post_delete
    """

    try:
        if isinstance(models_module, str):
            models_module: types.ModuleType = importlib.import_module(models_module)
        elif isinstance(models_module, types.ModuleType):
            pass
        else:
            raise ValueError(f'Wrong module type {type(models_module)}')

        # for name, model in models_module.__dict__.items():
        #     if isinstance(model, tortoise.models.ModelMeta):
        #         temp_model: tortoise.models.Model = model
        #         temp_model.register_listener(signal=signal_type, listener=signal_post_save)     # fixme uncomment me
        #         temp_model.register_listener(signal=Signals.pre_save, listener=signal_pre_save)   # fixme delete me
    except Exception as e:
        raise ImportError(f'Error while trying to load model from {models_module} to register signal.')
