
"""
Asset Management - Common functions and definitions.
    Functions.
        is_instrument(rd)
        is_platform(rd)
        is_mooring(rd)
        get_asset_class_by_rd(rd)
        get_asset_class_by_asset_type(asset_type)
        get_asset_type_by_rd(rd)

    Definitions
        get_asset_types()
        get_supported_asset_types()
        get_asset_classes()
        get_supported_asset_classes()
        get_event_types
        get_supported_event_types
        get_event_types_by_rd(rd)

"""
__author__ = 'Edna Donoughe'

from flask import current_app
import datetime as dt
from dateutil.parser import parse as parse_date
import calendar
import json
import pytz
from ooiservices.app.uframe.config import get_iris_base_url

#- - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Common functions
#- - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Is reference designator a mooring.
def is_mooring(rd):
    """ Verify reference designator is a valid mooring reference designator. Return True or False
    """
    result = False
    try:
        # Check rd is not empty or None
        if not rd or rd is None:
            return False

        # Check rd length equals rd length after trim (catch malformed reference designators)
        len_rd = len(rd)
        if len(rd) != len(rd.strip()):
            message = 'Mooring reference designator is malformed \'%s\'. ' % rd
            current_app.logger.info(message)
            return False

        # Check rd length is equal to 8 (i.e. CP02PMUI)
        if len_rd != 8:
            return False

        # Verify no hyphens ('-') present.
        if rd.count('-') != 0:
            return False

        result = True
        return result

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return result


# Is reference designator a platform.
def is_platform(rd):
    """ Verify reference designator is a valid platform reference designator. Return True or False
    """
    result = False
    try:
        # Check rd is not empty or None
        if not rd or rd is None:
            return False

        # Check rd length equals rd length after trim (catch malformed reference designators)
        len_rd = len(rd)
        if len(rd) != len(rd.strip()):
            message = 'Platform reference designator is malformed \'%s\'. ' % rd
            current_app.logger.info(message)
            return False

        # Check rd length is greater than 14 (i.e. CP02PMUI-WFP01)
        if len_rd != 14:
            return False

        # Verify '-' present and count is 1 (sample of valid: CP02PMUI-WFP01)
        if rd.count('-') != 1:
            return False

        result = True
        return result

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return result


# Is reference designator a instrument.
def is_instrument(rd):
    """ Verify reference designator is a valid instrument reference designator. Return True or False
    """
    debug = True
    result = False
    try:
        if debug: print '\n debug -- uframe/common_tools/is_instrument entered...'
        # Check rd is not empty or None
        if not rd or rd is None:
            return False

        # Check rd length equals rd length after trim (catch malformed reference designators)
        len_rd = len(rd)
        if debug: print '\n debug -- rd: %r' % rd
        if len(rd) != len(rd.strip()):
            message = 'Instrument reference designator is malformed \'%s\'. ' % rd
            current_app.logger.info(message)
            return False

        # Check rd length is greater than 14 and less than or equal to 27
        if len_rd < 14 or len_rd > 27:
            return False

        # Verify '-' present and count is three (sample of valid: CP02PMUI-WFP01-04-FLORTK000)
        if rd.count('-') != 3:
            return False
        result = True
        return result

    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        return result


# Is reference designator an array.
def is_array(rd):
    """ Verify reference designator is a valid array reference designator. Return True or False
    """
    result = False
    try:
        # Check rd is not empty or None
        if not rd or rd is None:
            return False

        # Check rd length equals rd length after trim (catch malformed reference designators)
        len_rd = len(rd)
        if len(rd) != len(rd.strip()):
            message = 'Array reference designator is malformed \'%s\'. ' % rd
            current_app.logger.info(message)
            return False

        # Check rd length is equal to 2.
        if len_rd != 2:
            return False

        # Verify '-' not present and count is zero. (sample of valid: CP)
        if rd.count('-') != 0:
            return False
        result = True
        return result

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return result


# Get asset class by reference designator.
def get_asset_class_by_rd(rd):
    """ Get asset class for reference designator.
    """
    try:
        if is_instrument(rd):
            asset_class = '.XInstrument'
        elif is_platform(rd):
            asset_class = '.XNode'
        elif is_mooring(rd):
            asset_class = '.XMooring'
        elif is_array(rd):
            asset_class = '.XArray'
        else:
            asset_class = '.XAsset'
        return asset_class
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Get asset class by asset type.
def get_asset_class_by_asset_type(asset_type):
    """ Get asset class for asset_type.
    """
    try:
        if asset_type == 'Mooring':
            asset_class = '.XMooring'
        elif asset_type == 'Node':
            asset_class = '.XNode'
        elif asset_type == 'Sensor':
            asset_class = '.XInstrument'
        elif asset_type == 'Array':
            asset_class = '.XArray'
        elif asset_type == 'notClassified':
            asset_class = '.XAsset'
        else:
            if asset_type not in get_asset_types():
                message = 'Unknown asset_type provided (%s), using .XAsset for class.' % asset_type
                current_app.logger.info(message)
            asset_class = '.XAsset'
        return asset_class

    except Exception as err:
        message = str(err)
        raise Exception(message)


# Get asset type by reference designator.
def get_asset_type_by_rd(rd):
    """ For reference designator, return asset type being processed or None.
    """
    result = None
    try:
        if is_instrument(rd):
            result = 'Sensor'
        elif is_mooring(rd):
            result = 'Mooring'
        elif is_platform(rd):
            result = 'Node'
        elif is_array(rd):
            result = 'Array'
        return result

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None

#- - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Raw data server support.
#- - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Get route for getting image thumbnail.
def get_image_thumbnail_route():
    # Used by UI when processing thumbnail images.
    # Original '/api/uframe/get_cam_image/', new '/api/uframe/get_image_thumbnail/'
    return '/api/uframe/get_cam_image/'

def rds_get_supported_array_codes():
    # Used when processing large format data from raw data server.
    # Note: Only those arrays which support normalized folder structure on the raw data
    # server shall be included here.
    return ['RS', 'CE']


def get_linx_support_array_codes():
    # Used when processing data from raw data server for large format index.
    return ['RS', 'CE', 'CP']


# Get years where data is provided on the raw data server.
def rds_get_supported_years():
    # The years where data is provided on the raw data server.
    return ['2009', '2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017']


# Get valid months to be used when searching the raw data server.
def rds_get_valid_months():
    # The valid months to be used when searching the raw data server.
    return ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']


# Get valid extensions.
def get_valid_extensions():
    # The valid file extensions to be used when searching/working with the raw data server.
    return ['.png', '.mseed', '.raw', '.mov', '.mp4']


# Get supported extensions.
def rds_get_supported_sensor_types():
    # The supported sensor types to be used when searching/working with the raw data server.
    return ['-HYD', '-CAMDS', '-CAMHD', '-ZPL']


# Get supported folder types.
def rds_get_supported_folder_types():
    # The supported folder types to be used when searching/working with the raw data server.
    return ['HY', 'CAMDS', 'CAMHD', 'ZPL']


# Get extensions for a sensor type.
def get_extensions_by_sensor_type(sensor_type):
    # The valid file extensions to be used when searching/working with the raw data server for a specific sensor_type.
    # Check if a known sensor type has been provided.
    extensions = []

    # If unknown sensor_type, return None.
    if sensor_type not in rds_get_supported_sensor_types():
        return None

    # Get list of extensions for each sensor_type.
    if sensor_type == '-HYD':
        extensions = ['.mseed', '.png']
    elif sensor_type == '-CAMDS':
        extensions = ['.png']
    elif sensor_type == '-CAMHD':
        extensions = ['.mov', '.mp4']
    elif sensor_type == '-ZPL':
        extensions = ['.raw', '.png']
    return extensions

# Complete lists...
#valid_extensions = ['.mseed', '.png', '.raw', '.mov', '.mp4']
#valid_sensor_types = ['CAMDS', 'CAMHD', 'ZPL', 'HYDBB', 'HYDLF', 'OBS']

# Sprint 10
valid_extensions = ['.png']
valid_sensor_types = ['CAMDS']

def rds_get_valid_sensor_types():
    return valid_sensor_types


def rds_get_valid_extensions():
    return valid_extensions


def rds_get_sensor_type(rd):
    """
    For reference designator, determine sensor type to process.
    """
    sensor_type = None
    try:
        for type in valid_sensor_types:
            check_type = '-' + type
            if check_type in rd:
                sensor_type = type
                break
        return sensor_type
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Gallery info link root for display. (Consider moving to config file.)
def rds_get_instrument_info_url_root():
    return "http://oceanobservatories.org/instruments/"

# Gallery site link root for display. (Consider moving to config file.)
def rds_get_instrument_site_url_root():
    return "http://oceanobservatories.org/site/"


#- - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Common definitions - assets
#- - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_asset_types():
    # Get all defined asset types.
    asset_types = ['Array', 'Mooring', 'Node', 'Sensor', 'notClassified']
    return asset_types


def get_supported_asset_types():
    # Get all supported asset types.
    asset_types = ['Array', 'Mooring', 'Node', 'Sensor', 'notClassified']
    return asset_types


def get_asset_types_for_display():
    # Get all supported asset types in vocabulary friendly display names.
    asset_types = ['Array', 'Platform', 'Node', 'Instrument', 'Not Classified']
    return asset_types

def get_supported_asset_types_for_display():
    # Get all supported asset types in vocabulary friendly display names.
    asset_types = ['Array', 'Platform', 'Node', 'Instrument', 'Not Classified']
    return asset_types


def get_asset_classes():
    # Get all asset classes.
    asset_classes = ['.XArray', '.XMooring', '.XNode', '.XInstrument', '.XAsset']
    return asset_classes


def get_supported_asset_classes():
    # Get all supported asset classes.
    asset_classes = ['.XArray', '.XInstrument', '.XNode', '.XMooring', '.XAsset']
    return asset_classes


def get_uframe_asset_type(value):
    try:
        if value in get_supported_asset_types():
            result = value
        elif value in get_supported_asset_types_for_display():
            if value == 'Platform':
                result = 'Mooring'
            elif value == 'Instrument':
                result = 'Sensor'
            elif value == 'Not Classified':
                result = 'notClassified'
            else:
                message = 'The value \'%s\' provided is not a valid asset type.' % value
                raise Exception(message)
        else:
            message = 'The value \'%s\' provided is not a valid asset type.' % value
            raise Exception(message)

        if result not in get_supported_asset_types():
            message = 'The value \'%s\' is not a supported asset type.' % value
            raise Exception(message)

        return result
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def get_asset_type_display_name(value):
    try:
        if value in get_supported_asset_types_for_display():
            result = value
        elif value in get_supported_asset_types():
            if value == 'Mooring':
                result = 'Platform'
            elif value == 'Sensor':
                result = 'Instrument'
            elif value == 'notClassified':
                result = 'Not Classified'
            else:
                message = 'The value \'%s\' provided is not a valid asset type for display.' % value
                raise Exception(message)
        else:
            message = 'The value \'%s\' provided is not a valid asset type for display.' % value
            raise Exception(message)

        if result not in get_supported_asset_types_for_display():
            message = 'The value \'%s\' is not a supported asset type.' % value
            raise Exception(message)
        return result
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def get_class_remote_resource():
    result = '.XRemoteResource'
    return result


def get_class_deployment():
    result = '.XDeployment'
    return result


#- - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Common definitions - events
#- - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Get event class for an event type.
def get_event_class(event_type):
    """ Get event class for a specific event_type.
    """
    try:
        if event_type not in get_event_types():
            message = 'Unknown event type (%s) provided; unable to return event class.' % event_type
            raise Exception(message)

        if event_type == 'ACQUISITION':
            event_class = '.AcquisitionEvent'
        elif event_type == 'ASSET_STATUS':
            event_class = '.AssetStatusEvent'
        elif event_type == 'ATVENDOR':
            event_class = '.AtVendorEvent'
        elif event_type == 'CALIBRATION_DATA':
            event_class = '.XCalibrationData'
        elif event_type == 'CRUISE_INFO':
            event_class = '.CruiseInfo'
        elif event_type == 'INTEGRATION':
            event_class = '.XIntegrationEvent'
        elif event_type == 'LOCATION':
            event_class = '.XLocationEvent'
        elif event_type == 'RETIREMENT':
            event_class = '.XRetirementEvent'
        elif event_type == 'STORAGE':
            event_class = '.XStorageEvent'
        elif event_type == 'UNSPECIFIED':
            event_class = '.XEvent'
        elif event_type == 'DEPLOYMENT':
            event_class = '.XDeployment'
        else:
            message = 'Unknown event type (%s), unable to return event class.' % event_type
            raise Exception(message)
        return event_class

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


def get_event_types():
    # Get all event type values.
    event_types = ['ACQUISITION', 'ASSET_STATUS', 'ATVENDOR', 'CALIBRATION_DATA', 'CRUISE_INFO',
                   'DEPLOYMENT', 'INTEGRATION', 'LOCATION', 'RETIREMENT', 'STORAGE', 'UNSPECIFIED']
    event_types.sort()
    return event_types

def get_supported_event_types():
    # Get all event type values. (remove 'INTEGRATION', 'LOCATION', , 'UNSPECIFIED')
    event_types = ['ACQUISITION', 'ASSET_STATUS', 'ATVENDOR', 'CALIBRATION_DATA', 'CRUISE_INFO',
                   'DEPLOYMENT',  'RETIREMENT', 'STORAGE']
    event_types.sort()
    return event_types


def get_event_types_by_rd(rd):
    # Get all supported event types values. (hide 'INTEGRATION', 'LOCATION', 'UNSPECIFIED')
    len_rd = len(rd)
    event_types = ['ACQUISITION', 'ASSET_STATUS', 'ATVENDOR', 'CRUISE_INFO', 'DEPLOYMENT',  'RETIREMENT', 'STORAGE']

    # For sensor assets, add event type 'CALIBRATION_DATA'.
    if len_rd >14 and len_rd <=27:
        event_types.append('CALIBRATION_DATA')
    event_types.sort()
    return event_types


def get_event_types_by_asset_type(asset_type):
    # Get all supported event types values. (hide 'INTEGRATION', 'LOCATION', 'UNSPECIFIED')
    event_types = ['ACQUISITION', 'ASSET_STATUS', 'ATVENDOR', 'CRUISE_INFO', 'DEPLOYMENT',  'RETIREMENT', 'STORAGE']

    # For sensor assets, add event type 'CALIBRATION_DATA'.
    if asset_type == 'Sensor':
        event_types.append('CALIBRATION_DATA')
    event_types.sort()
    return event_types


def event_edit_phase_values():
    # Get all editPhase values.
    values = ['EDIT', 'OPERATIONAL', 'STAGED']
    return values


def asset_edit_phase_values():
    # Get all editPhase values.
    values = ['EDIT', 'OPERATIONAL', 'STAGED']
    return values


def deployment_edit_phase_values():
    # Get all editPhase values.
    values = ['EDIT', 'OPERATIONAL', 'STAGED']
    return values


uframe_status_enum_values = ['operational', 'degraded', 'failed', 'notTracked', 'removedFromService', None]
ui_status_display_values = ['Operational', 'Degraded', 'Failed', 'Not Tracked', 'Removed From Service', '']
uframe_status_level_to_display_values_map = dict(zip(uframe_status_enum_values, ui_status_display_values))
display_status_value_to_uframe_level_map = dict(zip(ui_status_display_values, uframe_status_enum_values))


def convert_status_display_value(status_value):
    return display_status_value_to_uframe_level_map.get(status_value)


def convert_status_value_for_display(status_value):
    return uframe_status_level_to_display_values_map.get(status_value, status_value)


def operational_status_values():
    values = uframe_status_enum_values
    return values


def operational_status_display_values():
    values = ui_status_display_values
    return values

def get_status_map():
    result = display_status_value_to_uframe_level_map
    return result


uframe_annotation_qcflags = ['not_operational', 'not_available', 'pending_ingest', 'not_evaluated', 'suspect', 'fail', 'pass']
uframe_annotation_qcflags_display_values = ['Not Operational', 'Not Available', 'Pending Ingest', 'Not Evaluated', 'Suspect', 'Fail', 'Pass']
annotation_qcflags_map = dict(zip(uframe_annotation_qcflags_display_values, uframe_annotation_qcflags))
def get_supported_qcflags():
    # Get all qcflag enumeration values for annotations.
    result = uframe_annotation_qcflags
    result.sort()
    return result


def get_qcflags_map():
    # Get all qcflag enumeration values for annotations.
    result = annotation_qcflags_map
    return result


def get_array_locations():
    arrays_patch = {'CE': {'latitude': 44.37, 'longitude': -124.95},
                    'GP': {'latitude': 49.9795, 'longitude': -144.254},
                    'CP': {'latitude': 40.1, 'longitude': -70.88},
                    'GA': {'latitude': -42.5073, 'longitude': -42.8905},
                    'GI': {'latitude': 60.4582, 'longitude': -38.4407},
                    'GS': {'latitude': -54.0814, 'longitude': -89.6652},
                    'RS': {'latitude': 44.554, 'longitude': -125.352},
                   }
    return arrays_patch


def boolean_values():
    values = ['True', 'False']
    return values


def dump_dict(dict, debug=False):
    if debug:
        print '\n --------------\n %s' % json.dumps(dict, indent=4, sort_keys=True)


def verify_action(action):
    """ Simple error checking for input data.
    """
    valid_actions = ['create', 'update']
    try:
        # Verify action for which we are validating the field (create or update).
        if action is None:
            message = 'Action value of \'create\' or \'update\' required to validate deployment fields.'
            raise Exception(message)
        if not action:
            message = 'Invalid action (empty) provided, use either \'create\' or \'update\'.'
            raise Exception(message)
        if action not in valid_actions:
            message = 'Invalid action (%s) provided, use either \'create\' or \'update\'.' % action
            raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


def to_bool(value):
    """ Converts 'something' to boolean. Raises exception for invalid formats
           Possible True  values: 1, True, "1", "TRue", "yes", "y", "t"
           Possible False values: 0, False, None, [], {}, "", "0", "faLse", "no", "n", "f", 0.0, ...
    """
    if str(value).lower() in ("yes", "y", "true",  "t", "1"):
        return True
    if str(value).lower() in ("no",  "n", "false", "f", "0", "0.0", "", "none", "[]", "{}"):
        return False
    raise Exception('Invalid value for boolean conversion: ' + str(value))


def to_bool_str(value):
    """
       Converts 'something' to boolean. Raises exception for invalid formats
           Possible True  values: 1, True, "1", "TRue", "yes", "y", "t"
           Possible False values: 0, False, None, [], {}, "", "0", "faLse", "no", "n", "f", 0.0, ...
    """
    if str(value).lower() in ("yes", "y", "true",  "t", "1"):
        return "1"
    if str(value).lower() in ("no",  "n", "false", "f", "0", "0.0", "", "none", "[]", "{}"):
        return "0"
    raise Exception('Invalid value for boolean conversion: ' + str(value))


#- - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Common datetime functions
#- - - - - - - - - - - - - - - - - - - - - - - - - - - -
def iso_to_timestamp(iso8601):
    parse_date_time = parse_date(iso8601)
    t = (parse_date_time - dt.datetime(1970, 1, 1, tzinfo=pytz.utc)).total_seconds()
    return t


def get_timestamp_value(value):
    """ Convert float value into formatted string.
    """
    result = value
    try:
        formatted_value = timestamp_to_string(value)
        if formatted_value is not None:
            result = formatted_value
        return result
    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        return result


def timestamp_to_string(time_float):
    """ Convert float to formatted time string. If failure to convert, return None.
    """
    offset = 2208988800
    formatted_time = None
    try:
        if not isinstance(time_float, float):
            return None
        ts_time = convert_from_utc(time_float - offset)
        formatted_time = dt.strftime(ts_time, "%Y-%m-%dT%H:%M:%S")
        return formatted_time
    except Exception as err:
        current_app.logger.info(str(err.message))
        return None


# Note: start of unix epoch (jan 1, 1900 at midnight 00:00) in seconds == 2208988800
# http://stackoverflow.com/questions/13260863/convert-a-unixtime-to-a-datetime-object-
# and-back-again-pair-of-time-conversion (url continued from previous line)
# Convert a unix time u to a datetime object d, and vice versa
def convert_from_utc(u):
    return dt.utcfromtimestamp(u)


def ut(d):
    return calendar.timegm(d.timetuple())


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Location dictionary processing for Assets and Deployments
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Create location dictionary from fields.
def get_location_dict(latitude, longitude, depth, orbitRadius):
    try:
        location = {}
        # Provide latitude, but no longitude
        if latitude is not None and longitude is None:
            message = 'Provide both latitude and longitude; longitude not provided.'
            raise Exception(message)
        # Provide longitude, but no latitude
        elif longitude is not None and latitude is None:
            message = 'Provide both latitude and longitude; latitude not provided.'
            raise Exception(message)

        # Both latitude and longitude are None
        if latitude is None and longitude is None:
            location['location'] = None

        # Both latitude and longitude are provided
        else:
            location['location'] = [longitude, latitude]
        location['latitude'] = latitude
        location['longitude'] = longitude
        location['depth'] = depth
        location['orbitRadius'] = orbitRadius
        return location
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Get location fields from location dictionary.
def get_location_fields(location):
    """ Get fields from location dictionary.
    """
    try:
        lat = None
        lon = None
        location_list = None
        depth = None
        orbitRadius = None
        if location is not None:
            if location['latitude'] is not None and location['longitude'] is None:
                message = 'Provide both latitude and longitude; longitude not provided.'
                raise Exception(message)
            elif location['longitude'] is not None and location['latitude'] is None:
                message = 'Provide both latitude and longitude; latitude not provided.'
                raise Exception(message)
            elif location['latitude'] is not None and location['longitude'] is not None:
                lat = convert_float_field('latitude', location['latitude'])
                lon = convert_float_field('longitude', location['longitude'])
                location_list = [lon, lat]
            depth = location['depth']
            orbitRadius = location['orbitRadius']

        return lat, lon, depth, orbitRadius, location_list
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Used to convert float fields.
def convert_float_field(field, data_field):
    field_type = 'float'
    try:
        if isinstance(data_field, float):
            converted_data_field = data_field
        else:
            if data_field and len(data_field) > 0:
                tmp = float(data_field)
                if not isinstance(tmp, float):
                    raise Exception
                converted_data_field = tmp
            else:
                converted_data_field = None
        return converted_data_field
    except Exception:
        message = 'Invalid value provided for field \'%s\', provide a number.' %field
        raise Exception(message)


# Ensure no duplicates in list. On error return empty list.
def scrub_list(data):
    result = []
    try:
        if data is None:
            return result
        elif not isinstance(data, list):
            message = 'Data provided is not a list.'
            raise Exception(message)
        else:
            for item in data:
                if item not in result:
                    result.append(item)
            if result:
                result.sort()
        return result
    except Exception as err:
        message = err.message
        current_app.logger.info(message)
        return result


'''
def get_rd(data):
    """
    Process uframe reference designator dictionary to get reference designator.
    """
    debug = True
    rd = None
    try:
        if debug: print '\n debug -- Entered common_tools::get_rd: ', data
        if data and data is not None:
            if isinstance(data, dict):
                subsite = data['subsite']
                node = data['node']
                sensor = data['sensor']
                if subsite is not None and node is None:
                    rd = subsite
                elif subsite is not None and node is not None:
                    rd = '-'.join([subsite, node])

                if rd is not None and sensor is not None:
                    rd = '-'.join([rd, sensor])
            else:
                rd = data
        return rd
    except Exception as err:
        message = str(err)
        raise Exception(message)
'''