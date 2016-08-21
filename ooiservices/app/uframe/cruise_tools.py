
"""
Cruise supporting functions.
"""

__author__ = 'Edna Donoughe'

from flask import current_app
from ooiservices.app.uframe.asset_tools import (_get_asset_from_assets_dict, _get_id_by_uid)
from ooiservices.app.uframe.config import (get_url_info_cruises_inv)
from requests.exceptions import (ConnectionError, Timeout)
import requests
import requests.exceptions
import datetime as dt


# Get cruise inventory from uframe.
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
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting uframe cruises.'
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)


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
        # print '\n -- cruise_id: ', cruise_id
        return cruise_id
    except Exception as err:
        message = str(err)
        raise Exception(message)


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
        current_app.logger.info(message)
        raise Exception(message)


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


