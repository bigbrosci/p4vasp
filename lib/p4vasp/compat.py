"""Compatibility helpers for running the old p4vasp code on Python 3."""

import io
import sys
import builtins
import importlib
import string as _string
import types as _types

StringType = str
UnicodeType = str
StringTypes = (str,)
ListType = list
TupleType = tuple
DictType = dict
DictionaryType = dict
IntType = int
LongType = int
FloatType = float
ComplexType = complex
NoneType = type(None)
BooleanType = bool
ClassType = type
TypeType = type
InstanceType = object
ObjectType = object
FileType = io.IOBase

FunctionType = _types.FunctionType
LambdaType = _types.LambdaType
MethodType = _types.MethodType
BuiltinFunctionType = _types.BuiltinFunctionType
BuiltinMethodType = _types.BuiltinMethodType
ModuleType = _types.ModuleType
CodeType = _types.CodeType


def split(value, sep=None, maxsplit=-1):
    return value.split(sep, maxsplit)


def join(values, sep=" "):
    return sep.join(values)


def joinfields(values, sep=" "):
    return sep.join(values)


def strip(value, chars=None):
    return value.strip(chars)


def lower(value):
    return value.lower()


def upper(value):
    return value.upper()


def replace(value, old, new, maxsplit=-1):
    return value.replace(old, new, maxsplit)


def find(value, sub, start=0, end=None):
    if end is None:
        return value.find(sub, start)
    return value.find(sub, start, end)


def atoi(value, base=10):
    return int(value, base) if isinstance(value, str) else int(value)


def atof(value):
    return float(value)


def resolve_dotted_name(name, namespace=None):
    if not isinstance(name, str):
        return name
    parts = [x.strip() for x in name.split(".")]
    if not parts or not parts[0]:
        return None
    if len(parts) == 1:
        if namespace is not None and parts[0] in namespace:
            return namespace[parts[0]]
        return getattr(builtins, parts[0])
    module = importlib.import_module(".".join(parts[:-1]))
    return getattr(module, parts[-1])


def create_instance_from_name(name, namespace=None):
    return resolve_dotted_name(name, namespace)()


def install():
    builtins.intern = sys.intern

    for module in (_types,):
        for name in _TYPE_EXPORTS:
            setattr(module, name, globals()[name])
        _extend_all(module, _TYPE_EXPORTS)

    for name in _STRING_EXPORTS:
        setattr(_string, name, globals()[name])
    _extend_all(_string, _STRING_EXPORTS)


def _extend_all(module, names):
    exports = getattr(module, "__all__", None)
    if exports is not None:
        for name in names:
            if name not in exports:
                exports.append(name)


_TYPE_EXPORTS = [
    "StringType", "UnicodeType", "StringTypes", "ListType", "TupleType",
    "DictType", "DictionaryType", "IntType", "LongType", "FloatType",
    "ComplexType", "NoneType", "BooleanType", "ClassType", "TypeType",
    "InstanceType", "ObjectType", "FileType", "FunctionType",
    "LambdaType", "MethodType", "BuiltinFunctionType", "BuiltinMethodType",
    "ModuleType", "CodeType",
]

_STRING_EXPORTS = [
    "split", "join", "joinfields", "strip", "lower", "upper", "replace",
    "find", "atoi", "atof",
]

__all__ = _TYPE_EXPORTS + _STRING_EXPORTS + [
    "install", "intern", "resolve_dotted_name", "create_instance_from_name",
]

intern = sys.intern

install()
