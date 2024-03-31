import datetime
import inspect
import typing

import dateparser

"""
Простой десериализатор с использованием стандартной системы типов
"""


def _unpack_from_union(value: typing.Any, union_variants: typing.Iterable) -> typing.Tuple[typing.Any, str]:
    has_none_type = False
    for variant in union_variants:
        try:
            if variant == type(None):
                has_none_type = True
            v, err = unpack_from_annotation(value, variant)
            if len(err) == 0:
                return v, ''
        except Exception as e:
            pass
    if has_none_type:
        return None, ''
    return value, f'unable to decode type Union{union_variants}'


def _unpack_from_list(value: typing.Any, innertype) -> typing.Tuple[typing.Any, str]:
    if not isinstance(value, list):
        return value, f'unable to decode type List[{innertype}]'
    ret = []
    err = ''
    try:
        for v in value:
            _v, err = unpack_from_annotation(v, innertype)
            if len(err) > 0:
                return value, err
            ret.append(_v)
    except Exception as e:
        return value, f'unable to decode type List[{innertype}]'
    return ret, err


def _unpack_from_dict(value: typing.Any,
                      key_annot,
                      value_annot) -> typing.Tuple[typing.Any, str]:
    if not isinstance(value, dict):
        return value, f'unable to decode type Dict[{key_annot}, {value_annot}]'
    keys, _err = _unpack_from_list(list(value.keys()), key_annot)
    if len(_err) > 0:
        return value, f'unable to decode dict key type {key_annot}'
    values, _err = _unpack_from_list(list(value.values()), value_annot)
    if len(_err) > 0:
        return value, f'unable to decode dict value type {value_annot}'
    return dict(zip(keys, values)), ''


def _weak_isinstance(obj, sometype):
    if isinstance(sometype, str):
        obj_type = type(obj)
        return (obj_type.__module__ + '.' + obj_type.__qualname__) == sometype
    else:
        isinstance(obj, sometype)


def unpack_from_annotation(value: typing.Any, type_annotation) -> typing.Tuple[typing.Any, str]:
    if type_annotation == typing.Any \
            or type_annotation is None \
            or type(type_annotation) is None \
            or (getattr(type_annotation, '__origin__', None) is None and _weak_isinstance(value, type_annotation)):
        return value, ''

    if value is not None and type(value) not in [list, set, dict, tuple]:
        value = value,

    if isinstance(type_annotation, str):
        type_annotation = eval(type_annotation)

    type_error = ''

    origin = getattr(type_annotation, '__origin__', None)
    if origin == typing.Union:
        value, err = _unpack_from_union(value, type_annotation.__args__)
    elif origin in [list, tuple]:
        value, err = _unpack_from_list(value, type_annotation.__args__[0])
    elif origin == dict:
        value, err = _unpack_from_dict(value, *type_annotation.__args__)
    else:
        if type_annotation == datetime.datetime:
            type_annotation = dateparser.parse
        try:
            spec = inspect.getfullargspec(type_annotation.__init__)
            if len(spec.args) > 1:
                if isinstance(value, dict):
                    value = value.items()
                    new_values = []
                    for k, v in value:
                        _v, err = unpack_from_annotation(v, spec.annotations[k])
                        if len(err) > 0:
                            return value, err
                        new_values.append((k, _v))
                    value = dict(new_values)
                    value = type_annotation(**value)
                elif isinstance(value, list) or isinstance(value, tuple):
                    init_args = spec.args[1:]
                    new_values = []
                    for i, v in enumerate(value):
                        name = init_args[i]
                        _v, err = unpack_from_annotation(v, spec.annotations[name])
                        if len(err) > 0:
                            return value, err
                        new_values.append((name, _v))
                    value = dict(new_values)
                    value = type_annotation(**value)
            else:
                if isinstance(value, dict):
                    value = type_annotation(**value)
                else:
                    value = type_annotation(*value)
            err = ''
        except Exception as e:
            err = f'unable to decode type {type_annotation}'

    return value, err
