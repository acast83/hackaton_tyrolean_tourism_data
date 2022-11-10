"""
This is a small library with utils for the python dictionaries.
"""

from collections.abc import Iterable
import copy
import inspect
from typing import Callable


__all__ = [
    "merge_dicts",
    "apply_over_dict",
    "filter_dict",
    "rm_nones",
    "print_dict",
    "format_dict",
    "lower_dict_keys",
]


Empty = inspect.Parameter.empty


def filter_dict(obj: dict,
                value_condition: Callable[[any], bool] = lambda x: True,
                key_condition: Callable[[any], bool] = lambda x: True
                ) -> dict:
    """
    Arguments:
        obj:
            Python dictionary to filter.
        value_condition:
            Callable object that receives value and returns boolean.
            If True is returned the key-value pair will be preserved in
            a resulting dictionary.
        key_condition:
            Callable object that receives key and returns boolean.
            If True is returned the key-value will be preserved in
            a resulting dictionary.

    Returns:
        Filtered copy of supplied dictionary.
    """

    if not isinstance(obj, dict):
        raise TypeError(f'filter_dict() supports only dict objects, '
                        f'but {type(obj)} supplied.')
    result = dict()

    for key, value in obj.items():
        if key_condition(key):
            if isinstance(value, dict):
                value = filter_dict(obj=value,
                                    value_condition=value_condition)
            if value_condition(value):
                result[key] = value
    return result


def rm_nones(obj: dict) -> dict:
    """Deletes keys from dictionary if value is None."""

    if not isinstance(obj, dict):
        return obj

    return filter_dict(obj=obj, value_condition=lambda x: x is not None)


def apply_over_dict(obj: dict,
                    value_check: Callable[[any], bool] = lambda x: True,
                    value_apply: Callable[[any], any] = lambda x: x,
                    key_check: Callable[[any], bool] = lambda x: False,
                    key_apply: Callable[[any], any] = lambda x: x
                    ) -> dict:
    """
    Applies some action on dictionary items basing on condition.

    Arguments:
        obj:
        value_check:
            checks condition of value.
        value_apply:
            applies action on value if condition is True.
        key_check:
            checks keys of dictionary.
            If `key_check` returns True `key_apply` is executed with
            dictionary `key` as an argument and apply_func is executed
            with `value` as an argument. This behavior can lead to
            unexpected results (because dictionary value modified based
            on key check condition), considering this best way is to
            modify only keys or only values at the same.
        key_apply:
            Applies action on key if condition is True.

    Returns:
        Modified dictionary.
    """

    result = dict()

    if isinstance(obj, dict):
        for key in obj.keys():
            if key_check(key):
                result[key_apply(key)] = value_apply(
                    apply_over_dict(
                        obj[key],
                        value_check=value_check, value_apply=value_apply,
                        key_check=key_check, key_apply=key_apply
                    )
                )
            else:
                result[key] = apply_over_dict(
                    obj[key],
                    value_check=value_check, value_apply=value_apply,
                    key_check=key_check, key_apply=key_apply
                )
    else:
        if value_check(obj):
            return value_apply(obj)
        result = obj
    return result


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
        elif isinstance(left, (list, tuple, set)) and isinstance(right, (list, tuple, set)):
            temp = list(left) + list(right)
            return type(left)(temp)
    raise TypeError(f'Not expected {type(left)} as left argument '
                    f'and {type(right)} as right argument.')


def merge_dicts(*dicts) -> dict:
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


def format_dict(obj: dict, *args, **kwargs) -> str:
    """
    Arguments:
        obj:
        args:
        kwargs:
    """

    def is_flat(_obj) -> bool:
        def _is_iterable_inside_iterable(__obj):
            return bool([x for x in __obj if isinstance(x, (list, dict, tuple, set))])

        if isinstance(_obj, (list, set, tuple)):
            return not _is_iterable_inside_iterable(_obj)
        else:
            return False

    braces = {
        dict: {'open': '{', 'close': '}'},
        list: {'open': '[', 'close': ']'},
        tuple: {'open': '(', 'close': ')'},
        set: {'open': '{', 'close': '}'},
    }

    _type = type(obj)
    indent_size = 4 if 'indent' not in kwargs else kwargs.pop('indent')
    indent_number = 1 if 'indent_number' not in kwargs else kwargs.pop('indent_number')
    flat = is_flat(obj)

    def format_item(_item, _indent_number, _indent_size, is_last: bool, _key=None) -> str:
        _result = ' ' * (_indent_number * _indent_size)

        if _key is not None:
            _result += f'{_key}: '

        _result += format_dict(_item, *args,
                               indent=_indent_size,
                               indent_number=_indent_number + 1,
                               **kwargs)

        _result += ',' if is_last else ''
        _result += '\n'
        return _result

    result = ''

    result += braces.get(_type, {'open': ''})['open']
    result += '\n' if not flat else ''

    if not obj or flat:
        try:
            return str(_type(obj))
        except TypeError:
            return str(obj)

    if isinstance(obj, dict):
        obj_items = list(obj.items())

        while obj_items:
            key, value = obj_items.pop(0)
            result += format_item(value, indent_number, indent_size, is_last=bool(obj_items), _key=key)

    elif isinstance(obj, (list, set, tuple)):
        obj_items = list(obj)

        while obj_items:
            value = obj_items.pop(0)
            result += format_item(value, indent_number, indent_size, is_last=bool(obj_items))

    else:
        result = str(obj)
        indent_number = 1

    result += ' ' * ((indent_number - 1) * indent_size)
    result += braces.get(_type, {'close': ''})['close']
    return result


def lower_dict_keys(obj: dict):
    """
    From: {'A': 1, 'B': 1, 'C': {'C': 1, 'D': ['A', {'E': 2}, ({'F': 1}, 1)]}}
    To:   {'a': 1, 'b': 1, 'c': {'c': 1, 'd': ['A', {'e': 2}, ({'f': 1}, 1)]}}
    """

    def value_apply(x):
        if isinstance(x, (list, tuple, set)):
            return type(x)([lower_dict_keys(o) for o in x])
        return x

    return apply_over_dict(
        obj,
        key_check=lambda x: isinstance(x, str),
        key_apply=lambda x: x.lower(),
        value_check=lambda x: True,
        value_apply=value_apply,
    )


def print_dict(obj: dict, *args, **kwargs):
    result = format_dict(obj, *args, **kwargs)
    print(result)


def print_test_dict():
    a = {
        'a': 1,
        'b': 'y',
        'c': [{'q': 'bar', 'w': [1, 2, 3]}, 1, {'q', 'w', 'e'}, 2, ('this', 'is', 'tuple')],
        'd': {
            'e': 1,
            'f': [],
            'g': {'foo': 'bar'}
        }
    }
    # a = {'a': 1, 'b': 2}

    print_dict(a)


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


def lower_keys():
    cases = (
        {'A': 1},
        {'A': 1, 'B': 1},
        {'A': 1, 'B': 1, 'C': {'C': 1, 'D': ['A', {'E': 2}, ({'F': 1}, 1)]}},
        {1: 2, 'A': 1, 'B': 1, 'C': {'C': 1, 'D': ['A', {'E': 2}, ({'F': 1}, 1)]}},
    )
    for case in cases:
        result = lower_dict_keys(case)
        print(result)
        print()


if __name__ == '__main__':
    # main()
    # print_test_dict()
    lower_keys()
