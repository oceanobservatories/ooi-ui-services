#!/usr/bin/env python

"""
Support for images, utilized for image information and display.

Routes:

[GET] /get_cam_images                             # Get list of available camera thumbnail/images.( Filter orDeprecate?)
[GET] /get_cam_image/<string:image_id>.png'       # Get single thumbnail image. (Deprecate)
[GET] /get_image_thumbnail/<string:image_id>.png' # Get single thumbnail image.


Gallery routes
[GET] /get_data_slice/<string:rd>/<string:start>/<string:end>


Development/Test:
/get_first_date/rd
"""
__author__ = 'Edna Donoughe'


import os.path
from flask import (jsonify, current_app)
from ooiservices.app.uframe import uframe as api
from ooiservices.app.main.errors import bad_request
from ooiservices.app.uframe.media_tools import (_get_media_for_rd, validate_year_month, validate_year,
                                                 _get_base_url_thumbnails, _get_base_url_raw_data,
                                                 get_large_format_index)
from ooiservices.app.uframe.common_tools import (rds_get_sensor_type, rds_get_valid_sensor_types,
                                                 rds_get_instrument_info_url_root, rds_get_instrument_site_url_root)
from ooiservices.app.uframe.media_tools import (get_large_format_for_rd, get_large_format_index_for_rd,
                                                get_file_list_for_large_format_data, fetch_media_for_rd)
from ooiservices.app.uframe.gallery_tools import (get_range_data, _get_data_day, _get_date_bound)
from ooiservices.app.uframe.config import get_rds_base_url

"""
Populate sensor type page...
[GET] /media/get_instrument_list/<string:sensor_type>               # Get list of instruments for sensor type.
[GET] /media/get_instrument_information_link/<string:sensor_type>   # Get info link for sensor type.
[GET] /media/get_instrument_site_link/<string:rd>                   # Get instrument site link (for reference designator).
[GET] /media/get_instrument_rds_link/<string:rd>                    # Get instrument raw data server link.

[GET] /get_base_url_thumbnails                                      # Get thumbnail data store location.
[GET] /get_base_url_raw_data                                        # Get url for raw data server
[GET] /media/get_data_bounds/<string:rd>                        # Get first and last date of data available for instrument.
[GET] /media/get_first_date/<string:rd>                         # Get first date of data available for instrument.
[GET] /media/get_last_date/<string:rd>                          # Get last date of data available for instrument.

[GET] /media/<string:rd>/<string:year>/<string:month>           # Get all media for reference designator by year/month.
[GET] /media/<string:rd>/<string:year>                          # Hold. Due to performance related to response size.

[GET] /media/<string:rd>/date/<string:data_date>                # Get media for a specific date. yyyy-mm-dd
[GET] /media/<string:rd>/range/<string:start>/<string:end>      # Get media for range start/end (yyyy-mm-dd/yyyy-mm-dd)

Data availability routes (use to populate pull down year, month, day selections for reference designator.
[GET] /media/<string:rd>/da/map
[GET] /media/<string:rd>/da/years
[GET] /media/<string:rd>/da/<string:year>
[GET] /media/<string:rd>/da/<string:year>/<string:month>
"""


# Get thumbnail location on server.
@api.route('/media/get_base_url_thumbnails', methods=['GET'])
def media_get_base_url_thumbnails():
    """ Get location for cam images.
    Request: http://localhost:4000/uframe/media/get_base_url_thumbnails
    Response:
    {
      "base": "ooiservices/cam_images"
    }
    """
    try:
        data = _get_base_url_thumbnails()
        return jsonify({'base': data})
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get thumbnail location on server).
@api.route('/media/get_base_url_raw_data', methods=['GET'])
def media_get_base_url_raw_data():
    """ Get root data directory for raw data server.
    Request: http://localhost:4000/uframe/media/get_base_url_raw_data
    Response:
    {
      "base": "https://rawdata.oceanobservatories.org/files/"
    }
    """
    try:
        data = _get_base_url_raw_data()
        return jsonify({'base': data})
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


#- - - - - - - - - - - - - - - - - - - - - - - -
# Get list of instruments by sensor type.
#- - - - - - - - - - - - - - - - - - - - - - - -
# Get list of instruments by sensor type.
@api.route('/media/get_instrument_list/<string:sensor_type>', methods=['GET'])
def media_get_instruments_by_sensor_type(sensor_type):
    """ Get list of all instruments in large format index by sensor type.
    (Used to populate the instrument selection list for a specific sensor type page.)
    For instance. for 'Still Camera (CAMDS) Archive' use: /media/get_instrument_list/CAMDS

    sensor_type must be one of rds_valid_sensor_types: (common_tools.py)
    ['CAMDS', 'CAMHD', 'ZPL', 'HYDBB', 'HYDLF', 'OBS']

    Sample Requests:
    http://localhost:4000/uframe/media/get_instrument_list/CAMDS    # Sprint 10
    http://localhost:4000/uframe/media/get_instrument_list/CAMHD    # Future
    http://localhost:4000/uframe/media/get_instrument_list/ZPL      # Available
    http://localhost:4000/uframe/media/get_instrument_list/HYDBB    # Available
    http://localhost:4000/uframe/media/get_instrument_list/HYDLF    # Future
    http://localhost:4000/uframe/media/get_instrument_list/OBS      # Future

    Sample Requests with response results included.
    http://localhost:4000/uframe/media/get_instrument_list/CAMDS
    {
      "instruments": [
        "CE02SHBP-MJ01C-08-CAMDSB107",
        "CE04OSBP-LV01C-06-CAMDSB106",
        "RS01SBPS-PC01A-07-CAMDSC102",
        "RS01SUM2-MJ01B-05-CAMDSB103",
        "RS03AXPS-PC03A-07-CAMDSC302",
        "RS03INT1-MJ03C-05-CAMDSB303"
      ]
    }
    http://localhost:4000/uframe/media/get_instrument_list/CAMHD
    {
      "instruments": [
        "RS03ASHS-PN03B-06-CAMHDA301"
      ]
    }
    http://localhost:4000/uframe/media/get_instrument_list/ZPL
    {
      "instruments": [
        "CE02SHBP-MJ01C-07-ZPLSCB101",
        "CE04OSPS-PC01B-05-ZPLSCB102"
      ]
    }
    http://localhost:4000/uframe/media/get_instrument_list/HYDBB
    {
      "instruments": [
        "CE02SHBP-LJ01D-11-HYDBBA106",
        "CE04OSBP-LJ01C-11-HYDBBA105",
        "RS01SBPS-PC01A-08-HYDBBA103",
        "RS01SLBS-LJ01A-09-HYDBBA102",
        "RS03AXBS-LJ03A-09-HYDBBA302",
        "RS03AXPS-PC03A-08-HYDBBA303"
      ]
    }
    http://localhost:4000/uframe/media/get_instrument_list/HYDLF
    {
      "instruments": []
    }
    http://localhost:4000/uframe/media/get_instrument_list/OBS
    {
      "instruments": []
    }
    """
    try:
        # Get valid sensor types.
        valid_sensor_types = rds_get_valid_sensor_types()
        if sensor_type not in valid_sensor_types:
            message = 'Invalid sensor type (%s), not one of valid sensor types: %s' % (sensor_type, valid_sensor_types)
            raise Exception(message)

        # Get large format index and retrieve instrument list available.
        data = get_large_format_index()

        instruments_available = data.keys()
        instruments = []
        for instrument in instruments_available:
            if sensor_type in instrument:
                if instrument not in instruments:
                    instruments.append(instrument)
        if instruments:
            instruments.sort()
        return jsonify({'instruments': instruments})
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)

#- - - - - - - - - - - - - - - - - - - - - - - -
# Get instrument information link by sensor type.
#- - - - - - - - - - - - - - - - - - - - - - - -
@api.route('/media/get_instrument_information_link/<string:sensor_type>', methods=['GET'])
def media_get_instrument_information_link_by_sensor_type(sensor_type):
    """ Get instrument information link by sensor type.
    (Used to provided the link for the instrument information display on sensor type page.)
    For instance. for 'Still Camera (CAMDS) Archive' use: /media/get_instrument_list/CAMDS

    sensor_type must be one of rds_valid_sensor_types: (common_tools.py)
    ['CAMDS', 'CAMHD', 'ZPL', 'HYDBB', 'HYDLF', 'OBS']

    Sample Requests:
    http://localhost:4000/uframe/media/get_instrument_information_link/CAMDS    # Sprint 10
    http://localhost:4000/uframe/media/get_instrument_information_link/CAMHD    # Available
    http://localhost:4000/uframe/media/get_instrument_information_link/ZPL      # Available
    http://localhost:4000/uframe/media/get_instrument_information_link/HYDBB    # Available
    http://localhost:4000/uframe/media/get_instrument_information_link/HYDLF    # Available
    http://localhost:4000/uframe/media/get_instrument_information_link/OBS      # Available

    Sample Requests with response results included.
    http://localhost:4000/uframe/media/get_instrument_information_link/CAMDS
    {
      "instrument_information_url": "http://oceanobservatories.org/instruments/camds/"
    }
    http://localhost:4000/uframe/media/get_instrument_information_link/CAMHD
    {
      "instrument_information_url": "http://oceanobservatories.org/instruments/camhd/"
    }
    http://localhost:4000/uframe/media/get_instrument_information_link/ZPL
    {
      "instrument_information_url": "http://oceanobservatories.org/instruments/zpls/"
    }
    http://localhost:4000/uframe/media/get_instrument_information_link/HYDBB
    {
      "instrument_information_url": "http://oceanobservatories.org/instruments/hydbb/"
    }
    http://localhost:4000/uframe/media/get_instrument_information_link/HYDLF
    {
      "instrument_information_url": "http://oceanobservatories.org/instruments/hydlf/"
    }
    http://localhost:4000/uframe/media/get_instrument_information_link/OBS
    {
      "instrument_information_url": "http://oceanobservatories.org/instrument-class/obsbb/"
    }
    """
    try:
        # Get valid sensor types.
        valid_sensor_types = rds_get_valid_sensor_types()
        if sensor_type not in valid_sensor_types:
            message = 'Invalid sensor type (%s), not one of valid sensor types: %s' % (sensor_type, valid_sensor_types)
            raise Exception(message)

        # Get large format index and retrieve instrument list available.
        root_url = rds_get_instrument_info_url_root()
        suffix = ""
        if sensor_type and sensor_type is not None:
            if sensor_type == 'ZPL':
                suffix = 'zpls'
            else:
                suffix = sensor_type.lower()
            url = root_url + suffix
        return jsonify({'instrument_information_url': url})
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


#- - - - - - - - - - - - - - - - - - - - - - - -
# Get instrument site link by sensor type.
#- - - - - - - - - - - - - - - - - - - - - - - -
@api.route('/media/get_instrument_site_link/<string:rd>', methods=['GET'])
def media_get_instrument_site_link(rd):
    """ Get instrument site link from reference designator.
    (Used to provided the link for the site display on sensor type page.)

    Sample Requests:
    http://localhost:4000/uframe/media/get_instrument_site_link/CE02SHBP-MJ01C-08-CAMDSB107    # Sprint 10
    http://localhost:4000/uframe/media/get_instrument_site_link/RS03ASHS-PN03B-06-CAMHDA301    # Available
    http://localhost:4000/uframe/media/get_instrument_site_link/CE04OSPS-PC01B-05-ZPLSCB102    # Available
    http://localhost:4000/uframe/media/get_instrument_site_link/CE04OSBP-LJ01C-11-HYDBBA105    # Available

    Sample Requests with response results included.
    http://localhost:4000/uframe/media/get_instrument_site_link/CE02SHBP-MJ01C-08-CAMDSB107
    {
      "instrument_site_url": "http://oceanobservatories.org/site/ce02shbp"
    }
    http://localhost:4000/uframe/media/get_instrument_site_link/RS03ASHS-PN03B-06-CAMHDA301
    {
      "instrument_site_url": "http://oceanobservatories.org/site/rs03ashs"
    }
    http://localhost:4000/uframe/media/get_instrument_site_link/CE04OSPS-PC01B-05-ZPLSCB102
    {
      "instrument_site_url": "http://oceanobservatories.org/site/ce04osps"
    }
    http://localhost:4000/uframe/media/get_instrument_site_link/CE04OSBP-LJ01C-11-HYDBBA105
    {
      "instrument_site_url": "http://oceanobservatories.org/site/ce04osbp"
    }
    """
    try:
        # Get site from reference designator.
        if '-' not in rd:
            message = 'Malformed instrument reference designator provided (%r).' % rd
            raise Exception(message)

        site, remainder = rd.split('-', 1)

        if site and site is not None:
            site = site.lower()
        else:
            message = 'Site is invalid, check reference designator provided: %r' % rd
            raise Exception(message)
        url_root = rds_get_instrument_site_url_root()
        url = url_root + site
        return jsonify({'instrument_site_url': url})
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)

#- - - - - - - - - - - - - - - - - - - - - - - -
# Get instrument rds link by reference designator.
#- - - - - - - - - - - - - - - - - - - - - - - -
@api.route('/media/get_instrument_rds_link/<string:rd>', methods=['GET'])
def media_get_instrument_rds_link(rd):
    """ Get instrument raw data server (rds) link for reference designator.
    (Used to provided the link for the site display on sensor type page.)

    Sample Requests:
    http://localhost:4000/uframe/media/get_instrument_rds_link/CE02SHBP-MJ01C-08-CAMDSB107    # Sprint 10
    http://localhost:4000/uframe/media/get_instrument_rds_link/RS03ASHS-PN03B-06-CAMHDA301    # Available
    http://localhost:4000/uframe/media/get_instrument_rds_link/CE04OSPS-PC01B-05-ZPLSCB102    # Available
    http://localhost:4000/uframe/media/get_instrument_rds_link/CE04OSBP-LJ01C-11-HYDBBA105    # Available

    Sample Requests with response results included.
    http://localhost:4000/uframe/media/get_instrument_rds_link/CE02SHBP-MJ01C-08-CAMDSB107
    {
      "instrument_rds_url": "https://rawdata.oceanobservatories.org/files/CE02SHBP/MJ01C/08-CAMDSB107"
    }
    http://localhost:4000/uframe/media/get_instrument_rds_link/RS03ASHS-PN03B-06-CAMHDA301
    {
      "instrument_rds_url": "https://rawdata.oceanobservatories.org/files/RS03ASHS/PN03B/06-CAMHDA301"
    }
    http://localhost:4000/uframe/media/get_instrument_rds_link/CE04OSPS-PC01B-05-ZPLSCB102
    {
      "instrument_rds_url": "https://rawdata.oceanobservatories.org/files/CE04OSPS/PC01B/05-ZPLSCB102"
    }
    http://localhost:4000/uframe/media/get_instrument_rds_link/CE04OSBP-LJ01C-11-HYDBBA105
    {
      "instrument_rds_url": "https://rawdata.oceanobservatories.org/files/CE04OSBP/LJ01C/11-HYDBBA105"
    }
    """
    try:
        # Quick check reference designator.
        if '-' not in rd:
            message = 'Malformed instrument reference designator provided (%r).' % rd
            raise Exception(message)

        # Check availability of data for reference designator.
        check_data = get_large_format_index_for_rd(rd)
        if not check_data or check_data is None:
            message = 'Data not currently available for instrument \'%s\'. ' % rd
            raise Exception(message)

        # Format and return url.
        site, node, sensor = rd.split('-', 2)
        suffix = '/'.join([site, node, sensor])
        url_root = get_rds_base_url()
        url = '/'.join([url_root, suffix])
        return jsonify({'instrument_rds_url': url})
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


#- - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Data functions (all media types).
#- - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Get first_date from large format data.
@api.route('/media/get_first_date/<string:rd>', methods=['GET'])
def media_get_first_date(rd):
    """ Get string first date from /da/map.
    Request: http://localhost:4000/uframe/media/get_first_date/CE02SHBP-MJ01C-08-CAMDSB107
    Response:
    {
      "first_date": "2009-12-07"
    }
    """
    try:
        data = get_large_format_index_for_rd(rd)
        first_date = _get_date_bound(data, bound='first')
        return jsonify({'first_date': first_date})
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get last_date from large format data.
@api.route('/media/get_last_date/<string:rd>', methods=['GET'])
def media_get_last_date(rd):
    """ Get string first date from /da/map.
    Request: http://localhost:4000/uframe/media/get_last_date/CE02SHBP-MJ01C-08-CAMDSB107
    Response:
    {
      "last_date": "2016-10-03"
    }
    """
    try:
        data = get_large_format_index_for_rd(rd)
        last_date = _get_date_bound(data, bound='last')
        return jsonify({'last_date': last_date})
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get first and last_date from large format data for reference designator..
@api.route('/media/get_data_bounds/<string:rd>', methods=['GET'])
def media_get_data_bounds(rd):
    """ Get string first date and last date from /da/map.
    Request: http://localhost:4000/uframe/media/get_data_bounds/CE02SHBP-MJ01C-08-CAMDSB107
    Response:
    {
      "bounds": {
        "first_date": "2009-12-07",
        "last_date": "2016-10-03"
      }
    }
    """
    try:
        data = get_large_format_index_for_rd(rd)
        first_date = _get_date_bound(data, bound='first')
        last_date = _get_date_bound(data, bound='last')
        result = {'bounds':
                        {'first_date': first_date,
                        'last_date': last_date
                        }
                 }
        return jsonify(result)
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get data availability map (dict of years, months and days) for reference designator.
@api.route('/media/<string:rd>/da/map')
def media_get_da_map_for_rd(rd):
    """ Get all large format file indices for reference designator, year and month.
    Request: http://localhost:4000/uframe/media/CE02SHBP-MJ01C-08-CAMDSB107/da/map
    Response:
    {
      "map": {
        "2009": {
          "12": [
            7
          ]
        },
        "2010": {
          "01": [
            1
          ]
        },
        "2015": {
          "08": [
            18
          ]
        },
        "2016": {
          "01": [
            28
          ],
          "02": [
            2,
            3,
            4,
            5,
            8,
            9,
            10,
            12
          ],
          "05": [
            10,
            11,
            23
          ],
          "06": [
            29
          ],
          "07": [
            26,
            28
          ],
          "08": [
            2,
            8,
            12,
            18
          ],
          "09": [
            12
          ],
          "10": [
            3
          ]
        }
      }
    }

    Request:
        http://localhost:4000/uframe/media/CE02SHBP-MJ01C-07-ZPLSCB101/da/map
    Response:
    {
      "map": {
        "2014": {
          "09": [
            24,
            25,
            26,
            27,
            28,
            29,
            30
          ],
          "10": [
            1,
            2,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
            26,
            27,
            28,
            29,
            30,
            31
          ],
          . . .
          }
          . . .
        }

    Request: http://localhost:4000/uframe/media/RS01SBPS-PC01A-08-HYDBBA103/da/map
    Response:
    {
      "map": {
        "2015": {
          "09": [
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22
          ],
          "10": [
            20,
            21,
            22,
            23
          ],
          "11": [
            30
          ],
          "12": [
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
            16
          ]
        },
        "2016": {
          "01": [
            4,
            5,
            7,
            8,
            9,
            10,
            11,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            23,
            25,
            26,
            28,
            29,
            30,
            31
          ],
          . . .
        }
      . . .
    }
    """
    try:
        # Get large format index data..
        data = get_large_format_index_for_rd(rd)

        # Get reference designator data.
        years = [str(key) for key in data.keys()]

        # Get years in the reference designator data.
        result = {}
        if years and years is not None:
            if years and years is not None:
                for year in years:
                    result[year] = {}
                    months = [str(key) for key in data[year].keys()]
                    for month in months:
                        days = data[year][month]
                        if days:
                            _days = []
                            for day in days:
                                int_day = int(day)
                                _days.append(int_day)
                            _days.sort()
                            result[year][month] = _days
        return jsonify({'map': result}), 200
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get [list of] years of available data for reference designator.
@api.route('/media/<string:rd>/da/years')
def media_get_da_for_rd_years(rd):
    """ Get all large format index file indices for reference designator, year and month.

    Request: http://localhost:4000/uframe/media/CE02SHBP-MJ01C-08-CAMDSB107/da/years
    Response:
    {
      "years": [
        2009,
        2010,
        2015,
        2016
      ]
    }

    Request: http://localhost:4000/uframe/media/CE02SHBP-MJ01C-07-ZPLSCB101/da/years
    Response:
    {
      "years": [
        2014,
        2015,
        2016,
        2017
      ]
    }

    Request:  http://localhost:4000/uframe/media/RS01SBPS-PC01A-08-HYDBBA103/da/years
    Response:
    {
      "years": [
        2015,
        2016,
        2017
      ]
    }
    """
    try:
        # Get large format index data..
        data = get_large_format_index_for_rd(rd)
        # Get reference designator data.
        years = [str(key) for key in data.keys()]
        if years:
            years.sort()
        # Get years in the reference designator data.
        result = []
        if years and years is not None:
            years.sort()
            _years = []
            for year in years:
                int_year = int(year)
                _years.append(int_year)
                _years.sort()
                result = _years
        return jsonify({'years': result}), 200
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get [list of] months of available data or reference designator and year.
@api.route('/media/<string:rd>/da/<string:year>')
def media_get_da_for_rd_year(rd, year):
    """ Get all large format file indices for reference designator, year and month.

    Request: http://localhost:4000/uframe/media/CE02SHBP-MJ01C-08-CAMDSB107/da/2015
    Response:
    {
      "months": [
        8
      ]
    }

    http://localhost:4000/uframe/media/CE02SHBP-MJ01C-07-ZPLSCB101/da/2015
    {
      "months": [
        1,
        2,
        3,
        4,
        8,
        9,
        10,
        11,
        12
      ]
    }

    http://localhost:4000/uframe/media/RS01SBPS-PC01A-08-HYDBBA103/da/2015
    {
      "months": [
        9,
        10,
        11,
        12
      ]
    }
    """
    try:
        _year = validate_year(year)

        # Get large format index data..
        data = get_large_format_index_for_rd(rd)

        # Get reference designator data.
        years = [str(key) for key in data.keys()]

        # Get years in the reference designator data.
        result = []
        if years and years is not None:
            # If year requested has available data, present months.
            if _year in years:
                months = data[_year].keys()
                _months = []
                if months:
                    for m in months:
                        _months.append(int(m))
                _months.sort()
                result = _months
        return jsonify({'months': result}), 200
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get [list of] days of available data for reference designator, year and month.
@api.route('/media/<string:rd>/da/<string:year>/<string:month>')
def media_get_da_for_rd_years_months(rd, year, month):
    """ Get available for reference designator, year and month.

    http://localhost:4000/uframe/media/CE02SHBP-MJ01C-08-CAMDSB107/da/2015/08
    {
      "days": [
        18
      ]
    }

    -- Get days for year and month
    http://localhost:4000/uframe/media/CE02SHBP-MJ01C-07-ZPLSCB101/da/2015/10
    {
      "days": [
        1,
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
        25,
        26,
        27,
        28,
        29,
        30,
        31
      ]
    }
    http://localhost:4000/uframe/media/RS01SBPS-PC01A-08-HYDBBA103/da/2015/10
    http://localhost:4000/uframe/media/RS01SBPS-PC01A-08-HYDBBA103/da/2015/09
    """
    result = None
    try:
        _year, _month = validate_year_month(year, month)
        data = get_large_format_index_for_rd(rd)
        if _year in data:
            if _month in data[_year]:
                days = data[_year][_month]      # days is a list of strings
                # Convert list of str days into list of int days
                if days:
                    _days = []
                    for d in days:
                        _days.append(int(d))
                    _days.sort()
                    result = _days
        return jsonify({'days': result}), 200
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


#===========================================================================
# Development - under construction, review and discussion.
# Get list of available data from raw data server for reference designator.
@api.route('/media/<string:rd>/<string:year>/<string:month>', methods=['GET'])
def get_media_for_rd(rd, year, month):
    """ Get list of all data for reference designator, year, month; return list of dicts descending by date.

    Request: http://localhost:4000/uframe/media/CE02SHBP-MJ01C-08-CAMDSB107/2015/08
    Response:
    {
      "media": [
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": null,
          "date": "2015-08-18",
          "datetime": "20150818T214937.543Z",
          "filename": "CE02SHBP-MJ01C-08-CAMDSB107_20150818T214937,543Z.png",
          "reference_designator": "CE02SHBP-MJ01C-08-CAMDSB107",
          "thumbnail": "ooiservices/cam_images/imageNotFound404.png",
          "url": "https://rawdata.oceanobservatories.org/files/CE02SHBP/MJ01C/08-CAMDSB107/2015/08/18/CE02SHBP-MJ01C-08-CAMDSB107_20150818T214937,543Z.png"
        }
      ]
    }

    General response format:
    {
      "media": [{}, {}, {}, ...]
    }
    where each dict contains:
      {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": "link-to-data-file-on-remote-data-server",
          "date": "2017-01-16",
          "datetime": "20170116T000000.000Z",
          "filename": "some-actual-filename-on-remote-data-server.png",
          "reference_designator": "CE02SHBP-MJ01C-07-ZPLSCB101",
          "thumbnail": "<server_data_folder>/images/imageNotFound404.png",
          "url": "full-url-to-png-image-file-on-remote-data-server"
      }

    Notes:
    1. For sensor ZPL and raw data only, the url value should be null.
    1. For sensor HYD and mseed data only, the url value should be null.

    Request examples:
    1a. http://localhost:4000/uframe/media/CE02SHBP-MJ01C-07-ZPLSCB101/2017/01
    1b. http://localhost:4000/uframe/media/CE04OSPS-PC01B-05-ZPLSCB102/2017/01
    X 1c. http://localhost:4000/uframe/media/CE04OSPS-PC01B-05-ZPLSCB102/-1/-1        (provides current year and month)

    2a. http://localhost:4000/uframe/media/RS01SLBS-LJ01A-09-HYDBBA102/2017/01
    2b. http://localhost:4000/uframe/media/RS01SBPS-PC01A-08-HYDBBA103/2017/01
    2c. http://localhost:4000/uframe/media/RS01SLBS-LJ01A-09-HYDBBA102/-1/-1        (provides current year and month)

    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
    3a. http://localhost:4000/uframe/media/RS03ASHS-PN03B-06-CAMHDA301/2017/01  **  On hold.
    3b. http://localhost:4000/uframe/media/RS03ASHS-PN03B-06-CAMHDA301/-1/-1    **  On hold.


    Sample request/responses:
    1a. (png, raw) http://localhost:4000/uframe/media/CE02SHBP-MJ01C-07-ZPLSCB101/2017/01
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": "https://rawdata.oceanobservatories.org/files/CE02SHBP/MJ01C/07-ZPLSCB101/2017/01/16/CE02SHBP-MJ01C-07-ZPLSCB101_OOI-D20170116-T000000.raw",
          "date": "2017-01-16",
          "datetime": "20170116T000000.000Z",
          "filename": "CE02SHBP-MJ01C-07-ZPLSCB101_OOI-D20170116-T000000.png",
          "reference_designator": "CE02SHBP-MJ01C-07-ZPLSCB101",
          "thumbnail": "<server_data_folder>/images/imageNotFound404.png",
          "url": "https://rawdata.oceanobservatories.org/files/CE02SHBP/MJ01C/07-ZPLSCB101/2017/01/16/CE02SHBP-MJ01C-07-ZPLSCB101_OOI-D20170116-T000000.png"
        },
        . . .
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": "https://rawdata.oceanobservatories.org/files/CE02SHBP/MJ01C/07-ZPLSCB101/2017/01/13/CE02SHBP-MJ01C-07-ZPLSCB101_OOI-D20170113-T000000.raw",
          "date": "2017-01-13",
          "datetime": "20170113T000000.000Z",
          "filename": "CE02SHBP-MJ01C-07-ZPLSCB101_OOI-D20170113-T000000.png",
          "reference_designator": "CE02SHBP-MJ01C-07-ZPLSCB101",
          "thumbnail": "<server_data_folder>/images/CE02SHBP-MJ01C-07-ZPLSCB101_OOI-D20170113-T000000_thumbnail.png",
          "url": "https://rawdata.oceanobservatories.org/files/CE02SHBP/MJ01C/07-ZPLSCB101/2017/01/13/CE02SHBP-MJ01C-07-ZPLSCB101_OOI-D20170113-T000000.png"
        },
        . . .

    2a. (mseed) http://localhost:4000/uframe/media/RS01SLBS-LJ01A-09-HYDBBA102/2017/01
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": "https://rawdata.oceanobservatories.org/files/RS01SLBS/LJ01A/09-HYDBBA102/2017/01/25/OO-HYVM1--YDH-2017-01-25T00:00:00.000000.mseed",
          "date": "2017-01-25",
          "datetime": "20170125T000000.000000Z",
          "filename": "OO-HYVM1--YDH-2017-01-25T00:00:00.000000.mseed",
          "reference_designator": "RS01SLBS-LJ01A-09-HYDBBA102",
          "thumbnail": "<server_data_folder>/images/imageNotFound404.png",
          "url": null
        },
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": "https://rawdata.oceanobservatories.org/files/RS01SLBS/LJ01A/09-HYDBBA102/2017/01/25/OO-HYVM1--YDH-2017-01-25T00:05:00.000000.mseed",
          "date": "2017-01-25",
          "datetime": "20170125T000500.000000Z",
          "filename": "OO-HYVM1--YDH-2017-01-25T00:05:00.000000.mseed",
          "reference_designator": "RS01SLBS-LJ01A-09-HYDBBA102",
          "thumbnail": "<server_data_folder>/images/imageNotFound404.png",
          "url": null
        },
        . . .

    2b. (mseed) http://localhost:4000/uframe/media/RS01SBPS-PC01A-08-HYDBBA103/2017/01
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": "https://rawdata.oceanobservatories.org/files/RS01SBPS/PC01A/08-HYDBBA103/2017/01/25/OO-HYVM2--YDH-2017-01-25T00:00:00.000000.mseed",
          "date": "2017-01-25",
          "datetime": "20170125T000000.000000Z",
          "filename": "OO-HYVM2--YDH-2017-01-25T00:00:00.000000.mseed",
          "reference_designator": "RS01SBPS-PC01A-08-HYDBBA103",
          "thumbnail": "<server_data_folder>/images/imageNotFound404.png",
          "url": null
        },
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": "https://rawdata.oceanobservatories.org/files/RS01SBPS/PC01A/08-HYDBBA103/2017/01/25/OO-HYVM2--YDH-2017-01-25T00:05:00.000000.mseed",
          "date": "2017-01-25",
          "datetime": "20170125T000500.000000Z",
          "filename": "OO-HYVM2--YDH-2017-01-25T00:05:00.000000.mseed",
          "reference_designator": "RS01SBPS-PC01A-08-HYDBBA103",
          "thumbnail": "<server_data_folder>/images/imageNotFound404.png",
          "url": null
        },
        . . .

    (mseed and png) Another example, mseed file and image file but no thumbnail, mseed file and no thumbnail or image
        http://localhost:4000/uframe/media/RS01SBPS-PC01A-08-HYDBBA103/2016/01
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": "https://rawdata.oceanobservatories.org/files/RS01SBPS/PC01A/08-HYDBBA103/2016/01/31/OO-HYVM2--YDH-2016-01-31T01:50:00.000000.mseed",
          "date": "2016-01-31",
          "datetime": "20160131T015000.000000Z",
          "filename": "OO-HYVM2--YDH-2016-01-31T01:50:00.000000.mseed",
          "reference_designator": "RS01SBPS-PC01A-08-HYDBBA103",
          "thumbnail": "<server_data_folder>/images/imageNotFound404.png",
          "url": "https://rawdata.oceanobservatories.org/files/RS01SBPS/PC01A/08-HYDBBA103/2016/01/31/OO-HYVM2--YDH-2016-01-31T01:50:00.000000.png"
        },
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": "https://rawdata.oceanobservatories.org/files/RS01SBPS/PC01A/08-HYDBBA103/2016/01/31/OO-HYVM2--YDH-2016-01-31T01:55:00.000015.mseed",
          "date": "2016-01-31",
          "datetime": "20160131T015500.000015Z",
          "filename": "OO-HYVM2--YDH-2016-01-31T01:55:00.000015.mseed",
          "reference_designator": "RS01SBPS-PC01A-08-HYDBBA103",
          "thumbnail": "<server_data_folder>/images/imageNotFound404.png",
          "url": null
        },
        . . .

    4. CAMHD response output goes here. (On hold.)

    """
    try:
        _year, _month = validate_year_month(year, month)
        data = _get_media_for_rd(rd, year=_year, month=_month)
        return jsonify({'media': data})
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


'''
# Get media for reference designator for a given year.
@api.route('/media/<string:rd>/year/<string:year>')
def media_get_files_for_rd_year(rd, year):
    """ Get all large format file indices for reference designator and year.
    http://localhost:4000/uframe/media/RS01SBPS-PC01A-08-HYDBBA103/da/map

    http://localhost:4000/uframe/media/RS01SBPS-PC01A-08-HYDBBA103/year/2015
    {
      "media": [
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": "https://rawdata.oceanobservatories.org/files/RS01SBPS/PC01A/08-HYDBBA103/2015/09/03/OO-HYVM2--YDH.2015-09-03T23:53:17.272250.mseed",
          "date": "2015-09-03",
          "datetime": "20150903T235317272250Z",
          "filename": "OO-HYVM2--YDH.2015-09-03T23:53:17.272250.mseed",
          "reference_designator": "RS01SBPS-PC01A-08-HYDBBA103",
          "thumbnail": "ooiservices/cam_images/imageNotFound404.png",
          "url": null
        },
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": "https://rawdata.oceanobservatories.org/files/RS01SBPS/PC01A/08-HYDBBA103/2015/09/03/OO-HYVM2--YDH.2015-09-03T23:55:00.000000.mseed",
          "date": "2015-09-03",
          "datetime": "20150903T235500000000Z",
          "filename": "OO-HYVM2--YDH.2015-09-03T23:55:00.000000.mseed",
          "reference_designator": "RS01SBPS-PC01A-08-HYDBBA103",
          "thumbnail": "ooiservices/cam_images/imageNotFound404.png",
          "url": null
        },
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": "https://rawdata.oceanobservatories.org/files/RS01SBPS/PC01A/08-HYDBBA103/2015/09/04/OO-HYVM2--YDH.2015-09-04T00:00:00.000000.mseed",
          "date": "2015-09-04",
          "datetime": "20150904T000000000000Z",
          "filename": "OO-HYVM2--YDH.2015-09-04T00:00:00.000000.mseed",
          "reference_designator": "RS01SBPS-PC01A-08-HYDBBA103",
          "thumbnail": "ooiservices/cam_images/imageNotFound404.png",
          "url": null
        },
        . . .


    """
    #
    # Working here ==========================================================
    #
    # Need to limit the query based on outstanding data items.
    #
    # The following data queries will cripple interface - need a point to break on...
    #
    # http://localhost:4000/uframe/media/RS01SBPS-PC01A-08-HYDBBA103/da/map
    #
    # http://localhost:4000/uframe/media/RS01SBPS-PC01A-08-HYDBBA103/year/2016
    #
    debug = True
    try:
        _year = validate_year(year)

        # Get large format cache
        if debug: print '\n debug -- Entered test_get_media_year: %s for %r' % (rd, _year)
        if debug: print '\n debug -- Get get_large_format_for_rd for rd: %s' % rd
        data = get_large_format_for_rd(rd)
        if _year not in data:
            message = 'Invalid year (%s) for %s data set.' % (str(_year), rd)
            raise Exception(message)

        # Get year data from large format cache.
        data_slice = {}
        data_slice[_year] = {}
        data_slice[_year] = data[_year]

        # Determine sensor type using reference designator.
        #sensor_type = 'CAMDS'
        sensor_type = rds_get_sensor_type(rd)
        if debug: print '\n debug -- Get get_file_list_for_large_format_data for sensor_type: %s' % sensor_type
        result = get_file_list_for_large_format_data(data_slice, rd, sensor_type)

        # for data segment, process for media output.
        media = fetch_media_for_rd(result, rd)
        return jsonify({'media': media}), 200

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)
'''


# Get data for specific date (yyyy-mm-dd).
@api.route('/media/<string:rd>/date/<string:data_date>', methods=['GET'])
def media_get_day(rd, data_date):
    """ Get data slice for date from rd/da/map; process for sensor type identified in rd.

    Request: http://localhost:4000/uframe/media/CE02SHBP-MJ01C-08-CAMDSB107/date/2015-08-18
    {
      "media": [
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": null,
          "date": "2015-08-18",
          "datetime": "20150818T214937.543Z",
          "filename": "CE02SHBP-MJ01C-08-CAMDSB107_20150818T214937,543Z.png",
          "reference_designator": "CE02SHBP-MJ01C-08-CAMDSB107",
          "thumbnail": "ooiservices/cam_images/imageNotFound404.png",
          "url": "https://rawdata.oceanobservatories.org/files/CE02SHBP/MJ01C/08-CAMDSB107/2015/08/18/CE02SHBP-MJ01C-08-CAMDSB107_20150818T214937,543Z.png"
        }
      ]
    }

    Other examples....
    Request: http://localhost:4000/uframe/media/RS01SBPS-PC01A-08-HYDBBA103/date/2016-12-31
    Response:
    {
      "media": [
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": "https://rawdata.oceanobservatories.org/files/RS01SBPS/PC01A/08-HYDBBA103/2016/12/31/OO-HYVM2--YDH-2016-12-31T00:00:00.000016.mseed",
          "date": "2016-12-31",
          "datetime": "20161231T000000.000016Z",
          "filename": "OO-HYVM2--YDH-2016-12-31T00:00:00.000016.mseed",
          "reference_designator": "RS01SBPS-PC01A-08-HYDBBA103",
          "thumbnail": "ooiservices/cam_images/imageNotFound404.png",
          "url": null
        },
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": "https://rawdata.oceanobservatories.org/files/RS01SBPS/PC01A/08-HYDBBA103/2016/12/31/OO-HYVM2--YDH-2016-12-31T00:05:00.000015.mseed",
          "date": "2016-12-31",
          "datetime": "20161231T000500.000015Z",
          "filename": "OO-HYVM2--YDH-2016-12-31T00:05:00.000015.mseed",
          "reference_designator": "RS01SBPS-PC01A-08-HYDBBA103",
          "thumbnail": "ooiservices/cam_images/imageNotFound404.png",
          "url": null
        },
        . . .
      ]
    }
    """
    try:
        # Get large format cache
        data = get_large_format_for_rd(rd)

        # Get date from large format cache.
        data_slice = _get_data_day(data, data_date)

        # Determine sensor type using reference designator.
        sensor_type = rds_get_sensor_type(rd)
        result = get_file_list_for_large_format_data(data_slice, rd, sensor_type)

        # For data segment, process for media output.
        media = fetch_media_for_rd(result, rd)
        return jsonify({'media': media})
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get data slice, provide start and end date.
@api.route('/media/<string:rd>/range/<string:start>/<string:end>', methods=['GET'])
def media_get_data_slice_with_dates(rd, start, end):
    """ Get data slice, provide start and end date, (using start/end values from rd/da/map).
    For reference check the available dates to use for range.
    Request:
        http://localhost:4000/uframe/media/RS01SUM2-MJ01B-05-CAMDSB103/da/map
    Response:
    {
      "map": {
        "2015": {
          "07": [
            31
          ],
          "08": [
            4,
            7,
            21,
            26,
            31
          ],
          "09": [
            9,
            11,
            23
          ],
          "10": [
            6,
            26
          ],
          "11": [
            5,
            20
          ],
          "12": [
            7
          ]
        },
        "2016": {
          "01": [
            5,
            7,
            21
          ],
        . . .

    Request:
        http://localhost:4000/uframe/media/RS01SUM2-MJ01B-05-CAMDSB103/range/2015-12-07/2016-01-05
    Response:
    {
      "media": [
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": null,
          "date": "2015-12-07",
          "datetime": "20151207T215118.854Z",
          "filename": "RS01SUM2-MJ01B-05-CAMDSB103_20151207T215118,854Z.png",
          "reference_designator": "RS01SUM2-MJ01B-05-CAMDSB103",
          "thumbnail": "ooiservices/cam_images/imageNotFound404.png",
          "url": "https://rawdata.oceanobservatories.org/files/RS01SUM2/MJ01B/05-CAMDSB103/2015/12/07/RS01SUM2-MJ01B-05-CAMDSB103_20151207T215118,854Z.png"
        },
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": null,
          "date": "2015-12-07",
          "datetime": "20151207T215119.165Z",
          "filename": "RS01SUM2-MJ01B-05-CAMDSB103_20151207T215119,165Z.png",
          "reference_designator": "RS01SUM2-MJ01B-05-CAMDSB103",
          "thumbnail": "ooiservices/cam_images/imageNotFound404.png",
          "url": "https://rawdata.oceanobservatories.org/files/RS01SUM2/MJ01B/05-CAMDSB103/2015/12/07/RS01SUM2-MJ01B-05-CAMDSB103_20151207T215119,165Z.png"
        },
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": null,
          "date": "2015-12-07",
          "datetime": "20151207T215119.477Z",
          "filename": "RS01SUM2-MJ01B-05-CAMDSB103_20151207T215119,477Z.png",
          "reference_designator": "RS01SUM2-MJ01B-05-CAMDSB103",
          "thumbnail": "ooiservices/cam_images/imageNotFound404.png",
          "url": "https://rawdata.oceanobservatories.org/files/RS01SUM2/MJ01B/05-CAMDSB103/2015/12/07/RS01SUM2-MJ01B-05-CAMDSB103_20151207T215119,477Z.png"
        },
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": null,
          "date": "2015-12-07",
          "datetime": "20151207T220018.909Z",
          "filename": "RS01SUM2-MJ01B-05-CAMDSB103_20151207T220018,909Z.png",
          "reference_designator": "RS01SUM2-MJ01B-05-CAMDSB103",
          "thumbnail": "ooiservices/cam_images/imageNotFound404.png",
          "url": "https://rawdata.oceanobservatories.org/files/RS01SUM2/MJ01B/05-CAMDSB103/2015/12/07/RS01SUM2-MJ01B-05-CAMDSB103_20151207T220018,909Z.png"
        },
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": null,
          "date": "2015-12-07",
          "datetime": "20151207T220019.220Z",
          "filename": "RS01SUM2-MJ01B-05-CAMDSB103_20151207T220019,220Z.png",
          "reference_designator": "RS01SUM2-MJ01B-05-CAMDSB103",
          "thumbnail": "ooiservices/cam_images/imageNotFound404.png",
          "url": "https://rawdata.oceanobservatories.org/files/RS01SUM2/MJ01B/05-CAMDSB103/2015/12/07/RS01SUM2-MJ01B-05-CAMDSB103_20151207T220019,220Z.png"
        },
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": null,
          "date": "2015-12-07",
          "datetime": "20151207T220019.532Z",
          "filename": "RS01SUM2-MJ01B-05-CAMDSB103_20151207T220019,532Z.png",
          "reference_designator": "RS01SUM2-MJ01B-05-CAMDSB103",
          "thumbnail": "ooiservices/cam_images/imageNotFound404.png",
          "url": "https://rawdata.oceanobservatories.org/files/RS01SUM2/MJ01B/05-CAMDSB103/2015/12/07/RS01SUM2-MJ01B-05-CAMDSB103_20151207T220019,532Z.png"
        },
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": null,
          "date": "2015-12-07",
          "datetime": "20151207T220019.843Z",
          "filename": "RS01SUM2-MJ01B-05-CAMDSB103_20151207T220019,843Z.png",
          "reference_designator": "RS01SUM2-MJ01B-05-CAMDSB103",
          "thumbnail": "ooiservices/cam_images/imageNotFound404.png",
          "url": "https://rawdata.oceanobservatories.org/files/RS01SUM2/MJ01B/05-CAMDSB103/2015/12/07/RS01SUM2-MJ01B-05-CAMDSB103_20151207T220019,843Z.png"
        },
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": null,
          "date": "2015-12-07",
          "datetime": "20151207T220020.154Z",
          "filename": "RS01SUM2-MJ01B-05-CAMDSB103_20151207T220020,154Z.png",
          "reference_designator": "RS01SUM2-MJ01B-05-CAMDSB103",
          "thumbnail": "ooiservices/cam_images/imageNotFound404.png",
          "url": "https://rawdata.oceanobservatories.org/files/RS01SUM2/MJ01B/05-CAMDSB103/2015/12/07/RS01SUM2-MJ01B-05-CAMDSB103_20151207T220020,154Z.png"
        },
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": null,
          "date": "2015-12-07",
          "datetime": "20151207T220020.466Z",
          "filename": "RS01SUM2-MJ01B-05-CAMDSB103_20151207T220020,466Z.png",
          "reference_designator": "RS01SUM2-MJ01B-05-CAMDSB103",
          "thumbnail": "ooiservices/cam_images/imageNotFound404.png",
          "url": "https://rawdata.oceanobservatories.org/files/RS01SUM2/MJ01B/05-CAMDSB103/2015/12/07/RS01SUM2-MJ01B-05-CAMDSB103_20151207T220020,466Z.png"
        },
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": null,
          "date": "2015-12-07",
          "datetime": "20151207T220020.777Z",
          "filename": "RS01SUM2-MJ01B-05-CAMDSB103_20151207T220020,777Z.png",
          "reference_designator": "RS01SUM2-MJ01B-05-CAMDSB103",
          "thumbnail": "ooiservices/cam_images/imageNotFound404.png",
          "url": "https://rawdata.oceanobservatories.org/files/RS01SUM2/MJ01B/05-CAMDSB103/2015/12/07/RS01SUM2-MJ01B-05-CAMDSB103_20151207T220020,777Z.png"
        },
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": null,
          "date": "2015-12-07",
          "datetime": "20151207T220021.089Z",
          "filename": "RS01SUM2-MJ01B-05-CAMDSB103_20151207T220021,089Z.png",
          "reference_designator": "RS01SUM2-MJ01B-05-CAMDSB103",
          "thumbnail": "ooiservices/cam_images/imageNotFound404.png",
          "url": "https://rawdata.oceanobservatories.org/files/RS01SUM2/MJ01B/05-CAMDSB103/2015/12/07/RS01SUM2-MJ01B-05-CAMDSB103_20151207T220021,089Z.png"
        },
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": null,
          "date": "2015-12-07",
          "datetime": "20151207T220021.400Z",
          "filename": "RS01SUM2-MJ01B-05-CAMDSB103_20151207T220021,400Z.png",
          "reference_designator": "RS01SUM2-MJ01B-05-CAMDSB103",
          "thumbnail": "ooiservices/cam_images/imageNotFound404.png",
          "url": "https://rawdata.oceanobservatories.org/files/RS01SUM2/MJ01B/05-CAMDSB103/2015/12/07/RS01SUM2-MJ01B-05-CAMDSB103_20151207T220021,400Z.png"
        },
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": null,
          "date": "2015-12-07",
          "datetime": "20151207T220021.712Z",
          "filename": "RS01SUM2-MJ01B-05-CAMDSB103_20151207T220021,712Z.png",
          "reference_designator": "RS01SUM2-MJ01B-05-CAMDSB103",
          "thumbnail": "ooiservices/cam_images/imageNotFound404.png",
          "url": "https://rawdata.oceanobservatories.org/files/RS01SUM2/MJ01B/05-CAMDSB103/2015/12/07/RS01SUM2-MJ01B-05-CAMDSB103_20151207T220021,712Z.png"
        },
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": null,
          "date": "2015-12-07",
          "datetime": "20151207T220022.023Z",
          "filename": "RS01SUM2-MJ01B-05-CAMDSB103_20151207T220022,023Z.png",
          "reference_designator": "RS01SUM2-MJ01B-05-CAMDSB103",
          "thumbnail": "ooiservices/cam_images/imageNotFound404.png",
          "url": "https://rawdata.oceanobservatories.org/files/RS01SUM2/MJ01B/05-CAMDSB103/2015/12/07/RS01SUM2-MJ01B-05-CAMDSB103_20151207T220022,023Z.png"
        },
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": null,
          "date": "2015-12-07",
          "datetime": "20151207T220022.334Z",
          "filename": "RS01SUM2-MJ01B-05-CAMDSB103_20151207T220022,334Z.png",
          "reference_designator": "RS01SUM2-MJ01B-05-CAMDSB103",
          "thumbnail": "ooiservices/cam_images/imageNotFound404.png",
          "url": "https://rawdata.oceanobservatories.org/files/RS01SUM2/MJ01B/05-CAMDSB103/2015/12/07/RS01SUM2-MJ01B-05-CAMDSB103_20151207T220022,334Z.png"
        },
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": null,
          "date": "2015-12-07",
          "datetime": "20151207T223311.078Z",
          "filename": "RS01SUM2-MJ01B-05-CAMDSB103_20151207T223311,078Z.png",
          "reference_designator": "RS01SUM2-MJ01B-05-CAMDSB103",
          "thumbnail": "ooiservices/cam_images/imageNotFound404.png",
          "url": "https://rawdata.oceanobservatories.org/files/RS01SUM2/MJ01B/05-CAMDSB103/2015/12/07/RS01SUM2-MJ01B-05-CAMDSB103_20151207T223311,078Z.png"
        },
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": null,
          "date": "2015-12-07",
          "datetime": "20151207T223311.389Z",
          "filename": "RS01SUM2-MJ01B-05-CAMDSB103_20151207T223311,389Z.png",
          "reference_designator": "RS01SUM2-MJ01B-05-CAMDSB103",
          "thumbnail": "ooiservices/cam_images/imageNotFound404.png",
          "url": "https://rawdata.oceanobservatories.org/files/RS01SUM2/MJ01B/05-CAMDSB103/2015/12/07/RS01SUM2-MJ01B-05-CAMDSB103_20151207T223311,389Z.png"
        },
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": null,
          "date": "2015-12-07",
          "datetime": "20151207T223311.700Z",
          "filename": "RS01SUM2-MJ01B-05-CAMDSB103_20151207T223311,700Z.png",
          "reference_designator": "RS01SUM2-MJ01B-05-CAMDSB103",
          "thumbnail": "ooiservices/cam_images/imageNotFound404.png",
          "url": "https://rawdata.oceanobservatories.org/files/RS01SUM2/MJ01B/05-CAMDSB103/2015/12/07/RS01SUM2-MJ01B-05-CAMDSB103_20151207T223311,700Z.png"
        },
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": null,
          "date": "2015-12-07",
          "datetime": "20151207T223312.012Z",
          "filename": "RS01SUM2-MJ01B-05-CAMDSB103_20151207T223312,012Z.png",
          "reference_designator": "RS01SUM2-MJ01B-05-CAMDSB103",
          "thumbnail": "ooiservices/cam_images/imageNotFound404.png",
          "url": "https://rawdata.oceanobservatories.org/files/RS01SUM2/MJ01B/05-CAMDSB103/2015/12/07/RS01SUM2-MJ01B-05-CAMDSB103_20151207T223312,012Z.png"
        },
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": null,
          "date": "2015-12-07",
          "datetime": "20151207T223312.323Z",
          "filename": "RS01SUM2-MJ01B-05-CAMDSB103_20151207T223312,323Z.png",
          "reference_designator": "RS01SUM2-MJ01B-05-CAMDSB103",
          "thumbnail": "ooiservices/cam_images/imageNotFound404.png",
          "url": "https://rawdata.oceanobservatories.org/files/RS01SUM2/MJ01B/05-CAMDSB103/2015/12/07/RS01SUM2-MJ01B-05-CAMDSB103_20151207T223312,323Z.png"
        },
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": null,
          "date": "2015-12-07",
          "datetime": "20151207T223312.635Z",
          "filename": "RS01SUM2-MJ01B-05-CAMDSB103_20151207T223312,635Z.png",
          "reference_designator": "RS01SUM2-MJ01B-05-CAMDSB103",
          "thumbnail": "ooiservices/cam_images/imageNotFound404.png",
          "url": "https://rawdata.oceanobservatories.org/files/RS01SUM2/MJ01B/05-CAMDSB103/2015/12/07/RS01SUM2-MJ01B-05-CAMDSB103_20151207T223312,635Z.png"
        },
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": null,
          "date": "2015-12-07",
          "datetime": "20151207T223312.946Z",
          "filename": "RS01SUM2-MJ01B-05-CAMDSB103_20151207T223312,946Z.png",
          "reference_designator": "RS01SUM2-MJ01B-05-CAMDSB103",
          "thumbnail": "ooiservices/cam_images/imageNotFound404.png",
          "url": "https://rawdata.oceanobservatories.org/files/RS01SUM2/MJ01B/05-CAMDSB103/2015/12/07/RS01SUM2-MJ01B-05-CAMDSB103_20151207T223312,946Z.png"
        },
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": null,
          "date": "2015-12-07",
          "datetime": "20151207T223313.258Z",
          "filename": "RS01SUM2-MJ01B-05-CAMDSB103_20151207T223313,258Z.png",
          "reference_designator": "RS01SUM2-MJ01B-05-CAMDSB103",
          "thumbnail": "ooiservices/cam_images/imageNotFound404.png",
          "url": "https://rawdata.oceanobservatories.org/files/RS01SUM2/MJ01B/05-CAMDSB103/2015/12/07/RS01SUM2-MJ01B-05-CAMDSB103_20151207T223313,258Z.png"
        },
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": null,
          "date": "2015-12-07",
          "datetime": "20151207T223313.569Z",
          "filename": "RS01SUM2-MJ01B-05-CAMDSB103_20151207T223313,569Z.png",
          "reference_designator": "RS01SUM2-MJ01B-05-CAMDSB103",
          "thumbnail": "ooiservices/cam_images/imageNotFound404.png",
          "url": "https://rawdata.oceanobservatories.org/files/RS01SUM2/MJ01B/05-CAMDSB103/2015/12/07/RS01SUM2-MJ01B-05-CAMDSB103_20151207T223313,569Z.png"
        },
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": null,
          "date": "2016-01-05",
          "datetime": "20160105T012025.501Z",
          "filename": "RS01SUM2-MJ01B-05-CAMDSB103_20160105T012025,501Z.png",
          "reference_designator": "RS01SUM2-MJ01B-05-CAMDSB103",
          "thumbnail": "ooiservices/cam_images/imageNotFound404.png",
          "url": "https://rawdata.oceanobservatories.org/files/RS01SUM2/MJ01B/05-CAMDSB103/2016/01/05/RS01SUM2-MJ01B-05-CAMDSB103_20160105T012025,501Z.png"
        },
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": null,
          "date": "2016-01-05",
          "datetime": "20160105T012025.812Z",
          "filename": "RS01SUM2-MJ01B-05-CAMDSB103_20160105T012025,812Z.png",
          "reference_designator": "RS01SUM2-MJ01B-05-CAMDSB103",
          "thumbnail": "ooiservices/cam_images/imageNotFound404.png",
          "url": "https://rawdata.oceanobservatories.org/files/RS01SUM2/MJ01B/05-CAMDSB103/2016/01/05/RS01SUM2-MJ01B-05-CAMDSB103_20160105T012025,812Z.png"
        },
        {
          "baseUrl": "/api/uframe/get_cam_image/",
          "data_link": null,
          "date": "2016-01-05",
          "datetime": "20160105T012026.124Z",
          "filename": "RS01SUM2-MJ01B-05-CAMDSB103_20160105T012026,124Z.png",
          "reference_designator": "RS01SUM2-MJ01B-05-CAMDSB103",
          "thumbnail": "ooiservices/cam_images/imageNotFound404.png",
          "url": "https://rawdata.oceanobservatories.org/files/RS01SUM2/MJ01B/05-CAMDSB103/2016/01/05/RS01SUM2-MJ01B-05-CAMDSB103_20160105T012026,124Z.png"
        }
      ]
    }
    """
    try:
        # Validate start and end format (yyyy-mm-dd, bwe: '2015-12-07', '2016-01-05')
        data = get_large_format_for_rd(rd)
        if not data or data is None:
            message = 'Data is not defined (empty or null), unable to fulfill get_data_slice request.'
            return bad_request(message)
        data_slice = get_range_data(data, start, end)

        # Determine sensor type using reference designator.
        sensor_type = rds_get_sensor_type(rd)
        result = get_file_list_for_large_format_data(data_slice, rd, sensor_type)

        # for data segment, process for media output.
        media = fetch_media_for_rd(result, rd)
        return jsonify({'media': media})
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)