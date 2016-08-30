
"""
Cruise supporting functions.
"""

__author__ = 'Edna Donoughe'

from flask import current_app
from ooiservices.app.uframe.vocab import get_display_name_by_rd
from ooiservices.app.uframe.asset_tools import (_get_asset_from_assets_dict, _get_id_by_uid)
from ooiservices.app.uframe.config import (get_url_info_cruises_inv, get_uframe_assets_info, get_events_url_base,
                                           get_url_info_cruises, get_uframe_info)
import requests
import requests.exceptions
from requests.exceptions import (ConnectionError, Timeout)
import datetime as dt
import json


# Get cruise inventory.
def get_cruise_inv_from_uframe():
    """ Get cruise inventory list from uframe.
    """
    try:
        url, timeout, timeout_read = get_url_info_cruises_inv()
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = 'Unable to get cruise inventory from uframe.'
            raise Exception(message)
        result = response.json()
        return result

    except ConnectionError:
        message = 'ConnectionError getting uframe cruises.'
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting uframe cruises.'
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Get cruise inventory by subsite from uframe.
def uframe_get_cruise_by_subsite(subsite):
    """ Get cruise inventory list by subsite from uframe.
    """
    try:
        url, timeout, timeout_read = get_url_info_cruises()
        # host:12587/events/cruise/rec/{cruiseid}
        url = '/'.join([url, 'rec', subsite])
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = 'Unable to get cruise inventory for \'%s\' from uframe.' % subsite
            raise Exception(message)
        result = response.json()
        return result

    except ConnectionError:
        message = 'ConnectionError getting uframe cruises.'
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting uframe cruises.'
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Verify unique cruise id does not exist.
def uniqueCruiseIdentifier_exists(cruise_id):
    """ Verify cruise identifier provided does not exist. Boolean result True then exists, else False.
    """
    result = False
    try:
        try:
            # If uframe retuns a value, then cruise exists, otherwise it does not.
            value = uframe_get_cruise_by_subsite(cruise_id)
        except Exception:
            result = True
        return result

    except Exception as err:
        message = str(err)
        raise Exception(message)


def _get_cruise_by_cruise_id(cruise_id):
    """ Get all assets from uframe.
    """
    debug = False
    try:
        base_url, timeout, timeout_read = get_url_info_cruises_inv()
        url = '/'.join([base_url, cruise_id])
        if debug: print '\n check -- [get_cruise_by_cruise_id] url: ', url
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = '(%d) Unable to get cruise %s from uframe.' % (response.status_code, cruise_id)
            raise Exception(message)
        result = response.json()
        return result

    except ConnectionError:
        message = 'ConnectionError getting uframe cruises.'
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting uframe cruises.'
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Get cruise by event id.
def _get_cruise_by_event_id(event_id):
    """ Get cruise by event id.
    """
    check = False
    try:
        # Get base url with port and timeouts.
        url_base, timeout, timeout_read = get_uframe_assets_info()
        url = '/'.join([url_base, get_events_url_base(), str(event_id)])
        if check: print '\n check -- [get_cruise] url: ', url

        # Get cruise [event] information from uframe.
        payload = requests.get(url, timeout=(timeout, timeout_read))
        if payload.status_code != 200:
            message = 'Unable to locate a cruise with an id of %d.' % event_id
            raise Exception(message)
        result = payload.json()
        if result is None:
            result = {}
        return result

    except ConnectionError:
        message = 'Error: ConnectionError getting cruise with event id %d.' % event_id
        raise Exception(message)
    except Timeout:
        message = 'Error: Timeout getting cruise with event id %d.' % event_id
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Get arrays from sensor inventory.
def get_uframe_sensor_inv_arrays():
    """  Get arrays from sensor inventory. Return array list, or on error, raise exception.
    """
    debug = False
    arrays = []
    try:
        sensor_inv = get_uframe_sensor_inv()
        if debug: print '\n debug -- sensor inv: ', sensor_inv
        if sensor_inv:
            for item in sensor_inv:
                if item:
                    if debug: print '\n debug -- item: ', item
                    len_item = len(item)
                    if len_item >= 2:
                        code = item[0:2]
                        if code not in arrays:
                            if code:
                                arrays.append(code)
        if debug: print '\n debug -- arrays: ', arrays
        return arrays

    except ConnectionError:
        message = 'ConnectionError getting sensor inventory from uframe.'
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting sensor inventory from uframe.'
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Get uframe sensor inventory.
def get_uframe_sensor_inv():
    """ Get uframe sensor inventory.
    """
    debug = False
    try:
        url, timeout, timeout_read = get_uframe_info()
        if debug: print '\n debug -- get_uframe_sensor_inv url: ', url
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = 'Failed to get sensor inventory from uframe.'
            raise Exception(message)
        values = response.json()
        return values

    except ConnectionError:
        message = 'ConnectionError getting sensor inventory uframe.'
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting event sensor inventory uframe.'
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


# Get uframe deployments by cruise id.
def get_uframe_deployments_by_cruise_id(cruise_id, type=None):
    """ Get deployments from uframe for cruise_id.

    Requests to uframe:
        http://uframe-host:12587/events/cruise/deployments/CP-2016-0001?phase=all           [all=deploy+recover]
        http://uframe-host:12587/events/cruise/deployments/CP-2016-0001?phase=deploy
        http://uframe-host:12587/events/cruise/deployments/CP-2016-0001?phase=recover
    """
    debug = False
    try:
        if debug:
            print '\n debug -- cruise_id: ', cruise_id
            print '\n debug -- type: ', type


        base_url, timeout, timeout_read = get_url_info_cruises()
        url = '/'.join([base_url, 'deployments', cruise_id])
        if type is not None:
            url += '?type=' + type
        if debug: print '\n check -- [get_uframe_deployments_by_cruise_id] url: ', url
        payload = requests.get(url, timeout=(timeout, timeout_read))

        # If no content, return empty result
        if payload.status_code == 204:
            # Return None when unknown uid is provided; log invalid request.
            message = 'Unknown cruise id %s, failed to get deployments.' % cruise_id
            current_app.logger.info(message)
            return None

        # If error, raise exception
        elif payload.status_code != 200:
            message = 'Error getting deployments for cruise id %s from uframe.' % cruise_id
            raise Exception(message)
        deployments = payload.json()
        if not deployments or deployments is None:
            deployments = []
            #message = 'Unable to get deployments for cruise id %s from uframe.' % cruise_id
            #raise Exception(message)

        # Post process event content for display.
        #event = post_process_event(event)
        return deployments

    except ConnectionError:
        message = 'ConnectionError getting cruise id %s from uframe.' % cruise_id
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting cruise id %s from uframe.' % cruise_id
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


def get_cruises_by_array(cruise_inv):
    """ For all cruises in cruise inventory, create dict, key=array_code, value list of cruise_ids.
    """
    debug = False
    result = {}
    try:
        if debug: print '\n debug -- get_cruises_by_array...'
        if not cruise_inv:
            return result

        arrays = get_uframe_sensor_inv_arrays()
        for array in arrays:
            result[array] = []
            try:
                cruises = uframe_get_cruise_by_subsite(array)
            except Exception as err:
                message = str(err)
                current_app.logger.info(message)
                continue
            if cruises:
                result[array] = cruises
        return result

    except Exception as err:
        message = str(err)
        raise Exception(message)


def _get_cruises():
    """ Get list of cruises by array. On success return dict (key) of cruises for each array.
    """
    debug = False
    cruises_dict = {}
    try:
        cruise_list = get_cruise_inv_from_uframe()
        set_cruise_list = set(cruise_list)
        cruise_list = list(set_cruise_list)
        if cruise_list:
            if debug: print '\n debug -- cruise inventory: ', cruise_list

            # Get cruises by array, sorted (descending) by year then count.
            cruises_dict = get_cruises_by_array(cruise_list)
            if debug: print '\n debug -- cruises_dict: ', json.dumps(cruises_dict, indent=4, sort_keys=True)

            # redo this once new /events/cruises/rec/<subsite> is available
            """
            # for each array, get list of cruises, ordered by [descending] year.
            cruise_arrays = cruises_dict.keys()
            for array_code in cruise_arrays:
                if debug: print '\n Processing array: ', array_code
                array_dict = cruises_dict[array_code]
                if debug: print '\n debug -- array_dict(%s): %s' % (array_code, json.dumps(array_dict, indent=4, sort_keys=True) )

                # Get years for cruises, sort descending
                years = array_dict.keys()
                years.sort(reverse=True)
                if debug: print '\n debug -- Array %s Years: %s' % (array_code, years)

                # For each year collect cruise object list
                for year in years:
                    # Collect all cruises for this year in cruise_objects list.
                    cruise_objects = []
                    cruise_list = array_dict[year]
                    for cruise_id in cruise_list:
                        if debug: print '\n debug -- get cruise_id: ', cruise_id
                        cruise = _get_cruise_by_cruise_id(cruise_id)
                        if not cruise:
                            continue
                        if '@class' in cruise:
                            del cruise['@class']
                        cruise_objects.append(cruise)

                    # Add cruise for year
                    array_dict[year] = cruise_objects

            # Finally, for each array, add array 'name' attribute and re-group cruise information in 'years' attribute.
            for array_code in cruise_arrays:
                # Move all array cruise data by years into 'years' attribute
                array_dict = cruises_dict[array_code].copy()
                cruises_dict[array_code] = {}
                cruises_dict[array_code]['years'] = array_dict

                # Add 'array_name' attribute
                array_name = get_display_name_by_rd(array_code)
                if debug: print '\n debug -- array name: ', array_name
                cruises_dict[array_code]['array_name'] = array_name
            """

        return cruises_dict

    except Exception as err:
        message = str(err)
        raise Exception(message)

'''
# todo ======================================================================================================
# todo ======================================================================================================
# todo - Deprecate
# Create unique cruise id value.
def create_unique_cruise_identifier(data):
    """ Create unique cruise id value.
    """
    cruise_id = None
    try:
        uid = data['assetUid']
        id = _get_id_by_uid(uid)
        asset = _get_asset_from_assets_dict(id)
        rd = asset['ref_des']
        array_code = rd[0:2]
        _datetime = str(dt.datetime.now())
        year = _datetime[0:4]
        cruise_number = get_next_cruise_number(array_code, year)
        string_number = '{0:04d}'.format(cruise_number)
        cruise_id = '-'.join([array_code, year, string_number])
        #print '\n -- cruise_id: ', cruise_id
        return cruise_id
    except Exception as err:
        message = str(err)
        raise Exception(message)

# todo - Deprecate
def get_next_cruise_number(array_code, cruise_year):
    """ For all cruises in cruise inventory, create dict, key=array_code, value list of cruise_ids.
    """
    cruise_id = 0
    cruise_numbers = []
    try:
        cruise_inv = get_cruise_inv_from_uframe()
        if not cruise_inv:
            message = 'No cruise inventory returned from uframe.'
            raise Exception(message)
        inx = 0
        for cruise_id in cruise_inv:
            inx += 1
            if not cruise_id:
                continue
            # Must have '-'
            if '-' not in cruise_id:
                continue
            # Must have two '-', three parts
            if cruise_id.count('-') != 2:
                continue
            # Check for malformed cruise_id based on len
            len_cruise = len(cruise_id) #x-x-x CE-2016-0001
            if len_cruise < 5:
                continue

            code, year, count = cruise_id.split('-', 2)
            if code == array_code and year == cruise_year:
                cruise_numbers.append(count)
            if cruise_numbers:
                cruise_numbers.sort()
                try:
                    cruise_id = int(cruise_numbers[-1]) + 1
                except Exception:
                    message = 'Failed to get next cruise number using cruise inventory.'
                    raise Exception(message)

        return cruise_id

    except Exception as err:
        message = str(err)
        raise Exception(message)


# todo - Deprecate
# Verify unique cruise id format.
def verify_uniqueCruiseIdentifier_format(cruise_id):
    """ Verify the uniqueCruiseIdentifer is in the following format: AA-YYYY-0###, where
    AA      represents the array code, for instance 'RS' for cabled array.
    YYYY    represents the year
    0XXX   represents the cruise number 4 digit field left fill with zeros

    hyphens are used as the separator.
    Example:    "uniqueCruiseIdentifer" : "CP-2016-0001",
    """
    try:
        if len(cruise_id) != 12:
            message = 'Please provide unique cruise identifier in valid format (example: \'RS-2016-0001\')'
            raise Exception(message)

        if cruise_id.count('-') != 2:
            message = 'Please provide unique cruise identifier in valid format. (example: \'RS-2016-0001\')'
            raise Exception(message)

        array_code, year, number = cruise_id.split('-', 2)

        # Check array code
        if not array_code:
            message = 'A valid array code is required for unique cruise identifier. (example: \'RS-2016-0001\')'
            raise Exception(message)
        if len(array_code) != 2:
            message = 'A valid array code is required for unique cruise identifier. (example: \'RS-2016-0001\')'
            raise Exception(message)

        # Year of cruise
        if not year:
            message = 'A valid year is required for unique cruise identifier. (example: \'RS-2016-0001\')'
            raise Exception(message)

        if len(year) != 4:
            message = 'A valid year is required for unique cruise identifier. (example: \'RS-2016-0001\')'
            raise Exception(message)
        try:
            value = int(year)
        except Exception:
            message = 'The unique cruise identifier (\'%s\') has an invalid year field.'
            raise Exception(message)
        if value < 2000 or value > 2100:
            message = 'A valid year shall be greater than 2000 and less than 2100. (example: \'RS-2016-0001\')'
            raise Exception(message)

        # Cruise number
        if not number:
            message = 'A valid cruise number is required for unique cruise identifier. (example: \'RS-2016-0001\')'
            raise Exception(message)

        if len(number) != 4:
            message = 'A valid cruise number is required for unique cruise identifier. (example: \'RS-2016-0001\')'
            raise Exception(message)

        try:
            value = int(number)
        except Exception:
            message = 'A valid cruise number is required for unique cruise identifier. (example: \'RS-2016-0001\')'
            raise Exception(message)

        #string_number = '{0:04d}'.format(value)
        #if debug: print 'test for cruise number: %s' % string_number   # python >= 2.6'

    except Exception as err:
        message = str(err)
        raise Exception(message)
'''


