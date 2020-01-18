
"""
Asset Management - Status routes.

Routes:

[GET]  /status/arrays                               # Get status for all arrays.
[GET]  /status/sites/<string:array_rd>              # Get status for sites associated with an array.
[GET]  /status/platforms/<string:site_rd>           # Get status for platforms associated with a site.
[GET]  /status/instrument/<string:instrument_rd>    # Get instrument status.

"""
__author__ = 'Edna Donoughe'

from flask import jsonify, current_app
from ooiservices.app.main.errors import bad_request
from ooiservices.app.uframe import uframe as api
from ooiservices.app.uframe.status_tools import (_get_status_arrays, _get_status_sites,
                                                 _get_status_platforms, _get_status_instrument)


# Get status for all arrays.
@api.route('/status/arrays', methods=['GET'])
def get_status_arrays():
    """ Get status information for arrays.
    Sample request: http://localhost:4000/uframe/status/arrays
    """
    results = []
    try:
        data = _get_status_arrays()
        if data and data is not None:
            results = data
        return jsonify({'arrays': results})
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get status for sites associated with an array.
@api.route('/status/sites/<string:array_rd>', methods=['GET'])
def get_status_sites(array_rd):
    """ Get status for sites associated with an array.
    Sample request: http://localhost:4000/uframe/status/sites/CE
    """
    results = []
    try:
        data = _get_status_sites(array_rd)
        if data and data is not None:
            results = data
        return jsonify({'sites': results})
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get statuses for platforms associated with a site.
@api.route('/status/platforms/<string:site_rd>', methods=['GET'])
def get_status_platforms(site_rd):
    """ Get statuses for platforms associated with a site.
    Sample request: http://localhost:4000/uframe/status/platforms/CE01ISSM
    """
    results = []
    try:
        #data = _nav_get_platforms(site_rd)
        data = _get_status_platforms(site_rd)
        if data and data is not None:
            results = data
        return jsonify({'platforms': results})
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get instrument status.
@api.route('/status/instrument/<string:instrument_rd>', methods=['GET'])
def get_status_instrument(instrument_rd):
    """ Get instrument status.
    Sample request: http://localhost:4000/uframe/status/instrument/CE01ISSM-SBD17-03-DOSTAD000
    """
    results = []
    try:
        data = _get_status_instrument(instrument_rd)
        if data and data is not None:
            results = data
        return jsonify({'instrument': results})
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)