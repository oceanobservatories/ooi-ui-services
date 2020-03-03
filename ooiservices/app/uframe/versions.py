#!/usr/bin/env python

"""
Support functions for uframe/component version information.
"""
__author__ = 'Edna Donoughe'


from flask import (jsonify, current_app)
from ooiservices.app.uframe import uframe as api
from ooiservices.app.main.errors import bad_request
from ooiservices.app.uframe.uframe_tools import (uframe_get_versions, uframe_get_component_version, uframe_get_versions_list)


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


@api.route('/versions/<string:component>/release_notes')
def uframe_versions_component_release_notes(component=None):
    """
    Get release notes information for a specific component; descending version values.
    http://uframe-test.intra.oceanobservatories.org:12590/versions/uFrame/1.2.7

    Request: http://localhost:4000/uframe/versions/uFrame/release_notes
    Response:
    {
      "release_notes": [
        {
          "component": "uFrame",
          "notes": [
            "Develop a strategy for separately deploying uFrame software on test systems. (12557)",
            "Prevent creating/updating annotations where beginDT > endDT. (12509)",
            "Add support for open-ended annotations. (11444)",
            "Add virtual streams to stream and partition metadata on ingest. (12488)",
            "Handle \"PD\" prefix in alert filter pdIds. (12172)",
            "Enhance ingestion logging in EDEX. (12618)",
            "Uncabled_ingest mode unable to start. (12581)",
            "Gracefully handle error in Sensor Inventory Service TOC endpoint. (12546)",
            "Fix DOI SQL Errors on uframe-test and production. (12580)",
            "Add version endpoint. (12497)"
          ],
          "release": "2017-09-00",
          "version": "1.2.7"
        },
        {
          "component": "uFrame",
          "notes": [
            "Expand ingest request types in EDEX to include cabled playback. (12530)",
            "Handle comma separated values for param in data file ingestion. (12506)",
            "Expose data purge through web service. (12485)",
            "Drop FK constraint in new ingest engine. (12440)",
            "Promote uncabled particle timestamps from long to double if needed. (12434)",
            "Create ingestion tool for telemetered and recovered data. (12140)",
            "Increase default max memory. (12455)",
            "Add QcFlag Validation. (12461)",
            "DOI cruise handling and asset management updates. (12443)"
          ],
          "release": "2017-08-01",
          "version": "1.2.6"
        },
        . . .
        ]
    }
    """
    results = []
    try:
        # Get a specific component from list of EDEX version component dictionaries.
        versions_list = uframe_get_versions_list(component=component)
        # To just return the uframe component information.
        if not versions_list or versions_list is None:
            message = 'No versions returned for component: %s. ' % component
            message += 'Please verify the component name provided is a valid component name.'
            raise Exception(message)

        versions_list.sort(key=lambda s: map(int, s.split('.')), reverse=True)
        for version in versions_list:
            result = uframe_get_component_version(component, version)
            if result and result is not None:
                results.append(result)
        return jsonify({'release_notes': results}), 200
    except Exception as err:
        message = str(err)
        return bad_request(message)
