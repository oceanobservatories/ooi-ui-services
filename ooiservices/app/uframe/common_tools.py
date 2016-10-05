
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
import calendar
import json


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
    result = False
    try:
        # Check rd is not empty or None
        if not rd or rd is None:
            return False

        # Check rd length equals rd length after trim (catch malformed reference designators)
        len_rd = len(rd)
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
        message = str(err)
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


def get_asset_classes():
    # Get all asset classes.
    asset_classes = ['.XArray', '.XMooring', '.XNode', '.XInstrument', '.XAsset']
    return asset_classes


def get_supported_asset_classes():
    # Get all supported asset classes.
    asset_classes = ['.XArray', '.XInstrument', '.XNode', '.XMooring', '.XAsset']
    return asset_classes


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
    # Get all event type values. Missing 'DEPLOYMENT'.
    event_types = ['ACQUISITION', 'ASSET_STATUS', 'ATVENDOR', 'CALIBRATION_DATA', 'CRUISE_INFO',
                   'DEPLOYMENT', 'INTEGRATION', 'LOCATION', 'RETIREMENT', 'STORAGE', 'UNSPECIFIED']
    event_types.sort()
    return event_types


def get_event_types_by_rd(rd):
    # Get all supported event types values.
    len_rd = len(rd)
    event_types = ['ACQUISITION', 'ASSET_STATUS', 'ATVENDOR', 'CRUISE_INFO',
                   'DEPLOYMENT', 'INTEGRATION', 'LOCATION', 'RETIREMENT', 'STORAGE', 'UNSPECIFIED']

    # For sensor assets, add event type 'CALIBRATION_DATA'.
    if len_rd >14 and len_rd <=27:
        event_types.append('CALIBRATION_DATA')
    event_types.sort()
    return event_types


def get_event_types_by_asset_type(asset_type):
    # Get all supported event types values.
    event_types = ['ACQUISITION', 'ASSET_STATUS', 'ATVENDOR', 'CRUISE_INFO',
                   'DEPLOYMENT', 'INTEGRATION', 'LOCATION', 'RETIREMENT', 'STORAGE', 'UNSPECIFIED']

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


# todo - get this dynamically, sprint 2, or 3
def get_supported_array_codes():
    values = ['CP', 'CE', 'RS',  'GI', 'GS', 'GP', 'GA', 'SS']
    return values


def operational_status_values():
    values = ['Operational', 'Degraded', 'Failed', 'notTracked']
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


#- - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Common datetime functions
#- - - - - - - - - - - - - - - - - - - - - - - - - - - -
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
        formatted_time = dt.datetime.strftime(ts_time, "%Y-%m-%dT%H:%M:%S")
        return formatted_time
    except Exception as err:
        current_app.logger.info(str(err.message))
        return None


# Note: start of unix epoch (jan 1, 1900 at midnight 00:00) in seconds == 2208988800
# http://stackoverflow.com/questions/13260863/convert-a-unixtime-to-a-datetime-object-
# and-back-again-pair-of-time-conversion (url continued from previous line)
# Convert a unix time u to a datetime object d, and vice versa
def convert_from_utc(u):
    return dt.datetime.utcfromtimestamp(u)


def ut(d):
    return calendar.timegm(d.timetuple())
