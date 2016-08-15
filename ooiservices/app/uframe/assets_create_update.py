"""
Assets: Create and update functions.

"""
__author__ = 'Edna Donoughe'

from flask import current_app
from ooiservices.app import cache
from requests.exceptions import (ConnectionError, Timeout)
from ooiservices.app.uframe.common_tools import (get_asset_class_by_rd, get_asset_types, get_asset_class_by_asset_type)
from ooiservices.app.uframe.config import (get_uframe_assets_info, get_assets_url_base, headers)
from ooiservices.app.uframe.asset_tools import (uframe_get_asset_by_id, _compile_assets)
from ooiservices.app.uframe.assets_validate_fields import (convert_required_fields,
                                                           asset_get_required_fields_and_types_uframe)
import json
import requests

CACHE_TIMEOUT = 172800


# Create asset.
def _create_asset(data):
    """ For asset data, validate and marshall data to perform create.

    Asset data is from UI and must be transformed into uframe asset format.
    New asset is returned on success. On failure, log and raise exception.
    """
    debug = True
    asset_type = None
    action = 'create'
    try:
        if debug: print '\n debug -- _create_asset ...'
        keys = []
        if not data:
            message = 'Data is required to create an asset, none provided.'
            raise Exception(message)

        # Transform input data from UI into uframe format, get keys ()
        xasset = transform_asset_for_uframe(None, data, action=action)
        if debug: print '\n debug -- xasset(%d): %s' % (len(xasset), json.dumps(xasset, indent=4, sort_keys=True))
        xasset_keys = xasset.keys()
        xasset_keys.sort()

        # Update asset in uframe.
        _new_asset = uframe_create_asset(xasset)
        new_asset = _new_asset

        """
        # Verify asset exists: Get uframe asset (for 'calibration', 'events', 'location', 'lastModifiedTimestamp')
        asset = uframe_get_asset_by_id(id)
        if asset:
            keys = asset.keys()
            keys.sort()
            if debug: print '\n actual uframe asset keys(%d): %s' % (len(keys), keys)
            if 'assetType' in asset:
                asset_type = asset['assetType']


        # Assets: Reserved fields: fields which may not be modified by UI once assigned in uframe: assetId, uid, assetType
        reserved_fields = ['assetType', 'assetId', 'uid', 'lastModifiedTimestamp']

        # Determine missing items are in valid items list, is not error.
        valid_missing_keys = ['events', 'location']

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
                if debug: print '\n missing key: ', key

        for key in valid_missing_keys:
            if debug: print '\n Adding %s...' % key
            xasset[key] = asset[key]

        # Apply reserved fields
        for key in reserved_fields:
            if debug: print '\n Adding reserved %s...' % key
            xasset[key] = asset[key]

        # Check all keys required are accounted for.
        xasset_keys = xasset.keys()
        xasset_keys.sort()
        for key in keys:
            if key not in xasset_keys:
                if debug: print '\n Missing key: ', key

        # Format uframe asset data for UI.
        data_list = [_new_asset]
        try:
            asset_just_created, _ = _compile_assets(data_list)
            new_asset = asset_just_created[0]
        except Exception as err:
            message = 'Failed to process uframe asset for ui. %s' % str(err)
            raise Exception(message)

        if not new_asset or new_asset is None:
            raise Exception('Asset compilation failed to return a result; empty or None result.')

        if debug: print '\n debug ***** new_asset(%d): %s' % (len(new_asset),
                                                              json.dumps(new_asset, indent=4, sort_keys=True))

        if debug: print '\n debug -- after compile_assets to process....'
        if debug: print '\n Updating cache...'
        update_asset_cache(id, new_asset, action)
        # return updated asset
        """
        return new_asset

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
    debug = False
    asset_type = None
    try:
        if debug: print '\n debug -- _update_asset: %d' % id
        # Verify asset exists:
        # Get uframe asset (for 'calibration', 'events', 'location', 'lastModifiedTimestamp')
        asset = uframe_get_asset_by_id(id)
        keys = []
        if asset:
            keys = asset.keys()
            keys.sort()
            if debug: print '\n actual uframe asset keys(%d): %s' % (len(keys), keys)
            if 'assetType' in asset:
                asset_type = asset['assetType']

        # Transform input data from UI into uframe format, get keys ()
        xasset = transform_asset_for_uframe(id, data, action='update')
        xasset_keys = xasset.keys()
        xasset_keys.sort()
        if debug: print '\n debug -- xasset(%d): %s' % (len(xasset), json.dumps(xasset, indent=4, sort_keys=True))

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
                if debug: print '\n missing key: ', key

        for key in valid_missing_keys:
            if debug: print '\n Adding %s...' % key
            xasset[key] = asset[key]

        # Apply reserved fields
        for key in reserved_fields:
            if debug: print '\n Adding reserved %s...' % key
            xasset[key] = asset[key]

        # Check all keys required are accounted for.
        xasset_keys = xasset.keys()
        xasset_keys.sort()
        for key in keys:
            if key not in xasset_keys:
                if debug: print '\n Missing key: ', key

        # Update asset in uframe.
        modified_asset = uframe_update_asset(xasset)

        # Format modified asset from uframe for UI.
        updated_asset = format_asset_for_ui(modified_asset)

        if debug: print '\n Updating cache...'
        update_asset_cache(id, updated_asset)

        # return updated asset
        return updated_asset

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def format_asset_for_ui(modified_asset):
    """ Format uframe asset into ui asset.
    """
    debug = False
    try:
        data_list = [modified_asset]
        try:
            asset_with_update, _ = _compile_assets(data_list)
            updated_asset = asset_with_update[0]
        except Exception as err:
            message = 'Failed to format asset for ui. %s' % str(err)
            raise Exception(message)

        if not updated_asset or updated_asset is None:
            raise Exception('Asset compilation failed to return a result; empty or None result.')

        if debug: print '\n debug ***** updated_asset(%d): %s' % \
                        (len(updated_asset), json.dumps(updated_asset, indent=4, sort_keys=True))

        if debug: print '\n debug -- after compile_assets to process....'
        return updated_asset

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def update_asset_cache(id, asset):
    debug = False
    try:
        # Update asset cache ('asset_list')
        asset_cache = cache.get('asset_list')
        if asset_cache:
            if debug: print '\n Updating asset_list cache...'
            found_asset = False
            for item in asset_cache:
                if item['id'] == id:
                    item = asset
                    found_asset = True
                    if debug: print '\n Found and updated item in cache!'
                    break
            if found_asset:
                cache.set('asset_list', asset_cache, timeout=CACHE_TIMEOUT)
            else:
                print '\n Error: Did not find item in cache to update!'
        else:
            if debug: print '\n Did not update asset_list cache...'

        # Update assets_dict cache ('assets_dict')
        assets_dict_cache = cache.get('assets_dict')
        if assets_dict_cache:
            if debug: print '\n Updating assets_dict cache...'
            if id in assets_dict_cache:
                if debug: print '\n Found id %d in assets_dict cache...' % id
                assets_dict_cache[id] = asset
                cache.set('assets_dict', assets_dict_cache, timeout=CACHE_TIMEOUT)
                if debug: print '\n Updated id %d in assets_dict cache...\n' % id
        else:
            if debug: print '\n Did not update assets_dict cache...'

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


# Update asset in uframe.
def uframe_update_asset(asset):
    """ Update asset in uframe. On success return updated asset, on error, raise exception.
    """
    id = None
    check = False
    try:
        # Get asset id from asset data provided.
        if 'assetId' in asset:
            id = asset['assetId']
        if id is None:
            message = 'Invalid asset, missing attribute \'assetId\', request to update asset failed.'
            raise Exception(message)

        # Update asset in uframe.
        base_url, timeout, timeout_read = get_uframe_assets_info()
        url = '/'.join([base_url, get_assets_url_base(), str(id)])
        if check: print '\n check: url: ', url
        response = requests.put(url, data=json.dumps(asset), headers=headers())
        if check:
            print '\n debug -- id: ', id
            print '\n debug -- response.status_code: ', response.status_code
            print '\n debug -- json.loads(response.content): ', json.loads(response.content)
        if response.status_code != 200:
            message = '(%d) Failed to update asset %d.' % (response.status_code, id)
            raise Exception(message)

        # Get updated asset from uframe and return.
        updated_asset = uframe_get_asset_by_id(id)
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
        current_app.logger.info(message)
        raise Exception(message)


# Create asset in uframe.
def uframe_create_asset(asset):
    """ Create asset in uframe. On success return updated asset, on error, raise exception.
    """
    id = None
    check = True
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
        print '\n after uframe create asset: response.status_code: ', response.status_code
        if response.status_code != 201:
            message = '(%d) uframe failed to create asset.' % (response.status_code)
            #response_data = json.loads(response.content)
            #print '\n debug -- response_data: ', response_data
            raise Exception(message)

        #print '\n debug -- create status_code: ', response.status_code

        # Get id for new asset.
        print '\n debug -- get id for new asset...'
        if not response.content:
            message = 'No response content returned from create asset.'
            raise Exception(message)
        response_data = json.loads(response.content)

        # Get new asset from uframe.
        updated_asset = uframe_get_asset_by_id(id)
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
        current_app.logger.info(message)
        raise Exception(message)


def transform_asset_for_uframe(id, asset, action=None):
    """ Transform UI asset into uframe asset structure.

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
    debug = False
    uframe_asset = {}
    valid_actions = ['create', 'update']
    try:
        #print '\n debug -- transform_asset_for_uframe...'
        if action is None:
            message = 'Failed to transform asset, action value is None.'
            raise Exception(message)
        if action not in valid_actions:
            message = 'Invalid action (%s) received in transform asset for uframe. Must be one of %s' % (action,
                                                                                                         valid_actions)
            raise Exception(message)

        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Perform basic checks on input data
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        if debug: print '\n Entered transform_asset_for_uframe...'
        if not asset:
            message = 'Not input provided, unable to process.'
            raise Exception(message)
        if 'assetType' not in asset:
            message = 'Malformed asset; missing required attribute \'assetType\'. Failed to update asset.'
            raise Exception(message)
        asset_type = asset['assetType']
        if asset_type not in get_asset_types():
            message = 'Unknown assetType identified in asset during transform: \'%s\'.' % asset_type
            raise Exception(message)

        #- - - - - - - - - - - - - - - - - - - - - -
        # Convert values for fields in 'string asset'
        #- - - - - - - - - - - - - - - - - - - - - -
        converted_asset = convert_required_fields(asset_type, asset, action)
        if debug: print '\n **************** debug +++++ \n converted_asset(%d): %s' % \
                        (len(converted_asset), json.dumps(converted_asset, indent=4, sort_keys=True))

        # Action 'update' specific check: verify asset id in data is same as asset id on PUT
        if action == 'update':
            if 'id' in converted_asset:
                if converted_asset['id'] != id:
                    message = 'Unable to perform asset update; asset id in request does not match id provided in data.'
                    raise Exception(message)

            # Fields in assetInfo: description, asset_type
            if 'ref_des' not in converted_asset:
                message = 'Unable to process asset provided, no reference designator.'
                raise Exception(message)
            rd = asset['ref_des']
            #asset_class = get_asset_class_by_rd(rd)


        if debug: print '\n ====================== Marshalling converted_data =========================='
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Marshall all data for creation of uframe_asset, build uframe_asset.
        #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
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
            uframe_asset['assetId'] = -1
            uframe_asset['events'] = []
            uframe_asset['calibration'] = []

        # Fields: mobile, notes, remoteDocuments, remoteResources, dataSource
        uframe_asset['mobile'] = converted_asset['mobile']
        uframe_asset['notes'] = converted_asset['notes']
        uframe_asset['remoteDocuments'] = converted_asset['remoteDocuments']
        uframe_asset['remoteResources'] = converted_asset['remoteResources']
        uframe_asset['dataSource'] = converted_asset['dataSource']

        #- - - - - - - - - - - - - - - - - - - - - -
        # Validate uframe_asset object - fields present
        #- - - - - - - - - - - - - - - - - - - - - -
        #if debug: print '\n Before check required fields for uframe asset...'
        #required_fields, field_types = asset_get_required_fields_and_types_uframe(asset_type, action)
        #if debug: print '\n After check required fields for uframe asset...'
        #print '\n debug -- Completed asset transform to uframe_asset.'
        return uframe_asset

    except Exception as err:
        message = str(err)
        print '\n debug -- Exception message: ', message
        current_app.logger.info(message)
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
