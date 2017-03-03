#!/usr/bin/env python

"""
Support for uframe toc route(s), utilized for toc information.
"""
__author__ = 'Edna Donoughe'


from flask import jsonify, current_app
from ooiservices.app.uframe import uframe as api
from ooiservices.app.main.errors import internal_server_error
from ooiservices.app.uframe.toc_tools import process_uframe_toc


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# TOC routes and supporting functions
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@api.route('/get_toc')
def get_toc():
    """ Get uframe toc data; process and return data list; if exception then raise.
    """
    try:
        data = process_uframe_toc()
        if data is None:
            data = []
        return jsonify(toc=data)
    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        return internal_server_error(message)
