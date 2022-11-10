from typing import Callable


__all__ = [
    "filter_dict",
    "rm_nones",
    "apply_over_dict",
]


def filter_dict(obj: dict, condition: Callable[[any], bool]) -> dict:
    if not isinstance(obj, dict):
        raise TypeError(f'filter_dict() supports only dict objects, '
                        f'but {type(obj)} supplied.')
    result = dict()

    for k, v in obj.items():
        if isinstance(v, dict):
            result[k] = filter_dict(obj=v, condition=condition)
        elif condition(v):
            result[k] = v
    return result


def rm_nones(obj: dict) -> dict:
    """Deletes keys from dictionary if value is None."""

    if not isinstance(obj, dict):
        raise TypeError(f'rm_nones accepts only dicts objects, '
                        f'but {type(obj)} is supplied.')

    return filter_dict(obj=obj, condition=lambda x: x is not None)


def apply_over_dict(obj: dict,
                    check_func: Callable[[any], bool] = lambda x: False,
                    apply_func: Callable[[any], any] = lambda x: x,
                    key_check: Callable[[any], bool] = lambda x: False,
                    key_apply: Callable[[any], any] = lambda x: x
                    ) -> dict:
    """
    Applies some action on dictionary items basing on condition.

    Arguments:
        obj:
        check_func: checks condition of value.
        apply_func: applies action on value if condition is True.
        key_check:  checks key of dictionary.
        key_apply:  applies action on key if condition is True.

    Returns:
        Modified dictionary.

    """

    if isinstance(obj, dict):
        for key in obj.keys():
            if key_check(key):
                obj[key_apply(key)] = apply_func(apply_over_dict(obj[key],
                                                                 check_func=check_func, apply_func=apply_func,
                                                                 key_check=key_check, key_apply=key_apply))
            else:
                obj[key] = apply_over_dict(obj[key],
                                           check_func=check_func, apply_func=apply_func,
                                           key_check=key_check, key_apply=key_apply)
    else:
        if check_func(obj):
            return apply_func(obj)
    return obj
