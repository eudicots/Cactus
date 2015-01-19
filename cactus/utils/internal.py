#coding:utf-8
import six
import inspect

# Adapted from: http://kbyanc.blogspot.com/2007/07/python-more-generic-getargspec.html


FUNC_OBJ_ATTR = "__func__" if six.PY3 else "im_func"


def getargspec(obj):
    """
    Get the names and default values of a callable's
       arguments

    A tuple of four things is returned: (args, varargs,
    varkw, defaults).
      - args is a list of the argument names (it may
        contain nested lists).
      - varargs and varkw are the names of the * and
        ** arguments or None.
      - defaults is a tuple of default argument values
        or None if there are no default arguments; if
        this tuple has n elements, they correspond to
        the last n elements listed in args.

    Unlike inspect.getargspec(), can return argument
    specification for functions, methods, callable
    objects, and classes.  Does not support builtin
    functions or methods.
    """
    if not callable(obj):
        raise TypeError("%s is not callable" % type(obj))
    try:
        if inspect.isfunction(obj):
            return inspect.getargspec(obj)
        elif hasattr(obj, FUNC_OBJ_ATTR):
            # For methods or classmethods drop the first
            # argument from the returned list because
            # python supplies that automatically for us.
            # Note that this differs from what
            # inspect.getargspec() returns for methods.
            # NB: We use im_func so we work with
            #     instancemethod objects also.
            spec = inspect.getargspec(getattr(obj, FUNC_OBJ_ATTR))
            return inspect.ArgSpec(spec.args[:1], spec.varargs, spec.keywords, spec.defaults)
        elif inspect.isclass(obj):
            return getargspec(obj.__init__)
        elif isinstance(obj, object):
            # We already know the instance is callable,
            # so it must have a __call__ method defined.
            # Return the arguments it expects.
            return getargspec(obj.__call__)
    except NotImplementedError:
        # If a nested call to our own getargspec()
        # raises NotImplementedError, re-raise the
        # exception with the real object type to make
        # the error message more meaningful (the caller
        # only knows what they passed us; they shouldn't
        # care what aspect(s) of that object we actually
        # examined).
        pass
    raise NotImplementedError("do not know how to get argument list for %s" % type(obj))
