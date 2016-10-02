"""
Asset Management - Assets: Validate required fields based on asset type.
"""
__author__ = 'Edna Donoughe'


from ooiservices.app.uframe.common_tools import (get_asset_types, asset_edit_phase_values, verify_action)
from ooiservices.app.uframe.common_convert import convert_ui_data

from flask import current_app
import math


def assets_validate_required_fields_are_provided(asset_type, data, action=None):
    """ Verify for the asset_type and action, the required fields have been provided in the input data.
    """
    try:
        # Verify input, on error will raise exception; no error indicates success.
        verify_inputs(asset_type, data, action)

        # Get fields required (from UI) for action.
        required_fields, field_types = asset_ui_get_required_fields_and_types(asset_type, action)
        if not required_fields:
            message = 'Asset type %s action %s requires specific fields.' % (asset_type, action)
            raise Exception(message)

        if not field_types:
            message = 'Asset type %s action %s requires specific field types.' % (asset_type, action)
            raise Exception(message)

        # Convert field values - for all field values, convert into target type.
        converted_data = convert_required_fields(asset_type, data, required_fields, field_types, action)
        check_required_fields(converted_data, action, required_fields, field_types)

        return converted_data

    except Exception as err:
        message = str(err)
        raise Exception(message)


def check_required_fields(converted_data, action, required_fields, field_types):
    try:
        # Verify required fields are present in the data and each field has input data of correct type.
        number_of_required_fields = len(required_fields)
        data_fields = converted_data.keys()
        number_of_data_fields = len(data_fields)

        # Processing all fields and type versus value.
        for field in required_fields:

            # Verify field is provided in data
            if field not in converted_data:
                message = 'Required field %s not provided in data.' % field
                raise Exception(message)

            # Verify field type is provided in defined field_types.
            if field not in field_types:
                message = 'Required field %s does not have a defined field type value.' % field
                raise Exception(message)

            # Verify field value in converted data is of expected type.
            if converted_data[field] is not None:
                if field_types[field] == 'string':
                    if not isinstance(converted_data[field], str) and not isinstance(converted_data[field], unicode):
                        message = 'Required field %s provided, but value is not of type %s.' % (field, field_types[field])
                        raise Exception(message)
                elif field_types[field] == 'int':
                    if not isinstance(converted_data[field], int):
                        message = 'Required field %s provided, but value is not of type %s.' % (field, field_types[field])
                        raise Exception(message)
                elif field_types[field] == 'long':
                    if not isinstance(converted_data[field], long):
                        message = 'Required field %s provided, but value is not of type %s.' % (field, field_types[field])
                        raise Exception(message)
                elif field_types[field] == 'dict':
                    if not isinstance(converted_data[field], dict):
                        message = 'Required field %s provided, but value is not of type %s.' % (field, field_types[field])
                        raise Exception(message)
                elif field_types[field] == 'float':
                    if not isinstance(converted_data[field], float):
                        message = 'Required field %s provided, but value is not of type %s.' % (field, field_types[field])
                        raise Exception(message)
                elif field_types[field] == 'list' or \
                     field_types[field] == 'intlist' or \
                     field_types[field] == 'floatlist' or \
                     field_types[field] == 'dictlist':
                    if not isinstance(converted_data[field], list):
                        message = 'Required field %s provided, but value is not of type %s.' % (field, field_types[field])
                        raise Exception(message)
                elif field_types[field] == 'bool':
                    if not isinstance(converted_data[field], bool):
                        message = 'Required field %s provided, but value is not of type %s.' % (field, field_types[field])
                        raise Exception(message)
                else:
                    message = 'Required field %s provided, but value is undefined type %s.' % (field, field_types[field])
                    raise Exception(message)

        # Determine if 'extra' fields are being provided in the converted data, if so, report in log.
        extra_fields = []
        if number_of_data_fields != number_of_required_fields:
            data_fields = converted_data.keys()
            for field in data_fields:
                if field not in required_fields:
                    if field not in extra_fields:
                        extra_fields.append(field)
        if extra_fields:
            message = 'Data contains extra fields %s, ' % extra_fields
            message += 'correct and re-submit request to validate fields for %s asset request.' % action.upper()
            raise Exception(message)

        return
    except Exception as err:
        message = str(err)
        raise Exception(message)


def verify_inputs(asset_type, data, action):
    """ Simple error checking for input data.
    """
    try:
        # Verify action.
        verify_action(action)

        # Verify valid data.
        if not data:
            message = 'Field validation requires event type, data dict and a defined action; data is empty.'
            raise Exception(message)
        if not isinstance(data, dict):
            message = 'Field validation requires data to be of type dictionary.'
            raise Exception(message)

        # Verify valid asset_type provided.
        if not asset_type:
            message = 'Field validation requires asset_type to be provided, not empty.'
            raise Exception(message)
        if asset_type not in get_asset_types():
            message = 'Valid asset type is required to validate asset fields. Invalid value: %s' % asset_type
            raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


def asset_ui_get_required_fields_and_types(asset_type, action):
    """ Get required fields and field types for asset_type being processed.
    """
    required_fields = []
    field_types = {}
    try:
        # Check parameters.
        verify_action(action)
        if not asset_type:
            message = 'Asset type %s is required to get asset required fields and types for ui.' % asset_type
            raise Exception(message)
        if asset_type not in get_asset_types():
            message ='Asset type %s is required to get asset required fields and types for ui.' % asset_type
            raise Exception(message)

        # Set base required fields
        base_required_fields = get_base_required_fields()
        base_required_field_types = get_base_required_field_types()
        if asset_type in ['notClassified', 'Mooring', 'Node', 'Array']:
            required_fields = base_required_fields
            field_types = base_required_field_types
        elif asset_type == 'Sensor':
            required_fields = base_required_fields
            field_types = base_required_field_types
            #required_fields.append('calibration')
            #field_types['calibration'] = 'list'

        if required_fields and field_types:
            # Note additional fields: 'id', 'uid', 'lastModifiedTimestamp'
            if action == 'update':
                if 'id' not in required_fields:
                    required_fields.append('id')
                if 'id' not in field_types:
                    field_types['id'] = 'int'
                if 'uid' not in required_fields:
                    required_fields.append('uid')
                if 'uid' not in field_types:
                    field_types['uid'] = 'int'
                if 'lastModifiedTimestamp' not in required_fields:
                    required_fields.append('lastModifiedTimestamp')
                if 'lastModifiedTimestamp' not in field_types:
                    field_types['lastModifiedTimestamp'] = 'long'
            required_fields.sort()

        else:
            message = 'Asset type %s does not have required fields for ui %s (%d): %s' % \
                      (asset_type, action, len(required_fields), required_fields)
            raise Exception(message)
        return required_fields, field_types

    except Exception as err:
        message = str(err)
        raise Exception(message)


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Required fields in UI asset.
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_base_required_fields():
    """ Get required fields for base asset from UI.
    Fields required for update only: 'id', 'uid', ['lastModifiedTimestamp', 'location', 'events', 'calibration']
    Present in input, not required for output:
        'coordinates', 'hasDeploymentEvent', 'augmented', 'deployment_numbers', 'deployment_number',
        'Ref Des', 'depth',
    2016-08-24: removed 'coordinates'
    2016-08-26: removed 'augmented', 'Ref Des', 'remoteDocuments', 'hasDeploymentEvent',
    2016-09-26: removed 'tense',
    """
    base_required_fields = [
                            'assetInfo',
                            'assetType',
                            'dataSource',
                            'deployment_numbers',
                            'deployment_number',
                            'depth',
                            'editPhase',
                            'latitude',
                            'longitude',
                            'manufactureInfo',
                            'mobile',
                            'notes',
                            'orbitRadius',
                            'partData',
                            'physicalInfo',
                            'purchaseAndDeliveryInfo',
                            'ref_des',
                            'remoteResources',
                            'tense',
                            'uid'
                            ]

    return base_required_fields


def get_base_required_field_types():
    """ Get field types for UI asset required fields.
    2016-08-24: removed 'coordinates': 'floatlist',
    2016-08-26" remove 'augmented': 'bool', 'Ref Des': 'string','hasDeploymentEvent': 'bool','remoteDocuments': 'list',
    added 'editPhase' can have values: EDIT, STAGED, OPERATIONAL
    """
    base_required_field_types = {
                            'assetInfo': 'dict',
                            'assetType': 'string',
                            'dataSource': 'string',
                            'deployment_number': 'string',
                            'deployment_numbers': 'intlist',
                            'depth': 'float',
                            'editPhase': 'string',
                            'id': 'int',
                            'latitude': 'float',
                            'longitude': 'float',
                            'lastModifiedTimestamp': 'long',
                            'manufactureInfo': 'dict',
                            'mobile': 'bool',
                            'notes': 'string',
                            'orbitRadius': 'float',
                            'partData': 'dict',
                            'physicalInfo': 'dict',
                            'purchaseAndDeliveryInfo': 'dict',
                            'ref_des': 'string',
                            'remoteResources': 'dictlist',
                            'tense': 'string',
                            'uid': 'string'
                            }
    return base_required_field_types


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Required fields for uframe asset.
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_base_required_fields_uframe():
    """ Get required fields for base asset in uframe.
    """
    base_required_fields = [
                            'assetId',
                            'assetType',
                            '@class',
                            'dataSource'
                            'deliveryDate',
                            'deliveryOrderNumber',
                            'depthRating',
                            'description',
                            'events',
                            'firmwareVersion',
                            'institutionPropertyNumber',
                            'institutionPurchaseOrderNumber',
                            'location',
                            'manufacturer',
                            'mobile',
                            'modelNumber',
                            'name',
                            'notes',
                            'owner',
                            'ooiPropertyNumber',
                            'ooiPartNumber',
                            'ooiSerialNumber',
                            'serialNumber',
                            'remoteResources',
                            'softwareVersion',
                            'physicalInfo',
                            'powerRequirements',
                            'purchaseDate',
                            'purchasePrice',
                            'shelfLifeExpirationDate',
                            'uid'
                            ]

    return base_required_fields


def get_base_required_field_types_uframe():
    """ Get field types for uframe asset required fields.

    Field types supported: int, long, float, list, intlist, floatlist, string, bool and dict.
    """
    base_required_field_types = {
                            'assetId': 'int',
                            'assetType': 'string',
                            '@class': 'string',
                            'dataSource': 'string',
                            'description': 'string',
                            'deliveryDate': 'long',
                            'deliveryOrderNumber': 'string',
                            'depthRating': 'float',
                            'events': 'list',
                            'firmwareVersion': 'string',
                            'institutionPropertyNumber': 'string',
                            'institutionPurchaseOrderNumber': 'string',
                            'location': 'dict',
                            'manufacturer': 'string',
                            'mobile': 'bool',
                            'modelNumber': 'string',
                            'name': 'string',
                            'notes': 'string',
                            'ooiPropertyNumber': 'string',
                            'ooiPartNumber': 'string',
                            'ooiSerialNumber': 'string',
                            'owner': 'string',
                            'physicalInfo': 'dict',
                            'powerRequirements': 'string',
                            'purchaseDate': 'long',
                            'purchasePrice': 'float',
                            'remoteResources': 'list',
                            'shelfLifeExpirationDate': 'int',
                            'serialNumber': 'string',
                            'softwareVersion': 'string',
                            'uid': 'string'
                            }

    return base_required_field_types


def asset_get_required_fields_and_types_uframe(asset_type, action):
    """ Get uframe required fields (list) and field types (dict) for asset_type being processed.
    """
    required_fields = []
    field_types = {}
    valid_actions = ['create', 'update']
    try:
        if not action:
            message = 'Invalid action (empty) provided, use either \'create\' or \'update\'.'
            raise Exception(message)
        if action not in valid_actions:
            message = 'Invalid action (%s) provided, use either \'create\' or \'update\'.' % action
            raise Exception(message)
        if not asset_type:
            message ='Asset type %s is required to get asset required fields and types for uframe.' % asset_type
            raise Exception(message)
        if asset_type not in get_asset_types():
            message ='Asset type %s is required to get asset required fields and types for uframe.' % asset_type
            raise Exception(message)

        base_required_fields = get_base_required_fields_uframe()
        base_required_field_types = get_base_required_field_types_uframe()
        if asset_type in ['notClassified', 'Mooring', 'Node', 'Array']:
            required_fields = base_required_fields
            field_types = base_required_field_types

        elif asset_type == 'Sensor':
            required_fields = base_required_fields
            field_types = base_required_field_types
            if 'calibration' not in base_required_fields:
                required_fields.append('calibration')
            if 'calibration' not in base_required_field_types:
                field_types['calibration'] = 'list'

        if required_fields and field_types:
            update_additional_fields = ['assetId', 'lastModifiedTimestamp']
            if action == 'update':
                required_fields += update_additional_fields
                if 'assetId' not in field_types:
                    field_types['assetId'] = 'int'
                if 'lastModifiedTimestamp' not in field_types:
                    field_types['lastModifiedTimestamp'] = 'int'
            required_fields.sort()
        else:
            message = 'Asset type %s does not have required fields for uframe %s (%d): %s' % \
                      (asset_type, action, len(required_fields), required_fields)
            raise Exception(message)

        return required_fields, field_types

    except Exception as err:
        message = str(err)
        raise Exception(message)


def convert_required_fields(asset_type, data, required_fields, field_types, action=None):
    """ Verify for the asset_type and action, the required fields have been provided in the input data.
    """
    try:
        # General convert
        converted_data = convert_ui_data(data, required_fields, field_types)

        valid_edit_phases = asset_edit_phase_values()
        if 'editPhase' in converted_data:
            edit_phase = converted_data['editPhase']
            if edit_phase not in valid_edit_phases:
                message = 'Invalid editPhase value (not one of %s).' % valid_edit_phases
                raise Exception(message)

        # Dictionary convert
        for field in required_fields:
            if field_types[field] == 'dict':
                if field == 'manufactureInfo':
                    convert_manufactureInfo_fields(converted_data)
                elif field == 'purchaseAndDeliveryInfo':
                    convert_purchaseAndDeliveryInfo_fields(converted_data)
                elif field == 'physicalInfo':
                    convert_physicalInfo_fields(converted_data)
                elif field == 'assetInfo':
                    convert_assetInfo_fields(converted_data)
                elif field == 'partData':
                    continue
                else:
                    message = 'Unknown asset dict %s to convert: ' % field
                    raise Exception(message)
            elif field_types[field] == 'dictlist':
                if field == 'remoteResources':
                    convert_remoteResources_fields(converted_data)

        return converted_data

    except Exception as err:
        message = str(err)
        raise Exception(message)


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# UI Asset dict processing.
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def convert_assetInfo_fields(asset):
    """
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
    """
    try:
        assetInfo = None
        if 'assetInfo' in asset:
            assetInfo = asset['assetInfo']
        if assetInfo is None:
            message = 'Malformed asset, missing required field \'assetInfo\'.'
            raise Exception(message)

        # Convert to float
        if 'maxdepth' in assetInfo:
            if assetInfo['maxdepth']:
                try:
                    tmp = float(assetInfo['maxdepth'])
                    assetInfo['maxdepth'] = tmp
                except:
                    message = 'Failed to convert assetInfo field: maxdepth to float. '
                    raise Exception(message)

        # Convert to float
        if 'mindepth' in assetInfo:
            if assetInfo['mindepth']:
                try:
                    tmp = float(assetInfo['mindepth'])
                    assetInfo['mindepth'] = tmp
                except:
                    message = 'Failed to convert assetInfo field: mindepth to float. '
                    raise Exception(message)

        return
    except Exception as err:
        raise Exception(str(err))


def convert_manufactureInfo_fields(asset):
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
        manufactureInfo = None
        if 'manufactureInfo' in asset:
            manufactureInfo = asset['manufactureInfo']
        if manufactureInfo is None:
            message = 'Malformed asset, missing required field \'manufactureInfo\'.'
            raise Exception(message)

        # Convert to int
        if 'shelfLifeExpirationDate' in manufactureInfo:
            if manufactureInfo['shelfLifeExpirationDate']:
                try:
                    tmp = long(manufactureInfo['shelfLifeExpirationDate'])
                    manufactureInfo['shelfLifeExpirationDate'] = tmp
                except:
                    message = 'Failed to convert manufactureInfo field: shelfLifeExpirationDate to long. '
                    raise Exception(message)
        return
    except Exception as err:
        raise Exception(str(err))


def convert_physicalInfo_fields(asset):
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
            physicalInfo = asset['physicalInfo']
        if physicalInfo is None:
            message = 'Malformed asset, missing required field \'physicalInfo\'.'
            raise Exception(message)

        # Convert to float
        if 'depthRating' in physicalInfo:
            if physicalInfo['depthRating']:
                try:
                    tmp = float(physicalInfo['depthRating'])
                    physicalInfo['depthRating'] = tmp
                except:
                    message = 'Failed to convert physicalInfo field: depthRating to float.'
                    raise Exception(message)

        # Convert to float
        if 'height' in physicalInfo:
            if physicalInfo['height']:
                try:
                    tmp = float(physicalInfo['height'])
                    physicalInfo['height'] = tmp
                except:
                    message = 'Failed to convert physicalInfo field: height to float.'
                    raise Exception(message)

        # Convert to float
        if 'length' in physicalInfo:
            if physicalInfo['length']:
                try:
                    tmp = float(physicalInfo['length'])
                    physicalInfo['length'] = tmp
                except:
                    message = 'Failed to convert physicalInfo field: length to float.'
                    raise Exception(message)

        # Convert to float
        if 'powerRequirements' in physicalInfo:
            if physicalInfo['powerRequirements']:
                try:
                    tmp = float(physicalInfo['powerRequirements'])
                    physicalInfo['powerRequirements'] = tmp
                except:
                    message = 'Failed to convert physicalInfo field: powerRequirements to float.'
                    raise Exception(message)

        # Convert to float
        if 'weight' in physicalInfo:
            if physicalInfo['weight']:
                try:
                    tmp = float(physicalInfo['weight'])
                    physicalInfo['weight'] = tmp
                except:
                    message = 'Failed to convert physicalInfo field: weight to float.'
                    raise Exception(message)

        # Convert to float
        if 'width' in physicalInfo:
            if physicalInfo['width']:
                try:
                    tmp = float(physicalInfo['width'])
                    physicalInfo['width'] = tmp
                except:
                    message = 'Failed to convert physicalInfo field: width to float.'
                    raise Exception(message)

        return
    except Exception as err:
        raise Exception(str(err))


def convert_purchaseAndDeliveryInfo_fields(asset):
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

        # deliveryDate - Convert to long.
        if 'deliveryDate' in purchaseAndDeliveryInfo:
            if purchaseAndDeliveryInfo['deliveryDate']: # and len(purchaseAndDeliveryInfo['deliveryDate']) > 0:
                try:
                    tmp = long(purchaseAndDeliveryInfo['deliveryDate'])
                    purchaseAndDeliveryInfo['deliveryDate'] = tmp
                except:
                    message = 'Failed to convert purchaseAndDeliveryInfo field: deliveryDate to long.'
                    current_app.logger.info(message)
                    #raise Exception(message)
                    purchaseAndDeliveryInfo['deliveryDate'] = ''

        # purchaseDate - Convert to long
        if 'purchaseDate' in purchaseAndDeliveryInfo:
            if purchaseAndDeliveryInfo['purchaseDate']:
                try:
                    tmp = long(purchaseAndDeliveryInfo['purchaseDate'])
                    purchaseAndDeliveryInfo['purchaseDate'] = tmp
                except:
                    message = 'Failed to convert purchaseAndDeliveryInfo field: purchaseDate to long.'
                    current_app.logger.info(message)
                    #raise Exception(message)
                    purchaseAndDeliveryInfo['purchaseDate'] = ''


        # Convert to float
        if 'purchasePrice' in purchaseAndDeliveryInfo:
            if purchaseAndDeliveryInfo['purchasePrice']:
                try:
                    tmp = float(purchaseAndDeliveryInfo['purchasePrice'])
                    purchaseAndDeliveryInfo['purchasePrice'] = tmp
                except:
                    message = 'Failed to convert purchaseAndDeliveryInfo field: purchasePrice to float. '
                    current_app.logger.info(message)
                    #raise Exception(message)
                    purchaseAndDeliveryInfo['purchasePrice'] = ''

        return
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def convert_remoteResources_fields(asset):
    """
    "remoteResources" : [ {
        "@class": ".XRemoteResource",
        "dataSource": null,
        "keywords": null,
        "label": "testresource",
        "lastModifiedTimestamp": 1472138644728,
        "remoteResourceId": 8446,
        "resourceNumber": "1258.1548.58756.098",
        "status": "active",
        "url": null
        }
        ],
    """
    try:
        remoteResources = None
        if 'remoteResources' in asset:
            remoteResources = asset['remoteResources']
        if remoteResources is None:
            """
            message = 'Malformed asset, missing required field \'remoteResources\'.'
            raise Exception(message)
            """
            asset['remoteResources'] = []
            return

        for remote in remoteResources:
            # Convert to long
            if 'lastModifiedTimestamp' in remote:
                if remote['lastModifiedTimestamp']:
                    try:
                        tmp = long(remote['lastModifiedTimestamp'])
                        remote['lastModifiedTimestamp'] = tmp
                    except:
                        message = 'Failed to convert remoteResources field: lastModifiedTimestamp to long. '
                        raise Exception(message)

            # Convert to int
            if 'remoteResourceId' in remote:
                if remote['remoteResourceId']:
                    try:
                        tmp = int(remote['remoteResourceId'])
                        remote['remoteResourceId'] = tmp
                    except:
                        message = 'Failed to convert remoteResources field: remoteResourceId to int. '
                        raise Exception(message)
        return
    except Exception as err:
        raise Exception(str(err))


def validate_required_fields_remote_resource(asset_type, data, action=None):
    """ Verify the remote remote data provided contains all required fields.
            {
                "@class": ".XRemoteResource",
                "dataSource": null,
                "keywords": null,
                "label": "testresource",
                "lastModifiedTimestamp": 1472128206466,
                "remoteResourceId": 8441,
                "resourceNumber": "1258.1548.58756.098",
                "status": "active",
                "url": null
            },
    """
    try:
        # Note: required_fields must be equal to or a subset of valid fields.
        # Fields which are available in remote resource.
        required_fields = ['@class', 'dataSource', 'keywords', 'label', 'remoteResourceId', 'resourceNumber', 'status', 'url']
        field_types = {
            'dataSource': 'string',
            'keywords': 'string',
            'label': 'string',
            'remoteResourceId': 'int',
            'resourceNumber': 'string',
            'status': 'string',
            'url': 'string',
            '@class': 'string'
        }
        # Fields which must have a value.
        required_values = ['remoteResourceId', '@class']
        if action == 'update':
            required_fields.append('lastModifiedTimestamp')
            field_types['lastModifiedTimestamp'] = 'long'

        for field in required_fields:
            if field not in data:
                message = 'Required field \'%s\' not in remote resource data provided.' % field
                raise Exception(message)

        for field in required_values:
            if not data[field]:
                message = 'Required field \'%s\' value is empty.' % field
                raise Exception(message)

        converted_data = convert_ui_data(data, required_fields, field_types)
        convert_required_fields(asset_type, converted_data, required_fields, field_types, action=None)

        return converted_data

    except Exception as err:
        message = str(err)
        raise Exception(message)
