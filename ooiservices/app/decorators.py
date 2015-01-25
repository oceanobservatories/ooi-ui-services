#!/usr/bin/env python
'''
ooiservices.decorators

Custom decorators for OOI services
'''
__author__ = 'M@Campbell'

from functools import wraps
from flask import g
from ooiservices.app.main.errors import forbidden


def scope_required(scope):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not any(g.current_user.user_name in s for s in g.current_user.can(scope)):
                return forbidden('Scope required.')
            return f(*args, **kwargs)
        return decorated_function
    return decorator