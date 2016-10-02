"""
Asset Management - Deployments: Create and update functions.
"""
__author__ = 'Edna Donoughe'

from flask import current_app
from ooiservices.app.uframe.common_tools import (get_class_deployment, get_asset_class_by_asset_type, is_instrument,
                                                 dump_dict)
from ooiservices.app.uframe.config import (get_uframe_deployments_info, get_deployments_url_base, headers)
from ooiservices.app.uframe.deployments_validate_fields import deployments_validate_required_fields_are_provided
from ooiservices.app.uframe.uframe_tools import get_uframe_event
from ooiservices.app.uframe.deployment_cache_tools import refresh_deployment_cache
from ooiservices.app.uframe.events_create_update import update_event_type
from ooiservices.app.uframe.deployment_tools import (format_deployment_for_ui, get_rd_deployments)
from ooiservices.app.uframe.assets_create_update import refresh_asset_deployment
from copy import deepcopy
import requests
from requests.exceptions import (ConnectionError, Timeout)
import json


# Create deployment.
def _create_deployment(data):
    """ Create a new deployment, return new deployment on success. On failure, log and raise exception.
    curl -H "Content-Type: application/json" -X POST --upload-file ui_deployment_create.txt  http://localhost:4000/uframe/deployments
    Input data:
    {
        "assetUid" : null,
        "rd": "CE01ISSP-SP001-02-DOSTAJ000",
        "dataSource": "UI:user=edna",
        "deployCruiseInfo": null,
        "deployedBy": "Test engineer",
        "deploymentNumber": 3027,
        "editPhase" : "OPERATIONAL",
        "eventName": "Coastal Pioneer:Central Surface Piercing Profiler Mooring",
        "eventStartTime": 1506434340000,
        "eventStopTime": 1509034390000,
        "eventType": "DEPLOYMENT",
        "inductiveId" : null,
        "ingestInfo": null,
        "depth": 0.0,
        "longitude" : -124.09567,
        "latitude" : 44.66415,
        "orbitRadius": 0.0,
        "mooring_uid": "N00262",
        "node_uid": "N00122",
        "notes" : null,
        "recoverCruiseInfo": null,
        "recoveredBy": "Test engineer",
        "sensor_uid": "N00580",
        "tense": "UNKNOWN",
        "versionNumber": 3027
    }
    """
    debug = False
    action = 'create'
    try:
        if not data:
            message = 'Data is required to create a deployment, none provided.'
            raise Exception(message)

        # Transform input data from UI into format required by uframe for create.
        xdeployment = transform_deployment_for_uframe(None, data, action=action)
        if not xdeployment or xdeployment is None:
            print '\n debug -- Failed to receive xdeployment from transform_deployment_for_uframe...'

        if debug:
            print '\n debug -- xdeployment: '
            dump_dict(xdeployment, debug)

        # Create new asset in uframe.
        new_uframe_deployment = uframe_create_deployment(xdeployment)

        # Get deployment event id
        id = None
        if new_uframe_deployment:
            if 'eventId' in new_uframe_deployment:
                id = new_uframe_deployment['eventId']
        if id is None:
            message = 'Failed to retrieve id from newly created deployment in uframe.'
            raise Exception(message)

        # Format uframe deployment data for UI.
        ui_deployment = format_deployment_for_ui(new_uframe_deployment)
        if not ui_deployment or ui_deployment is None:
            message = 'Failed to format uframe deployment for UI; deployment event id: %d' % id
            raise Exception(message)

        # Minimize data for cache.
        deployment_store = deepcopy(ui_deployment)
        if 'deployCruiseInfo' in deployment_store:
            del deployment_store['deployCruiseInfo']
        if 'recoverCruiseInfo' in deployment_store:
            del deployment_store['recoverCruiseInfo']
        if 'ingestInfo' in deployment_store:
            del deployment_store['ingestInfo']
        if 'location' in deployment_store:
            del deployment_store['location']
        if debug:
            print '\n debug -- deployment_store...'
            dump_dict(deployment_store, debug)

        # Refresh deployment cache - todo - finish refresh_deployment_cache, move to asset_cache_tools
        if debug: print '\n debug -- calling refresh_deployment_cache...'
        refresh_deployment_cache(id, deployment_store, action)

        # Refresh deployment information for assets associated with deployment.
        if 'mooring_uid' in ui_deployment:
            mooring_uid = ui_deployment['mooring_uid']
            if mooring_uid and mooring_uid is not None:
                if debug: print '\n\t debug -- refresh_asset_deployment: mooring_uid: ', mooring_uid
                refresh_asset_deployment(mooring_uid)
        if 'node_uid' in ui_deployment:
            node_uid = ui_deployment['node_uid']
            if node_uid and node_uid is not None:
                if debug: print '\n\t debug -- refresh_asset_deployment: node_uid: ', node_uid
                refresh_asset_deployment(node_uid)
        if 'sensor_uid' in ui_deployment:
            sensor_uid = ui_deployment['sensor_uid']
            if sensor_uid and sensor_uid is not None:
                if debug: print '\n\t debug -- refresh_asset_deployment: sensor_uid: ', sensor_uid
                refresh_asset_deployment(sensor_uid)

        if debug: print '\n debug -- after calling refresh_deployment_cache...'


        # return updated deployment
        return ui_deployment


    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# Update deployment.
def _update_deployment(id, data):
    """ Update deployment, deployment is returned on success. On failure, log and raise exception.
    curl -H "Content-Type: application/json" -X PUT --upload-file ui_deployment_update.txt  http://localhost:4000/uframe/deployments/38105
    """
    action = 'update'
    try:
        # Transform input data for uframe.
        xdeployment = transform_deployment_for_uframe(id, data, action=action)
        if not xdeployment or xdeployment is None:
            message = 'Failed to format information for uframe update, deployment event id: %d' % id
            raise Exception(message)

        xdeployment_keys = xdeployment.keys()
        xdeployment_keys.sort()

        # Verify asset exists:
        # Get uframe deployment (for 'ingestInfo', 'lastModifiedTimestamp')
        deployment = get_uframe_event(id)
        if not deployment or deployment is None:
            message = 'Failed to get deployment with event id %d from uframe.' % id
            raise Exception(message)

        keys = []
        if deployment:
            keys = deployment.keys()
            keys.sort()

        # Deployments: Reserved fields: fields which may not be modified by UI once assigned in uframe:
        #   eventId, lastModifiedTimestamp, assetUid
        reserved_fields = ['eventId', 'lastModifiedTimestamp', 'assetUid']

        # Determine any missing items are in valid items list, is not error.
        valid_missing_keys = ['ingestInfo']

        # Assets: Fields location and events are not provided by UI, get from asset. If asset is Sensor, calibration too.
        missing_keys = []
        for key in keys:
            if key not in xdeployment_keys:
                if key not in valid_missing_keys:
                    message = 'Input data is invalid; missing required key: %s' % key
                    raise Exception(message)
                if key not in missing_keys:
                    missing_keys.append(key)

        # Apply standard fields.
        for key in valid_missing_keys:
            xdeployment[key] = deployment[key]

        # Apply reserved fields.
        for key in reserved_fields:
            xdeployment[key] = deployment[key]

        # Check all keys required are accounted for.
        xdeployment_keys = xdeployment.keys()
        xdeployment_keys.sort()
        for key in keys:
            if key not in xdeployment_keys:
                message = 'Missing required attribute \'%s\'.' % key
                raise Exception(message)

        # Update deployment in uframe.
        #modified_deployment = uframe_update_deployment(xdeployment)

        # Update deployment event.
        modified_deployment = update_event_type(id, xdeployment)
        """
        id = uframe_put_event(event_type, id, xdeployment)
        # Get updated event, return event
        modified_deployment = get_uframe_event(id)
        """

        # Format modified asset from uframe for UI.
        ui_deployment = format_deployment_for_ui(modified_deployment)

        # Minimize data for cache.
        deployment_store = deepcopy(ui_deployment)
        if 'deployCruiseInfo' in deployment_store:
            del deployment_store['deployCruiseInfo']
        if 'recoverCruiseInfo' in deployment_store:
            del deployment_store['recoverCruiseInfo']
        if 'ingestInfo' in deployment_store:
            del deployment_store['ingestInfo']
        if 'location' in deployment_store:
            del deployment_store['location']

        refresh_deployment_cache(id, deployment_store, action)

        # Refresh deployment information for assets associated with deployment.
        if 'mooring_uid' in ui_deployment:
            mooring_uid = ui_deployment['mooring_uid']
            if mooring_uid and mooring_uid is not None:
                refresh_asset_deployment(mooring_uid)
        if 'node_uid' in ui_deployment:
            node_uid = ui_deployment['node_uid']
            if node_uid and node_uid is not None:
                refresh_asset_deployment(node_uid)
        if 'sensor_uid' in ui_deployment:
            sensor_uid = ui_deployment['sensor_uid']
            if sensor_uid and sensor_uid is not None:
                refresh_asset_deployment(sensor_uid)

        # return updated asset
        return ui_deployment

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def transform_deployment_for_uframe(id, deployment, action=None):
    """ Transform UI deployment data into uframe deployment structure.
    """
    uframe_deployment = {}
    valid_actions = ['create', 'update']
    try:

        if action is None:
            message = 'Failed to transform deployment, action value is None.'
            raise Exception(message)
        if action not in valid_actions:
            message = 'Invalid action (%s) for transform deployment for uframe.' % action
            raise Exception(message)

        deployment['@class'] = get_class_deployment()

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Perform basic checks on input data
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not deployment:
            message = 'No input provided, unable to process transform for deployment %s.' % action
            raise Exception(message)

        #- - - - - - - - - - - - - - - - - - - - - -
        # Convert values for fields in 'string asset'
        #- - - - - - - - - - - - - - - - - - - - - -
        converted_deployment = deployments_validate_required_fields_are_provided(deployment, action)

        # Action 'update' specific check: verify asset id in data is same as asset id on PUT
        if action == 'update':
            if 'eventId' in converted_deployment:
                if converted_deployment['eventId'] != id:
                    message = 'The deployment event id provided in url does not match id provided in data.'
                    raise Exception(message)

        # Get rd in ui deployment
        if 'rd' not in converted_deployment:
            message = 'Unable to process deployment provided, no reference designator.'
            raise Exception(message)
        if not converted_deployment['rd']:
            message = 'Unable to process deployment provided, empty reference designator.'
            raise Exception(message)

        # Build referenceDesignator dictionary.
        rd = converted_deployment['rd']
        if not is_instrument(rd):
            message = 'The reference designator provided does not contain subsite, node and sensor.'
            raise Exception(message)

        # Build referenceDesignator
        subsite, node, sensor = rd.split('-', 2)
        referenceDesignator = { 'subsite': subsite, 'node': node, 'sensor': sensor}
        uframe_deployment['referenceDesignator'] = referenceDesignator

        # Build location dictionary attribute.
        location = None
        latitude = None
        if 'latitude' in converted_deployment:
            latitude = converted_deployment['latitude']
        longitude = None
        if 'longitude' in converted_deployment:
            longitude = converted_deployment['longitude']
        orbitRadius = 0.0
        if 'orbitRadius' in converted_deployment:
            orbitRadius = converted_deployment['orbitRadius']
        depth = 0.0
        if 'depth' in converted_deployment:
            depth = converted_deployment['depth']

        # If latitude and longitude both provided, build location dictionary.
        if latitude is None or longitude is None:
            location = None
        else:
            location = {}
            location['latitude'] = latitude
            location['longitude'] = longitude
            location['orbitRadius'] = orbitRadius
            location['depth'] = depth
            location['location'] = {}
            location['location'] = [longitude, latitude]
        uframe_deployment['location'] = location

        # Get deploymentNumber in ui deployment
        if 'deploymentNumber' not in converted_deployment:
            message = 'Unable to process deployment provided, no deploymentNumber.'
            raise Exception(message)
        if not converted_deployment['deploymentNumber']:
            message = 'Unable to process deployment provided, deploymentNumber is empty.'
            raise Exception(message)
        uframe_deployment['deploymentNumber'] = converted_deployment['deploymentNumber']

        # Ensure 'tense' attribute is available.
        if 'tense' in converted_deployment:
            uframe_deployment['tense'] = converted_deployment['tense']
        else:
            uframe_deployment['tense'] = None

        # Get versionNumber in ui deployment
        if 'versionNumber' not in converted_deployment:
            message = 'Unable to process deployment provided, no versionNumber.'
            raise Exception(message)
        if not converted_deployment['versionNumber']:
            message = 'Unable to process deployment provided, versionNumber is empty.'
            raise Exception(message)
        uframe_deployment['versionNumber'] = converted_deployment['versionNumber']

        # mooring attribute.
        if converted_deployment['mooring_uid'] is None:
            uframe_deployment['mooring'] = None
        else:
            uframe_deployment['mooring'] = {}
            uframe_deployment['mooring']['uid'] = converted_deployment['mooring_uid']
            uframe_deployment['mooring']['@class'] = get_asset_class_by_asset_type('Mooring')

        # node attribute.
        if converted_deployment['node_uid'] is None:
            uframe_deployment['node'] = None
        else:
            uframe_deployment['node'] = {}
            uframe_deployment['node']['uid'] = converted_deployment['node_uid']
            uframe_deployment['node']['@class'] = get_asset_class_by_asset_type('Node')

        # sensor attribute.
        if converted_deployment['sensor_uid'] is None:
            uframe_deployment['sensor'] = None
        else:
            uframe_deployment['sensor'] = {}
            uframe_deployment['sensor']['uid'] = converted_deployment['sensor_uid']
            uframe_deployment['sensor']['@class'] = get_asset_class_by_asset_type('Sensor')

        # Get deployCruiseInfo provided.
        if 'deployCruiseInfo' in converted_deployment:
            if converted_deployment['deployCruiseInfo'] is not None:
                uframe_deployment['deployCruiseInfo'] = converted_deployment['deployCruiseInfo']
            else:
                uframe_deployment['deployCruiseInfo'] = None

        # Get recoverCruiseInfo provided.
        if 'recoverCruiseInfo' in converted_deployment:
            if converted_deployment['recoverCruiseInfo'] is not None:
                uframe_deployment['recoverCruiseInfo'] = converted_deployment['recoverCruiseInfo']
            else:
                uframe_deployment['recoverCruiseInfo'] = None

        # todo - Sprint 2, not yet supported completely in uframe.
        uframe_deployment['ingestInfo'] = None

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Marshall all remaining data for creation of uframe_deployment.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get the rest of the fields and values.
        regular_fields = ['assetUid', 'dataSource', 'deployedBy',
                          'editPhase', 'eventId', 'eventName', 'eventStartTime', 'eventStopTime', 'eventType',
                          'inductiveId', 'notes', 'recoveredBy']
        for key in regular_fields:
            if key in converted_deployment:
                uframe_deployment[key] = converted_deployment[key]

        # Fields: eventId, assetUid, lastModifiedTimestamp
        uframe_deployment['@class'] = get_class_deployment()
        if action == 'update':
            uframe_deployment['eventId'] = converted_deployment['eventId']
            uframe_deployment['lastModifiedTimestamp'] = converted_deployment['lastModifiedTimestamp']
        else:
            uframe_deployment['lastModifiedTimestamp'] = None
            uframe_deployment['eventId'] = -1

        #- - - - - - - - - - - - - - - - - - - - - -
        # Validate uframe_deployment object - fields present
        #- - - - - - - - - - - - - - - - - - - - - -
        #required_fields, field_types = deployment_get_required_fields_and_types_uframe(action)
        uframe_deployment_keys = uframe_deployment.keys()
        uframe_deployment_keys.sort()
        return uframe_deployment

    except Exception as err:
        message = str(err)
        raise Exception(message)


# Create asset in uframe.
def uframe_create_deployment(deployment):
    """ Create deployment in uframe. On success return updated asset, on error, raise exception.
    """
    debug = False
    check = False
    success = 'CREATED'
    try:
        if debug:
            print '\n debug -- entered uframe_create_deployment...'
            dump_dict(deployment, debug)
        # Check deployment data provided.
        if not deployment or deployment is None:
            message = 'Deployment data must be provided to create deployment in uframe.'
            raise Exception(message)
        if not isinstance(deployment, dict):
            message = 'Deployment data must be provided in dict form to create deployment in uframe.'
            raise Exception(message)

        # Create deployment in uframe.
        base_url, timeout, timeout_read = get_uframe_deployments_info()
        url = '/'.join([base_url, get_deployments_url_base()])
        if check: print '\n check: url: ', url
        response = requests.post(url, data=json.dumps(deployment), headers=headers())
        if debug:
            print '\n response.status_code: ', response.status_code
            if response.content:
                print '\n debug -- response.content: ', json.loads(response.content)
        if response.status_code != 201:
            message = '(%d) uframe failed to create deployment.' % response.status_code
            if response.content:
                uframe_message = json.loads(response.content)
                if 'message' in uframe_message:
                    uframe_message = uframe_message['message']
                message += ' %s' % uframe_message
            current_app.logger.info(message)
            raise Exception(message)

        # Get id for new deployment.
        if not response.content:
            message = 'No response content returned from create asset.'
            raise Exception(message)

        # Review response.content:
        #   {u'message': u'Element created successfully.', u'id': 4292, u'statusCode': u'CREATED'}
        response_data = json.loads(response.content)
        if debug: print '\n debug -- response_data: ', response_data
        id = None
        if 'id' in response_data and 'statusCode' in response_data:
            if response_data['statusCode'] and response_data['id']:
                if response_data['statusCode'] == success and response_data['id'] > 0:
                    id = response_data['id']
        if id is None:
            message = 'Failed to create uframe deployment.'
            raise Exception(message)

        # Get new deployment from uframe.
        new_deployment = get_uframe_event(id)
        if not new_deployment or new_deployment is None:
            message = 'Failed to get deployment with event id %d from uframe.' % id
            raise Exception(message)
        return new_deployment
    except ConnectionError:
        message = 'Error: ConnectionError during uframe create deployment.'
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Error: Timeout during during uframe create deployment.'
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


# get deployment by event id, return formmated for ui.
def _get_deployment_by_event_id(event_id):
    """ Get ui formatted deployment event by event id.
    """
    try:
        # Get deployment event from uframe.
        uframe_deployment = get_uframe_event(event_id)
        if not uframe_deployment or uframe_deployment is None:
            message = 'Failed to get deployment with event id %d from uframe.' % event_id
            raise Exception(message)
        # Format deployment event for ui.
        ui_deployment = format_deployment_for_ui(uframe_deployment)
        return ui_deployment

    except Exception as err:
        message = str(err)
        raise Exception(message)


# Get list of deployments, return formatted for ui.
def _get_deployments_by_rd(rd):
    """ Get list of deployments for a reference designator; return formatted for UI.
    """
    ui_deployments = []
    try:
        # Get deployment event from uframe.
        uframe_deployments = get_rd_deployments(rd)
        if not uframe_deployments or uframe_deployments is None:
            message = 'Failed to get deployments using reference designator \'%s\' from uframe.' % rd
            raise Exception(message)

        # Format deployment event for ui.
        for uframe_deployment in uframe_deployments:
            ui_deployment = format_deployment_for_ui(uframe_deployment)
            if not ui_deployment and ui_deployment is not None:
                continue
            ui_deployments.append(ui_deployment)
        return ui_deployments

    except Exception as err:
        message = str(err)
        raise Exception(message)