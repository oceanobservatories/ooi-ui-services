"""
Asset Management - Assets: Create and update functions.
"""
__author__ = 'Edna Donoughe'

from flask import current_app
from copy import deepcopy

from ooiservices.app.uframe.asset_tools import format_asset_for_ui
from ooiservices.app.uframe.asset_cache_tools import (refresh_asset_cache, asset_cache_refresh)
from ooiservices.app.uframe.common_tools import (get_asset_types, get_asset_class_by_asset_type, verify_action,
                                                 get_class_remote_resource, asset_edit_phase_values, get_location_dict,
                                                 convert_float_field, get_uframe_asset_type)
from ooiservices.app.uframe.assets_validate_fields import (assets_validate_required_fields_are_provided,
                                                           validate_required_fields_remote_resource)
from ooiservices.app.uframe.uframe_tools import (uframe_get_asset_by_id, uframe_get_asset_by_uid,
                                                 uframe_postto_asset, uframe_create_asset, uframe_update_asset,
                                                 uframe_get_remote_resource_by_id,
                                                 uframe_update_remote_resource_by_resource_id)


# Create asset.
def _create_asset(data):
    """ Create new asset, return asset on success. On failure, log and raise exception.
    """
    action = 'create'
    try:
        if not data:
            message = 'Data is required to create an asset, none provided.'
            raise Exception(message)

        # Transform input data for uframe create.
        xasset = transform_asset_for_uframe(None, data, action=action)

        # Check asset uid BEFORE creating in uframe.
        # Get proposed asset uid.
        uid = None
        if xasset:
            if 'uid' in xasset:
                uid = xasset['uid']
        if uid is None:
            message = 'The uid is not defined in request data, unable to create asset.'
            raise Exception(message)

        # Check uid for spaces and slashes. (temporary)
        if ' ' in uid or '/' in uid:
            message = 'Asset uid should not contain spaces or slashes, unable to create asset.'
            raise Exception(message)

        #- - - - - - - - - - - - - - - - - - - - - - - - -
        # Create new asset in uframe.
        #- - - - - - - - - - - - - - - - - - - - - - - - -
        new_uframe_asset = uframe_create_asset(xasset)

        #--------------------
        # Get asset id.
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

        # Minimize data for cache.
        asset_store = deepcopy(ui_asset)
        if 'events' in asset_store:
            del asset_store['events']
        if 'calibration' in asset_store:
            del asset_store['calibration']

        # Refresh asset cache.
        refresh_asset_cache(id, asset_store, action)
        #--------------------

        # return updated asset
        return ui_asset

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def refresh_asset_deployment(uid, rd):
    """ When a deployment is created, each asset cache must be updated to reflect deployment updates.
    """
    from ooiservices.app.uframe.common_tools import dump_dict
    debug = False
    try:
        if debug: print '\n debug -- Entered refresh_asset_deployment...'
        if uid is None:
            return

        # Get asset from uframe by uid.
        asset = uframe_get_asset_by_uid(uid)
        if not asset:
            message = 'Failed to get asset by uid \'%s\'.' % uid
            raise Exception(message)

        # Get asset id.
        id = None
        if 'assetId' in asset:
            id = asset['assetId']
        if id is None:
            message = 'Failed to retrieve id from uframe asset with uid \'%s\'.' % uid
            raise Exception(message)

        # Format uframe asset data for UI.
        if debug: print '\n debug -- Calling format_asset_for_ui: uid/id: %s/%d' % (uid, id)
        ui_asset = format_asset_for_ui(asset)
        if debug:
            print '\n debug -- After calling format_asset_for_ui: uid/id: %s/%d' % (uid, id)
            dump_dict(ui_asset, debug)
        if not ui_asset or ui_asset is None:
            message = 'Failed to format uframe asset for UI; asset id/uid: %d/%s' % (id, uid)
            raise Exception(message)

        # Minimize data for cache.
        asset_store = deepcopy(ui_asset)
        if 'events' in asset_store:
            del asset_store['events']
        if 'calibration' in asset_store:
            del asset_store['calibration']

        # Refresh asset cache.
        if debug:
            print '\n debug -- Calling asset_cache_refresh for %s/%d/%s: ' % (uid, id, rd)
            dump_dict(asset_store, debug)
        asset_cache_refresh(id, asset_store, rd)
        if debug: print '\n debug -- Calling asset_cache_refresh...'
        return

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# Update asset.
def _update_asset(id, data):
    """ For asset data and asset id, validate and marshall data to perform update.

    Asset data is from UI and must be transformed into uframe asset format.
    Updated asset is returned on success. On failure, log and raise exception.
    """
    asset_type = None
    action = 'update'
    debug = False
    try:
        # Transform input data from UI into uframe format, get keys ()
        xasset = transform_asset_for_uframe(id, data, action='update')
        if debug:
            print('xasset')
            print(xasset)
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

        # Verify no assetType change.
        existing_asset_type = asset['assetType']
        proposed_asset_type = xasset['assetType']
        if existing_asset_type != proposed_asset_type:
            message = 'The assetType \'%s\' modified to \'%s\'.' % (existing_asset_type, proposed_asset_type)
            current_app.logger.info('Update Asset: %s ' % message)

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
        valid_missing_keys = ['events', 'remoteResources'] # 'location',

        # Assets: Field events are not provided by UI, get from asset. If asset is Sensor, calibration too.
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
            if asset[key] is None:
                asset[key] = []
            else:
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
        if debug:
            print('modified_asset')
            print(modified_asset)

        # Format modified asset from uframe for UI.
        ui_asset = format_asset_for_ui(modified_asset)
        if debug:
            print('ui_asset')
            print(ui_asset)

        # Minimize data for cache.
        asset_store = deepcopy(ui_asset)
        if 'events' in asset_store:
            del asset_store['events']
        if 'calibration' in asset_store:
            del asset_store['calibration']
        refresh_asset_cache(id, asset_store, action)

        # return updated asset
        return ui_asset

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def transform_asset_for_uframe(id, asset, action=None):
    """ Transform UI asset into uframe asset structure.
    """
    uframe_asset = {}
    debug = False
    try:
        verify_action(action)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Perform basic checks on input data
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if not asset:
            message = 'No input provided, unable to process transform for asset %s.' % action
            raise Exception(message)
        if 'assetType' not in asset:
            message = 'Malformed asset; missing required attribute \'assetType\'.'
            raise Exception(message)

        # Convert asset type display names to valid assetType value.
        asset_type = get_uframe_asset_type(asset['assetType'])
        if asset_type not in get_asset_types():
            message = 'Unknown assetType identified in asset during transform: \'%s\'.' % asset_type
            raise Exception(message)

        # Must have an asset uid, otherwise do not proceed.
        if 'uid' not in asset:
            message = 'Malformed asset; missing required attribute \'uid\'.'
            raise Exception(message)
        if not asset['uid'] or  asset['uid'] is None:
            message = 'The uid is undefined.'
            raise Exception(message)

        #- - - - - - - - - - - - - - - - - - - - - -
        # Convert values for fields in 'string asset'
        #- - - - - - - - - - - - - - - - - - - - - -
        converted_asset = assets_validate_required_fields_are_provided(asset_type, asset, action)
        if 'uid' not in converted_asset:
            message = 'Malformed asset; missing required attribute \'uid\'.'
            raise Exception(message)
        if not converted_asset['uid'] or converted_asset['uid'] is None:
            message = '%s asset uid is empty or undefined.' % asset_type
            raise Exception(message)

        # Verify editPhase is provided and valid.
        edit_phase = None
        if 'editPhase' in converted_asset:
            edit_phase = converted_asset['editPhase']
            if edit_phase not in asset_edit_phase_values():
                message = 'The edit phase value provided (\'%s\') is invalid, not one of %s.' % \
                          (edit_phase, asset_edit_phase_values())
                raise Exception(message)

        # Action 'update' specific check.
        if action == 'update':
            # verify asset id in data is same as asset id on PUT.
            if 'id' in converted_asset:
                if converted_asset['id'] != id:
                    message = 'The asset id provided in url does not match id provided in data.'
                    raise Exception(message)
            if 'ref_des' not in converted_asset:
                message = 'Unable to process asset provided, no reference designator field provided.'
                raise Exception(message)
        else:
            # Processing create request.
            # Verify uid is not None.
            if 'uid' in converted_asset:
                if not converted_asset['uid']:
                    message = 'Asset \'uid\' provided is empty; unable to create asset.'
                    raise Exception(message)
                if converted_asset['uid'] is None:
                    message = 'Asset \'uid\' provided is null; unable to create asset.'
                    raise Exception(message)

            # Verify asset uid is unique, if not unique, present error here.
            uid = converted_asset['uid']
            test = None
            try:
                test = uframe_get_asset_by_uid(uid)
            except Exception:
                pass
            if test is not None:
                message = 'An asset already exists with this uid: \'%s\'.' % uid
                raise Exception(message)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Marshall all data for creation of uframe_asset.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        uframe_asset['editPhase'] = edit_phase
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

        # height, length, weight, width
        del asset['physicalInfo']

        # Fields: deliveryDate, deliveryOrderNumber, purchaseDate, purchasePrice
        deliveryDate, deliveryOrderNumber, purchaseDate, purchasePrice = marshall_purchaseAndDeliveryInfo_fields(converted_asset)
        uframe_asset['deliveryDate'] = deliveryDate
        uframe_asset['deliveryOrderNumber'] = deliveryOrderNumber
        uframe_asset['purchaseDate'] = purchaseDate
        uframe_asset['purchasePrice'] = purchasePrice
        #del asset['purchaseAndDeliveryInfo']

        # Fields: assetId, uid, lastModifiedTimestamp [reserved]
        uframe_asset['uid'] = converted_asset['uid']

        if action == 'update':
            uframe_asset['assetId'] = converted_asset['id']
            uframe_asset['lastModifiedTimestamp'] = None #converted_asset['lastModifiedTimestamp']
        else:
            #uframe_asset['lastModifiedTimestamp'] = None
            uframe_asset['assetId'] = -1

        # Fields: mobile, notes, remoteDocuments, remoteResources, dataSource
        uframe_asset['mobile'] = converted_asset['mobile']
        uframe_asset['notes'] = converted_asset['notes']
        uframe_asset['remoteResources'] = converted_asset['remoteResources']
        uframe_asset['dataSource'] = converted_asset['dataSource']

        # Set location.
        if debug:
            print(converted_asset['depth'])
        location = get_location_dict(converted_asset['latitude'], converted_asset['longitude'],
                                     converted_asset['depth'], converted_asset['orbitRadius'])
        if debug:
            print(location)
        uframe_asset['location'] = location
        uframe_asset['depth'] = converted_asset['depth']

        # remoteResources, events and, when necessary, calibration
        if action == 'create':
            #- - - - - - - - - - - - - - - - - - - -
            # Create processing.
            #- - - - - - - - - - - - - - - - - - - -
            uframe_asset['remoteResources'] = None
            uframe_asset['events'] = None
            if asset_type == 'Sensor':
                uframe_asset['calibration'] = None
        else:
            #- - - - - - - - - - - - - - - - - - - -
            # Update processing
            #- - - - - - - - - - - - - - - - - - - -
            # Remote Resources.
            if 'remoteResources' in converted_asset:
                if not converted_asset['remoteResources']:
                    uframe_asset['remoteResources'] = None
                else:
                    uframe_asset['remoteResources'] = converted_asset['remoteResources']
            else:
                uframe_asset['remoteResources'] = None

            # Events.
            if 'events' in converted_asset:
                if not converted_asset['events']:
                    uframe_asset['events'] = None
                else:
                    uframe_asset['events'] = converted_asset['events']
            else:
                uframe_asset['events'] = None

        uframe_asset['tense'] = 'UNKNOWN'
        if debug:
            print('uframe_asset')
            print(uframe_asset)
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
            description = convert_string_field('description', asset_info['description'])
        owner = None
        if 'owner' in asset_info:
            owner = convert_string_field('owner', asset_info['owner'])
        name = None
        if 'name' in asset_info:
            name = convert_string_field('name', asset_info['asset_name'])

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
            firmwareVersion = convert_string_field('firmwareVersion', manufacture_info['firmwareVersion'])

        manufacturer = None
        if 'manufacturer' in manufacture_info:
            manufacturer = convert_string_field('manufacturer', manufacture_info['manufacturer'])

        modelNumber = None
        if 'modelNumber' in manufacture_info:
            modelNumber = convert_string_field('modelNumber', manufacture_info['modelNumber'])

        serialNumber = None
        if 'serialNumber' in manufacture_info:
            serialNumber = convert_string_field('serialNumber', manufacture_info['serialNumber'])


        shelfLifeExpirationDate = None
        if 'shelfLifeExpirationDate' in manufacture_info:
            try:
                if manufacture_info['shelfLifeExpirationDate'] and manufacture_info['shelfLifeExpirationDate'] is not None:
                    shelfLifeExpirationDate = long(manufacture_info['shelfLifeExpirationDate'])
            except Exception as err:
                message = 'Failed to convert shelfLifeExpirationDate to long, set to None. %s' % str(err)
                current_app.logger.info(message)
                raise Exception(message)

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
            institutionPropertyNumber = convert_string_field('institutionPropertyNumber',
                                                             part_info['institutionPropertyNumber'])

        institutionPurchaseOrderNumber = None
        if 'institutionPurchaseOrderNumber' in part_info:
            institutionPurchaseOrderNumber = convert_string_field('institutionPurchaseOrderNumber',
                                                                  part_info['institutionPurchaseOrderNumber'])

        ooiPartNumber = None
        if 'ooiPartNumber' in part_info:
            ooiPartNumber = convert_string_field('ooiPartNumber', part_info['ooiPartNumber'])

        ooiPropertyNumber = None
        if 'ooiPropertyNumber' in part_info:
            ooiPropertyNumber = convert_string_field('ooiPropertyNumber', part_info['ooiPropertyNumber'])

        ooiSerialNumber = None
        if 'ooiSerialNumber' in part_info:
            ooiSerialNumber = convert_string_field('ooiSerialNumber', part_info['ooiSerialNumber'])

        return institutionPropertyNumber, institutionPurchaseOrderNumber, ooiPartNumber, \
               ooiPropertyNumber, ooiSerialNumber
    except Exception as err:
        raise Exception(str(err))


def convert_string_field(field, data_field):
    field_type = 'string'
    try:
        if data_field is None:
            return None
        if not isinstance(data_field, str) and not isinstance(data_field, unicode):
            message = 'Required field \'%s\' provided, but value is not of type %s.' % (field, field_type)
            raise Exception(message)
        if data_field and len(data_field) > 0:
            tmp = str(data_field)
            if not isinstance(tmp, str) and not isinstance(tmp, unicode):
                message = 'Required field \'%s\' provided, but value is not of type %s.' % (field, field_type)
                raise Exception(message)
            converted_data_field = tmp
        else:
            converted_data_field = None
        return converted_data_field

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


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
            physicalInfo = deepcopy(asset['physicalInfo'])
        if physicalInfo is None:
            message = 'Malformed asset, missing required field \'physicalInfo\'.'
            raise Exception(message)

        depthRating = None
        if 'depthRating' in physicalInfo:
            depthRating = convert_float_field('depthRating', physicalInfo['depthRating'])
        del physicalInfo['depthRating']

        powerRequirements = None
        if 'powerRequirements' in physicalInfo:
            powerRequirements = convert_float_field('powerRequirements', physicalInfo['powerRequirements'])
        del physicalInfo['powerRequirements']

        if 'height' in physicalInfo:
            height = convert_float_field('height', physicalInfo['height'])
            physicalInfo['height'] = height

        if 'length' in physicalInfo:
            length = convert_float_field('length', physicalInfo['length'])
            physicalInfo['length'] = length

        if 'weight' in physicalInfo:
            weight = convert_float_field('weight', physicalInfo['weight'])
            physicalInfo['weight'] = weight

        if 'width' in physicalInfo:
            width = convert_float_field('width', physicalInfo['width'])
            physicalInfo['width'] = width

        return depthRating, powerRequirements, physicalInfo
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
            purchaseAndDeliveryInfo = deepcopy(asset['purchaseAndDeliveryInfo'])
        if purchaseAndDeliveryInfo is None:
            message = 'Malformed asset, missing required field \'purchaseAndDeliveryInfo\'.'
            raise Exception(message)

        deliveryDate = None
        if 'deliveryDate' in purchaseAndDeliveryInfo:
            try:
                if purchaseAndDeliveryInfo['deliveryDate'] and purchaseAndDeliveryInfo['deliveryDate'] is not None:
                    deliveryDate = long(purchaseAndDeliveryInfo['deliveryDate'])
                else:
                    deliveryDate = None
            except Exception as err:
                message = 'Failed to convert deliveryDate to long, set to None. %s' % str(err)
                current_app.logger.info(message)
                raise Exception(message)

        deliveryOrderNumber = None
        if 'deliveryOrderNumber' in purchaseAndDeliveryInfo:
            deliveryOrderNumber = convert_string_field('deliveryOrderNumber', purchaseAndDeliveryInfo['deliveryOrderNumber'])

        purchaseDate = None
        if 'purchaseDate' in purchaseAndDeliveryInfo:
            try:
                if purchaseAndDeliveryInfo['purchaseDate'] and purchaseAndDeliveryInfo['purchaseDate'] is not None:
                    purchaseDate = long(purchaseAndDeliveryInfo['purchaseDate'])
            except Exception as err:
                message = 'Failed to convert purchaseDate to long, set to None. %s' % str(err)
                current_app.logger.info(message)
                raise Exception(message)

        purchasePrice = None
        if 'purchasePrice' in purchaseAndDeliveryInfo:
            purchasePrice = convert_float_field('purchasePrice', purchaseAndDeliveryInfo['purchasePrice'])

        return deliveryDate, deliveryOrderNumber, purchaseDate, purchasePrice
    except Exception as err:
        message = str(err)
        raise Exception(str(err))


# Asset update for remoteResources (or child objects).
def process_asset_update(uid, xasset=None, action='update'):
    """ Process asset update after child object updated, for instance after create or update remoteResources.
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
        ui_asset = format_asset_for_ui(modified_asset)

        # Minimize data for cache.
        asset_store = deepcopy(ui_asset)
        if 'events' in asset_store:
            del asset_store['events']
        if 'calibration' in asset_store:
            del asset_store['calibration']
        refresh_asset_cache(id, asset_store, action)

        return ui_asset

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


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
        refresh_asset_cache(id, updated_asset, action, remote_id=remoteResourceId)
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
        remote_resource = uframe_get_remote_resource_by_id(resource_id)
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