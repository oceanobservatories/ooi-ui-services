"""
Asset Management - Deployments: Create and update functions.
"""
__author__ = 'Edna Donoughe'

from flask import current_app
from copy import deepcopy
from ooiservices.app.uframe.deployments_validate_fields import deployments_validate_required_fields_are_provided
from ooiservices.app.uframe.uframe_tools import (get_uframe_event, uframe_create_deployment)
from ooiservices.app.uframe.deployment_tools import format_deployment_for_ui
from ooiservices.app.uframe.events_create_update import update_event_type
from ooiservices.app.uframe.assets_create_update import refresh_asset_deployment
from ooiservices.app.uframe.common_tools import (get_class_deployment, get_asset_class_by_asset_type, get_event_class,
                                                 is_instrument, is_platform, is_mooring, get_location_dict)

#from ooiservices.app.uframe.deployment_cache_tools import refresh_deployment_cache
# Create deployment.
def _create_deployment(data):
    """ Create a new deployment, return new deployment on success. On failure, log and raise exception.
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
        "versionNumber": 3027
    }
    """
    action = 'create'
    try:
        if not data:
            message = 'Data is required to create a deployment, none provided.'
            raise Exception(message)

        # Transform input data from UI into format required by uframe for create.
        xdeployment = transform_deployment_for_uframe(None, data, action=action)
        if not xdeployment or xdeployment is None:
            message = 'Failed to receive xdeployment from transform_deployment_for_uframe.'
            raise Exception(message)

        # Create new deployment in uframe.
        new_uframe_deployment = uframe_create_deployment(xdeployment)

        # Get deployment event id
        id = None
        if new_uframe_deployment:
            if 'eventId' in new_uframe_deployment:
                id = new_uframe_deployment['eventId']
        if id is None:
            message = 'Failed to retrieve id from newly created deployment in uframe.'
            raise Exception(message)

        # Get original ids from uframe deployment object.
        mid, nid, sid = get_ids_from_deployment(new_uframe_deployment)

        # Get reference designator from request data.
        rd = None
        if 'rd' in data:
            rd = data['rd']
        if not rd or rd is None:
            message = 'Unable to refresh assets associated with deployment, no reference designator in request data.'
            raise Exception(message)

        # Get deployment number from newly created uframe deployment.
        deploymentNumber = None
        if 'deploymentNumber' in new_uframe_deployment:
            deploymentNumber = new_uframe_deployment['deploymentNumber']
        if not deploymentNumber or deploymentNumber is None:
            message = 'Unable to refresh assets associated with deployment, no deployment number.'
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

        # Refresh deployment cache for newly created deployment.
        #refresh_deployment_cache(id, deployment_store, action, mid, nid, sid)

        # Get reference designator from request data.
        rd = None
        if 'rd' in data:
            rd = data['rd']
        if not rd or rd is None:
            message = 'Unable to refresh assets associated with deployment, no reference designator in request data.'
            raise Exception(message)

        # Update deployment assets. Any asset associated with this deployment will have cache updated here.
        update_deployment_assets(ui_deployment, rd)

        # return updated deployment
        return ui_deployment
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# Update deployment.
def _update_deployment(id, data):
    """ Update deployment, deployment is returned on success. On failure, log and raise exception.
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

        # Verify deployment exists:
        # Get uframe deployment (for 'ingestInfo', 'lastModifiedTimestamp', 'eventId' and 'assetUID')
        deployment = get_uframe_event(id)
        if not deployment or deployment is None:
            message = 'Failed to get deployment with event id %d from uframe.' % id
            raise Exception(message)

        # Get original ids from uframe deployment object.
        mid, nid, sid = get_ids_from_deployment(deployment)

        keys = []
        if deployment:
            keys = deployment.keys()
            if keys:
                keys.sort()

        # Deployments: Reserved fields: fields which may not be modified by UI once assigned in uframe:
        #   eventId, lastModifiedTimestamp, assetUid
        reserved_fields = ['eventId', 'lastModifiedTimestamp', 'assetUid']

        # Determine any missing items are in valid items list, is not error.
        valid_missing_keys = ['ingestInfo']

        # Deployments: Fields location and events are not provided by UI, get from deployment.
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
        modified_deployment = update_event_type(id, xdeployment)

        # Format modified deployment from uframe for UI.
        ui_deployment = format_deployment_for_ui(modified_deployment)

        # Minimize data for cache.
        deployment_store = deepcopy(ui_deployment)
        if 'ingestInfo' in deployment_store:
            del deployment_store['ingestInfo']
        if 'location' in deployment_store:
            del deployment_store['location']

        # Do cache refresh for deployment
        #refresh_deployment_cache(id, deployment_store, action, mid, nid, sid)

        # Get reference designator from request data.
        rd = None
        if 'rd' in data:
            rd = data['rd']
        if not rd or rd is None:
            message = 'Unable to refresh assets associated with deployment, no reference designator in request data.'
            raise Exception(message)

        # update deployment assets. Any asset associated with this deployment will have cache updated here.
        update_deployment_assets(ui_deployment, rd)

        # return updated deployment
        return ui_deployment

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def get_ids_from_deployment(uframe_deployment):
    """ For a uframe deployment get all three uids.
    """
    mooring_id = None
    node_id = None
    sensor_id = None
    try:
        if 'mooring' in uframe_deployment:
            if uframe_deployment['mooring'] and uframe_deployment['mooring'] is not None:
                if 'assetId' in uframe_deployment['mooring']:
                    mooring_id = uframe_deployment['mooring']['assetId']

        if 'node' in uframe_deployment:
            if uframe_deployment['node'] and uframe_deployment['node'] is not None:
                if 'assetId' in uframe_deployment['node']:
                    node_id = uframe_deployment['node']['assetId']

        if 'sensor' in uframe_deployment:
            if uframe_deployment['sensor'] and uframe_deployment['sensor'] is not None:
                if 'assetId' in uframe_deployment['sensor']:
                    sensor_id = uframe_deployment['sensor']['assetId']
        return mooring_id, node_id, sensor_id
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def update_deployment_assets(ui_deployment, rd):
    """ Refresh deployment information for assets associated with deployment.
    """
    try:
        # Refresh deployment information for assets associated with deployment.
        mooring_rd, node_rd, sensor_rd = rd.split('-', 2)
        if 'mooring_uid' in ui_deployment:
            mooring_uid = ui_deployment['mooring_uid']
            refresh_asset_deployment(mooring_uid, mooring_rd)

        if 'node_uid' in ui_deployment:
            node_uid = ui_deployment['node_uid']
            target_rd = '-'.join([mooring_rd, node_rd])
            refresh_asset_deployment(node_uid, target_rd)

        if 'sensor_uid' in ui_deployment:
            sensor_uid = ui_deployment['sensor_uid']
            refresh_asset_deployment(sensor_uid, rd)
        return
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

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Perform basic checks on input data
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not deployment:
            message = 'No input provided, unable to process transform for deployment %s.' % action
            raise Exception(message)

        deployment['@class'] = get_class_deployment()
        deployment['eventName'] = 'DEPLOYMENT'

        #- - - - - - - - - - - - - - - - - - - - - -
        # Convert values for fields.
        #- - - - - - - - - - - - - - - - - - - - - -
        converted_deployment = deployments_validate_required_fields_are_provided(deployment, action)

        # Action 'update' specific check: verify event id in data is same as event id on PUT
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

        # Get subsite, node and sensor (if available), otherwise raise exception.
        node = None
        sensor = None
        if is_instrument(rd):
            subsite, node, sensor = rd.split('-', 2)
        elif is_platform(rd):
            subsite, node = rd.split('-')
        elif is_mooring(rd):
            subsite = rd
        else:
            message = 'Invalid reference designator (not mooring, platform or instrument) (\'%s\').' % rd
            raise Exception(message)

        referenceDesignator = {'subsite': subsite, 'node': node, 'sensor': sensor}
        uframe_deployment['referenceDesignator'] = referenceDesignator

        # Set location dictionary.
        location = get_location_dict(converted_deployment['latitude'], converted_deployment['longitude'],
                                     converted_deployment['depth'], converted_deployment['orbitRadius'])

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
        uframe_deployment['tense'] = 'UNKNOWN'

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
                tmp = {'@class': get_event_class('CRUISE_INFO'),
                       'uniqueCruiseIdentifier': converted_deployment['deployCruiseInfo']}
                uframe_deployment['deployCruiseInfo'] = tmp
            else:
                uframe_deployment['deployCruiseInfo'] = None

        # Get recoverCruiseInfo provided.
        if 'recoverCruiseInfo' in converted_deployment:
            if converted_deployment['recoverCruiseInfo'] is not None:
                tmp = {'@class': get_event_class('CRUISE_INFO'),
                       'uniqueCruiseIdentifier': converted_deployment['recoverCruiseInfo']}
                uframe_deployment['recoverCruiseInfo'] = tmp
            else:
                uframe_deployment['recoverCruiseInfo'] = None

        # todo - Sprint 2, not yet supported completely in uframe.
        uframe_deployment['ingestInfo'] = None

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Marshall all remaining data for creation of uframe_deployment.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Get the rest of the fields and values.
        regular_fields = ['assetUid', 'dataSource', 'deployedBy',
                          'editPhase', 'eventId', 'eventName', 'eventStartTime', 'eventStopTime',
                          'inductiveId', 'notes', 'recoveredBy']
        for key in regular_fields:
            if key in converted_deployment:
                uframe_deployment[key] = converted_deployment[key]

        # Fields: eventId, assetUid, lastModifiedTimestamp
        uframe_deployment['@class'] = get_class_deployment()
        uframe_deployment['eventType'] = 'DEPLOYMENT'
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


