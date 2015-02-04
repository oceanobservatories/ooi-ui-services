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
            if not g.current_user.can(scope):
                return forbidden('Scope %s required.' % scope)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
