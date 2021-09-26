# Copyright 2018, National Technology & Engineering Solutions of Sandia, LLC
# (NTESS).  Under the terms of Contract DE-NA0003525 with NTESS, the U.S.
# Government retains certain rights in this software.

"""Adapted from https://github.com/salesforce/decorator-operations."""

import functools
import threading

def debounce(wait):
    def decorator(f):
        @functools.wraps(f)
        def debounced(*args, **kwargs):
            def call_function():
                debounced._timer = None
                f(*args, **kwargs)
            if debounced._timer is not None:
                debounced._timer.cancel()
            debounced._timer = threading.Timer(wait, call_function)
            debounced._timer.start()
        debounced._timer = None
        return debounced
    return decorator

