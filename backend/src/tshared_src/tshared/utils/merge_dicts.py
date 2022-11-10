from collections.abc import Iterable
import copy
import inspect
import typing
from typing import Callable, Union, Optional


__all__ = ['merge_dicts',
           'iterate_over_dict',
           'iterate_over_common',
           'filter_dict',
           'apply_over_dict'
           ]


Empty = inspect.Parameter.empty


#
#   Iterate over dictionary begin
#

def iterate_over_dict(obj: dict, check_func, apply_func, prev_key: str = None) -> dict:
    if isinstance(obj, dict):
        for key in obj.keys():
            obj[key] = iterate_over_dict(obj[key], check_func=check_func, apply_func=apply_func, prev_key=key)
    else:
        if isinstance(obj, str) and check_func(obj):
            return apply_func(obj, prev_key)
    return obj


def iterate_over_common(obj: typing.Union[dict, list],
                        check_func=lambda x: False,
                        apply_func=lambda x: x) -> typing.Union[dict, list]:
    if isinstance(obj, dict):
        for key in obj.keys():
            obj[key] = iterate_over_common(obj[key], check_func=check_func, apply_func=apply_func)
    elif isinstance(obj, list):
        for index in range(len(obj)):
            obj[index] = iterate_over_common(obj[index], check_func=check_func, apply_func=apply_func)
    else:
        if check_func(obj):
            return apply_func(obj)
    return obj


def filter_dict(obj: dict, condition: typing.Callable[[any], bool]) -> dict:
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


def apply_over_dict(obj: dict,
                    check_func: Callable[[any], bool] = lambda x: False,
                    apply_func: Callable[[any], any] = lambda x: x,
                    key_check: Callable[[any], bool] = lambda x: False,
                    key_apply: Callable[[any], any] = lambda x: x
                    ) -> dict:
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


#
#   Iterate over dictionary end
#


#
#   Merge Dictionaries begin
#

def is_iterable(item: any) -> bool:
    return not isinstance(item, str) and isinstance(item, Iterable)


def add_item_to_iterable(iterable_object: Iterable, item: any) -> Iterable:
    if isinstance(iterable_object, list):
        result = copy.deepcopy(iterable_object)
        result.append(item)
        return result
    elif isinstance(iterable_object, tuple):
        result = copy.deepcopy(list(iterable_object))
        result.append(item)
        return tuple(result)
    elif isinstance(iterable_object, dict):
        # item value ignored
        # because key is unknown
        result = copy.deepcopy(list(iterable_object))
        return result
    elif isinstance(iterable_object, set):
        result = copy.deepcopy(iterable_object)
        result.add(item)
        return result
    else:
        raise NotImplemented(f'Not implemented for {type(iterable_object)}')


def merge_dict_to_dict(left: any, right: any) -> any:
    if isinstance(left, dict) and isinstance(right, dict):
        result = copy.deepcopy(left)

        for key in left:
            right_item = right.pop(key, Empty)
            if right_item != Empty:
                result[key] = merge_dict_to_dict(left[key], right_item)
            else:
                pass
        return {**result, **right}
    else:
        if not is_iterable(left) and not is_iterable(right):
            return right
        elif not is_iterable(left) and is_iterable(right):
            return add_item_to_iterable(iterable_object=right, item=left)
        elif is_iterable(left) and not is_iterable(right):
            return add_item_to_iterable(iterable_object=left, item=right)
        # elif is_iterable(left) and is_iterable(right) and isinstance(left, type(right)):
        elif isinstance(left, (list, tuple, set)) and isinstance(right, (list, tuple, set)):
            temp = list(left) + list(right)
            return type(left)(temp)
        else:
            pass
    raise TypeError(f'Not expected {type(left)} as left argument '
                    f'and {type(right)} as right argument.')


def merge_dicts(*dicts):
    """Merges dicts to each other.

    For merging of list-like Iterable type yet supported only:
    list, set, tuple. Other types are ignored. Also, resulting type
    merging of merging iterable objects is same as it was in left dictionary.

    Example:
        merge_dicts(left, right) -> result

        right  = {'1': 'b', '2': {'a': ['b'],      'b': 'b'}, '3': 'b', '4': ('b',)}
          V
        left   = {'1': 'a', '2': {'a': ['a']},                          '4': ['a']}
          =
        result = {'1': 'b', '2': {'a': ['a', 'b'], 'b': 'b'}, '3': 'b', '4': ['a', 'b']}
    """

    result = dict()

    for d in dicts:
        result = merge_dict_to_dict(left=result, right=d)

    return result

#
#   Merge Dictionaries end
#


def main():
    left = {
        '1': 'a',
        '2': {'a': ['a']},
        '4': ['a']
    }

    right = {
        '1': 'b',
            '2': {'a': ['b'], 'b': 'b'},
            '3': 'b',
            '4': ('b',)
    }

    result = merge_dicts(left, right)
    print(result)


if __name__ == '__main__':
    main()
