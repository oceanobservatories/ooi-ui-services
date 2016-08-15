
"""
Common functions and definitions.
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


#- - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Common functions
#- - - - - - - - - - - - - - - - - - - - - - - - - - - -
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
        return result

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


#- - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Common definitions (assets, events)
#- - - - - - - - - - - - - - - - - - - - - - - - - - - -
def get_asset_types():
    # Get all defined asset types.
    asset_types = ['Mooring', 'Node', 'Sensor', 'notClassified', 'Array']
    return asset_types


def get_supported_asset_types():
    # Get all supported asset types.
    asset_types = ['Mooring', 'Node', 'Sensor']
    return asset_types


def get_asset_classes():
    # Get all asset classes.
    asset_classes = ['.XInstrument', '.XNode', '.XMooring', '.XAsset']
    return asset_classes


def get_supported_asset_classes():
    # Get all supported asset classes.
    asset_classes = ['.XInstrument', '.XNode', '.XMooring']
    return asset_classes


def get_event_types():
    # Get all event type values.
    event_types = ['ACQUISITION', 'ASSET_STATUS', 'ATVENDOR', 'CALIBRATION_DATA', 'CRUISE_INFO',
                   'DEPLOYMENT', 'INTEGRATION', 'LOCATION', 'RETIREMENT', 'STORAGE', 'UNSPECIFIED']
    return event_types

def get_supported_event_types():
    # Get all event type values.
    event_types = ['ACQUISITION', 'ASSET_STATUS', 'ATVENDOR', 'CALIBRATION_DATA', 'CRUISE_INFO',
                   'DEPLOYMENT', 'INTEGRATION', 'LOCATION', 'RETIREMENT', 'STORAGE', 'UNSPECIFIED']
    return event_types


def get_event_types_by_rd(rd):
    # Get all supported event types values.
    len_rd = len(rd)
    event_types = ['ACQUISITION', 'ASSET_STATUS', 'ATVENDOR', 'CRUISE_INFO',
                   'DEPLOYMENT', 'INTEGRATION', 'LOCATION', 'RETIREMENT', 'STORAGE', 'UNSPECIFIED']

    # For sensor assets, add event type 'CALIBRATION_DATA'.
    if len_rd >14 and len_rd <=27:
        event_types.append('CALIBRATION_DATA')
    return event_types

