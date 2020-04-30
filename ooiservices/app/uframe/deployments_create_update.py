"""
Asset Management - Deployments: Create and update functions.
"""
__author__ = 'Edna Donoughe'

from flask import current_app
from ooiservices.app import cache
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
        #mid, nid, sid = get_ids_from_deployment(new_uframe_deployment)

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
    from ooiservices.app.uframe.common_tools import dump_dict
    debug = False
    action = 'update'
    try:
        if debug:
            print '\n debug ********************************'
            print '\n debug -- Entered _update_deployment...'
        # Transform input data for uframe.
        xdeployment = transform_deployment_for_uframe(id, data, action=action)
        if not xdeployment or xdeployment is None:
            message = 'Failed to format information for uframe update, deployment event id: %d' % id
            raise Exception(message)

        if debug: print '\n\t debug -- Step 1...'
        xdeployment_keys = xdeployment.keys()
        xdeployment_keys.sort()

        if debug:
            print '\n -------------------------------------------------------------------------'
            print '\n Deployment object received for update: '
            dump_dict(xdeployment, debug)

        # Verify deployment exists:
        # Get uframe deployment (for 'ingestInfo', 'lastModifiedTimestamp', 'eventId' and 'assetUID')
        deployment = get_uframe_event(id)
        if not deployment or deployment is None:
            message = 'Failed to get deployment with event id %d from uframe.' % id
            raise Exception(message)

        # Get original ids from uframe deployment object.
        #mid, nid, sid = get_ids_from_deployment(deployment)

        if debug: print '\n\t debug -- Step 2...'
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

        if debug: print '\n\t debug -- Step 3...'
        # Deployments: Fields location and events are not provided by UI, get from deployment.
        missing_keys = []
        for key in keys:
            if key not in xdeployment_keys:
                if key not in valid_missing_keys:
                    message = 'Input data is invalid; missing required key: %s' % key
                    raise Exception(message)
                if key not in missing_keys:
                    missing_keys.append(key)

        if debug: print '\n\t debug -- Step 4...'
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

        if debug: print '\n\t debug -- Step 5...'
        # Update deployment in uframe.
        modified_deployment = update_event_type(id, xdeployment)

        # Format modified deployment from uframe for UI.
        if debug: print '\n\t debug -- Step 6...'
        ui_deployment = format_deployment_for_ui(modified_deployment)
        if debug:
            print '\n debug -- ui_deployment: '
            dump_dict(ui_deployment, debug)

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
        if debug: print '\n debug -- calling update_deployment_assets (%s)...' % rd
        update_deployment_assets(ui_deployment, rd)

        # return updated deployment
        if debug:
            print '\n debug -- Exit _update_deployment...'
            print '\n ************************************'
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

'''
# original with debug
def update_deployment_assets(ui_deployment, rd):
    """ Refresh deployment information for assets associated with deployment.
    """
    debug = True
    try:
        if debug: print '\n debug -- Entered update_deployment_assets...'
        # Refresh deployment information in uid_digests and rd_digests and rd_digests_operational.

        # Refresh deployment information for assets associated with deployment.
        mooring_rd, node_rd, sensor_rd = rd.split('-', 2)
        if 'mooring_uid' in ui_deployment:
            mooring_uid = ui_deployment['mooring_uid']
            """
            if debug:
                print '\n\t debug -- mooring_uid: ', mooring_uid
                print '\n\t debug -- Before calling refresh_asset_deployment....'
            """
            refresh_asset_deployment(mooring_uid, mooring_rd)
            #if debug: print '\n\t debug -- After calling refresh_asset_deployment....'

        if 'node_uid' in ui_deployment:
            node_uid = ui_deployment['node_uid']
            if debug: print '\n\t debug -- node_uid: ', node_uid
            target_rd = '-'.join([mooring_rd, node_rd])
            refresh_asset_deployment(node_uid, target_rd)

        if 'sensor_uid' in ui_deployment:
            sensor_uid = ui_deployment['sensor_uid']
            if debug:
                print '\n\t debug -- sensor_uid: ', sensor_uid
                print '\n\t debug -- Before calling refresh_asset_deployment....'
            refresh_asset_deployment(sensor_uid, rd)
            if debug: print '\n\t debug -- After calling refresh_asset_deployment....'

        if debug: print '\n debug -- Exit update_deployment_assets...'
        return
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)
'''

def update_deployment_assets(ui_deployment, rd):
    """ Refresh deployment information for assets associated with deployment.
    """
    from ooiservices.app.uframe.common_tools import dump_dict
    from ooiservices.app.uframe.status_tools import (get_last_deployment_digest,
                                                    update_uid_digests_cache) #, update_uid_digests_operational_cache)

    debug = False
    try:
        if debug:
            print '\n-------------------------------------------------------------------------'
            print '\n-------------------------------------------------------------------------'
            print '\n debug -- Entered update_deployment_assets...'
            if 'editPhase' in ui_deployment:
                print '\n debug -- ui_deployment editPhase: ', ui_deployment['editPhase']

        editPhase = None
        if 'editPhase' in ui_deployment:
            editPhase = ui_deployment['editPhase']

        # Refresh deployment information for assets associated with deployment.
        # Mooring
        mooring_rd, node_rd, sensor_rd = rd.split('-', 2)
        mooring_uid = None
        if 'mooring_uid' in ui_deployment:
            mooring_uid = ui_deployment['mooring_uid']
            #refresh_asset_deployment(mooring_uid, mooring_rd)

        # Node
        node_uid = None
        if 'node_uid' in ui_deployment:
            node_uid = ui_deployment['node_uid']
            #target_rd = '-'.join([mooring_rd, node_rd])
            #refresh_asset_deployment(node_uid, target_rd)

        # Sensor
        sensor_uid = None
        if 'sensor_uid' in ui_deployment:
            sensor_uid = ui_deployment['sensor_uid']
            #refresh_asset_deployment(sensor_uid, rd)

        if debug:
            print '\n\t debug -- mooring_uid: %s' % mooring_uid
            print '\t debug -- node_uid: %s' % node_uid
            print '\t debug -- sensor_uid: %s' % sensor_uid

        #==============================================================================================
        # Update asset and associated cache as required.
        # (Refresh deployment information in uid_digests, rd_digests and rd_digests_operational.)
        #==============================================================================================

        # Mooring Asset
        if mooring_uid and mooring_uid is not None:
            if debug: print '\n (Mooring) Calling get_last_deployment_digest: ', mooring_uid

            # Get latest deployment information and update digests cache.
            #digest, digest_operational = get_last_deployment_digest(mooring_uid)
            digest = get_last_deployment_digest(mooring_uid)
            if digest and digest is not None:
                if debug:
                    print '\n (Mooring) digest: ', mooring_uid
                    dump_dict(digest, debug)
                update_uid_digests_cache(mooring_uid, digest)
                """
                cache_test = cache.get('uid_digests')
                if cache_test is not None and cache_test and isinstance(cache_test, dict):
                    if mooring_uid in cache_test:
                        if debug:
                            print '\n debug -- cache test data:'
                            dump_dict(cache_test[mooring_uid], debug)
                    else:
                        if debug: print '\n debug -- Error: mooring_uid NOT in uid_digests cache.'
                """
            else:
                if debug: print '\n debug -- digest is None for mooring_uid: ', mooring_uid
            """
            if digest_operational and digest_operational is not None:
                if editPhase and editPhase is not None:
                    if editPhase == 'OPERATIONAL':
                        if debug:
                            print '\n (Mooring) digest_operational: ', mooring_uid
                            dump_dict(digest_operational, debug)
                        update_uid_digests_operational_cache(mooring_uid, digest_operational)
                        cache_test = cache.get('uid_digests_operational')
                        if cache_test is not None and cache_test and isinstance(cache_test, dict):
                            if mooring_uid in cache_test:
                                if debug:
                                    print '\n debug -- cache test data (operational):'
                                    dump_dict(cache_test[mooring_uid], debug)
                            else:
                                if debug: print '\n debug -- Error: mooring_uid NOT in uid_digests_operational cache.'
            else:
                if debug: print '\n debug -- digest_operational is None for mooring_uid: ', mooring_uid
            """
            # Refresh mooring asset
            refresh_asset_deployment(mooring_uid, mooring_rd)

        # Node Asset
        if node_uid and node_uid is not None:

            if debug: print '\n (Node) Calling get_last_deployment_digest: ', node_uid

            # Get latest deployment information and update uid_digests cache.
            #digest, digest_operational = get_last_deployment_digest(node_uid)
            digest = get_last_deployment_digest(node_uid)
            if digest and digest is not None:
                if debug:
                    print '\n (Node) digest: ', node_uid
                    dump_dict(digest, debug)
                update_uid_digests_cache(node_uid, digest)

            """
            # Get latest deployment information and update uid_digests_operational cache.
            if digest_operational and digest_operational is not None:
                if editPhase and editPhase is not None:
                    if editPhase == 'OPERATIONAL':
                        if debug:
                            print '\n (Node) digest_operational: ', node_uid
                            dump_dict(digest_operational, debug)
                        update_uid_digests_operational_cache(node_uid, digest_operational)
            """
            # Refresh node asset
            target_rd = '-'.join([mooring_rd, node_rd])
            refresh_asset_deployment(node_uid, target_rd)


        # Sensor Asset
        if sensor_uid and sensor_uid is not None:

            if debug: print '\n (Sensor) Calling get_last_deployment_digest: ', sensor_uid

            # Get latest deployment information and update uid_digests cache.
            #digest, digest_operational = get_last_deployment_digest(sensor_uid)
            digest = get_last_deployment_digest(sensor_uid)
            if digest and digest is not None:
                if debug:
                    print '\n (Sensor) digest: ', sensor_uid
                    dump_dict(digest, debug)
                update_uid_digests_cache(sensor_uid, digest)
                """
                cache_test = cache.get('uid_digests')
                if cache_test is not None and cache_test and isinstance(cache_test, dict):
                    if sensor_uid in cache_test:
                        if debug:
                            print '\n debug -- cache test data:'
                            dump_dict(cache_test[sensor_uid], debug)
                    else:
                        if debug: print '\n debug -- Error: sensor_uid NOT in uid_digests cache.'
                """
            else:
                if debug: print '\n debug -- digest is None for sensor_uid: ', sensor_uid
            """
            # Get latest deployment information and update uid_digests_operational cache.
            if digest_operational and digest_operational is not None:
                if editPhase and editPhase is not None:
                    if editPhase == 'OPERATIONAL':
                        if debug:
                            print '\n (Sensor) digest_operational: ', sensor_uid
                            dump_dict(digest_operational, debug)
                        update_uid_digests_operational_cache(sensor_uid, digest_operational)
                        cache_test = cache.get('uid_digests_operational')
                        if cache_test is not None and cache_test and isinstance(cache_test, dict):
                            if sensor_uid in cache_test:
                                if debug:
                                    print '\n debug -- cache test data (operational):'
                                    dump_dict(cache_test[sensor_uid], debug)
                            else:
                                if debug: print '\n debug -- Error: sensor_uid NOT in uid_digests_operational cache.'
            else:
                if debug: print '\n debug -- digest_operational is None for sensor_uid: ', sensor_uid
            """
            # Refresh sensor asset
            refresh_asset_deployment(sensor_uid, rd)


        if debug: print '\n debug -- Exit update_deployment_assets...'
        return
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def transform_deployment_for_uframe(id, deployment, action=None):
    """ Transform UI deployment data into uframe deployment structure.
    """
    debug = False
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
        if debug: print '\n debug -- before convert...'
        converted_deployment = deployments_validate_required_fields_are_provided(deployment, action)
        if debug: print '\n debug -- after convert...'

        # Action 'update' specific check: verify event id in data is same as event id on PUT
        if action == 'update':
            if 'eventId' in converted_deployment:
                if debug:
                    print("converted_deployment['eventId']")
                    print(converted_deployment['eventId'])
                    print('id')
                    print(id)
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

        uframe_deployment['referenceDesignator'] = converted_deployment['rd']

        # Add water depth information
        uframe_deployment['waterDepth'] = None

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

        # editPhase - use operational until editPhase work is completed. (2016-12-15)
        uframe_deployment['editPhase'] = 'OPERATIONAL'

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


