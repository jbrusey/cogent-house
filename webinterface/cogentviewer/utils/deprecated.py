import warnings
import functools
import inspect

def deprecated(func):
    '''This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.'''

    @functools.wraps(func)
    def new_func(*args, **kwargs):
        stk = inspect.stack()
        try:
            caller_filename = stk[1][1]
            caller_lno = stk[1][2]
            warnings.warn_explicit(
                "Call to deprecated function {}.".format(func.__name__),
                category=DeprecationWarning,
                filename=caller_filename,
                #func.func_code.co_filename,
                lineno=caller_lno,
                #func.func_code.co_firstlineno + 1
            )
        finally:
            del stk
        return func(*args, **kwargs)
    return new_func
