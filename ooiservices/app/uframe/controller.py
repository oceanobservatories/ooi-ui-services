#!/usr/bin/env python
"""
Mixture of route endpoints and supporting functions.
"""

from flask import (jsonify, request, current_app, make_response)
from ooiservices.app import db
from ooiservices.app.uframe import uframe as api
from ooiservices.app.models import DisabledStreams
from ooiservices.app.main.authentication import auth
from ooiservices.app.main.errors import bad_request
from ooiservices.app.uframe.common_tools import to_bool
from ooiservices.app.uframe.plotting import generate_plot
from ooiservices.app.uframe.vocab import (get_display_name_by_rd, get_long_display_name_by_rd)
from ooiservices.app.uframe.config import (get_uframe_info, get_uframe_url_info, get_uframe_plot_timeout)
from ooiservices.app.uframe.data import (get_data, get_simple_data, find_parameter_ids, get_multistream_data)
from ooiservices.app.uframe.stream_tools import get_stream_name_byname

from urllib import urlencode
import json
import numpy as np

from contextlib import closing
import time
import urllib2
from operator import itemgetter
import requests
import requests.adapters
import requests.exceptions
from requests.exceptions import (ConnectionError, Timeout)

from copy import deepcopy
import math
import datetime as dt

__author__ = 'Andy Bird'

COSMO_CONSTANT = 2208988800


def split_stream_name(ui_stream_name):
    """ Splits the hyphenated reference designator and stream type into a tuple of
    (mooring, platform, instrument, stream_type, stream)
    """
    mooring, platform, instrument = ui_stream_name.split('-', 2)
    instrument, stream_type, stream = instrument.split('_', 2)
    stream_type = stream_type.replace("-","_")
    stream = stream.replace("-","_")
    return (mooring, platform, instrument, stream_type, stream)


def combine_stream_name(mooring, platform, instrument, stream_type, stream):
    first_part = '-'.join([mooring, platform, instrument])
    all_of_it = '_'.join([first_part, stream_type, stream])
    return all_of_it


# Move to streams.py
@api.route('/disabled_streams', methods=['GET', 'POST'])
@api.route('/disabled_streams/<int:id>', methods=['DELETE'])
def disabled_streams(id=None):
    """ Process GET, POST and DELETE for disabled streams.

    @method GET:
        Returns the list of all the disabled streams from our database.

    @method POST:
        @params: ID
        Create a new 'disabled streams' in our local database.

    @method DELETE:
        @params: ID
        Delete a disabled streams identifier from our local database.
    """

    if request.method == 'GET':
        disabled_streams = DisabledStreams.query.all()
        return jsonify({'disabled_streams':
                        [disabled_stream.to_json() \
                         for disabled_stream in disabled_streams]})

    elif request.method == 'POST':
        try:
            # grab the json payload
            payload = json.loads(request.data)

            # create a new instance of the disabled streams with the data
            disabled_stream = DisabledStreams.from_json(payload)

            # add to the databse
            db.session.add(disabled_stream)
            db.session.commit()
            return jsonify({ 'disabled_streams': 'Stream Disabled!'}), 200
        except Exception as e:
            print type(e)
            # roll it back if there is a problem.
            db.session.rollback()
            db.session.commit()
            return make_response(e.message), 409

    elif request.method == 'DELETE':
        try:
            # get the item to delete
            disabled_stream = DisabledStreams.query.get_or_404(id)

            # obliterate it form the db
            db.session.delete(disabled_stream)
            db.session.commit()
            return jsonify({'message': 'Stream Enabled!'}), 200
        except Exception as e:
            # roll it back if there is a problem.
            db.session.rollback()
            db.session.commit()
            return jsonify({'message': 'Problem activating stream: %s'%e}), 409


# Deprecate.
@api.route('/antelope_acoustic/list', methods=['GET'])
def get_acoustic_datalist():
    """ Get all available acoustic data sets.
    """
    antelope_url = current_app.config['UFRAME_ANTELOPE_URL']
    r = requests.get(antelope_url)
    data = r.json()

    for ind, record in enumerate(data):
        data[ind]['filename'] = record['downloadUrl'].split("/")[-1]
        data[ind]['startTime'] = data[ind]['startTime'] - COSMO_CONSTANT
        data[ind]['endTime'] = data[ind]['endTime'] - COSMO_CONSTANT

    try:
        is_reverse = False
        if request.args.get('sort') and request.args.get('sort') != "":
            sort_by = request.args.get('sort')
            if request.args.get('order') and request.args.get('order') != "":
                order = request.args.get('order')
                if order == 'reverse':
                    is_reverse = True
        else:
            sort_by = 'endTime'
        data = sorted(data, key=itemgetter(sort_by), reverse=is_reverse)
    except (TypeError, KeyError):
        raise

    if request.args.get('startAt'):
        start_at = int(request.args.get('startAt'))
        count = int(request.args.get('count'))
        total = int(len(data))
        retval_slice = data[start_at:(start_at + count)]
        result = jsonify({"count": count,
                          "total": total,
                          "startAt": start_at,
                          "results": retval_slice})
        return result
    else:
        return jsonify(results=data)

'''
Deprecate this function.
def map_common_error_message(response, default):
    """ This function parses the error response from uFrame into a meaningful message for the UI.
    """
    message = default
    if 'requestUUID' in response:
        UUID = response.split('requestUUID":')[1].split('"')[1]
        message = 'Error Occurred During Product Creation<br>UUID for reference: ' + UUID
    elif 'Failed to respond' in response:
        message = 'Internal System Error in Data Repository'
    return message
'''

'''
# Deprecate this function - it only returns end_time.
def validate_date_time(start_time, end_time):
    """
    uframe_data_request_limit = int(current_app.config['UFRAME_DATA_REQUEST_LIMIT'])/1440
    new_end_time_strp = datetime.datetime.strptime(start_time, "
                                                   ") + datetime.timedelta(days=uframe_data_request_limit)
    old_end_time_strp = datetime.datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    new_end_time = datetime.datetime.strftime(new_end_time_strp, "%Y-%m-%dT%H:%M:%S.%fZ")
    if old_end_time_strp > new_end_time_strp:
        end_time = new_end_time
    """
    return end_time
'''

def make_cache_key():
    return urlencode(request.args)


# Restore event processing as needed.
def get_events_by_ref_des(data, ref_des):
    """
    """
    result = []
    return result


'''
# Deprecate or move to uframe_tools.py
# todo: Return exception in consistent manner.
def get_uframe_streams(mooring, platform, instrument, stream_type):
    """ Get a list of all the streams.
    """
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = '/'.join([uframe_url, mooring, platform, instrument, stream_type])
        current_app.logger.info("GET %s", url)
        response = requests.get(url, timeout=(timeout, timeout_read))
        return response
    except ConnectionError:
        message = 'ConnectionError getting uframe streams.'
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting uframe streams.'
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err)
        #return internal_server_error('uframe connection cannot be made.' + str(e.message))
        return internal_server_error(message)


# todo: Return exception in consistent manner.
def get_uframe_stream(mooring, platform, instrument, stream):
    """ Get a list the reference designators for the streams.
    """
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, mooring, platform, instrument, stream])
        current_app.logger.info("GET %s", url)
        response = requests.get(url, timeout=(timeout, timeout_read))
        return response
    except ConnectionError:
        message = 'ConnectionError getting uframe stream.'
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting uframe stream.'
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as e:
        #return internal_server_error('uframe connection cannot be made.' + str(e.message))
        return _response_internal_server_error(str(e))
'''


@api.route('/get_instrument_metadata/<string:ref>', methods=['GET'])
def get_uframe_instrument_metadata(ref):
    """ Returns the metadata response for a given instrument - all streams.
    """
    try:
        mooring, platform, instrument = ref.split('-', 2)
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, mooring, platform, instrument, 'metadata'])
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code == 200:
            data = response.json()
            return jsonify(metadata=data['parameters'])
        return jsonify(metadata={}), 404
    except Exception as err:
        message = str(err)
        return bad_request(message)


@api.route('/get_metadata_parameters/<string:ref>', methods=['GET'])
def get_uframe_instrument_metadata_parameters(ref):
    """ Returns the metadata parameters for a given instrument - all streams.
    """
    results = []
    try:
        mooring, platform, instrument = ref.split('-', 2)
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = '/'.join([uframe_url, mooring, platform, instrument, 'metadata', 'parameters'])
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code == 200:
            results = response.json()
        return jsonify(parameters=results), 200
    except ConnectionError:
        message = 'ConnectionError getting uframe instrument metadata parameters.'
        current_app.logger.info(message)
        return bad_request(message)
    except Timeout:
        message = 'Timeout getting uframe instrument metadata parameters.'
        current_app.logger.info(message)
        return bad_request(message)
    except Exception as err:
        message = str(err)
        return bad_request(message)


@api.route('/get_metadata_times/<string:ref>', methods=['GET'])
def get_uframe_stream_metadata_times(ref):
    """ Returns the time bounds response for a given instrument - all streams.
    """
    mooring, platform, instrument = ref.split('-', 2)
    results = []
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, mooring, platform, instrument, 'metadata','times'])
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code == 200:
            results = response.json()
        return jsonify(times=results), 200
    except ConnectionError:
        message = 'ConnectionError getting uframe instrument metadata times.'
        current_app.logger.info(message)
        return bad_request(message)
    except Timeout:
        message = 'Timeout getting uframe instrument metadata times.'
        current_app.logger.info(message)
        return bad_request(message)
    except Exception as err:
        message = 'Error getting uframe instrument metadata times, ' + str(err)
        current_app.logger.info(message)
        message = str(err)
        return bad_request(message)


@api.route('/get_metadata_stream_times/<string:ref>/<string:stream>/<string:method>', methods=['GET'])
def get_uframe_stream_metadata_stream_by_method(ref, stream, method):
    """ Returns the metadata time bounds response for a given stream and method.
    """
    mooring, platform, instrument = ref.split('-', 2)
    results = []
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, mooring, platform, instrument, 'metadata','times'])
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            return jsonify(times=results), response.status_code
        data = response.json()
        if data and data is not None:
            for item in data:
                if item['method'] == method and item['stream'] == stream:
                    results.append(item)
        return jsonify(times=results), 200
    except ConnectionError:
        message = 'ConnectionError getting uframe stream metadata times.'
        current_app.logger.info(message)
        return bad_request(message)
    except Timeout:
        message = 'Timeout getting uframe stream metadata times.'
        current_app.logger.info(message)
        return bad_request(message)
    except Exception as err:
        message = 'Error getting uframe stream metadata times, ' + str(err)
        current_app.logger.info(message)
        message = str(err)
        return bad_request(message)


@api.route('/get_multistream/<string:instrument1>/<string:instrument2>/<string:stream1>/<string:stream2>/<string:var1>/<string:var2>', methods=['GET'])
def multistream_api(instrument1, instrument2, stream1, stream2, var1, var2):
    """
    Service endpoint to get multistream interpolated data.
    Example request:
    http://localhost:4000/uframe/get_multistream/CP05MOAS-GL340-03-CTDGVM000/CP05MOAS-GL340-02-FLORTM000/
    telemetered_ctdgv-m-glider-instrument/telemetered_flort-m-glider-instrument/sci_water_pressure/sci_flbbcd_chlor_units
    ?startdate=2015-05-07T02:49:22.745Z&enddate=2015-06-28T04:00:41.282Z

    """
    try:
        # Format of streams:
        #   stream1 = 'telemetered_ctdgv-m-glider-instrument'
        #   stream2 = 'telemetered_flort-m-glider-instrument'
        try:
            resp_data, units = get_multistream_data(instrument1, instrument2, stream1, stream2, var1, var2)
        except Exception as err:
            message = str(err)
            return bad_request(message)

        method1, stream_name1 = stream1.split('_')
        method2, stream_name2 = stream2.split('_')

        # Get title and subtitle (review title and subtitle length may cause display issues in plot)
        title = get_long_display_name_by_rd(instrument1)
        subtitle = get_long_display_name_by_rd(instrument2)

        # Prepare response data.
        new_resp_data = []
        try:
            actual_stream2_name = str(stream_name2).replace('-','_')
            key_to_find = '-'.join([actual_stream2_name, str(var2)])
            for data in resp_data:
                keys = data.keys()
                new_data = deepcopy(data)
                for key in keys:
                    if key_to_find in str(key) or key_to_find == str(key):
                        new_data[str(var2)] = data[key]
                        new_data['time'] = data['pk']['time']
                        del new_data[key]
                        new_resp_data.append(new_data)
                        break
        except IndexError:
            message = 'Data array length error (IndexError).'
            raise Exception(message)
        except KeyError:
            message = 'Missing data in data repository. (KeyError)'
            raise Exception(message)
        except Exception as err:
            message = str(err)
            raise Exception(message)
        return jsonify(data=new_resp_data, units=units, title=title, subtitle=subtitle)
    except Exception as err:
        message = str(err)
        raise Exception(message)


def is_nan(x):
    return isinstance(x, float) and math.isnan(x)


def get_uframe_multi_stream_contents(stream1_dict, stream2_dict, start_time, end_time):
    """ Gets the data from an interpolated multi stream request.

    Example request:
        http://server:12576/sensor?r=r1&r=r2&r1.refdes=CP05MOAS-GL340-03-CTDGVM000&
        r2.refdes=CP05MOAS-GL340-02-FLORTM000&r1.method=telemetered&r2.method=telemetered&r1.stream=ctdgv_m_glider_instrument&
        r2.stream=flort_m_glider_instrument&r1.params=PD1527&r2.params=PD1485&limit=1000&beginDT=2015-05-07T02:49:22.745Z&endDT=2015-06-28T04:00:41.282Z
    """
    debug = False
    try:
        # Get the parts of the request from the input stream dicts
        refdes1 = stream1_dict['refdes']
        refdes2 = stream2_dict['refdes']
        method1 = stream1_dict['method']
        method2 = stream2_dict['method']
        stream1 = stream1_dict['stream']
        stream2 = stream2_dict['stream']
        params1 = stream1_dict['params']
        params2 = stream2_dict['params']

        limit = current_app.config['DATA_POINTS']
        #GA_URL = current_app.config['GOOGLE_ANALYTICS_URL']+'&ec=multistreamdata&ea=%s&el=%s' % \
        #         ('-'.join([refdes1+stream1, refdes1+stream2]), '-'.join([start_time, end_time]))
        query = ('sensor?r=r1&r=r2&r1.refdes=%s&r2.refdes=%s&r1.method=%s&r2.method=%s'
                 '&r1.stream=%s&r2.stream=%s&r1.params=%s&r2.params=%s&limit=%s&beginDT=%s&endDT=%s&user=plotting'
                 % (refdes1, refdes2, method1, method2, stream1, stream2,
                    params1, params2, limit, start_time, end_time))

        base_url, timeout, timeout_read = get_uframe_url_info()
        url = "/".join([base_url, query])
        current_app.logger.debug("***:" + url)
        response = requests.get(url, timeout=(timeout, timeout_read))
        if debug: print '\n debug -- response.status_code: ', response.status_code
        if response.status_code != 200:
            message = '(%d) Failed to get multistream contents. %s' % (response.status_code,  response.text)
            if debug: print '\n debug -- message: ', message
            raise Exception(message)
        else:
            return response.json(), response.status_code
    except ConnectionError:
        message = 'Error: ConnectionError getting uframe multi stream contents.'
        raise Exception(message)
    except Timeout:
        message = 'Error: Timeout getting uframe multi stream contents.'
        raise Exception(message)
    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- get_uframe_multi_stream_contents exception message: ', message
        raise Exception(message)


@auth.login_required
@api.route('/get_csv/<string:stream>/<string:ref>/<string:start_time>/<string:end_time>/<string:dpa_flag>', methods=['GET'])
def get_csv(stream, ref, start_time, end_time, dpa_flag):
    mooring = None
    platform = None
    instrument = None
    stream_type = None
    try:
        mooring, platform, instrument = ref.split('-', 2)
        stream_type, stream = stream.split('_', 1)
        stream_type = stream_type.replace('-','_')
        stream = stream.replace('-','_')
        GA_URL = current_app.config['GOOGLE_ANALYTICS_URL']+'&ec=download_csv&ea=%s&el=%s' % \
                 ('-'.join([mooring, platform, instrument, stream]), '-'.join([start_time, end_time]))
        urllib2.urlopen(GA_URL)
    except KeyError:
        pass

    uframe_url, timeout, timeout_read = get_uframe_info()
    user = request.args.get('user', '')
    email = request.args.get('email', '')
    if dpa_flag == '0':
        query = '?beginDT=%s&endDT=%s&user=%s&email=%s' % (start_time, end_time, user, email)
    else:
        query = '?beginDT=%s&endDT=%s&execDPA=true&user=%s&email=%s' % (start_time, end_time, user, email)
    query += '&format=application/csv'
    url = "/".join([uframe_url, mooring, platform, instrument, stream_type, stream + query])
    current_app.logger.debug('***** url: ' + url)
    response = requests.get(url, timeout=(timeout, timeout_read))
    return response.text, response.status_code


@auth.login_required
@api.route('/get_json/<string:stream>/<string:ref>/<string:start_time>/<string:end_time>/<string:dpa_flag>/<string:provenance>/<string:annotations>', methods=['GET'])
def get_json(stream, ref, start_time, end_time, dpa_flag, provenance, annotations):
    mooring = None
    platform = None
    instrument = None
    stream_type = None
    try:
        mooring, platform, instrument = ref.split('-', 2)
        stream_type, stream = stream.split('_', 1)
        stream_type = stream_type.replace('-', '_')
        stream = stream.replace('-', '_')
        GA_URL = current_app.config['GOOGLE_ANALYTICS_URL']+'&ec=download_json&ea=%s&el=%s' % \
                 ('-'.join([mooring, platform, instrument, stream]), '-'.join([start_time, end_time]))
        urllib2.urlopen(GA_URL)
    except KeyError:
        pass

    uframe_url, timeout, timeout_read = get_uframe_info()
    user = request.args.get('user', '')
    email = request.args.get('email', '')
    if dpa_flag == '0':
        query = '?beginDT=%s&endDT=%s&include_provenance=%s&include_annotations=%s&user=%s&email=%s' % \
                (start_time, end_time, provenance, annotations, user, email)
    else:
        query = '?beginDT=%s&endDT=%s&include_provenance=%s&include_annotations=%s&execDPA=true&user=%s&email=%s' % \
                (start_time, end_time, provenance, annotations, user, email)
    query += '&format=application/json'
    url = "/".join([uframe_url, mooring, platform, instrument, stream_type, stream + query])
    current_app.logger.debug('***** url: ' + url)
    response = requests.get(url, timeout=(timeout, timeout_read))
    return response.text, response.status_code


@auth.login_required
@api.route('/get_netcdf/<string:stream>/<string:ref>/<string:start_time>/<string:end_time>/<string:dpa_flag>/<string:provenance>/<string:annotations>', methods=['GET'])
def get_netcdf(stream, ref, start_time, end_time, dpa_flag, provenance, annotations):
    mooring = None
    platform = None
    instrument = None
    stream_type = None
    try:
        mooring, platform, instrument = ref.split('-', 2)
        stream_type, stream = stream.split('_', 1)
        stream_type = stream_type.replace('-', '_')
        stream = stream.replace('-', '_')
        GA_URL = current_app.config['GOOGLE_ANALYTICS_URL']+'&ec=download_netcdf&ea=%s&el=%s' % \
                 ('-'.join([mooring, platform, instrument, stream]), '-'.join([start_time, end_time]))
        urllib2.urlopen(GA_URL)
    except KeyError:
        pass

    user = request.args.get('user', '')
    email = request.args.get('email', '')
    if dpa_flag == '0':
        query = '?beginDT=%s&endDT=%s&include_provenance=%s&include_annotations=%s&user=%s&email=%s' % \
                (start_time, end_time, provenance, annotations, user, email)
    else:
        query = '?beginDT=%s&endDT=%s&include_provenance=%s&include_annotations=%s&execDPA=true&user=%s&email=%s' % \
                (start_time, end_time, provenance, annotations, user, email)
    query += '&format=application/netcdf'
    uframe_url, timeout, timeout_read = get_uframe_info()
    url = "/".join([uframe_url, mooring, platform, instrument, stream_type, stream + query])
    response = requests.get(url, timeout=(timeout, timeout_read))
    return response.text, response.status_code


def get_process_profile_data(stream, instrument, xvar, yvar):
    """ NOTE: i have to swap the inputs (xvar, yvar) around at this point to get the plot to work....
    """
    try:
        join_name = '_'.join([str(instrument), str(stream)])
        mooring, platform, instrument, stream_type, stream = split_stream_name(join_name)
        parameter_ids, y_units, x_units = find_parameter_ids(mooring, platform, instrument, [yvar], [xvar])
        data = get_profile_data(mooring, platform, instrument, stream_type, stream, parameter_ids)
        if not data or data is None:
            raise Exception('Profiles not present in data.')
    except Exception as e:
        raise Exception('%s' % str(e.message))

    '''
    # check the data is in the first row
    if yvar not in data[0] or xvar not in data[0]:
        data = {'error':'requested fields not in data'}
        return data
    if 'profile_id' not in data[0]:
        data = {'error':'profiles not present in data'}
        return data
    '''

    y_data = []
    x_data = []
    time = []
    profile_id_list = []
    profile_count = -1
    for i, row in enumerate(data):
        if (row['profile_id']) >= 0:
            profile_id = int(row['profile_id'])
            if profile_id not in profile_id_list:
                y_data.append([])
                x_data.append([])
                time.append(float(row['pk']['time']))
                profile_id_list.append(profile_id)
                profile_count += 1
            try:
                y_data[profile_count].append(row[yvar])
                x_data[profile_count].append(row[xvar])
            except Exception as e:
                raise Exception('profiles not present in data')

    return {'x': x_data, 'y': y_data, 'x_field': xvar, "y_field": yvar, 'time': time}


def get_profile_data(mooring, platform, instrument, stream_type, stream, parameter_ids):
    """ Process uframe data into profiles.
    """
    try:
        data = []
        if 'startdate' in request.args and 'enddate' in request.args:
            st_date = request.args['startdate']
            ed_date = request.args['enddate']
            if 'dpa_flag' in request.args:
                dpa_flag = request.args['dpa_flag']
            else:
                dpa_flag = '0'
            #ed_date = validate_date_time(st_date, ed_date)
            data, status_code = get_uframe_plot_contents_chunked(mooring, platform, instrument, stream_type, stream, st_date, ed_date, dpa_flag, parameter_ids)
        else:
            message = 'Failed to make plot - start end dates not applied'
            current_app.logger.info(message)
            raise Exception(message)

        if status_code != 200:
            #raise IOError("uFrame unable to get data for this request.")
            message = 'Unable to get uframe profile data for this request.'
            raise Exception(message)

        current_app.logger.debug('\n --- retrieved data from uframe for profile processing...')

        # Note: assumes data has depth and time is ordinal
        # Need to add assertions and try and exceptions to check data
        time = []
        depth = []

        request_xvar = None
        if request.args['xvar']:
            junk = request.args['xvar']
            test_request_xvar = junk.encode('ascii', 'ignore')
            if type(test_request_xvar) == type(''):
                if ',' in test_request_xvar:
                    chunk_request_var = test_request_xvar.split(',',1)
                    if len(chunk_request_var) > 0:
                        request_xvar = chunk_request_var[0]
                else:
                    request_xvar = test_request_xvar
        else:
            message = 'Failed to make plot - no xvar provided in request'
            current_app.logger.info(message)
            raise Exception(message)
        if not request_xvar:
            message = 'Failed to make plot - unable to process xvar provided in request'
            current_app.logger.info(message)
            raise Exception(message)

        for row in data:
            depth.append(int(row[request_xvar]))
            time.append(float(row['pk']['time']))

        matrix = np.column_stack((time, depth))
        tz = matrix
        origTz = tz
        INT = 10
        # tz length must equal profile_list length

        # maxi = np.amax(tz[:, 0])
        # mini = np.amin(tz[:, 0])
        # getting a range from min to max time with 10 seconds or milliseconds. I have no idea.
        ts = (np.arange(np.amin(tz[:, 0]), np.amax(tz[:, 0]), INT)).T

        # interpolation adds additional points on the line within f(t), f(t+1)  time is a function of depth
        itz = np.interp(ts, tz[:, 0], tz[:, 1])

        newtz = np.column_stack((ts, itz))
        # 5 unit moving average
        WINDOW = 5
        weights = np.repeat(1.0, WINDOW) / WINDOW
        ma = np.convolve(newtz[:, 1], weights)[WINDOW-1:-(WINDOW-1)]
        # take the diff and change negatives to -1 and postives to 1
        dZ = np.sign(np.diff(ma))

        # repeat for second derivative
        dZ = np.convolve(dZ, weights)[WINDOW-1:-(WINDOW-1)]
        dZ = np.sign(dZ)

        r0 = 1
        r1 = len(dZ) + 1
        dZero = np.diff(dZ)

        start = []
        stop = []
        # find where the slope changes
        dr = [start.append(i) for (i, val) in enumerate(dZero) if val != 0]
        if len(start) == 0:
            raise Exception('Unable to determine where slope changes.')

        for i in range(len(start)-1):
            stop.append(start[i+1])

        stop.append(start[0])
        start_stop = np.column_stack((start, stop))
        start_times = np.take(newtz[:, 0], start)
        stop_times = np.take(newtz[:, 0], stop)
        start_times = start_times - INT*2
        stop_times = stop_times + INT*2

        depth_profiles = []

        for i in range(len(start_times)):
            profile_id = i
            proInds = origTz[(origTz[:, 0] >= start_times[i]) & (origTz[:, 0] <= stop_times[i])]
            value = proInds.shape[0]
            z = np.full((value, 1), profile_id)
            pro = np.append(proInds, z, axis=1)
            depth_profiles.append(pro)

        depth_profiles = np.concatenate(depth_profiles)
        # Check for duplicate times, not yet done.
        # Start stop times may result in overlaps on original data set. (see function above)
        # May be an issue, requires further investigation.
        profile_list = []
        for row in data:
            try:
                # Need to add epsilon. Floating point error may occur
                where = np.argwhere(depth_profiles == float(row['pk']['time']))
                index = where[0]
                rowloc = index[0]
                if len(where) and int(row[request_xvar]) == depth_profiles[rowloc][1]:
                    row['profile_id'] = depth_profiles[rowloc][2]
                    profile_list.append(row)
            except IndexError:
                row['profile_id'] = None
                profile_list.append(row)
            except Exception as err:
                raise Exception('%s' % str(err.message))
        # profile length should equal tz  length
        return profile_list

    except Exception as err:
        current_app.logger.info('\n* (pass) exception: ' + str(err.message))


@api.route('/get_profiles/<string:stream>/<string:instrument>', methods=['GET'])
def get_profiles(stream, instrument):
    filename = '-'.join([stream, instrument, 'profiles'])
    content_headers = {'Content-Type': 'application/json',
                       'Content-Disposition': "attachment; filename=%s.json" % filename}
    try:
        profiles = get_profile_data(instrument, stream)
    except Exception as e:
        return jsonify(error=e.message), 400, content_headers
    if profiles is None:
        return jsonify(), 204, content_headers
    return jsonify(profiles=profiles), 200, content_headers


#==============================================================================================
#==============================================================================================
@api.route('/get_data/<string:instrument>/<string:stream>/<string:yvar>/<string:xvar>', methods=['GET'])
def get_data_api(stream, instrument, yvar, xvar):
    """ Get x-y plot data and return with units and title.
    """
    try:
        xvar = xvar.split(',')
        yvar = yvar.split(',')
        title = instrument
        if instrument and instrument is not None and len(instrument) > 8:
            title = get_display_name_by_rd(instrument)
        resp_data, units = get_simple_data(stream, instrument, yvar, xvar)
        return jsonify(data=resp_data, units=units, title=title)
    except Exception as err:
        message = str(err)
        return bad_request(message)


@api.route('/plot/<string:instrument>/<string:stream>', methods=['GET'])
def get_svg_plot(instrument, stream):
    """ Create plot image and return to client.
    """
    debug = False
    number_of_data_points = 1000
    if debug:
        print '\n debug -- =============================================='
        print '\n debug -- =============================================='
        print '\n debug -- Entered /plot - get_svg_plot...'
        print '\n debug -- instrument: ', instrument
        print '\n debug -- stream: ', stream

    # Make a list out of instrument.
    instrument = instrument.split(',')
    #instrument.append(instrument[0])

    # Get stream name to forward off for plotting image, used for parameter name (english)
    tmp = stream.split('_')
    tmp_stream_name = str(tmp[1])
    tmp_stream_name = tmp_stream_name.replace('-', '_')
    if debug: print '\n debug -- tmp_stream_name: ', tmp_stream_name

    stream = stream.split(',')
    #stream.append(stream[0])

    # Get request arguments.
    plot_format = request.args.get('format', 'svg')
    # time series vs profile
    plot_layout = request.args.get('plotLayout', 'timeseries')
    if debug: print '\n debug -- Plot Layout requested: ', plot_layout

    xvar = request.args.get('xvar', 'time')
    yvar = request.args.get('yvar', None)

    # There can be multiple variables so get into a list
    xvar = xvar.split(',')
    yvar = yvar.split(',')

    if len(instrument) == len(stream):
        pass
    else:
        instrument = [instrument[0]]
        stream = [stream[0]]
        yvar = [yvar[0]]
        xvar = [xvar[0]]

    # Create booleans from request arguments
    # use_line = to_bool(request.args.get('line', True))
    use_scatter = to_bool(request.args.get('scatter', True))
    #use_event = to_bool(request.args.get('event', True))
    qaqc = int(request.args.get('qaqc', 0))

    # Get events.
    events = {}
    """
    if use_event:
        try:
            response = get_events_by_ref_des(instrument[0])
            events = json.loads(response.data)
        except Exception as err:
            current_app.logger.info(str(err.message))
            return jsonify(error=str(err.message)), 400
    """

    profileid = request.args.get('profileId', None)

    # A yvar is required.
    if yvar is None:
        message = 'A y variable is required.'
        return bad_request(message)

    # For conversion of the data from pixels to inches for plot
    height = float(request.args.get('height', 100))  # px
    width = float(request.args.get('width', 100))  # px
    height_in = height / 96.
    width_in = width / 96.

    #- - - - - - - - - - - - - - - -
    # Get data.
    #- - - - - - - - - - - - - - - -
    try:
        if debug: print '\n debug -- Plot Layout: ', plot_layout

        # Depth Profile
        if plot_layout == "depthprofile":
            data = get_process_profile_data(stream[0], instrument[0], yvar[0], xvar[0])

        # All plots types other than profile.
        else:
            # One instrument
            if len(instrument) == 1:
                if debug: print '\n debug -- Branch 1...'

                # Review for sparse data presentation (add more data).
                # Plot types stacked or 3d_scatter.
                if plot_layout == '3d_scatter' or plot_layout == 'stacked':
                    # 3D Scatter plot should use a larger number of data points than stacked.
                    number_of_data_points = 2000
                    if plot_layout == '3d_scatter':
                        number_of_data_points = 8000 #number_of_data_points * 2
                    #data = get_max_data(stream[0], instrument[0], yvar, xvar, number_of_data_points)
                    #if data and data is not None:
                    #    data['number_of_data_points'] = number_of_data_points

                # All other plot types.
                #else:
                #    data = get_data(stream[0], instrument[0], yvar, xvar, number_of_data_points)
                data = get_max_data(stream[0], instrument[0], yvar, xvar, number_of_data_points)
                if data and data is not None:
                    data['number_of_data_points'] = number_of_data_points
                #if not data or data is None:
                else:
                    message = 'No data returned for stream %s and instrument %s, y-var: %s and x-var: %s' % \
                              (stream[0], instrument[0], yvar, xvar)
                    raise Exception(message)

            # Multiple instruments.
            elif len(instrument) > 1:
                if debug: print '\n debug -- Branch 2...'
                data = []
                for idx, instr in enumerate(instrument):
                    stream_data = get_data(stream[idx], instr, [yvar[idx]], [xvar[idx]])
                    data.append(stream_data)
            # Added
            else:
                if debug: print '\n debug -- Branch 3...'
                data = []
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)

    if not data:
        message = 'No data returned for %s.' % plot_layout
        return bad_request(message)

    # return if error
    if 'error' in data or 'Error' in data:
        #return jsonify(error=data['error']), 400
        return bad_request(data['error'])

    # Generate plot
    some_tuple = ('a', 'b')
    if str(type(data)) == str(type(some_tuple)) and plot_layout == 'depthprofile':
        message = 'Depth profile error: tuple data returned for %s' % plot_layout
        return bad_request(message)


    # Get title. Get vocabulary names for plot title. (Reference designator is returned if no vocabulary)
    if isinstance(data, dict):
        title = get_long_display_name_by_rd(instrument[0])
        if len(title) > 50:
            title = title.replace(' - ', '\n')
        if plot_layout == 'rose':
            # Get stream display name to be used in plotting title.
            stream_display_name = get_stream_name_byname(tmp_stream_name)
            title = title + '\n' + stream_display_name

        data['title'] = title
        data['height'] = height_in
        data['width'] = width_in
        data['stream_name'] = tmp_stream_name
    else:
        for idx, streamx in enumerate(stream):
            title = get_display_name_by_rd(instrument[idx])
            if len(title) > 50:
                title = ''.join(title.split('-')[0:-1]) + '\n' + title.split('-')[-1]
            data[idx]['title'] = title
            data[idx]['height'] = height_in
            data[idx]['width'] = width_in

    plot_options = {'plot_format': plot_format,
                    'plot_layout': plot_layout,
                    'use_scatter': use_scatter,
                    'events': events,
                    'profileid': profileid,
                    'width_in': width_in,
                    'use_qaqc': qaqc,
                    'st_date': request.args['startdate'],
                    'ed_date': request.args['enddate']}

    try:
        # Check data before requesting plot
        if not data or data is None:
            message = 'No data provided from uframe for plotting.'
            raise Exception(message)
        if debug:
            print '\n debug -- len(data): ', len(data)
            print '\n debug -- calling generate plot....for ', plot_layout

        # Generate plot. The plot type/format is provided in plot options.
        buf = generate_plot(data, plot_options)

        # Return resulting svg or png plot to UI.
        content_header_map = {
            'svg': 'image/svg+xml',
            'png': 'image/png'
        }
        return buf.read(), 200, {'Content-Type': content_header_map[plot_format]}
    except Exception as err:
        message = 'Error generating {0} plot: {1}'.format(plot_options['plot_layout'], str(err))
        current_app.logger.info(str(err))
        return bad_request(message)


'''
def get_uframe_stream_contents_chunked(mooring, platform, instrument, stream_type, stream,
                                       start_time, end_time, dpa_flag):
    """ Gets the bounded stream contents, start_time and end_time need to be datetime objects.
    """
    debug = False
    try:
        if debug:
            print '\n debug -- ********************************************************************'
            print '\n debug -- Entered get_uframe_stream_contents_chunked...'

        query = '?beginDT=%s&endDT=%s&user=download' % (start_time, end_time)
        UFRAME_DATA = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE']
        url = "/".join([UFRAME_DATA, mooring, platform, instrument, stream_type, stream + query])
        current_app.logger.debug("***:%s" % url)
        TOO_BIG = 1024 * 1024 * 15 # 15MB
        CHUNK_SIZE = 1024 * 32   #...KB
        TOTAL_SECONDS = 20
        dataBlock = ""
        idx = 0

        #counter
        t0 = time.time()

        with closing(requests.get(url, stream=True)) as response:
            content_length = 0
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                content_length = content_length + len(chunk)
                t1 = time.time()
                total = t1-t0
                idx+=1
                if content_length > TOO_BIG or total > TOTAL_SECONDS:
                    #('uframe response to large.')
                    # break it down to the last know good spot
                    t00 = time.time()
                    idx_c = dataBlock.rfind('}, {')
                    dataBlock = dataBlock[:idx_c]
                    dataBlock+="} ]"
                    t11 = time.time()
                    totaln = t11-t00

                    print "size_limit or time reached",content_length/(1024 * 1024),total,totaln,idx
                    return json.loads(dataBlock),200
                # all the data is in the response return it as normal
                #previousBlock = dataBlock
                dataBlock+=chunk
            #print "transfer complete",content_length/(1024 * 1024),total

            #if str(dataBlock[-3:-1]) != '} ]':
            #    idx_c = dataBlock.rfind('}')
            #    dataBlock = dataBlock[:idx_c]
            #    dataBlock+="} ]"
            #    print 'uFrame appended Error Message to Stream',"\n",dataBlock[-3:-1]
            idx_c = dataBlock.rfind('} ]')
            if idx_c == -1:
                dataBlock+="]"

            return json.loads(dataBlock), 200

    except Exception as err:
        #return json.loads(dataBlock), 200
        message = str(err)
        return bad_request(message)
'''

def get_uframe_plot_contents_chunked(mooring, platform, instrument, stream_type, stream,
                                     start_time, end_time, dpa_flag, parameter_ids):
    """ Gets uframe streamed contents.
    """
    rd = None
    try:
        number_of_data_points = current_app.config['DATA_POINTS']
        rd = '-'.join([mooring, platform, instrument])
        if dpa_flag == '0' and len(parameter_ids) < 1:
            query = '?beginDT=%s&endDT=%s&limit=%s&user=plotting' % (start_time, end_time, number_of_data_points)
        elif dpa_flag == '1' and len(parameter_ids) < 1:
            query = '?beginDT=%s&endDT=%s&limit=%s&user=plotting&execDPA=true' % \
                    (start_time, end_time, number_of_data_points)
        elif dpa_flag == '0' and len(parameter_ids) > 0:
            query = '?beginDT=%s&endDT=%s&limit=%s&parameters=%s&user=plotting' % \
                    (start_time, end_time, number_of_data_points, ','.join(parameter_ids))
        elif dpa_flag == '1' and len(parameter_ids) > 0:
            query = '?beginDT=%s&endDT=%s&limit=%s&parameters=%s&user=plotting&execDPA=true' % \
              (start_time, end_time, number_of_data_points, ','.join(map(str, parameter_ids)))
        else:
            message = 'Unable to determine criteria for query, query undefined.'
            return bad_request(message)

        # Create data request url.
        base_url, timeout, timeout_read = get_uframe_info()
        url = '/'.join([base_url, mooring, platform, instrument, stream_type, stream + query])
        print '\n***: ' + url

        # Set limits on data size and time to process.
        TOO_BIG = 1024 * 1024 * 15 # 15MB
        CHUNK_SIZE = 1024 * 32   #...KB  # 1024
        TOTAL_SECONDS = 20
        dataBlock = ''
        idx = 0
        t0 = time.time()  # counter
        # Get uframe [streaming] data.
        try:
            with closing(requests.get(url, stream=True)) as response:
                content_length = 0
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    content_length = content_length + len(chunk)
                    t1 = time.time()
                    total = t1-t0
                    idx += 1
                    if content_length > TOO_BIG:
                        message = 'Data request greater than 15MB.'
                        current_app.logger.info(message)
                        if dataBlock:
                            idx_c = dataBlock.rfind('}, \n  {')
                            if idx_c != -1:
                                dataBlock = dataBlock[:idx_c]
                                dataBlock += '} ]'
                                return json.loads(dataBlock), 200
                            else:
                                raise Exception(message)
                        else:
                            print '\n**** (size) No dataBlock, return error.'
                            raise Exception(message)

                    if total > TOTAL_SECONDS:
                        message = 'Data request timeout.'
                        current_app.logger.info(message)
                        if dataBlock:
                            idx_c = dataBlock.rfind('}, \n  {')
                            if idx_c != -1:
                                dataBlock = dataBlock[:idx_c]
                                dataBlock += '} ]'
                                return json.loads(dataBlock), 200
                            else:
                                raise Exception(message)
                        else:
                            print '\n**** (time) No dataBlock, return error.'
                            raise Exception(message)
                    dataBlock += chunk

                # Look for end of list in data.
                idx_c = dataBlock.rfind('}\n]')
                if idx_c == -1:
                    # Check for failure...
                    if not dataBlock or dataBlock is None or len(dataBlock) == 0:
                        message = 'No data returned from uframe for request.'
                        raise Exception(message)
                    result = json.loads(dataBlock)
                    # Look for error message indicating failure...
                    # {u'requestUUID': u'49b32b32-cd04-4a32-8929-0b3e676c4dfe',
                    # u'message': u'Unexpected internal error during request'}
                    if 'message' in result and 'requestUUID' in result:
                        #message = 'uframe error message: ' + result['message'] + ', requestUUID: ' + result['requestUUID']
                        message = 'Uframe error message: ' + str(result)
                        raise Exception(message)

                result = json.loads(dataBlock)
                return result, 200

        # Expand the exceptions for this block.
        except Exception as err:
            message = str(err)
            raise Exception(message)

        return None, 400

    except ConnectionError:
        message = 'ConnectionError getting uframe plot contents chunked for reference designator: %s' % rd
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting uframe plot contents chunked for reference designator: %s' % rd
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


#=====================================================================================
# Get streamed data from uframe (used for 3D Scatter and Binned pseudo color plots.)
#=====================================================================================
def get_uframe_plot_contents_chunked_max_data(mooring, platform, instrument, stream_type, stream,
                                     start_time, end_time, dpa_flag, parameter_ids, request_data_points=1000):
    """ Gets the uframe stream contents (streamed).
    The start_time and end_time need to be datetime objects
    """
    debug = False
    timing = False
    rd = None
    number_of_data_points = request_data_points
    try:
        start = dt.datetime.now()
        if timing: print '\t-- Start time: ', start

        # Build query for data request.
        rd = '-'.join([mooring, platform, instrument])
        if dpa_flag == '0' and len(parameter_ids) < 1:
            query = '?beginDT=%s&endDT=%s&limit=%s&user=plotting' % (start_time, end_time, number_of_data_points)
        elif dpa_flag == '1' and len(parameter_ids) < 1:
            query = '?beginDT=%s&endDT=%s&limit=%s&user=plotting&execDPA=true' % \
                    (start_time, end_time, number_of_data_points)
        elif dpa_flag == '0' and len(parameter_ids) > 0:
            query = '?beginDT=%s&endDT=%s&limit=%s&parameters=%s&user=plotting' % \
                    (start_time, end_time, number_of_data_points, ','.join(parameter_ids))
        elif dpa_flag == '1' and len(parameter_ids) > 0:
            query = '?beginDT=%s&endDT=%s&limit=%s&parameters=%s&user=plotting&execDPA=true' % \
              (start_time, end_time, number_of_data_points, ','.join(map(str, parameter_ids)))
        else:
            message = 'Unable to determine criteria for query, query undefined.'
            return bad_request(message)

        # Build url for data request.
        base_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([base_url, mooring, platform, instrument, stream_type, stream + query])
        if timing:
            print '\t***: ' + url
        else:
            print '\n***: ' + url

        # Prepare for stream data request; get data in chunk of 32k.
        TOO_BIG = 1024 * 1024 * 15  # 15MB
        CHUNK_SIZE = 1024 * 32      #...KB
        TOTAL_SECONDS = get_uframe_plot_timeout() # 20
        dataBlock = ''
        idx = 0
        t0 = time.time()

        # Request and process streaming data.
        try:
            with closing(requests.get(url, stream=True)) as response:
                content_length = 0
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    content_length = content_length + len(chunk)
                    t1 = time.time()
                    total = t1-t0
                    idx += 1
                    if content_length > TOO_BIG:
                        message = '[max] Data request greater than 15MB.'
                        print message
                        if dataBlock:
                            idx_c = dataBlock.rfind('}, \n  {')
                            if idx_c != -1:
                                dataBlock = dataBlock[:idx_c]
                                dataBlock += '} ]'
                                result = json.loads(dataBlock)
                                if debug: print '\n debug -- len(result): ', len(result)
                                return result, 200
                            else:
                                raise Exception(message)
                        else:
                            print '\n-- (size) No dataBlock, returning error message.'
                            raise Exception(message)

                    if total > TOTAL_SECONDS:
                        message = '[max] Data request timeout.'
                        print message
                        if dataBlock:
                            idx_c = dataBlock.rfind('}, \n  {')
                            if idx_c != -1:
                                dataBlock = dataBlock[:idx_c]
                                dataBlock += '} ]'
                                return json.loads(dataBlock), 200
                            else:
                                if debug: print '\n debug -- idx_c == -1...'
                                if debug: print '\n debug -- error message: ', message
                                raise Exception(message)
                        else:
                            print '\n-- (time) No dataBlock, returning error message.'
                            raise Exception(message)

                    dataBlock += chunk

                # Check dataBlock contents; if not contents raise exception.
                if debug: print '\n debug -- Step A...'
                if not dataBlock or dataBlock is None or len(dataBlock) == 0:
                    message = 'No data returned or processed from uframe for request.'
                    if debug: print '\n debug -- error message (not dataBlock or dataBlock is None): ', message
                    raise Exception(message)

                # Verify dataBlock is a properly terminated list.
                idx_c = dataBlock.rfind('}\n]')
                if debug: print '\n debug -- Step B...'
                if idx_c == -1:
                    # This is a possible failure, check for dataBlock and error message content.
                    if debug: print '\n debug -- Step C...'
                    result = json.loads(dataBlock)
                    # Look for error message in dataBlock.
                    # {u'requestUUID': u'49b32b32-cd04-4a32-8929-0b3e676c4dfe',
                    # u'message': u'Unexpected internal error during request'}
                    if 'message' in result and 'requestUUID' in result:
                        #message = 'uframe error message: ' + result['message'] + ', requestUUID: ' + result['requestUUID']
                        message = 'uframe error message: ' + str(result)
                        raise Exception(message)

                    # If no uframe error message and dataBlock has content.
                    dataBlock += ']'
                else:
                    if debug: print '\n debug -- Step D...', idx_c

                if debug: print '\n debug -- Step E...'
                result = json.loads(dataBlock)
                if debug: print '\n debug Step F...'
                if debug:
                    print '\n debug -- len(result): ', len(result)
                    print '\n debug -- result: '
                    #print '\n debug -- result(%d): %s' % (len(result), json.dumps(result, indent=4, sort_keys=True))

                # Timing
                end = dt.datetime.now()
                if timing:
                    print '\t-- End time:   ', end
                    print '\t-- Time to get stream list: %s' % str(end - start)
                return result, 200

        except Exception as err:
            message = str(err)
            raise Exception(message)

        if debug: print '\n debug -***** Step 2 -- get_uframe_plot_contents_chunked_max_data returning...'
        #return None, 400
        message = 'No data identified after stream processing.'
        print '\n*** ', message
        raise Exception(message)


    except ConnectionError:
        message = 'ConnectionError getting uframe plot contents chunked for reference designator: %s' % rd
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout getting uframe plot contents chunked for reference designator: %s' % rd
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as err:
        raise Exception(str(err))


# 3D Scatter and binned data.
def get_max_data(stream, instrument, yfields, xfields, number_of_data_points=1000, include_time=True):
    from collections import OrderedDict
    from ooiservices.app.uframe.common_tools import to_bool_str
    from ooiservices.app.uframe.data import find_parameter_ids
    debug = False
    data = []
    try:
        if debug:
            print '\n debug ------------------------------------------------------------'
            print '\n debug -- Step 1 -- (get_max_data) have data, review data......'
        mooring, platform, instrument = instrument.split('-', 2)
        #stream_value = stream[:]
        stream_type, stream = stream.split('_')
        stream = stream.replace('-', '_')
        stream_type = stream_type.replace('-', '_')
        parameter_ids, y_units, x_units, units_mapping = find_parameter_ids(mooring, platform, instrument, yfields, xfields)

        # Get start and end dates; if not provided raise exception.
        st_date = None
        ed_date = None
        if 'startdate' in request.args and 'enddate' in request.args:
            st_date = request.args.get('startdate', None)
            ed_date = request.args.get('enddate', None)
        if not st_date or st_date is None or ed_date is None:
            message = 'Required parameter start date undefined.'
            current_app.logger.info(message)
            raise Exception(message)
        if not ed_date or ed_date is None:
            message = 'Required parameter end date undefined.'
            current_app.logger.info(message)
            raise Exception(message)

        # Get dpa_flag
        if 'dpa_flag' in request.args:
            dpa_flag = to_bool_str(request.args['dpa_flag'])
        else:
            dpa_flag = '0'

        # Get data from uframe.
        data, status_code = get_uframe_plot_contents_chunked_max_data(mooring, platform, instrument, stream_type,
                                                             stream, st_date, ed_date, dpa_flag, parameter_ids,
                                                             number_of_data_points)
        if status_code != 200:
            message = 'Failed to get max streamed data, status code: %d' % status_code
            current_app.logger.info(message)
            raise Exception(message)
        if not data or data is None:
            message = 'No data returned for stream %s and instrument %s.' % (stream[0], instrument[0])
            raise Exception(message)

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        raise Exception(message)

    if debug: print '\n debug -- Step 2 -- have data?, review data......len(data): ', len(data)
    try:
        if data is None or not data or len(data) == 0:
            raise Exception('No data available to process.')

        if 'pk' not in data[0]:
            message = 'Primary information not available'
            current_app.logger.info(message)
            raise Exception(message)

        for xfield in xfields:
            if xfield == 'time':
                if 'time' not in data[0]:
                    message = 'Time variable not available'
                    current_app.logger.info(message)
                    raise Exception(message)
            else:
                if xfield not in data[0]:
                    message = 'Requested data (%s) not available (xfield).' % xfield
                    current_app.logger.info(message)
                    raise Exception(message)

        for yfield in yfields:
            if yfield == 'time':
                if 'time' not in data[0]:
                    message = 'Time variable not available (yfield).'
                    current_app.logger.info(message)
                    raise Exception(message)
            else:
                if yfield not in data[0]:
                    message = 'Requested data (%s) not available (yfield).' % yfield
                    current_app.logger.info(message)
                    raise Exception(message)

        # Initialize the data dicts
        vals = [[] for field in xfields]
        x = OrderedDict(zip(xfields, vals))
        vals = [[] for field in yfields]
        y = OrderedDict(zip(yfields, vals))

        if len(yfields) >= len(xfields):
            qaqc_fields = yfields
        else:
            qaqc_fields = xfields

        # vals = [np.zeros(len(data)) for field in qaqc_fields]
        vals = [[] for field in qaqc_fields]
        qaqc = OrderedDict(zip(qaqc_fields, vals))

        # Loop through rows of data and fill the response data
        for ind, row in enumerate(data):
            # used to handle multiple streams
            if row['pk']['stream'] == stream:
                # x
                for xfield in xfields:
                    if xfield == 'time':
                        x[xfield].append(float(row['time']))
                    else:
                        x[xfield].append(row[xfield])
                        key = xfield + '_qc_results'
                        if key in row:
                            qaqc[xfield].append(int(row[key]))
                        # else:
                        #     current_app.logger.info('QAQC not found for {0}'.format(xfield))
                # y
                for yfield in yfields:
                    if yfield == 'time':
                        y[yfield].append(float(row['time']))
                    else:
                        y[yfield].append(row[yfield])
                        key = yfield + '_qc_results'
                        if key in row:
                            qaqc[yfield].append(int(row[key]))
                        # else:
                        #     current_app.logger.info('QAQC not found for {0}'.format(yfield))

        # generate dict for the data thing
        resp_data = {'x': x,
                     'y': y,
                     'data_length': len(data),
                     'x_field': xfields,
                     'x_units': x_units,
                     'y_field': yfields,
                     'y_units': y_units,
                     'dt_units': 'seconds since 1900-01-01 00:00:00',
                     'qaqc': qaqc
                     }

        return resp_data
    except Exception as err:
        message = str(err)
        if debug: print '\n (controller.py - get_max_data) Exception: %s' % message
        raise Exception(message)