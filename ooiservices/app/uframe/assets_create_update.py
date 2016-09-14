"""
Assets: Create and update functions.

"""
__author__ = 'Edna Donoughe'

from flask import current_app
from requests.exceptions import (ConnectionError, Timeout)
from ooiservices.app.uframe.config import (get_uframe_assets_info, get_assets_url_base, headers, get_url_info_resources)
from ooiservices.app.uframe.common_tools import (get_asset_types, get_asset_class_by_asset_type,
                                                 get_class_remote_resource, asset_edit_phase_values, dump_dict)
from ooiservices.app.uframe.asset_tools import (uframe_get_asset_by_id, uframe_get_asset_by_uid, format_asset_for_ui,
                                                refresh_asset_cache, uframe_get_remote_resource_by_id)
from ooiservices.app.uframe.assets_validate_fields import (assets_validate_required_fields_are_provided,
                                                           asset_get_required_fields_and_types_uframe,
                                                           validate_required_fields_remote_resource)
import json
import requests


# Create asset.
def _create_asset(data):
    """ For asset data, validate and marshall data to perform create.

    Asset data is from UI and must be transformed into uframe asset format.
    New asset is returned on success. On failure, log and raise exception.
    """
    action = 'create'
    try:
        keys = []
        if not data:
            message = 'Data is required to create an asset, none provided.'
            raise Exception(message)

        # Transform input data from UI into format required by uframe for create.
        xasset = transform_asset_for_uframe(None, data, action=action)

        # Create new asset in uframe.
        new_uframe_asset = uframe_create_asset(xasset)

        # Get new asset's id and uid.
        uid = None
        if new_uframe_asset:
            if 'uid' in new_uframe_asset:
                uid = new_uframe_asset['uid']
        if uid is None:
            message = 'Failed to retrieve uid from newly created asset from uframe.'
            raise Exception(message)
        id = None
        if new_uframe_asset:
            if 'assetId' in new_uframe_asset:
                id = new_uframe_asset['assetId']
        if id is None:
            message = 'Failed to retrieve id from newly created asset from uframe.'
            raise Exception(message)
        # Format uframe asset data for UI.
        ui_asset = format_asset_for_ui(new_uframe_asset)
        if not ui_asset or ui_asset is None:
            message = 'Failed to format uframe asset for UI; asset id/uid: %d/%s' % (id, uid)
            raise Exception(message)

        # Refresh asset cache
        refresh_asset_cache(id, ui_asset, action)

        # return updated asset
        return ui_asset

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def _update_remote_resource(uid, data):
    """ Update a remote resource for an asset.
    """
    action = 'update'
    try:
        if not uid or uid is None:
            message = 'Failed to receive asset uid in request data, unable to update remote resource.'
            raise Exception(message)
        if not data:
            message = 'No data received to process remote resource update.'
            raise Exception(message)

        # Remove extra 'uid', add '@class' and 'remoteResourceId' fields to data
        if 'uid' in data:
            del data['uid']

        # Get asset uid to post remote resource to.
        class_value, remoteResourceId, lastModifiedTimeStamp = get_remote_resource_info(data, action)
        data['@class'] = class_value
        data['remoteResourceId'] = remoteResourceId
        data['lastModifiedTimeStamp'] = lastModifiedTimeStamp

        # Verify remote resource fields and required values are provided.
        validate_required_fields_remote_resource('update', data, action=None)

        # Check: Current number of remote resources
        current_remote_resources = None
        current_asset = uframe_get_asset_by_uid(uid)
        if 'remoteResources' in current_asset:
            current_remote_resources = current_asset['remoteResources']

        # Post remote resource to asset, returns asset.
        remote_resource = uframe_update_remote_resource_by_resource_id(remoteResourceId, data)
        updated_remote_resource = uframe_get_remote_resource_by_id(remoteResourceId)
        if remote_resource['lastModifiedTimestamp'] != updated_remote_resource['lastModifiedTimestamp']:
            message = 'The updated remote resource lastModifiedTimestamp does not match timestamp after uframe get...'
            raise Exception(message)

        # Check: Current number of remote resources
        after_remote_resources = None
        updated_asset = uframe_get_asset_by_uid(uid)
        if 'remoteResources' in updated_asset:
            after_remote_resources = updated_asset['remoteResources']
        if len(after_remote_resources) != len(current_remote_resources):
            message = 'Created remote resource rather than updated?'
            raise Exception(message)

        ui_asset = format_asset_for_ui(updated_asset)
        id = None
        if 'id' in ui_asset:
            id = ui_asset['id']
        if 'events' in ui_asset:
                del ui_asset['events']
        if 'calibration' in ui_asset:
            del ui_asset['calibration']
        if 'location' in ui_asset:
            del ui_asset['location']
        refresh_asset_cache(id, updated_asset, action, remote_id=remoteResourceId)
        # Return complete asset with new remote resource
        return remote_resource

    except Exception as err:
        message = str(err)
        raise Exception(message)


# Update asset.
def _update_asset(id, data):
    """ For asset data and asset id, validate and marshall data to perform update.

    Asset data is from UI and must be transformed into uframe asset format.
    Updated asset is returned on success. On failure, log and raise exception.
    """
    asset_type = None
    action = 'update'
    try:
        # Transform input data from UI into uframe format, get keys ()
        xasset = transform_asset_for_uframe(id, data, action='update')
        xasset_keys = xasset.keys()
        xasset_keys.sort()

        # Verify asset exists:
        # Get uframe asset (for 'calibration', 'events', 'location', 'lastModifiedTimestamp')
        asset = uframe_get_asset_by_id(id)

        if not asset or asset is None:
            message = 'Failed to get asset with id %d from uframe.' % id
            raise Exception(message)

        uid = None
        if 'uid' in asset:
            uid = asset['uid']
        if uid is None:
            message = 'Failed to receive asset with id %s from uframe.' % id
            raise Exception(message)

        keys = []
        if asset:
            keys = asset.keys()
            keys.sort()
            if 'assetType' in asset:
                asset_type = asset['assetType']

        # Assets: Reserved fields: fields which may not be modified by UI once assigned in uframe:
        #   assetId, assetType, lastModifiedTimestamp, uid
        reserved_fields = ['assetId', 'assetType', 'lastModifiedTimestamp', 'uid']

        # Determine any missing items are in valid items list, is not error.
        valid_missing_keys = ['events', 'location', 'remoteResources']

        # Assets: Fields location and events are not provided by UI, get from asset. If asset is Sensor, calibration too.
        if asset_type == 'Sensor':
            valid_missing_keys.append('calibration')

        missing_keys = []
        for key in keys:
            if key not in xasset_keys:
                if key not in valid_missing_keys:
                    message = 'Input data is invalid; missing required key: %s' % key
                    raise Exception(message)
                if key not in missing_keys:
                    missing_keys.append(key)

        # Apply standard fields.
        for key in valid_missing_keys:
            xasset[key] = asset[key]

        # Apply reserved fields.
        for key in reserved_fields:
            xasset[key] = asset[key]

        # Check all keys required are accounted for.
        xasset_keys = xasset.keys()
        xasset_keys.sort()
        for key in keys:
            if key not in xasset_keys:
                message = 'Missing required attribute \'%s\'.' % key
                raise Exception(message)

        # Update asset in uframe.
        modified_asset = uframe_update_asset(xasset)

        # Format modified asset from uframe for UI.
        updated_asset = format_asset_for_ui(modified_asset)
        # todo -- remove calibration, location and events?
        refresh_asset_cache(id, updated_asset, action)

        # return updated asset
        return updated_asset

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def process_asset_update(uid, xasset=None, action='update'):
    """ Process asset update, for instance after create or update remoteResources.
    """
    asset_type = None
    try:
        # Verify asset exists. Get uframe asset for:
        #  'calibration', 'events', 'location', 'remoteResources', 'lastModifiedTimestamp'
        asset = uframe_get_asset_by_uid(uid)

        # Get asset id for cache update.
        id = None
        if 'assetId' in asset:
            id = asset['assetId']
        if id is None:
            message = 'uframe asset did not return \'assetId\'.'
            raise Exception(message)

        if id < 1:
            message = 'uframe asset id is invalid: %d.' % id
            raise Exception(message)

        keys = []
        if asset:
            keys = asset.keys()
            keys.sort()
            if 'assetType' in asset:
                asset_type = asset['assetType']

        if xasset is None:
            xasset = asset.copy()

        xasset_keys = xasset.keys()
        xasset_keys.sort()

        # Assets: Reserved fields: fields which may not be modified by UI once assigned in uframe:
        #   assetId, assetType, lastModifiedTimestamp, uid
        reserved_fields = ['assetId', 'assetType', 'lastModifiedTimestamp', 'uid']

        # Determine any missing items are in valid items list, is not error.
        valid_missing_keys = ['events', 'location', 'remoteResources']

        # Assets: Fields location and events are not provided by UI, get from asset. If asset is Sensor, calibration too.
        if asset_type == 'Sensor':
            valid_missing_keys.append('calibration')

        missing_keys = []
        for key in keys:
            if key not in xasset_keys:
                if key not in valid_missing_keys:
                    message = 'Input data is invalid; missing required key: %s' % key
                    raise Exception(message)
                if key not in missing_keys:
                    missing_keys.append(key)

        # Apply valid missing keys.
        for key in valid_missing_keys:
            xasset[key] = asset[key]

        # Apply reserved fields
        for key in reserved_fields:
            xasset[key] = asset[key]

        # Check all keys required are accounted for.
        xasset_keys = xasset.keys()
        xasset_keys.sort()
        for key in keys:
            if key not in xasset_keys:
                message = 'Missing required key: %s' % key
                raise Exception(message)

        # Update asset in uframe.
        modified_asset = uframe_update_asset(xasset)

        # Format modified asset from uframe for UI.
        updated_asset = format_asset_for_ui(modified_asset)
        # todo -- remove calibration, location and events?
        refresh_asset_cache(id, updated_asset, action)

        return updated_asset

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# Update asset in uframe.
def uframe_update_asset(asset):
    """ Update asset in uframe. On success return updated asset, on error, raise exception.
    """
    id = None
    uid = None
    try:
        # Get asset id from asset data provided.
        if 'assetId' in asset:
            id = asset['assetId']
        if id is None:
            message = 'Invalid asset, missing attribute \'assetId\', unable to request asset update.'
            raise Exception(message)
        if 'uid' in asset:
            uid = asset['uid']
        if uid is None:
            message = 'Invalid asset, missing attribute \'uid\', unable to request asset update.'
            raise Exception(message)

        # Update asset in uframe.
        base_url, timeout, timeout_read = get_uframe_assets_info()
        url = '/'.join([base_url, get_assets_url_base(), str(id)])
        response = requests.put(url, data=json.dumps(asset), headers=headers())
        if response.status_code != 200:
            message = '(%d) Failed to update asset %d.' % (response.status_code, id)
            raise Exception(message)

        # Get updated asset from uframe and return.
        updated_asset = uframe_get_asset_by_uid(uid)
        return updated_asset

    except ConnectionError:
        message = 'Error: ConnectionError during uframe asset update(id: %d)' % id
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Error: Timeout during during uframe asset update (id: %d)' % id
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Create asset in uframe.
def uframe_create_asset(asset):
    """ Create asset in uframe. On success return updated asset, on error, raise exception.
    """
    check = False
    success = 'CREATED'
    try:
        # Check asset data provided.
        if not asset or asset is None:
            message = 'Asset data must be provided to create asset in uframe.'
            raise Exception(message)
        if not isinstance(asset, dict):
            message = 'Asset data must be provided in dict form to create asset in uframe.'
            raise Exception(message)

        # Create asset in uframe.
        base_url, timeout, timeout_read = get_uframe_assets_info()
        url = '/'.join([base_url, get_assets_url_base()])
        if check: print '\n check: url: ', url
        response = requests.post(url, data=json.dumps(asset), headers=headers())
        if response.status_code != 201:
            message = '(%d) uframe failed to create asset.' % response.status_code
            if response.content:
                uframe_message = json.loads(response.content)
                if 'message' in uframe_message:
                    uframe_message = uframe_message['message']
                message += ' %s' % uframe_message
            current_app.logger.info(message)
            raise Exception(message)

        # Get id for new asset.
        if not response.content:
            message = 'No response content returned from create asset.'
            raise Exception(message)

        # Review response.content:
        #   {u'message': u'Element created successfully.', u'id': 4292, u'statusCode': u'CREATED'}
        response_data = json.loads(response.content)
        id = None
        if 'id' in response_data and 'statusCode' in response_data:
            if response_data['statusCode'] and response_data['id']:
                if response_data['statusCode'] == success and response_data['id'] > 0:
                    id = response_data['id']
        if id is None:
            message = 'Failed to create uframe asset.'
            raise Exception(message)

        # Get new asset from uframe.
        new_asset = uframe_get_asset_by_id(id)
        if not new_asset or new_asset is None:
            message = 'Failed to get asset with id %d from uframe.' % id
            raise Exception(message)
        return new_asset
    except ConnectionError:
        message = 'Error: ConnectionError during uframe asset create.'
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Error: Timeout during during uframe asset create.'
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


def uframe_postto_asset(uid, data):
    try:
        # Post request. Get configuration url and timeout information, build request url and post.
        base_url, timeout, timeout_read = get_uframe_assets_info()
        url = '/'.join([base_url, 'resource', 'postto', uid])
        response = requests.post(url, data=json.dumps(data), headers=headers())

        # Process error.
        if response.status_code == 204:
            message = 'Failed to get an asset with the uid (\'%s\') provided.' % uid
            raise Exception(message)
        elif response.status_code != 201:
            if response.content is None:
                message = 'Failed to create remote resource; status code: %d' % response.status_code
                raise Exception(message)

            elif response.content is not None:
                response_data = json.loads(response.content)
                # Determine if success or failure.
                if 'error' not in response_data:
                    # Success? If success get id.
                    if 'statusCode' in response_data:
                        # Failure? If failure build error message.
                        if 'message' in response_data and 'statusCode' in response_data:
                            message = str(response_data['statusCode']) + ': ' + str(response_data['message'])
                            raise Exception(message)
                else:
                    # Failure? If failure build error message.
                    if 'message' in response_data and 'statusCode' in response_data:
                        message = str(response_data['statusCode']) + ': ' + str(response_data['message'])
                        raise Exception(message)

        # Get response data, check status code returned from uframe. Return error in exception.
        id = 0
        if response.content is not None:
            response_data = json.loads(response.content)
            # Determine if success or failure.
            if 'error' not in response_data:
                # Success? If success get id.
                if 'statusCode' in response_data:
                    if response_data['statusCode'] == 'CREATED':
                        id = response_data['id']
                    else:
                        message = 'Failed to create remote resource; statusCode from uframe: %s' % \
                                  response_data['statusCode']
                        raise Exception(message)
            else:
                # Failure? If failure build error message.
                if 'message' in response_data and 'statusCode' in response_data:
                    message = response_data['statusCode'] + ': ' + response_data['message']
                    raise Exception(message)

        if id == 0:
            message = 'Failed to create a remote resource for asset with uid %s' % uid
            raise Exception(message)

        # Get newly created event and return.
        remote_resource = uframe_get_remote_resource_by_id(id)
        return remote_resource

    except Exception as err:
        message = str(err)
        raise Exception(message)


def transform_asset_for_uframe(id, asset, action=None):
    """ Transform UI asset into uframe asset structure.

    <-- This section needs updated to reflect UI content for asset -->
    Input from UI (will be in 'string form'):
        {
          "Ref Des": "CP03ISSM-MFD37-00-DCLENG000",
          "assetInfo": {
            "array": "Coastal Pioneer",
            "assembly": "Oregon Inshore Surface Mooring - Multi-Function Node",
            "asset_name": "CP03ISSM-00003-DCL37",
            "description": "Data Concetrator Logger",
            "longName": "Coastal Pioneer Oregon Inshore Surface Mooring - Multi-Function Node - Data Concentrator Logger (DCL)",
            "maxdepth": 0,
            "mindepth": 0,
            "name": "Coastal Pioneer Oregon Inshore Surface Mooring - Multi-Function Node - Data Concentrator Logger (DCL)",
            "owner": null,
            "type": "Sensor"
          },
          "assetType": "Sensor",
          "augmented": true,
          "coordinates": [
            -70.885,
            40.3595
          ],
          "dataSource": "/home/asadev/uframes/uframe_ooi_20160727_90f4540c71d3fc4f6a4fc8262903c92c722535ee/uframe-1.0/edex/data/ooi/xasset_spreadsheet/bulk_load-AssetRecord.csv",
          "deployment_number": "3",
          "deployment_numbers": [
            3
          ],
          "depth": 0.0,
          "hasDeploymentEvent": true,
          "id": 8409,
          "lastModifiedTimestamp": 1469665799021,
          "manufactureInfo": {
            "firmwareVersion": null,
            "manufacturer": "WHOI",
            "modelNumber": "DCL",
            "serialNumber": "CP03ISSM-00003-DCL37",
            "shelfLifeExpirationDate": null,
            "softwareVersion": null
          },
          "mobile": false,
          "notes": null,
          "partData": {
            "institutionPropertyNumber": null,
            "institutionPurchaseOrderNumber": null,
            "ooiPartNumber": null,
            "ooiPropertyNumber": null,
            "ooiSerialNumber": null
          },
          "physicalInfo": {
            "depthRating": null,
            "height": -1.0,
            "length": -1.0,
            "powerRequirements": null,
            "weight": -1.0,
            "width": -1.0
          },
          "purchaseAndDeliveryInfo": {
            "deliveryDate": 1358812800000,
            "deliveryOrderNumber": null,
            "purchaseDate": 1358812800000,
            "purchasePrice": null
          },
          "ref_des": "CP03ISSM-MFD37-00-DCLENG000",
          "remoteDocuments": [],
          "remoteResources": [],
          "tense": "PAST",
          "uid": "R00035"
        }

    Reserved:
        calibration
        events
        location
        lastModifiedTimestamp

    Output(33) to uframe:
        {
          "@class" : ".XInstrument",
          "calibration" : [ ],
          "events" : [ {
            "@class" : ".XEvent",
            "eventId" : 15255,
            "assetUid" : "R00035",
            "eventType" : "UNSPECIFIED",
            "eventName" : "CP03ISSM-MFD37-00-DCLENG000",
            "eventStartTime" : 1398039060000,
            "eventStopTime" : 1405382400000,
            "notes" : "Create new UNSPECIFIED event for CP03ISSM-MFD37-00-DCLENG000, (assetUid: R00035)",
            "tense" : "UNKNOWN",
            "dataSource" : null,
            "lastModifiedTimestamp" : 1470366111443
          } ],
          "assetId" : 8409,
          "remoteResources" : [ ],
          "name" : "CP03ISSM-00003-DCL37",
          "location" : null,
          "owner" : null,
          "notes" : "Updated notes.",
          "serialNumber" : "CP03ISSM-00003-DCL37",
          "description" : "Data Concetrator Logger",
          "physicalInfo" : {
            "length" : -1.0,
            "height" : -1.0,
            "width" : -1.0,
            "weight" : -1.0
          },
          "firmwareVersion" : null,
          "softwareVersion" : null,
          "powerRequirements" : null,
          "uid" : "R00035",
          "assetType" : "Sensor",
          "mobile" : false,
          "manufacturer" : "WHOI",
          "modelNumber" : "DCL",
          "purchasePrice" : null,
          "purchaseDate" : 1358812800000,
          "deliveryDate" : 1358812800000,
          "depthRating" : null,
          "ooiPropertyNumber" : null,
          "ooiPartNumber" : null,
          "ooiSerialNumber" : null,
          "deliveryOrderNumber" : null,
          "institutionPropertyNumber" : null,
          "institutionPurchaseOrderNumber" : null,
          "shelfLifeExpirationDate" : null,
          "dataSource" : "/home/asadev/uframes/uframe_ooi_20160727_90f4540c71d3fc4f6a4fc8262903c92c722535ee/uframe-1.0/edex/data/ooi/xasset_spreadsheet/bulk_load-AssetRecord.csv",
          "lastModifiedTimestamp" : 1470493081598
        }
    """
    uframe_asset = {}
    valid_actions = ['create', 'update']
    try:
        if action is None:
            message = 'Failed to transform asset, action value is None.'
            raise Exception(message)
        if action not in valid_actions:
            message = 'Invalid action (%s) for transform asset for uframe. Must be one of %s' % (action, valid_actions)
            raise Exception(message)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Perform basic checks on input data
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not asset:
            message = 'No input provided, unable to process transform for asset %s.' % action
            raise Exception(message)
        if 'assetType' not in asset:
            message = 'Malformed asset; missing required attribute \'assetType\'.'
            raise Exception(message)
        asset_type = asset['assetType']
        if asset_type not in get_asset_types():
            message = 'Unknown assetType identified in asset during transform: \'%s\'.' % asset_type
            raise Exception(message)

        #- - - - - - - - - - - - - - - - - - - - - -
        # Convert values for fields in 'string asset'
        #- - - - - - - - - - - - - - - - - - - - - -
        converted_asset = assets_validate_required_fields_are_provided(asset_type, asset, action)

        # Business rules.
        edit_phase = None
        valid_edit_phases = asset_edit_phase_values()
        if 'editPhase' in converted_asset:
            edit_phase = converted_asset['editPhase']
            if edit_phase not in valid_edit_phases and edit_phase is not None:
                message = 'Invalid editPhase value (use one of %s).' % valid_edit_phases
                raise Exception(message)

        # Action 'update' specific check: verify asset id in data is same as asset id on PUT
        if action == 'update':
            if 'id' in converted_asset:
                if converted_asset['id'] != id:
                    message = 'The asset id provided in url does not match id provided in data.'
                    raise Exception(message)

            # Fields in assetInfo: description, asset_type
            if 'ref_des' not in converted_asset:
                message = 'Unable to process asset provided, no reference designator.'
                raise Exception(message)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Marshall all data for creation of uframe_asset.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        uframe_asset['editPhase'] = edit_phase
        # Field: assetType [reserved]
        uframe_asset['assetType'] = asset_type

        # Marshall data from asset into uframe_asset.
        # Field: @class
        asset_class = get_asset_class_by_asset_type(asset_type)
        uframe_asset['@class'] = asset_class

        # Fields: description, owner, name (assetInfo)
        description, owner, name = marshall_assetInfo_fields(converted_asset)
        uframe_asset['description'] = description
        uframe_asset['owner'] = owner
        uframe_asset['name'] = name
        del asset['assetInfo']

        # Fields: firmwareVersion, manufacturer, modelNumber, serialNumber, shelfLifeExpirationDate, softwareVersion
        firmwareVersion, manufacturer, modelNumber, serialNumber, shelfLifeExpirationDate, softwareVersion = \
            marshall_manufactureInfo_fields(converted_asset)
        uframe_asset['firmwareVersion'] = firmwareVersion
        uframe_asset['manufacturer'] = manufacturer
        uframe_asset['modelNumber'] = modelNumber
        uframe_asset['serialNumber'] = serialNumber
        uframe_asset['shelfLifeExpirationDate'] = shelfLifeExpirationDate
        uframe_asset['softwareVersion'] = softwareVersion
        del asset['manufactureInfo']

        # Fields:
        # institutionPropertyNumber, institutionPurchaseOrderNumber, ooiPartNumber, ooiPropertyNumber, ooiSerialNumber
        institutionPropertyNumber, institutionPurchaseOrderNumber, ooiPartNumber, \
               ooiPropertyNumber, ooiSerialNumber = marshall_partData_fields(converted_asset)
        uframe_asset['institutionPropertyNumber'] = institutionPropertyNumber
        uframe_asset['institutionPurchaseOrderNumber'] = institutionPurchaseOrderNumber
        uframe_asset['ooiPartNumber'] = ooiPartNumber
        uframe_asset['ooiPropertyNumber'] = ooiPropertyNumber
        uframe_asset['ooiSerialNumber'] = ooiSerialNumber
        del asset['partData']

        # Fields: depthRating, powerRequirements, physicalInfo
        depthRating, powerRequirements, physicalInfo = marshall_physicalInfo_fields(converted_asset)
        # height, length, weight, width =
        uframe_asset['depthRating'] = depthRating
        uframe_asset['powerRequirements'] = powerRequirements
        uframe_asset['physicalInfo'] = physicalInfo
        del asset['physicalInfo']

        # Fields: deliveryDate, deliveryOrderNumber, purchaseDate, purchasePrice
        deliveryDate, deliveryOrderNumber, purchaseDate, purchasePrice = marshall_purchaseAndDeliveryInfo_fields(converted_asset)
        uframe_asset['deliveryDate'] = deliveryDate
        uframe_asset['deliveryOrderNumber'] = deliveryOrderNumber
        uframe_asset['purchaseDate'] = purchaseDate
        uframe_asset['purchasePrice'] = purchasePrice
        del asset['purchaseAndDeliveryInfo']

        # Fields: assetId, uid, lastModifiedTimestamp [reserved]
        uframe_asset['uid'] = converted_asset['uid']
        if action == 'update':
            uframe_asset['assetId'] = converted_asset['id']
            uframe_asset['lastModifiedTimestamp'] = converted_asset['lastModifiedTimestamp']
        else:
            uframe_asset['lastModifiedTimestamp'] = None
            uframe_asset['assetId'] = -1
            uframe_asset['events'] = []
            uframe_asset['remoteResources'] = []
            if asset_type == 'Sensor':
                uframe_asset['calibration'] = []
            uframe_asset['location'] = None

        # Fields: mobile, notes, remoteDocuments, remoteResources, dataSource
        uframe_asset['mobile'] = converted_asset['mobile']
        uframe_asset['notes'] = converted_asset['notes']
        uframe_asset['remoteResources'] = converted_asset['remoteResources']
        uframe_asset['dataSource'] = converted_asset['dataSource']

        #- - - - - - - - - - - - - - - - - - - - - -
        # Validate uframe_asset object - fields present
        #- - - - - - - - - - - - - - - - - - - - - -
        #if debug: print '\n Before check required fields for uframe asset...'
        #required_fields, field_types = asset_get_required_fields_and_types_uframe(asset_type, action)
        #if debug: print '\n After check required fields for uframe asset...'
        uframe_asset_keys = uframe_asset.keys()
        uframe_asset_keys.sort()
        return uframe_asset

    except Exception as err:
        message = str(err)
        raise Exception(message)


# Marshall fields from assetInfo.
def marshall_assetInfo_fields(asset):
    try:
        asset_info = None
        if 'assetInfo' in asset:
            asset_info = asset['assetInfo'].copy()
        if asset_info is None:
            message = 'Malformed asset, missing required field \'assetInfo\'.'
            raise Exception(message)

        description = None
        if 'description' in asset_info:
            description = asset_info['description']
        owner = None
        if 'owner' in asset_info:
            owner = asset_info['owner']
        name = None
        if 'name' in asset_info:
            name = asset_info['asset_name']

        return description, owner, name
    except Exception as err:
        raise Exception(str(err))


# Marshall fields from manufactureInfo.
def marshall_manufactureInfo_fields(asset):
    """
    "manufactureInfo": {
            "firmwareVersion": null,
            "manufacturer": "WHOI",
            "modelNumber": "DCL",
            "serialNumber": "CP03ISSM-00003-DCL37",
            "shelfLifeExpirationDate": null,
            "softwareVersion": null
          }
    """
    try:
        manufacture_info = None
        if 'manufactureInfo' in asset:
            manufacture_info = asset['manufactureInfo']
        if manufacture_info is None:
            message = 'Malformed asset, missing required field \'manufactureInfo\'.'
            raise Exception(message)

        firmwareVersion = None
        if 'firmwareVersion' in manufacture_info:
            firmwareVersion = manufacture_info['firmwareVersion']

        manufacturer = None
        if 'manufacturer' in manufacture_info:
            manufacturer = manufacture_info['manufacturer']

        modelNumber = None
        if 'modelNumber' in manufacture_info:
            modelNumber = manufacture_info['modelNumber']

        serialNumber = None
        if 'serialNumber' in manufacture_info:
            serialNumber = manufacture_info['serialNumber']

        shelfLifeExpirationDate = None
        if 'shelfLifeExpirationDate' in manufacture_info:
            shelfLifeExpirationDate = manufacture_info['shelfLifeExpirationDate']

        softwareVersion = None
        if 'softwareVersion' in manufacture_info:
            softwareVersion = manufacture_info['softwareVersion']

        return firmwareVersion, manufacturer, modelNumber, serialNumber, shelfLifeExpirationDate, softwareVersion
    except Exception as err:
        raise Exception(str(err))


# Marshall fields from partData.
def marshall_partData_fields(asset):
    """
    "partData": {
            "institutionPropertyNumber": null,
            "institutionPurchaseOrderNumber": null,
            "ooiPartNumber": null,
            "ooiPropertyNumber": null,
            "ooiSerialNumber": null
          },
    """
    try:
        part_info = None
        if 'partData' in asset:
            part_info = asset['partData']
        if part_info is None:
            message = 'Malformed asset, missing required field \'partData\'.'
            raise Exception(message)

        institutionPropertyNumber = None
        if 'institutionPropertyNumber' in part_info:
            institutionPropertyNumber = part_info['institutionPropertyNumber']

        institutionPurchaseOrderNumber = None
        if 'institutionPurchaseOrderNumber' in part_info:
            institutionPurchaseOrderNumber = part_info['institutionPurchaseOrderNumber']

        ooiPartNumber = None
        if 'ooiPartNumber' in part_info:
            ooiPartNumber = part_info['ooiPartNumber']

        ooiPropertyNumber = None
        if 'ooiPropertyNumber' in part_info:
            ooiPropertyNumber = part_info['ooiPropertyNumber']

        ooiSerialNumber = None
        if 'ooiSerialNumber' in part_info:
            ooiSerialNumber = part_info['ooiSerialNumber']

        return institutionPropertyNumber, institutionPurchaseOrderNumber, ooiPartNumber, \
               ooiPropertyNumber, ooiSerialNumber
    except Exception as err:
        raise Exception(str(err))


def marshall_physicalInfo_fields(asset):
    """
    "physicalInfo": {
            "depthRating": null,
            "height": -1.0,
            "length": -1.0,
            "powerRequirements": null,
            "weight": -1.0,
            "width": -1.0
          },
    """
    try:
        physicalInfo = None
        if 'physicalInfo' in asset:
            physicalInfo = (asset['physicalInfo']).copy()
        if physicalInfo is None:
            message = 'Malformed asset, missing required field \'physicalInfo\'.'
            raise Exception(message)

        depthRating = None
        if 'depthRating' in physicalInfo:
            depthRating = physicalInfo['depthRating']
        del physicalInfo['depthRating']

        powerRequirements = None
        if 'powerRequirements' in physicalInfo:
            powerRequirements = physicalInfo['powerRequirements']
        del physicalInfo['powerRequirements']

        return depthRating, powerRequirements, physicalInfo #, height, length, weight, width
    except Exception as err:
        raise Exception(str(err))


def marshall_purchaseAndDeliveryInfo_fields(asset):
    """
    "purchaseAndDeliveryInfo": {
            "deliveryDate": 1358812800000,
            "deliveryOrderNumber": null,
            "purchaseDate": 1358812800000,
            "purchasePrice": null
          },
    """
    try:
        purchaseAndDeliveryInfo = None
        if 'purchaseAndDeliveryInfo' in asset:
            purchaseAndDeliveryInfo = asset['purchaseAndDeliveryInfo']
        if purchaseAndDeliveryInfo is None:
            message = 'Malformed asset, missing required field \'purchaseAndDeliveryInfo\'.'
            raise Exception(message)

        deliveryDate = None
        if 'deliveryDate' in purchaseAndDeliveryInfo:
            deliveryDate = purchaseAndDeliveryInfo['deliveryDate']
        deliveryOrderNumber = None
        if 'deliveryOrderNumber' in purchaseAndDeliveryInfo:
            deliveryOrderNumber = purchaseAndDeliveryInfo['deliveryOrderNumber']
        purchaseDate = None
        if 'purchaseDate' in purchaseAndDeliveryInfo:
            purchaseDate = purchaseAndDeliveryInfo['purchaseDate']
        purchasePrice = None
        if 'purchasePrice' in purchaseAndDeliveryInfo:
            purchasePrice = purchaseAndDeliveryInfo['purchasePrice']

        return deliveryDate, deliveryOrderNumber, purchaseDate, purchasePrice
    except Exception as err:
        raise Exception(str(err))


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Remote Resources support functions.
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def _create_remote_resource(uid, data):
    """ Create a remote resource for an asset.
    """
    action = 'create'
    asset_action = 'update'
    try:
        # Get asset uid to post remote resource to.
        class_value, remoteResourceId, lastModifiedTimeStamp  = get_remote_resource_info(data, action)

        # Remove extra 'uid', add '@class' and 'remoteResourceId' fields to data
        if 'uid' in data:
            del data['uid']
        data['@class'] = class_value
        data['remoteResourceId'] = -1
        # Verify remote resource fields and required values are provided.
        converted_data = validate_required_fields_remote_resource('create', data, action=None)

        # Post remote resource to asset, returns remote_resource.
        remote_resource = uframe_postto_asset(uid, converted_data)
        updated_asset = process_asset_update(uid, xasset=None, action=asset_action)
        if not updated_asset:
            message = 'Failed to return updated asset from uframe.'
            raise Exception(message)

        # Return complete asset with new remote resource
        return remote_resource

    except Exception as err:
        message = str(err)
        raise Exception(message)


def _get_remote_resources_by_asset_id(id):
    """ Get remote resources for an asset using the asset id.
    """
    try:
        remote_resources = uframe_get_remote_resources_for_asset_by_id(id)
        return remote_resources
    except Exception as err:
        message = str(err)
        raise Exception(message)


def _get_remote_resources_by_asset_uid(uid):
    """ Get remote resources for an asset using the asset uid.
    """
    try:
        remote_resources = uframe_get_remote_resources_for_asset_by_uid(uid)
        return remote_resources
    except Exception as err:
        message = str(err)
        raise Exception(message)


def _get_remote_resource_by_resource_id(resource_id):
    """ Get remote resource using the remote resource id.
    """
    try:
        if not isinstance(resource_id, int) or resource_id < 1:
            message = 'Invalid remote resource id (%d) provided, unable to get remote resource.' % resource_id
            raise Exception(message)
        remote_resource = uframe_get_remote_resource(resource_id)
        return remote_resource
    except Exception as err:
        message = str(err)
        raise Exception(message)


def uframe_get_remote_resources_for_asset_by_id(id):
    remote_resources = []
    try:
        if not isinstance(id, int) or id < 1:
            message = 'Invalid asset id (%d) provided, unable to get remote resources.' % id
            raise Exception(message)

        asset = uframe_get_asset_by_id(id)
        if 'remoteResources' not in asset:
            return remote_resources
        remote_resources = asset['remoteResources']
        return remote_resources
    except Exception as err:
        message = str(err)
        raise Exception(message)


def uframe_get_remote_resources_for_asset_by_uid(uid):
    remote_resources = []
    try:
        if not uid or uid is None:
            message = 'Invalid asset uid provided, unable to get remote resources.'
            raise Exception(message)
        asset = uframe_get_asset_by_uid(uid)
        if 'remoteResources' not in asset:
            return remote_resources
        remote_resources = asset['remoteResources']
        return remote_resources
    except Exception as err:
        message = str(err)
        raise Exception(message)


def uframe_get_remote_resource(resource_id):
    try:
        # Get remote resource.
        base_url, timeout, timeout_read = get_url_info_resources()
        url = '/'.join([base_url, str(resource_id)])
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = 'Failed to get remote resource from uframe using remoteResourceId: %d.' % resource_id
            raise Exception(message)

        if not response.content or response.content is None:
            message = 'No value returned from uframe for remote resource id: %d' % resource_id
            raise Exception(message)
        remote_resource = json.loads(response.content)
        if not remote_resource or remote_resource is None:
            message = 'No value returned from uframe for remote resource id: %d' % resource_id
            raise Exception(message)
        return remote_resource
    except Exception as err:
        message = str(err)
        raise Exception(message)

'''
def uframe_update_remote_resource_by_asset_uid(uid, resource_id, data):
    try:
        # Update remote resource.
        base_url, timeout, timeout_read = get_url_info_resources()
        url = '/'.join([base_url, str(resource_id)])
        response = requests.put(url, data=json.dumps(data), headers=headers())
        if response.status_code != 200:
            message = 'Failed to update remote resource in uframe using remoteResourceId: %d.' % resource_id
            raise Exception(message)

        if not response.content or response.content is None:
            message = 'No value returned from uframe for remote resource id: %d' % resource_id
            raise Exception(message)
        # response.content on success:
        # {u'message': u'Element updated successfully.', u'id': 5481, u'statusCode': u'OK'}

        # Get remote resource.
        base_url, timeout, timeout_read = get_url_info_resources()
        url = '/'.join([base_url, str(resource_id)])
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = 'Failed to get remote resource from uframe using remoteResourceId: %d.' % resource_id
            raise Exception(message)

        remote_resource = json.loads(response.content)
        if not remote_resource or remote_resource is None:
            message = 'No value returned from uframe for remote resource id: %d' % resource_id
            raise Exception(message)

        # Refresh asset cache with remote resource information.
        asset = process_asset_update(uid)

        # Return remote resource.
        return remote_resource
    except Exception as err:
        message = str(err)
        raise Exception(message)
'''


def get_remote_resource_info(data, action=None):
    """ Get information from asset request.data to process the remote resource.
    """
    try:
        # Get remote resource class
        _class = get_class_remote_resource()

        # Get remoteResourceId
        remoteResourceId = None
        if 'remoteResourceId' in data:
            remoteResourceId = data['remoteResourceId']

        # Get lastModifiedTimeStamp
        lastModifiedTimestamp = None
        if 'lastModifiedTimestamp' in data:
            lastModifiedTimestamp = data['lastModifiedTimestamp']

        if action == 'update':
            if remoteResourceId is None or lastModifiedTimestamp is None:
                message = 'Update remoteResource requires a lastModifiedTimestamp and remoteResourceId.'
                raise Exception(message)

            if not isinstance(remoteResourceId, int):
                message = 'The remoteResourceId value must be of type int.'
                raise Exception(message)
            if not isinstance(lastModifiedTimestamp, long) and not isinstance(lastModifiedTimestamp, int):
                message = 'The lastModifiedTimestamp value must be of type long.'
                raise Exception(message)
            if lastModifiedTimestamp <= 0:
                message = 'Invalid lastModifiedTimestamp value provided.'
                raise Exception(message)
            if remoteResourceId <= 0:
                message = 'Invalid remoteResourceId value provided.'
                raise Exception(message)

        return _class, remoteResourceId, lastModifiedTimestamp

    except Exception as err:
        message = str(err)
        raise Exception(message)


def uframe_update_remote_resource_by_resource_id(resource_id, data):
    try:
        # Put remote resource.
        base_url, timeout, timeout_read = get_url_info_resources()
        url = '/'.join([base_url, str(resource_id)])
        response = requests.put(url, data=json.dumps(data), headers=headers())
        if response.status_code != 200:
            message = 'Failed to update remote resource in uframe using remoteResourceId: %d.' % resource_id
            raise Exception(message)

        if not response.content or response.content is None:
            message = 'No value returned from uframe for remote resource id: %d' % resource_id
            raise Exception(message)

        # Get remote resource.
        base_url, timeout, timeout_read = get_url_info_resources()
        url = '/'.join([base_url, str(resource_id)])
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = 'Failed to get remote resource from uframe using remoteResourceId: %d.' % resource_id
            raise Exception(message)

        remote_resource = json.loads(response.content)
        if not remote_resource or remote_resource is None:
            message = 'No value returned from uframe for remote resource id: %d' % resource_id
            raise Exception(message)
        return remote_resource
    except Exception as err:
        message = str(err)
        raise Exception(message)
