#!/usr/bin/env python

"""
Support for IRIS integration.
"""
__author__ = 'Edna Donoughe'

from flask import current_app
from ooiservices.app.uframe.vocab import get_vocab_name_collection
from ooiservices.app.uframe.config import get_iris_base_url
import datetime as dt


def get_iris_rds():
    """ Get a list of all IRIS related reference designators. (no IRIS web service.)
    """
    result = [
            'RS03ASHS-MJ03B-06-OBSSPA301',
            'RS03ASHS-MJ03B-05-OBSSPA302',
            # 'RS03AXBS-MJ03A-05-HYDLFA301',
            'RS03AXBS-MJ03A-05-OBSBBA303',
            'RS03CCAL-MJ03F-05-BOTPTA301',
            # 'RS03CCAL-MJ03F-06-HYDLFA305',
            'RS03CCAL-MJ03F-06-OBSBBA301',
            'RS03ECAL-MJ03E-05-OBSSPA303',
            'RS03ECAL-MJ03E-06-BOTPTA302',
            # 'RS03ECAL-MJ03E-09-HYDLFA304',
            'RS03ECAL-MJ03E-09-OBSBBA302',
            'RS03ECAL-MJ03E-08-OBSSPA304',
            'RS03INT2-MJ03D-06-BOTPTA303',
            'RS03INT2-MJ03D-05-OBSSPA305',
            'RS01SUM1-LJ01B-06-OBSSPA103',
            'RS01SUM1-LJ01B-07-OBSSPA102',
            'RS01SUM1-LJ01B-08-OBSSPA101',
            # 'RS01SUM1-LJ01B-05-HYDLFA104',
            'RS01SUM1-LJ01B-05-OBSBBA101',
            # 'RS01SLBS-MJ01A-05-HYDLFA101',
            'RS01SLBS-MJ01A-05-OBSBBA102'
            ]
    return result

def get_iris_station(rd):
    """ Get the station for a reference designator, return station value or None.
    (No IRIS web service.)
    """
    try:
        if rd not in get_iris_rds():
            return None

        if rd == 'RS03ASHS-MJ03B-06-OBSSPA301':
            result = 'AXAS1'
        elif rd == 'RS03ASHS-MJ03B-05-OBSSPA302':
            result = 'AXAS2'
        elif rd == 'RS03AXBS-MJ03A-05-HYDLFA301':
            result = 'AXBA1'
        elif rd == 'RS03AXBS-MJ03A-05-OBSBBA303':
            result = 'AXBA1'
        elif rd == 'RS03CCAL-MJ03F-05-BOTPTA301':
            result = 'AXCC1'
        elif rd == 'RS03CCAL-MJ03F-06-HYDLFA305':
            result = 'AXCC1'
        elif rd == 'RS03CCAL-MJ03F-06-OBSBBA301':
            result = 'AXCC1'
        elif rd == 'RS03ECAL-MJ03E-05-OBSSPA303':
            result = 'AXEC1'
        elif rd == 'RS03ECAL-MJ03E-06-BOTPTA302':
            result = 'AXEC2'
        elif rd == 'RS03ECAL-MJ03E-09-HYDLFA304':
            result = 'AXEC2'
        elif rd == 'RS03ECAL-MJ03E-09-OBSBBA302':
            result = 'AXEC2'
        elif rd == 'RS03ECAL-MJ03E-08-OBSSPA304':
            result = 'AXEC3'
        elif rd == 'RS03INT2-MJ03D-06-BOTPTA303':
            result = 'AXID1'
        elif rd == 'RS03INT2-MJ03D-05-OBSSPA305':
            result = 'AXID1'
        elif rd == 'RS01SUM1-LJ01B-06-OBSSPA103':
            result = 'HYS13'
        elif rd == 'RS01SUM1-LJ01B-07-OBSSPA102':
            result = 'HYS12'
        elif rd == 'RS01SUM1-LJ01B-08-OBSSPA101':
            result = 'HYS11'
        elif rd == 'RS01SUM1-LJ01B-05-HYDLFA104':
            result = 'HYS14'
        elif rd == 'RS01SUM1-LJ01B-05-OBSBBA101':
            result = 'HYS14'
        elif rd == 'RS01SLBS-MJ01A-05-HYDLFA101':
            result = 'HYSB1'
        elif rd == 'RS01SLBS-MJ01A-05-OBSBBA102':
            result = 'HYSB1'
        else:
            message = 'Reference designator (\'%s\') in IRIS list but station not defined.'
            raise Exception(message)
        return result
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


def get_iris_data(rd):
    """ Get IRIS specific data (originates from metadata aggregator for station)
    (No IRIS web service.)
    """
    result = None
    try:
        if rd not in get_iris_rds():
            return None
        station = get_iris_station(rd)
        if station is None:
            return None
        base_url = get_iris_base_url()
        iris_link = '/'.join([base_url, station])
        if rd == 'RS03ASHS-MJ03B-06-OBSSPA301':
            # station: 'AXAS1'
            result = {'dc': False,
                    'latitude': 45.933560,
                    'longitude': -129.999200,
                    'depth': 1529.0,
                    'start': '2014-08-01T00:00:00.000Z'
                     }
        elif rd == 'RS03ASHS-MJ03B-05-OBSSPA302':
            # station: 'AXAS2'
            result = {'dc': False,
                    'latitude': 45.933770,
                    'longitude': -130.014100,
                    'depth': 1544.4,
                    'start': '2014-08-01T00:00:00.000Z'
                     }

        elif rd == 'RS03AXBS-MJ03A-05-HYDLFA301':
            # station: 'AXBA1'
            result = {'dc': False,
                    'latitude': 45.820180,
                    'longitude': -129.736700,
                    'depth': 2607.2,
                    'start': '2014-08-01T00:00:00.000Z'
                     }
        elif rd == 'RS03AXBS-MJ03A-05-OBSBBA303':
            # station:  'AXBA1'
            result = {'dc': False,
                    'latitude': 45.820180,
                    'longitude': -129.736700,
                    'depth': 2607.2,
                    'start': '2014-08-01T00:00:00.000Z'
                     }
        elif rd == 'RS03CCAL-MJ03F-05-BOTPTA301':
            # station:  'AXCC1'
            result = {'dc': True,
                    'latitude': 45.954680,
                    'longitude': -130.008900,
                    'depth': 1528,
                    'start': '2014-08-01T00:00:00.000Z'
                     }
        elif rd == 'RS03CCAL-MJ03F-06-HYDLFA305':
            # station:  'AXCC1'
            result = {'dc': False,
                    'latitude': 45.954680,
                    'longitude': -130.008900,
                    'depth': 1528,
                    'start': '2014-08-01T00:00:00.000Z'
                     }
        elif rd == 'RS03CCAL-MJ03F-06-OBSBBA301':
            # station:  'AXCC1'
            result = {'dc': False,
                    'latitude': 45.954680,
                    'longitude': -130.008900,
                    'depth': 1528,
                    'start': '2014-08-01T00:00:00.000Z'
                     }
        elif rd == 'RS03ECAL-MJ03E-05-OBSSPA303':
            # station: 'AXEC1'
            result = {'dc': False,
                    'latitude': 45.949580,
                    'longitude': -129.979700,
                    'depth': 1512,
                    'start': '2014-08-01T00:00:00.000Z'
                     }
        elif rd == 'RS03ECAL-MJ03E-06-BOTPTA302':
            # station:  'AXEC2'
            result = {'dc': True,
                    'latitude': 45.939670,
                    'longitude': -129.973800,
                    'depth': 1519,
                    'start': '2014-08-01T00:00:00.000Z'
                     }
        elif rd == 'RS03ECAL-MJ03E-09-HYDLFA304':
            # station:  'AXEC2'
            result = {'dc': False,
                    'latitude': 45.939670,
                    'longitude': -129.973800,
                    'depth': 1519,
                    'start': '2014-08-01T00:00:00.000Z'
                     }
        elif rd == 'RS03ECAL-MJ03E-09-OBSBBA302':
            # station:  'AXEC2'
            result = {'dc': False,
                    'latitude': 45.939670,
                    'longitude': -129.973800,
                    'depth': 1519,
                    'end': '2599-12-31T00:00:00.000Z',
                    'start': '2014-08-01T00:00:00.000Z'
                     }
        elif rd == 'RS03ECAL-MJ03E-08-OBSSPA304':
            # station:  'AXEC3'
            result = {'dc': False,
                    'latitude': 45.936070,
                    'longitude': -129.978500,
                    'depth': 1516,
                    'start': '2014-08-01T00:00:00.000Z'
                     }
        elif rd == 'RS03INT2-MJ03D-06-BOTPTA303':
            # station:  'AXID1'
            result = {'dc': True,
                    'latitude': 45.925730,
                    'longitude': -129.978000,
                    'depth': 1527.5,
                    'start': '2014-08-01T00:00:00.000Z'
                     }
        elif rd == 'RS03INT2-MJ03D-05-OBSSPA305':
            # station:  'AXID1'
            result = {'dc': False,
                    'latitude': 45.925730,
                    'longitude': -129.978000,
                    'depth': 1527.5,
                    'start': '2014-08-01T00:00:00.000Z'
                    }
        elif rd == 'RS01SUM1-LJ01B-06-OBSSPA103':
            # station:  'HYS11'
            result = {'dc': False,
                    'latitude': 44.573030,
                    'longitude': -125.152500,
                    'depth': 817.5,
                    'start': '2014-08-01T00:00:00.000Z'
                    }
        elif rd == 'RS01SUM1-LJ01B-07-OBSSPA102':
            # station: 'HYS12'
            result = {'dc': False,
                    'latitude': 44.573200,
                    'longitude': -125.143900,
                    'depth': 788,
                    'start': '2014-08-01T00:00:00.000Z'
                     }
        elif rd == 'RS01SUM1-LJ01B-08-OBSSPA101':
            # station:  'HYS13'
            result = {'dc': False,
                    'latitude': 44.567400,
                    'longitude': -125.144200,
                    'depth': 789,
                    'start': '2014-08-01T00:00:00.000Z'
                     }
        elif rd == 'RS01SUM1-LJ01B-05-HYDLFA104':
            # station:  'HYS14'
            result = {'dc': False,
                    'latitude': 44.569120,
                    'longitude': -125.147900,
                    'depth': 784.7,
                    'start': '2014-08-01T00:00:00.000Z'
                     }
        elif rd == 'RS01SUM1-LJ01B-05-OBSBBA101':
            # station:  'HYS14'
            result = {'dc': False,
                    'latitude': 44.569120,
                    'longitude': -125.147900,
                    'depth': 784.7,
                    'start': '2014-08-01T00:00:00.000Z'
                     }
        elif rd == 'RS01SLBS-MJ01A-05-HYDLFA101':
            # station:  'HYSB1'
            result = {'dc': False,
                    'latitude': 44.509780,
                    'longitude': -125.405300,
                    'depth': 2920.5,
                    'start': '2014-08-01T00:00:00.000Z'}
        elif rd == 'RS01SLBS-MJ01A-05-OBSBBA102':
            # station:  'HYSB1'
            result = {'dc': False,
                    'latitude': 44.509780,
                    'longitude': -125.405300,
                    'depth': 2920.5,
                    'start': '2014-08-01T00:00:00.000Z'
                     }
        else:
            print '\n-- The reference designator (\'%s\') does not have IRIS characteristics defined.'

        if result:
            if result['depth'] is not None:
                round(result['depth'], 5)
            if result['latitude'] is not None:
                round(result['latitude'], 5)
            if result['longitude'] is not None:
                round(result['longitude'], 5)
            if result['longitude'] is not None:
                round(result['longitude'], 5)
            result['end'] = '2599-12-31T00:00:00.000Z'
            result['rds'] = False
            result['iris_link'] = iris_link
            result['station'] = station
        return result
    except Exception as err:
        message = str(err)
        raise Exception(message)


def build_iris_streams():
    """ Create stream dictionary for an IRIS reference designator.
    """
    from ooiservices.app.uframe.status_tools import get_rd_digests_dict
    debug = False
    iris_streams = []
    try:
        # Calculate approximate end date (current date at 00:00:00)
        end_time = dt.datetime.strftime(dt.datetime.now(), '%Y-%m-%dT00:00:00.000Z')

        # Get iris reference designators.
        iris_rds = get_iris_rds()
        for rd in iris_rds:

            # Get iris_data
            if debug: print '\n Get data for IRIS rd: ', rd
            iris_data = get_iris_data(rd)

            # Update the static IRIS end time.
            iris_data['end'] = end_time
            if iris_data is None:
                continue
            # If an entry exists in data catalog for reference designator, it is processed elsewhere.
            if iris_data['dc'] == True:
                continue

            # Populate iris_stream.
            iris_stream = {}

            #Populate IRIS data; round to 5 decimal places - note this modifies IRIS data.
            iris_stream['iris_enabled'] = True
            iris_stream['iris_link'] = iris_data['iris_link']
            iris_stream['depth'] = iris_data['depth']
            iris_stream['latitude'] = iris_data['latitude']
            iris_stream['longitude'] = iris_data['longitude']
            iris_stream['start'] = iris_data['start']
            iris_stream['end'] = iris_data['end']

            # Get vocabulary items for response.
            if debug: print '\n Get vocabulary for IRIS rd: ', rd
            array, subsite, platform, sensor, long_display_name = get_vocab_name_collection(rd)
            iris_stream['array_name'] = array
            iris_stream['display_name'] = sensor
            iris_stream['assembly_name'] = platform
            iris_stream['site_name'] = subsite
            iris_stream['platform_name'] = subsite
            iris_stream['long_display_name'] = long_display_name

            # Get deployment related information, if available.
            # Only using 'water_depth' from deployment for IRIS at this time.
            # Really should consider adding deployment number for development/review.
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - -
            # Use deployment information from asset management (water_depth only for now)
            #latitude = None
            #longitude = None
            #depth = None
            water_depth = None
            try:
                rd_digests_dict = get_rd_digests_dict()
                if rd_digests_dict and rd_digests_dict is not None:
                    if rd in rd_digests_dict:
                        digest = rd_digests_dict[rd]
                        if digest and digest is not None:
                            #latitude = digest['latitude']
                            #longitude = digest['longitude']
                            #depth = digest['depth']
                            water_depth = digest['waterDepth']
            except Exception:
                pass

            #if latitude and latitude is not None:
            #    latitude = round(latitude, 5)
            #if longitude and longitude is not None:
            #    longitude = round(longitude, 5)
            #iris_stream['latitude'] = latitude
            #iris_stream['longitude'] = longitude
            #iris_stream['depth'] = depth
            iris_stream['water_depth'] = water_depth
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - -

            # General
            if debug: print '\n Get general stream items for IRIS rd: ', rd
            iris_stream['reference_designator'] = rd
            iris_stream['stream'] = None
            iris_stream['stream_dataset'] = ''
            iris_stream['stream_display_name'] = None
            iris_stream['stream_method'] = None
            iris_stream['stream_name'] = None
            iris_stream['stream_type'] = None
            iris_streams.append(iris_stream)

        if debug: print '\n-- Number of IRIS streams created: ', len(iris_streams)
        return iris_streams
    except Exception as err:
        message = str(err)
        raise Exception(message)
