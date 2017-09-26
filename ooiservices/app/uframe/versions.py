#!/usr/bin/env python

"""
Support functions for uframe/component version information.
"""
__author__ = 'Edna Donoughe'


from flask import (jsonify, current_app)
from ooiservices.app.uframe import uframe as api
from ooiservices.app.main.errors import bad_request
from ooiservices.app.uframe.uframe_tools import uframe_get_versions


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Get uframe versions information.
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
@api.route('/versions')
def uframe_versions():
    try:
        # Get a list of component dictionaries.
        """
        [
         {"component":"uFrame", "version": "v1.2.4", "release": "2017-08-14"},
         {"component":"mi-instrument", "version": "v1.2.1", "release": "2017-04-24"}
        ]
        """
        results = uframe_get_versions()
        return jsonify({'versions': results}), 200
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


@api.route('/versions/<string:component>')
def uframe_versions_component(component=None):
    """
    Get version information for a specific component.
    """
    try:
        # Get a specific component from list of uframe version component dictionaries.
        result = uframe_get_versions(component=component)
        # To just return the uframe component information.
        if result and result is not None:
            if 'component' in result:
                if result['component'] == component:
                    return jsonify({'component_versions': result}), 200
        else:
            message = 'Null or empty result returned from uframe for version of component: %s. ' % component
            message += 'Please verify the component name provided is a valid component name.'
            raise Exception(message)

        return jsonify({'result': result}), 200
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)
