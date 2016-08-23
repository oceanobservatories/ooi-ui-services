"""
Assets: Validate required fields based on asset type.

"""
from ooiservices.app.uframe.common_tools import get_asset_types
from ooiservices.app.uframe.common_convert import convert_ui_data


def validate_required_fields_are_provided(asset_type, data, action=None):
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
        #updated_data = convert_required_fields(asset_type, data, required_fields, field_types, action)

        # Verify required fields are present in the data and each field has input data of correct type.
        number_of_required_fields = len(required_fields)
        data_fields = data.keys()
        number_of_data_fields = len(data_fields)
        # Processing all fields and type versus value.
        for field in required_fields:

            # Verify field is provided in data
            if field not in data:
                message = 'Required field %s not provided in data.' % field
                raise Exception(message)

            # Verify field type is provided in defined field_types.
            if field not in field_types:
                message = 'Required field %s does not have a defined field type value.' % field
                raise Exception(message)

            # Verify field value in data is of expected type.
            if data[field] is not None:
                if field_types[field] == 'string':
                    if not isinstance(data[field], str) and not isinstance(data[field], unicode):
                        message = 'Required field %s provided, but value is not of type %s.' % (field, field_types[field])
                        raise Exception(message)
                elif field_types[field] == 'int':
                    if not isinstance(data[field], int):
                        message = 'Required field %s provided, but value is not of type %s.' % (field, field_types[field])
                        raise Exception(message)
                elif field_types[field] == 'long':
                    if not isinstance(data[field], long):
                        message = 'Required field %s provided, but value is not of type %s.' % (field, field_types[field])
                        raise Exception(message)
                elif field_types[field] == 'dict':
                    if not isinstance(data[field], dict):
                        message = 'Required field %s provided, but value is not of type %s.' % (field, field_types[field])
                        raise Exception(message)
                elif field_types[field] == 'float':
                    if not isinstance(data[field], float):
                        message = 'Required field %s provided, but value is not of type %s.' % (field, field_types[field])
                        raise Exception(message)
                elif field_types[field] == 'list' or \
                     field_types[field] == 'intlist' or field_types[field] == 'floatlist':
                    if not isinstance(data[field], list):
                        message = 'Required field %s provided, but value is not of type %s.' % (field, field_types[field])
                        raise Exception(message)
                elif field_types[field] == 'bool':
                    if not isinstance(data[field], bool):
                        message = 'Required field %s provided, but value is not of type %s.' % (field, field_types[field])
                        raise Exception(message)
                else:
                    message = 'Required field %s provided, but value is undefined type %s.' % (field, field_types[field])
                    raise Exception(message)

        # Determine if 'extra' fields are being provided in the data, if so, report in log.
        extra_fields = []
        if number_of_data_fields != number_of_required_fields:
            data_fields = data.keys()
            for field in data_fields:
                if field not in required_fields:
                    if field not in extra_fields:
                        extra_fields.append(field)
        if extra_fields:
            message = 'Data contains extra fields %s, ' % extra_fields
            message += 'correct and re-submit request to validate fields for %s %s asset request.' % \
                       (action.upper(), asset_type)
            raise Exception(message)

        return

    except Exception as err:
        message = str(err)
        raise Exception(message)


def verify_inputs(asset_type, data, action):
    """ Simple error checking for input data.
    """
    valid_actions = ['create', 'update']
    try:
        if not action:
            message = 'Invalid action (empty) provided, use either \'create\' or \'update\'.'
            raise Exception(message)
        if action not in valid_actions:
            message = 'Invalid action (%s) provided, use either \'create\' or \'update\'.' % action
            raise Exception(message)
        if not data:
            message = 'Field validation requires event type, data dict and a defined action; data is empty.'
            raise Exception(message)
        if not isinstance(data, dict):
            message = 'Field validation requires data to be of type dictionary.'
            raise Exception(message)
        if not asset_type:
            message = 'Field validation requires asset_type to be provided, not empty.'
            raise Exception(message)

        # Verify action for which we are validating the field (create or update).
        actions = ['create', 'update']
        if action is None:
            message = 'Action value of \'create\' or \'update\' required to validate %s asset fields.' % asset_type
            raise Exception(message)
        if action not in actions:
            message = 'Valid action value of \'create\' or \'update\' required to validate %s asset fields.' % asset_type
            raise Exception(message)

        # Verify valid asset_type provided.
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
    valid_actions = ['create', 'update']
    try:
        # Check parameters.
        if not action:
            message = 'Invalid action (empty) provided, use either \'create\' or \'update\'.'
            raise Exception(message)
        if action not in valid_actions:
            message = 'Invalid action (%s) provided, use either \'create\' or \'update\'.' % action
            raise Exception(message)
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
    """ Get 23 required fields for base asset from UI.
    Fields required for update only: 'id', 'uid', ['lastModifiedTimestamp', 'location', 'events', 'calibration']
    Present in input, not required for output:
        'coordinates', 'hasDeploymentEvent', 'augmented', 'deployment_numbers', 'deployment_number', 'Ref Des',
        'depth',
    """
    base_required_fields = [
                            'assetInfo',
                            'assetType',
                            'augmented',
                            'coordinates',
                            'dataSource',
                            'deployment_numbers',
                            'deployment_number',
                            'hasDeploymentEvent',
                            'depth',
                            'latitude',
                            'longitude',
                            'manufactureInfo',
                            'mobile',
                            'notes',
                            'partData',
                            'physicalInfo',
                            'purchaseAndDeliveryInfo',
                            'ref_des',
                            'Ref Des',
                            'remoteDocuments',
                            'remoteResources',
                            'tense',
                            ]
    """
    base_required_fields = [
                            'remoteResources',
                            'notes',
                            'physicalInfo',

                            'assetType',
                            'mobile',
                            'dataSource',
                            'purchaseAndDeliveryInfo',
                            'latitude',
                            'longitude',
                            'ref_des',
                            'manufactureInfo',
                            'tense',
                            'partData',
                            'assetInfo',

                            'remoteDocuments',
                            ]
    """


    return base_required_fields


def get_base_required_field_types():
    """ Get (23) field types for UI asset required fields.
    """
    base_required_field_types = {
                            'id': 'int',
                            'remoteResources': 'list',
                            'notes': 'string',
                            'physicalInfo': 'dict',
                            'uid': 'string',
                            'assetType': 'string',
                            'mobile': 'bool',
                            'dataSource': 'string',
                            'purchaseAndDeliveryInfo': 'dict',
                            'ref_des': 'string',
                            'Ref Des': 'string',
                            'manufactureInfo': 'dict',
                            'hasDeploymentEvent': 'bool',
                            'tense': 'string',
                            'partData': 'dict',
                            'deployment_number': 'string',
                            'lastModifiedTimestamp': 'long',
                            'assetInfo': 'dict',
                            'depth': 'float',
                            'remoteDocuments': 'list',
                            'deployment_numbers': 'intlist',
                            'augmented': 'bool',
                            'coordinates': 'floatlist',
                            'latitude': 'float',
                            'longitude': 'float'
                            }

    return base_required_field_types



#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Required fields for uframe asset.
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_base_required_fields_uframe():
    """ Get (31) required fields for base asset in uframe.
    """
    """

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
    """ Get field types for uframe asset required fields (31).

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
    """ Get UFRAME required fields (list) and field types (dict) for asset_type being processed.

    Asset types: notClassified, Mooring, Node, Sensor, Array
    asset_types = ['Mooring', 'Node', 'Sensor', 'notClassified', 'Array']

    Asset Data structures: base, mooring, node, sensor, array

    Asset       assetType       Defined by @class
    base        notClassified   "@class" : ".XAsset"
    mooring     Mooring         "@class" : ".XMooring"
    node        Node            "@class" : ".XNode"
    sensor      Sensor          "@class" : ".XInstrument"
    array       Array           "@class" : ".XAsset"

    """
    debug = False
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

        if debug: print '\n Getting required fields for asset type %s, action: %s.' % (asset_type, action)
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


def convert_required_fields(asset_type, data, action=None):
    """ Verify for the asset_type and action, the required fields have been provided in the input data.
    asset_types = ['Mooring', 'Node', 'Sensor', 'notClassified', 'Array']
    """
    debug = False
    try:
        # Fields required (from UI) for uframe create event.
        verify_inputs(asset_type, data, action)
        required_fields, field_types = asset_ui_get_required_fields_and_types(asset_type, action)
        if not required_fields:
            message = 'Asset type %s action %s requires specific fields.' % (asset_type, action)
            raise Exception(message)
        if not field_types:
            message = 'Asset type %s action %s requires specific field types.' % (asset_type, action)
            raise Exception(message)

        converted_data = convert_ui_data(data, required_fields, field_types)

        # Verify required fields are present in the data and each field has input data of correct type.
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

        # Convert to int
        if 'deliveryDate' in purchaseAndDeliveryInfo:
            if purchaseAndDeliveryInfo['deliveryDate']:
                try:
                    tmp = long(purchaseAndDeliveryInfo['deliveryDate'])
                    purchaseAndDeliveryInfo['deliveryDate'] = tmp
                except:
                    message = 'Failed to convert purchaseAndDeliveryInfo field: deliveryDate to long. '
                    raise Exception(message)

        # Convert to int
        if 'purchaseDate' in purchaseAndDeliveryInfo:
            if purchaseAndDeliveryInfo['purchaseDate']:
                try:
                    tmp = long(purchaseAndDeliveryInfo['purchaseDate'])
                    purchaseAndDeliveryInfo['purchaseDate'] = tmp
                except:
                    message = 'Failed to convert purchaseAndDeliveryInfo field: purchaseDate to long. '
                    raise Exception(message)

        # Convert to float
        if 'purchasePrice' in purchaseAndDeliveryInfo:
            if purchaseAndDeliveryInfo['purchasePrice']:
                try:
                    tmp = float(purchaseAndDeliveryInfo['purchasePrice'])
                    purchaseAndDeliveryInfo['purchasePrice'] = tmp
                except:
                    message = 'Failed to convert purchaseAndDeliveryInfo field: purchasePrice to float. '
                    raise Exception(message)

        return
    except Exception as err:
        raise Exception(str(err))