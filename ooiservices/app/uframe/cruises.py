
"""
Asset Management - Cruise routes.

Routes:
[GET]   /cruises                                 # Get all cruises in inventory.
[GET]   /cruises/<int:id>                        # Get cruise by event id.
[GET]   /cruises/<string:event_id>/deployments   # Get all deployments for a cruise by unique cruise identifier.
[GET]   /cruises/<int:event_id>/deployment       # Get a specific deployment for a specific cruise.
"""
__author__ = 'Edna Donoughe'

from flask import request, jsonify, current_app
from ooiservices.app.main.errors import bad_request
from ooiservices.app.uframe import uframe as api
from ooiservices.app.uframe.cruise_tools import (_get_cruises, _get_cruise,_get_cruise_deployments,
                                                 _get_cruise_deployment)


# Get cruises.
@api.route('/cruises', methods=['GET'])
def get_cruises():
    """ Get list of cruises.
    """
    try:
        cruises_list = _get_cruises()
        return jsonify({'cruises': cruises_list})
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get cruise information by event id.
@api.route('/cruises/<int:event_id>', methods=['GET'])
def get_cruise(event_id):
    """ Get cruise by event id.
    """
    try:
        result = _get_cruise(event_id)
        return jsonify(result)
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get deployments for cruise using event id.
@api.route('/cruises/<int:event_id>/deployments', methods=['GET'])
def get_cruise_deployments(event_id):
    """ Get deployments for cruise event id.

    Sample requests:
        localhost:4000/uframe/cruises/10/deployments                           [all=deploy+recover]
        localhost:4000/uframe/cruises/10/deployments?phase=deploy
        localhost:4000/uframe/cruises/10/deployments?phase=recover
    """
    try:
        if event_id < 1:
            message = 'Invalid event id (%d), must be a valid event id.' % event_id
            raise Exception(message)
        # Determine if phase parameter provided, if so process
        type = None
        if request.args.get('phase'):
            type = request.args.get('phase')
        deployments = _get_cruise_deployments(event_id, type)
        return jsonify({'cruise_deployments': deployments})
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get deployment by event id.
@api.route('/cruises/<int:event_id>/deployment', methods=['GET'])
def get_cruise_deployment(event_id):
    """ Get deployment by event id; result to be used in deployment form view for UI.
    """
    try:
        if event_id < 1:
            message = 'Invalid event id, failed to get deployment event id %d.' % event_id
            raise Exception(message)
        deployment = _get_cruise_deployment(event_id)
        return jsonify({'deployment': deployment})
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)