"""
Python2/3 compatible version of inspect.
Source: https://github.com/timgraham/django/blob/3872a33132a4bb6aa22b237927597bbfdf6f21d7/django/utils/inspect.py

Slightly modified so getargspec() always returns a named tuple (ArgSpec).
"""

from __future__ import absolute_import

import inspect
import six
from collections import namedtuple

ArgSpec = namedtuple('ArgSpec', 'args varargs keywords defaults')


def getargspec(func):
    if six.PY2:
        return inspect.getargspec(func)

    sig = inspect.signature(func)
    args = [
        p.name for p in sig.parameters.values()
        if p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
    ]
    varargs = [
        p.name for p in sig.parameters.values()
        if p.kind == inspect.Parameter.VAR_POSITIONAL
    ]
    varargs = varargs[0] if varargs else None
    varkw = [
        p.name for p in sig.parameters.values()
        if p.kind == inspect.Parameter.VAR_KEYWORD
    ]
    varkw = varkw[0] if varkw else None
    defaults = [
        p.default for p in sig.parameters.values()
        if p.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD and p.default is not p.empty
    ] or None
    return ArgSpec(args, varargs, varkw, defaults)


def get_func_args(func):
    if six.PY2:
        argspec = inspect.getargspec(func)
        return argspec.args[1:]  # ignore 'self'

    sig = inspect.signature(func)
    return [
        arg_name for arg_name, param in sig.parameters.items()
        if param.kind == inspect.Parameter.POSITIONAL_OR_KEYWORD
    ]


def func_accepts_kwargs(func):
    if six.PY2:
        # Not all callables are inspectable with getargspec, so we'll
        # try a couple different ways but in the end fall back on assuming
        # it is -- we don't want to prevent registration of valid but weird
        # callables.
        try:
            argspec = inspect.getargspec(func)
        except TypeError:
            try:
                argspec = inspect.getargspec(func.__call__)
            except (TypeError, AttributeError):
                argspec = None
        return not argspec or argspec[2] is not None

    return any(
        p for p in inspect.signature(func).parameters.values()
        if p.kind == p.VAR_KEYWORD
    )


def func_has_no_args(func):
    args = inspect.getargspec(func)[0] if six.PY2 else [
        p for p in inspect.signature(func).parameters.values()
        if p.kind == p.POSITIONAL_OR_KEYWORD and p.default is p.empty
    ]
    return len(args) == 1


def func_supports_parameter(func, parameter):
    if six.PY3:
        return parameter in inspect.signature(func).parameters
    else:
        args, varargs, varkw, defaults = inspect.getargspec(func)
        return parameter in args