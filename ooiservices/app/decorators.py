#!/usr/bin/env python
'''
ooiservices.decorators

Custom decorators for OOI services
'''
__author__ = 'M@Campbell'

from functools import wraps
from flask import g
from ooiservices.app.main.errors import forbidden
from flask import jsonify

def scope_required(scope):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.current_user.can(scope):
                return forbidden('Scope %s required.' % scope)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def json(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        rv = f(*args, **kwargs)

        status = None
        headers = None

        if isinstance(rv, tuple):
            rv, status, headers = rv + (None,) * (3 - len(rv))
        if isinstance(status, (dict, list)):
            headers, status = status, None

        if not isinstance(rv, dict):
            rv = rv.export_data()

        rv = jsonify(rv)
        if status is not None:
            rv.status_code = status
        if headers is not None:
            rv.headers.extend(headers)
        return rv
    return wrapped
