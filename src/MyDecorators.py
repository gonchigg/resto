import functools
import time


def debug(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if "debug" in kwargs:
            if kwargs["debug"]:
                args_repr = [repr(a) for a in args]
                kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
                signature = ", ".join(args_repr + kwargs_repr)
                print(f"Calling {func.__name__}({signature})")
                result = func(*args, **kwargs)
                print(f"{func.__name__!r} returned {result!r}")
                return result
        result = func(*args, **kwargs)
        return result

    return wrapper


def timeit(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if "timeit" in kwargs:
            if kwargs["timeit"]:
                ts = time.time()
                result = func(*args, **kwargs)
                te = time.time()
                print(f"({func.__name__} finished in {te - ts:0.6f}s)")
                return result
        result = func(*args, **kwargs)
        return result

    return wrapper
