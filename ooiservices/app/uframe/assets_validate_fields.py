"""
Assets: Validate required fields based on asset type.

"""
from ooiservices.app.uframe.common_tools import (get_asset_types)


def validate_required_fields_are_provided(asset_type, data, action=None):
    """ Verify for the asset_type and action, the required fields have been provided in the input data.
    asset_types = ['Mooring', 'Node', 'Sensor', 'notClassified', 'Array']
    """
    debug = False
    try:
        if debug: print '\n debug -- validate_required_fields_are_provided...'
        # Verify input, on error will raise exception; no error indicates success.
        verify_inputs(asset_type, data, action)

        # Get fields required (from UI) for action.
        required_fields, field_types = asset_ui_get_required_fields_and_types(asset_type, action)
        if not required_fields:
            message = 'Asset type %s action %s requires specific fields.' % (asset_type, action)
            if debug: print '\n exception: ', message
            raise Exception(message)

        if not field_types:
            message = 'Asset type %s action %s requires specific field types.' % (asset_type, action)
            if debug: print '\n exception: ', message
            raise Exception(message)

        # Convert field values - for all field values, convert into target type.
        #updated_data = convert_required_fields(asset_type, data, required_fields, field_types, action)

        # Verify required fields are present in the data and each field has input data of correct type.
        number_of_required_fields = len(required_fields)
        data_fields = data.keys()
        number_of_data_fields = len(data_fields)
        # Processing all fields and type versus value.
        for field in required_fields:
            if not field:
                if debug: print '\n ***** Null or empty field provided in required_fields.'
            if debug: print '\n Processing field: ', field

            # Verify field is provided in data
            if field not in data:
                message = 'required field %s not provided in data.' % field
                raise Exception(message)

            # Verify field type is provided in defined field_types.
            if field not in field_types:
                message = 'required field %s does not have a defined field type value.' % field
                raise Exception(message)

            # Verify field value in data is of expected type.
            if data[field] is not None:
                if field_types[field] == 'string':
                    if not isinstance(data[field], str) and not isinstance(data[field], unicode):
                        message = 'required field %s provided, but value is not of type %s.' % (field, field_types[field])
                        raise Exception(message)
                elif field_types[field] == 'int':
                    if not isinstance(data[field], int):
                        message = 'required field %s provided, but value is not of type %s.' % (field, field_types[field])
                        raise Exception(message)
                elif field_types[field] == 'long':
                    if not isinstance(data[field], long):
                        message = 'required field %s provided, but value is not of type %s.' % (field, field_types[field])
                        raise Exception(message)
                elif field_types[field] == 'dict':
                    if not isinstance(data[field], dict):
                        message = 'required field %s provided, but value is not of type %s.' % (field, field_types[field])
                        raise Exception(message)
                elif field_types[field] == 'float':
                    if not isinstance(data[field], float):
                        message = 'required field %s provided, but value is not of type %s.' % (field, field_types[field])
                        raise Exception(message)
                elif field_types[field] == 'list' or \
                     field_types[field] == 'intlist' or field_types[field] == 'floatlist':
                    if not isinstance(data[field], list):
                        #print '\n Field (list) data[%s]: %s' % (field, data[field])
                        message = 'required field %s provided, but value is not of type %s.' % (field, field_types[field])
                        raise Exception(message)
                elif field_types[field] == 'bool':
                    if not isinstance(data[field], bool):
                        #print '\n Field (list) data[%s]: %s' % (field, data[field])
                        message = 'required field %s provided, but value is not of type %s.' % (field, field_types[field])
                        raise Exception(message)
                else:
                    message = 'required field %s provided, but value is undefined type %s.' % (field, field_types[field])
                    raise Exception(message)

        # Determine if 'extra' fields are being provided in the data, if so, report in log.
        extra_fields = []
        if debug:
            print '\n Number_of_data_fields: ', number_of_data_fields
            print '\n number_of_required_fields: ', number_of_required_fields
        if number_of_data_fields != number_of_required_fields:
            data_fields = data.keys()
            for field in data_fields:
                if field not in required_fields:
                    if field not in extra_fields:
                        extra_fields.append(field)

        if extra_fields:
            if debug: print '\n data contains extra fields: ',  extra_fields
            message = 'data contains extra fields %s, ' % extra_fields
            message += 'correct and re-submit request to validate fields for %s %s asset request.' % \
                       (action.upper(), asset_type)
            raise Exception(message)

        if debug: print '\n Done with validation of required fields.'
        return

    except Exception as err:
        if debug: print '\n Exception processing required fields: %s' % str(err)
        message = str(err)
        raise Exception(message)


def verify_inputs(asset_type, data, action):
    """ Simple error checking for input data.
    """
    debug = False
    valid_actions = ['create', 'update']
    try:
        if debug:
            print '\n ***************** Processing %s asset type.' % asset_type

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
        if debug:
            print '\n validate required fields: \nasset_type: %s\naction: %s' % (asset_type, action)
            print '\n data: ', data

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
        if debug: print '\n Exception processing required fields: %s' % str(err)
        message = str(err)
        raise Exception(message)


def asset_ui_get_required_fields_and_types(asset_type, action):
    """ Get required fields and field types for asset_type being processed.


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
        if debug: print '\n debug -- entering asset_ui_get_required_fields_and_types...'
        # Check parameters.
        if not action:
            message = 'Invalid action (empty) provided, use either \'create\' or \'update\'.'
            raise Exception(message)
        if action not in valid_actions:
            message = 'Invalid action (%s) provided, use either \'create\' or \'update\'.' % action
            raise Exception(message)
        if not asset_type:
            message = 'Asset type %s is required to get asset required fields and types for ui.' % asset_type
            if debug: print '\n Error -- ', message
            raise Exception(message)
        if asset_type not in get_asset_types():
            message ='Asset type %s is required to get asset required fields and types for ui.' % asset_type
            if debug: print '\n Error -- ', message
            raise Exception(message)

        # Set base required fields
        base_required_fields = get_base_required_fields()
        base_required_field_types = get_base_required_field_types()

        if debug: print '\n Getting required fields for asset type %s, action: %s.' % (asset_type, action)
        if asset_type in ['notClassified', 'Mooring', 'Node', 'Array']:
            required_fields = base_required_fields
            field_types = base_required_field_types

        elif asset_type == 'Sensor':
            required_fields = base_required_fields
            field_types = base_required_field_types
            #required_fields.append('calibration')
            #field_types['calibration'] = 'list'

        if required_fields and field_types:
            update_additional_fields = ['id', 'uid', 'lastModifiedTimestamp']
            if action == 'update':
                #required_fields += update_additional_fields
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
                """
                if 'assetId' not in field_types:
                    field_types['assetId'] = 'int'

                """

            required_fields.sort()
            if debug:
                print '\n Asset type %s has required fields for ui(%d): %s' % \
                      (asset_type, len(required_fields), required_fields)
                print '\n Leaving validation; have required_fields and field_types.'
                print '\n debug -- leaving asset_ui_get_required_fields_and_types...'
        else:
            message = 'Asset type %s does not have required fields for ui %s (%d): %s' % \
                      (asset_type, action, len(required_fields), required_fields)
            raise Exception(message)
        return required_fields, field_types

    except Exception as err:
        message = str(err)
        if debug:
            print '\n Exception processing required fields for asset type %s, action %s.\n%s' % \
                  (asset_type, action, message)
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
        if debug: print '\n debug -- asset_get_required_fields_and_types_uframe...'
        if not action:
            message = 'Invalid action (empty) provided, use either \'create\' or \'update\'.'
            raise Exception(message)
        if action not in valid_actions:
            message = 'Invalid action (%s) provided, use either \'create\' or \'update\'.' % action
            raise Exception(message)
        if not asset_type:
            message ='Asset type %s is required to get asset required fields and types for uframe.' % asset_type
            print '\n Error -- ', message
            raise Exception(message)
        if asset_type not in get_asset_types():
            message ='Asset type %s is required to get asset required fields and types for uframe.' % asset_type
            print '\n Error -- ', message
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
            if debug:
                print '\n Asset type %s has required fields for uframe(%d): %s' % \
                      (asset_type, len(required_fields), required_fields)
                print '\n Leaving validation; have required_fields and field_types.'
                print '\n debug -- leaving asset_get_required_fields_and_types_uframe...'
        else:
            message = 'Asset type %s does not have required fields for uframe %s (%d): %s' % \
                      (asset_type, action, len(required_fields), required_fields)
            raise Exception(message)

        return required_fields, field_types

    except Exception as err:
        message = str(err)
        if debug:
            print '\n Exception processing required fields for asset type %s, action %s.\n%s' % \
                  (asset_type, action, message)
        raise Exception(message)


def convert_required_fields(asset_type, data, action=None):
    """ Verify for the asset_type and action, the required fields have been provided in the input data.
    asset_types = ['Mooring', 'Node', 'Sensor', 'notClassified', 'Array']
    """
    converted_data = data.copy()
    debug = False
    try:
        if debug: print '\n =========== Converting asset of %s asset type, action: %s' % (asset_type, action)

        # Fields required (from UI) for uframe create event.
        verify_inputs(asset_type, data, action)
        required_fields, field_types = asset_ui_get_required_fields_and_types(asset_type, action)
        if not required_fields:
            message = 'Asset type %s action %s requires specific fields.' % (asset_type, action)
            if debug: print '\n exception: ', message
            raise Exception(message)
        if not field_types:
            message = 'Asset type %s action %s requires specific field types.' % (asset_type, action)
            if debug: print '\n exception: ', message
            raise Exception(message)

        # Verify required fields are present in the data and each field has input data of correct type.
        number_of_required_fields = len(required_fields)
        data_fields = data.keys()
        number_of_data_fields = len(data_fields)
        # Processing all fields and type versus value.
        for field in required_fields:

            if not field:
                if debug: print '\n ***** Null or empty field provided in required_fields.'
            if debug: print '\n  ----- Converting field: ', field

            # Verify field is provided in data
            if field not in data:
                message = 'required field %s not provided in data.' % field
                raise Exception(message)

            # Verify field type is provided in defined field_types.
            if field not in field_types:
                message = 'required field %s does not have a defined field type value.' % field
                raise Exception(message)

            # Verify field value in data is of expected type.
            if data[field] is not None:

                # 'string' or 'unicode'
                if field_types[field] == 'string':
                    if not isinstance(data[field], str) and not isinstance(data[field], unicode):
                        message = 'required field %s provided, but value is not of type %s.' % (field, field_types[field])
                        raise Exception(message)

                # 'int'
                elif field_types[field] == 'int':
                    try:
                        if debug: print '\n convert to int: %r' % data[field]
                        if data[field] and len(data[field]) > 0:
                            tmp = int(data[field])
                            if debug: print '\n int tmp: %r' % tmp
                        else:
                            tmp = None
                    except:
                        message = 'required field %s provided, but type conversion error (type %s).' % (field, field_types[field])
                        raise Exception(message)
                    converted_data[field] = tmp
                    if not isinstance(converted_data[field], int):
                        message = 'required field %s provided, but value is not of type %s.' % (field, field_types[field])
                        raise Exception(message)

                # 'long'
                elif field_types[field] == 'long':
                    try:
                        if debug: print '\n convert %s to long: %r' % (field, data[field])
                        if data[field] and len(data[field]) > 0:
                            value = str(data[field])
                            tmp = long(value)
                            if debug: print '\n long tmp: %r' % tmp
                        else:
                            tmp = None
                    except:
                        message = 'required field %s provided, but type conversion error (type %s).' % (field, field_types[field])
                        raise Exception(message)
                    converted_data[field] = tmp
                    if tmp is not None:
                        if not isinstance(converted_data[field], long):
                            message = 'required field %s provided, but value is not of type %s.' % (field, field_types[field])
                            raise Exception(message)

                # 'float'
                elif field_types[field] == 'float':
                    try:
                        if data[field] and len(data[field]) > 0:
                            tmp = float(data[field])
                            converted_data[field] = tmp
                            if not isinstance(converted_data[field], float):
                                message = 'required field %s provided, but value is not of type %s.' % (field, field_types[field])
                                raise Exception(message)
                        else:
                            converted_data[field] = None
                    except:
                        message = 'required field %s provided, but type conversion error (type %s).' % (field, field_types[field])
                        raise Exception(message)

                # 'bool'
                elif field_types[field] == 'bool':
                    try:
                        if debug: print '\n convert to bool: %r' % data[field]
                        value = str(data[field])
                        if debug: print '\n value: %r' % value
                        if not value:
                            message = 'Boolean value provided is empty; unable to convert asset field %s' % field
                            raise Exception(message)

                        if value.lower() == 'true':
                            converted_data[field] = True
                        else:
                            converted_data[field] = False
                        if debug: print '\n converted_data[%s]: %r' % (field, converted_data[field])
                    except Exception as err:
                        message = str(err)
                        raise Exception(message)

                    if not isinstance(converted_data[field], bool):
                        if debug: print '\n Field (list) data[%s]: %r' % (field, data[field])
                        message = 'required field %s provided, but value is not of type %s.' % (field, field_types[field])
                        raise Exception(message)

                # 'dict'
                elif field_types[field] == 'dict':
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
                    """
                    if not isinstance(data[field], dict):
                        message = 'required field %s provided, but value is not of type %s.' % (field, field_types[field])
                        raise Exception(message)
                    """
                    #continue

                # 'list'
                elif field_types[field] == 'list':
                    try:
                        #if debug: print '\n convert to list: %r' % data[field]

                        tmp = data[field].strip()
                        if len(tmp) < 2:
                            message = 'Invalid value (%s) for list.' % data[field]
                            #print '\n exception: ', message
                            raise Exception(message)
                        if len(tmp) == 2:
                            if '[' in data[field] and ']' in data[field]:
                                tmp = []
                        else:
                            if '[' in data[field]:
                                tmp = tmp.replace('[', '')
                            if ']' in data[field]:
                                tmp = tmp.replace(']', '')
                            tmp = tmp.strip()
                            if ',' not in tmp:
                                tmp = [int(tmp)]
                            elif ',' in tmp:
                                subs = tmp.split(',')
                                if debug: print '\n subs(%d): %r' % (len(subs), subs)
                                newtmp = []
                                for sub in subs:
                                    sub = sub.strip()
                                    if sub:
                                        if '.' in sub:
                                            #if debug: print '\n convert %r to float...' % sub
                                            val = float(sub)
                                            if debug: print '\n val: %r' % val
                                            newtmp.append(val)
                                        else:
                                            #if debug: print '\n convert %r to int...' % sub
                                            val = int(sub)
                                            if debug: print '\n val: %r' % val
                                            newtmp.append(val)

                                if debug: print '\n subs: newtmp: ', newtmp
                                tmp = newtmp

                        #if debug: print '\n list converted: %r ' % tmp
                    except:
                        message = 'required field %s provided, but type conversion error (type %s).' % (field, field_types[field])
                        raise Exception(message)

                    if not isinstance(tmp, list):
                        #print '\n Field (list) data[%s]: %s' % (field, data[field])
                        message = 'required field %s provided, but value is not of type %s.' % (field, field_types[field])
                        raise Exception(message)
                    converted_data[field] = tmp

                # 'intlist' or 'floatlist'
                elif field_types[field] == 'intlist' or field_types[field] == 'floatlist':
                    try:
                        if debug: print '\n convert to list of ints or floats: %r' % data[field]
                        tmp = data[field].strip()
                        if len(tmp) < 2:
                            message = 'Invalid input value (%s) for list.' % data[field]
                            if debug: print '\n exception: ', message
                            raise Exception(message)
                        if len(tmp) == 2:
                            if '[' in data[field] and ']' in data[field]:
                                tmp = []
                        else:
                            if '[' in data[field]:
                                tmp = tmp.replace('[', '')
                            if ']' in data[field]:
                                tmp = tmp.replace(']', '')
                            tmp = tmp.strip()
                            if ',' not in tmp:
                                if field_types[field] == 'floatlist':
                                    tmp = [float(tmp)]
                                else:
                                    tmp = [int(tmp)]
                            elif ',' in tmp:
                                subs = tmp.split(',')
                                if debug: print '\n subs(%d): %r' % (len(subs), subs)
                                newtmp = []
                                for sub in subs:
                                    if debug: print '\n debug type(sub): ', type(sub)
                                    if not isinstance(sub, float) and not isinstance(sub, float):
                                        if isinstance(sub, str) or isinstance(sub, unicode):
                                            sub = sub.strip()
                                            if sub:
                                                if field_types[field] == 'floatlist':
                                                    if not isinstance(sub, float):
                                                        if debug: print '\n convert %r to float...' % sub
                                                        val = float(sub)
                                                        if debug: print '\n val: %r' % val
                                                        newtmp.append(val)
                                                else:
                                                    if not isinstance(sub, int):
                                                        if debug: print '\n convert %r to int...' % sub
                                                        val = int(sub)
                                                        if debug: print '\n val: %r' % val
                                                        newtmp.append(val)
                                        if debug: print '\n subs: newtmp: ', newtmp
                                        tmp = newtmp

                        if debug: print '\n list converted: %r ' % tmp
                    except:
                        message = 'required field %s provided, but type conversion error (type %s).' % (field, field_types[field])
                        raise Exception(message)

                    if not isinstance(tmp, list):
                        #print '\n Field (list) data[%s]: %s' % (field, data[field])
                        message = 'required field %s provided, but value is not of type %s.' % (field, field_types[field])
                        raise Exception(message)
                    converted_data[field] = tmp
                else:
                    message = 'required field %s provided, but value is undefined type %s.' % (field, field_types[field])
                    raise Exception(message)

        """
        # Determine if 'extra' fields are being provided in the data, if so, report in log.
        extra_fields = []
        if debug:
            print '\n Number_of_data_fields: ', number_of_data_fields
            print '\n number_of_required_fields: ', number_of_required_fields
        if number_of_data_fields != number_of_required_fields:
            data_fields = data.keys()
            for field in data_fields:
                if field not in required_fields:
                    if field not in extra_fields:
                        extra_fields.append(field)

        if extra_fields:
            if debug: print '\n data contains extra fields: ',  extra_fields
            message = 'data contains extra fields %s, ' % extra_fields
            message += 'correct and re-submit request to validate fields for %s %s event request.' % \
                       (action.upper(), asset_type)
            raise Exception(message)
        """

        if debug: print '\n debug -- Completed asset converting_required_fields....\n'
        return converted_data

    except Exception as err:
        if debug: print '\n Exception processing required fields: %s' % str(err)
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