#!/usr/bin/env python
'''
Routes for end to end testing, can only be called when in test mode.

'''
__author__ = 'M@Campbell'

from flask import jsonify, request, abort, current_app
from ooiservices.app.main import api
from ooiservices import manage
import urllib

@api.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'

@api.route('/list_routes', methods=['GET'])
def list_routes():
    """
    Create a list of (url, endpoint) tuples from app.url_map
    Used for performance testing
    :return:
    """
    app = manage.app
    routes = []
    for rule in app.url_map.iter_rules():
        if 'GET' in rule.methods:
            url = urllib.unquote("{}".format(rule))
            routes.append((url, rule.endpoint))

    if not routes:
        return '{}', 204

    return jsonify({'routes' : routes})

