#!/usr/bin/env python
'''
Routes for end to end testing, can only be called when in test mode.

'''
__author__ = 'M@Campbell'

from ooiservices.app.main import api

@api.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'
