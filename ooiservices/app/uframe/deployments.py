
"""
Asset Management - Deployment routes.

Routes:

[GET]  /deployments/edit_phase_values   # Get edit phase values for deployments.
[GET]  /deployments/<int:event_id>      # Get deployment by event id.
[GET]  /deployments/<string:rd>         # Get deployments list by reference designator.

[POST]  /deployments                    # Create a deployment
[PUT]   /assets/<int:id>                # Update a deployment

*[GET]  /deployments/<string:rd>/deployment/<int:deployment_number> # Get deployment by reference designator and deployment_number

"""
__author__ = 'Edna Donoughe'

from flask import request, jsonify, current_app
from ooiservices.app.main.errors import bad_request
from ooiservices.app.uframe import uframe as api
from ooiservices.app.main.authentication import auth
from ooiservices.app.decorators import scope_required
from ooiservices.app.uframe.common_tools import deployment_edit_phase_values
from ooiservices.app.uframe.deployment_tools import (_get_deployment_subsites, _get_deployment_nodes,
                                                     _get_deployment_sensors, _get_deployments_by_rd)
from ooiservices.app.uframe.deployments_create_update import (_create_deployment, _update_deployment,
                                                              _get_deployment_by_event_id )
import json


# Get deployment edit phase values.
@auth.login_required
@scope_required(u'asset_manager')
@api.route('/deployments/edit_phase_values', methods=['GET'])
def get_deployment_edit_phase_values():
    """ Get deployment edit phase values.
    """
    return jsonify({'values': deployment_edit_phase_values()})


# Get deployment by event id.
@auth.login_required
@scope_required(u'asset_manager')
@api.route('/deployments/<int:event_id>', methods=['GET'])
def get_deployment_by_event_id(event_id):
    """ Get deployment by event id. Returns deployment dictionary or error.
    """
    try:
        result = _get_deployment_by_event_id(event_id)
        return jsonify(result)
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get deployments by reference designator.
@auth.login_required
@scope_required(u'asset_manager')
@api.route('/deployments/<string:rd>', methods=['GET'])
def get_deployments_by_rd(rd):
    """ Get deployments by reference designator, return list of deployment dictionaries, [], or error.

    Sample requests:
        http://localhost:4000/uframe/deployments/GS01SUMO
        http://localhost:4000/uframe/deployments/GS01SUMO-SBD12
        http://localhost:4000/uframe/deployments/GS01SUMO-SBD12-08-FDCHPA000

    Sample response (list of deployment dictionaries):
        {
          "deployments": [
            {
              "assetUid": null,
              "dataSource": "Load from [GS01SUMO_Deploy.xlsx]",
              "deployCruiseInfo": {
                "@class": ".CruiseInfo",
                "assetUid": null,
                "cruiseIdentifier": "AT26-29",
                "dataSource": "Load from [CruiseInformation.xlsx]",
                "editPhase": "OPERATIONAL",
                "eventId": 114,
                "eventName": "AT26-29",
                . . .
            },
            . . .
          ]
        }
    """
    try:
        result = _get_deployments_by_rd(rd)
        return jsonify({'deployments': result})
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Create deployment.
@auth.login_required
@scope_required(u'asset_manager')
@api.route('/deployments', methods=['POST'])
def create_deployment():
    """ Create deployment. Returns newly created deployment dictionary or error.
    """
    try:
        if not request.data:
            message = 'No data provided to create a deployment.'
            raise Exception(message)
        data = json.loads(request.data)
        deployment = _create_deployment(data)
        return jsonify({'deployment': deployment}), 201
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Update deployment.
@auth.login_required
@scope_required(u'asset_manager')
@api.route('/deployments/<int:event_id>', methods=['PUT'])
def update_deployment(event_id):
    """ Update deployment. Returns updated deployment or error
    """
    try:
        if not request.data:
            message = 'No data provided to update deployment %d.' % event_id
            raise Exception(message)
        data = json.loads(request.data)
        deployment = _update_deployment(event_id, data)
        result = jsonify({'deployment': deployment})
        return result
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get subsites in deployment inventory.
@api.route('/deployments/inv', methods=['GET'])
def get_deployment_subsites():
    """ Get list of subsites in deployment inventory.

    Sample:
        request:    http://localhost:4000/uframe/deployments/inv
        response:
            {
              "subsites": [
                {
                  "array": "Coastal Endurance",
                  "key": "CE01ISSM",
                  "name": "Oregon Inshore Surface Mooring",
                  "rd": "CE01ISSM"
                },
                {
                  "array": "Coastal Endurance",
                  "key": "CE01ISSP",
                  "name": "Oregon Inshore Surface Piercing Profiler Mooring",
                  "rd": "CE01ISSP"
                },
                . . .
              }
            }

    """
    try:
        subsites_list = _get_deployment_subsites()
        return jsonify({'subsites': subsites_list})
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get nodes in deployment inventory for a subsite.
@api.route('/deployments/inv/<string:subsite>', methods=['GET'])
def get_deployment_nodes(subsite):
    """ Get list of deployment nodes in inventory for a subsite.
    Sample:
        request:    http://localhost:4000/uframe/deployments/inv/CE01ISSM
        response:
            {
              "nodes": [
                {
                  "array": "Coastal Endurance",
                  "key": "MFC31",
                  "name": "Oregon Inshore Surface Mooring - Seafloor Multi-Function Node (MFN)",
                  "rd": "CE01ISSM-MFC31"
                },
                {
                  "array": "Coastal Endurance",
                  "key": "MFD35",
                  "name": "Oregon Inshore Surface Mooring - Seafloor Multi-Function Node (MFN)",
                  "rd": "CE01ISSM-MFD35"
                },
                . . .
              }
            }
    """
    try:
        nodes_list = _get_deployment_nodes(subsite)
        return jsonify({'nodes': nodes_list})
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get sensors in deployment inventory for a subsite and node.
@api.route('/deployments/inv/<string:subsite>/<string:node>', methods=['GET'])
def get_deployment_sensors(subsite, node):
    """ Get list of deployment sensors in inventory for a mooring and node.
    Sample
        request: http://localhost:4000/uframe/deployments/inv/CE01ISSM/MFC31
        response:
            {
              "sensors": [
                {
                  "array": "Coastal Endurance",
                  "key": "00-CPMENG000",
                  "name": "Platform Controller",
                  "rd": "CE01ISSM-MFC31-00-CPMENG000"
                }
              ]
            }

    """
    try:
        sensors_list = _get_deployment_sensors(subsite, node)
        return jsonify({'sensors': sensors_list})
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)