
"""
Cruise routes and supporting functions.

Routes:
[GET]   /cruises                       # Get all cruises from uframe.
[GET]   /cruises/<int:id>              # Get cruise by event id.
[GET]   /cruises/<string:cruise_id>    # Get cruise by unique cruise id.
[GET]   /cruises/<int:id>/deployments  # Get all deployments for a cruise.
"""
__author__ = 'Edna Donoughe'

from flask import request, jsonify, current_app
from ooiservices.app.main.errors import (bad_request, conflict)
from ooiservices.app.uframe import uframe as api
from ooiservices.app.uframe.cruise_tools import (_get_cruise_by_cruise_id, _get_cruise_by_event_id,
                                                 _get_cruises, _get_cruise_deployments, _get_cruise_deployment)

# Get cruises.
@api.route('/cruises', methods=['GET'])
def get_cruises():
    """ Get list of cruises.
    """
    try:
        cruises_list = _get_cruises()
        print '\n deployments: ', len(cruises_list)
        return jsonify({'cruises': cruises_list})
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get cruise information by event id.
@api.route('/cruises/<int:event_id>', methods=['GET'])
def get_cruise_by_event_id(event_id):
    """ Get cruise (event) by event id.
    """
    try:
        result = _get_cruise_by_event_id(event_id)
        if result is None:
            result = {}
        return jsonify(result)

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get cruise information by unique cruise id.
@api.route('/cruises/<string:cruise_id>', methods=['GET'])
def get_cruise_by_cruise_id(cruise_id):
    """ Get cruise (event) by unique cruise id.
    """
    try:
        results = _get_cruise_by_cruise_id(cruise_id)
        if not results or results is None:
            message = 'No cruise with a unique cruise id of \'%s\' available.' % cruise_id
            return conflict(message)
        #print '\n deployments: ', len(results)
        return jsonify(results)

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get deployments for cruise using cruise id.
@api.route('/cruises/<string:cruise_id>/deployments', methods=['GET'])
def get_cruise_deployments(cruise_id):
    """ Get deployments for unique cruise id.

    Sample requests:
        localhost:4000/uframe/cruises/CP-2016-0001/deployments                           [all=deploy+recover]
        localhost:4000/uframe/cruises/CP-2016-0001/deployments?phase=deploy
        localhost:4000/uframe/cruises/CP-2016-0001/deployments?phase=recover
    """
    try:
        if not cruise_id:
            message = 'Invalid cruise id value, unable to get cruise deployments without valid cruise id.'
            raise Exception(message)

        # Determine if phase parameter provided, if so process
        type = None
        if request.args.get('phase'):
            type = request.args.get('phase')
        deployments = _get_cruise_deployments(cruise_id, type)
        return jsonify({'cruise_deployments': deployments})

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get deployment by event id.
@api.route('/cruises/deployment/<int:event_id>', methods=['GET'])
def get_deployment_by_id(event_id):
    """ Get deployment by event id; result used in deployment form view for UI.
    """
    try:
        if event_id <= 0:
            message = 'Invalid event id, failed to get deployment event id %d.' % event_id
            raise Exception(message)

        deployment = _get_cruise_deployment(event_id)
        return jsonify({'deployment': deployment})

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)