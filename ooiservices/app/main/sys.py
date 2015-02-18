#!/usr/bin/env python
'''
Routes for end to end testing, can only be called when in test mode.

'''
__author__ = 'M@Campbell'

from flask import jsonify, current_app
from ooiservices.app.main import api
import urllib

@api.route('/list_routes', methods=['GET'])
def list_routes():
    """
    Create a list of (url, endpoint) tuples from app.url_map
    Used for performance testing
    :return:
    """
    routes = []
    for rule in current_app.url_map.iter_rules():
        if 'GET' in rule.methods:
            url = urllib.unquote("{}".format(rule))
            routes.append((url, rule.endpoint))

    if not routes:
        return '{}', 204

    return jsonify({'routes' : routes})

