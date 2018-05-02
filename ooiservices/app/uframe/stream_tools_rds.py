#!/usr/bin/env python

"""
Support for Raw Data Server integration.
"""
__author__ = 'Edna Donoughe'

from ooiservices.app.uframe.vocab import get_vocab_name_collection
from ooiservices.app.uframe.config import (get_rds_base_url)
from ooiservices.app.uframe.toc_tools import get_toc_reference_designators
from ooiservices.app.uframe.stream_tools_iris import get_iris_rds
from ooiservices.app.uframe.image_tools import (get_index_rds, get_rds_index)
from copy import deepcopy


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Raw Data Server common enumerations, data and functions.
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# List of reference designators providing data on the raw data server.
def get_rds_rds():
    """ Get a list of all reference designators which have a raw data server association.

    (15 reference designators)
    [
    "CE02SHBP-LJ01D-11-HYDBBA106",          ['2015', '2016', 2017]
    "CE02SHBP-MJ01C-07-ZPLSCB101",         *['2014', '2015', '2016', '2017']
    "CE02SHBP-MJ01C-08-CAMDSB107",         *['2009', '2010', '2015', '2016']
    "CE04OSBP-LJ01C-11-HYDBBA105",          ['2015', '2016', 2017]
    "CE04OSBP-LV01C-06-CAMDSB106",         *['2014', '2015', '2016', '2017']
    "CE04OSPS-PC01B-05-ZPLSCB102",         *['2015', '2016', '2017']
    "RS01SBPS-PC01A-07-CAMDSC102",         *['2009', '2010', '2016', '2017']
    "RS01SBPS-PC01A-08-HYDBBA103",         *['2015', '2016', '2017']
    "RS01SLBS-LJ01A-09-HYDBBA102",         *['2015', '2016', '2017']
    "RS01SUM2-MJ01B-05-CAMDSB103",         *['2015', '2016', '2017']
    "RS03ASHS-PN03B-06-CAMHDA301",          ['2015', '2016', '2017']
    "RS03AXBS-LJ03A-09-HYDBBA302",          ['2015', '2016', '2017']
    "RS03AXPS-PC03A-07-CAMDSC302",          ['2009', '2010', '2015', '2016']
    "RS03AXPS-PC03A-08-HYDBBA303",          ['2015', '2016', '2017']
    "RS03INT1-MJ03C-05-CAMDSB303"          *['2009', '2010', '2015', '2016']
    ]
    """
    rds = get_index_rds()
    return rds

def get_rds_suffix(rd):
    try:
        a, b, c = rd.split('-', 2)
        suffix = '/'.join([a, b, c])
        return suffix
    except Exception:
        return None


def get_rds_link(rd):
    from ooiservices.app.uframe.image_tools import get_sensor_type_from_rd, get_rds_nav_urls_cache_by_sensor_type
    from ooiservices.app.uframe.common_tools import rds_get_nonstandard_sensor_types
    debug = False
    try:
        if debug: print '\n debug -- Entered get_rds_link: ', rd
        base_url = get_rds_base_url()
        link = base_url
        suffix = get_rds_suffix(rd)

        sensors_no_ports = rds_get_nonstandard_sensor_types()
        sensor_type = get_sensor_type_from_rd(rd)
        if debug: print '\t debug -- sensor_type: ', sensor_type

        # Define the navigation link.
        if sensor_type not in sensors_no_ports:
            link = '/'.join([link, suffix])
        else:
            link = None
            if debug: print '\n debug -- Processing special rds external link for sensor type: ', sensor_type
            sensor_url_cache = get_rds_nav_urls_cache_by_sensor_type(sensor_type)
            if sensor_url_cache is None:
                link = None
            else:
                if debug: print '\n debug -- looking for %s in sensor_url_cache' % rd
                if rd in sensor_url_cache:
                    link = sensor_url_cache[rd]
                    if debug: print '\n debug -- Found link from cache!!!! ', link

        return link
    except Exception as err:
        message = str(err)
        raise Exception(message)


def get_rds_data(rd):
    """ Get available Raw Data Server specific data.
    """
    from ooiservices.app.uframe.image_tools import get_sensor_type_from_rd, get_rds_nav_urls_cache_by_sensor_type
    from ooiservices.app.uframe.common_tools import rds_get_nonstandard_sensor_types
    debug = False
    try:
        if rd not in get_rds_rds():
            return None

        suffix = get_rds_suffix(rd)
        link = get_rds_link(rd)
        result = {'dc': False,
                'iris': False,
                'end': '2599-12-31T00:00:00.000Z',
                'start': '2014-08-01T00:00:00.000Z',
                'rds_link': link,
                'suffix': suffix
                }
        return result
    except Exception as err:
        message = str(err)
        raise Exception(message)


def build_rds_streams():
    """ Create stream dictionary for a raw data server reference designator.
    Use deployment information, if available, for latitude, longitude, depth, water depth,
    [
    'CE02SHBP-MJ01C-07-ZPLSCB101',
    'CE02SHBP-MJ01C-08-CAMDSB107',
    'CE04OSBP-LV01C-06-CAMDSB106',
    'CE04OSPS-PC01B-05-ZPLSCB102',
    'RS01SBPS-PC01A-07-CAMDSC102',
    'RS01SBPS-PC01A-08-HYDBBA103',
    'RS01SLBS-LJ01A-09-HYDBBA102',
    'RS01SUM2-MJ01B-05-CAMDSB103',
    'RS03AXPS-PC03A-07-CAMDSC302',
    'RS03INT1-MJ03C-05-CAMDSB303',
    ]
    Sample dictionary (21):
            {
              "array_name": "Coastal Endurance",
              "assembly_name": "Medium-Power JBox (MJ01C)",
              "depth": None,
              "display_name": "Bio-acoustic Sonar (Coastal)",
              "end": "2599-12-31T00:00:00.000Z",
              "latitude": None,
              "long_display_name": "Coastal Endurance Oregon Shelf Cabled Benthic Experiment Package - Medium-Power JBox (MJ01C) - Bio-acoustic Sonar (Coastal)",
              "longitude": None,
              "platform_name": "Oregon Shelf Cabled Benthic Experiment Package",
              "reference_designator": "CE02SHBP-MJ01C-07-ZPLSCB101",
              "site_name": "Oregon Shelf Cabled Benthic Experiment Package",
              "start": "2014-08-01T00:00:00.000Z",
              "stream": None,
              "stream_dataset": "Science",
              "stream_display_name": None,
              "stream_method": None,
              "stream_name": None,
              "stream_type": None,
              "water_depth": None,
              "rds_enabled": True,
              "rds_link": "https://rawdata.oceanobservatories.org/files/CE02SHBP/MJ01C/07-ZPLSCB101"
            }
    """
    from ooiservices.app.uframe.status_tools import get_rd_digests_dict
    debug = False
    streams = []
    try:
        if debug: print '\n debug -- Entered build_rds_streams......'
        # Get available Raw Data Server reference designators.
        rds_rds = get_rds_rds()

        # Get rd_digest dictionary.
        rd_digests_dict = get_rd_digests_dict()

        # Get known reference designators in data catalog.
        toc_rds = get_toc_reference_designators()

        # Get raw data server index for rds
        large_format_inx = get_rds_index()

        # Build stream dictionary for each reference designator.
        for rd in rds_rds:

            # Get raw data server information for stream processing.
            data = get_rds_data(rd)
            if data is None:
                continue

            # Create stream dictionary for reference designator.
            stream = {}

            # If an entry exists in data catalog for reference designator, it is processed elsewhere.
            if rd in get_iris_rds():
                stream['iris'] = True
            if rd in toc_rds:
                stream['dc'] = True

            # Get deployment information from asset management.
            latitude = None
            longitude = None
            depth = None
            water_depth = None
            try:
                if rd in rd_digests_dict:
                    if rd_digests_dict[rd] and rd_digests_dict[rd] is not None:
                        digest = deepcopy(rd_digests_dict[rd])
                        if digest and digest is not None:
                            depth, latitude, longitude, water_depth = get_stream_digest_data(digest)
            except Exception:
                pass

            # Set stream value with data available from deployment, otherwise None.
            stream['depth'] = depth
            stream['latitude'] = latitude
            stream['longitude'] = longitude
            stream['water_depth'] = water_depth

            # Populate Raw Data Server data.
            if data['rds_link'] is not None:
                stream['rds_enabled'] = True
                stream['rds_link'] = data['rds_link']
            else:
                stream['rds_enabled'] = False

            # Get start and end dates from raw data server index.
            start = None
            end = None
            if large_format_inx and large_format_inx is not None and 'error' not in large_format_inx:
                if rd in large_format_inx:
                    inx_data = large_format_inx[rd]
                    start, end = get_timespan(inx_data)
            stream['start'] = start
            stream['end'] = end

            # Get vocabulary items.
            array, subsite, platform, sensor, long_display_name = get_vocab_name_collection(rd)
            stream['array_name'] = array
            stream['display_name'] = sensor
            stream['assembly_name'] = platform
            stream['site_name'] = subsite
            stream['platform_name'] = subsite
            stream['long_display_name'] = long_display_name

            # General items.
            stream['reference_designator'] = rd
            stream['stream'] = None
            stream['stream_dataset'] = ''
            stream['stream_display_name'] = None
            stream['stream_method'] = None
            stream['stream_name'] = None
            stream['stream_type'] = None
            streams.append(stream)

        return streams
    except Exception as err:
        message = str(err)
        raise Exception(message)


def get_stream_digest_data(digest):
    """ Process deployment digest for stream.
    """
    try:
        # Process deployment information for stream.
        latitude = None
        longitude = None
        depth = None
        water_depth = None
        if digest and digest is not None:
            latitude = digest['latitude']
            longitude = digest['longitude']
            depth = digest['depth']
            water_depth = digest['waterDepth']
            if latitude is not None:
                latitude = round(latitude, 5)
            if longitude is not None:
                longitude = round(longitude, 5)
            if depth is not None:
                depth = round(depth, 5)
            if water_depth is not None:
                water_depth = round(water_depth, 5)
        return depth, latitude, longitude, water_depth
    except Exception as err:
        message = str(err)
        raise Exception(message)



def get_timespan(data):
    """ Get latest start and end times for a reference designator in the index rds data.
    Returns dictionary with start and end values.
    Sample request: http://localhost:4000/uframe/dev/get_rd_start_end/CE02SHBP-MJ01C-07-ZPLSCB101
    Sample response:
      {
        "end": "2017-01-29T00:00:00.000Z",
        "start": "2014-09-24T00:00:00.000Z"
      }

    If reference designator is not found None is returned for start and end.
    start and end datetime format: '2014-08-01T00:00:00.000Z'
    For 'Thh:mm:ss.sssZ' use actual datetime from actual file on server. (suffix for now)
    """
    T_suffix = 'T00:00:00.000Z'
    try:
        # Get the start and end year.
        years = [str(key) for key in data.keys()]
        if not years:
            return None, None
        years.sort()
        if len(years) > 1:
            start_year = years[0]
            end_year = years[-1]
        else:
            start_year = years[0]
            end_year = years[0]

        #- - - - - - - - - - - - - - - - - - - - - - - - -
        # Get first datetime entry in start_year.
        #- - - - - - - - - - - - - - - - - - - - - - - - -
        months = [str(key) for key in data[start_year].keys()]
        if not months:
            return None, None
        months.sort()
        month = months[0]
        days = data[start_year][month]
        if not days:
            return None, None
        days.sort()
        day = days[0]
        start = '-'.join([start_year, month, day]) + T_suffix

        #- - - - - - - - - - - - - - - - - - - - - - - - -
        # Get last datetime entry in end_year.
        #- - - - - - - - - - - - - - - - - - - - - - - - -
        months = [str(key) for key in data[end_year].keys()]
        if not months:
            return None, None
        months.sort(reverse=True)
        month = months[0]
        days = data[end_year][month]
        if not days:
            return None, None
        days.sort(reverse=True)
        day = days[0]
        end = '-'.join([end_year, month, day]) + T_suffix
        return start, end
    except Exception as err:
        message = str(err)
        raise Exception(message)
