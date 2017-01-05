#!/usr/bin/env python
"""
Mixture of route endpoints and supporting functions.
"""

from flask import (jsonify, request, current_app, make_response)
from ooiservices.app import db
from ooiservices.app.uframe import uframe as api
from ooiservices.app.models import DisabledStreams
from ooiservices.app.main.authentication import auth
from ooiservices.app.main.errors import (internal_server_error, bad_request)
from ooiservices.app.uframe.vocab import get_display_name_by_rd
from ooiservices.app.uframe.config import get_uframe_info
from ooiservices.app.uframe.common_tools import to_bool
from ooiservices.app.uframe.data import (get_data, get_simple_data, find_parameter_ids, get_multistream_data)
from ooiservices.app.uframe.plotting import generate_plot

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


# todo: Move to streams.py
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


# Returns response object for error.
def _response_internal_server_error(msg=None):
    message = json.dumps('"error" : "uframe connection cannot be made."')
    if msg:
        message = json.dumps(msg)
    response = make_response()
    response.content = message
    response.status_code = 500
    response.headers["Content-Type"] = "application/json"
    return response


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
    except Exception as e:
        return internal_server_error('uframe connection cannot be made.' + str(e.message))


@api.route('/get_metadata_parameters/<string:ref>', methods=['GET'])
def get_uframe_instrument_metadata_parameters(ref):
    """ Returns the metadata parameters for a given instrument - all streams.
    """
    results = []
    try:
        mooring, platform, instrument = ref.split('-', 2)
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, mooring, platform, instrument, 'metadata', 'parameters'])
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


@api.route('/get_multistream/<string:stream1>/<string:stream2>/<string:instrument1>/<string:instrument2>/<string:var1>/<string:var2>', methods=['GET'])
def multistream_api(stream1, stream2, instrument1, instrument2, var1, var2):
    """
    Service endpoint to get multistream interpolated data.
    Example request:
        http://localhost:4000/uframe/get_multistream/CP05MOAS-GL340-03-CTDGVM000/CP05MOAS-GL340-02-FLORTM000/telemetered_ctdgv_m_glider_instrument/
        telemetered_flort_m_glider_instrument/sci_water_pressure/sci_flbbcd_chlor_units?startdate=2015-05-07T02:49:22.745Z&enddate=2015-06-28T04:00:41.282Z
    """
    try:
        resp_data, units = get_multistream_data(instrument1, instrument2, stream1, stream2, var1, var2)
    except Exception as err:
        return jsonify(error='%s' % str(err.message)), 400

    header1 = '-'.join([stream1.replace('_', '-'), instrument1.split('_')[0].replace('-', '_'), instrument1.split('_')[1].replace('-', '_')])
    header2 = '-'.join([stream2.replace('_', '-'), instrument2.split('_')[0].replace('-', '_'), instrument2.split('_')[1].replace('-', '_')])

    # Need to reformat the data a bit
    try:
        for ind, data in enumerate(resp_data[header2]):
            resp_data[header1][ind][var2] = data[var2]
        title = get_display_name_by_rd(stream1)
        subtitle = get_display_name_by_rd(stream2)
    except IndexError:
        return jsonify(error='Data Array Length Error'), 500
    except KeyError:
        return jsonify(error='Missing Data in Data Repository'), 500

    return jsonify(data=resp_data[header1], units=units, title=title, subtitle=subtitle)


def get_uframe_multi_stream_contents(stream1_dict, stream2_dict, start_time, end_time):
    """ Gets the data from an interpolated multi stream request.

    Example request:
        http://uframe-test.ooi.rutgers.edu:12576/sensor?r=r1&r=r2&r1.refdes=CP05MOAS-GL340-03-CTDGVM000&
        r2.refdes=CP05MOAS-GL340-02-FLORTM000&r1.method=telemetered&r2.method=telemetered&r1.stream=ctdgv_m_glider_instrument&
        r2.stream=flort_m_glider_instrument&r1.params=PD1527&r2.params=PD1485&limit=1000&startDT=2015-05-07T02:49:22.745Z&endDT=2015-06-28T04:00:41.282Z
    """
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
                 '&r1.stream=%s&r2.stream=%s&r1.params=%s&r2.params=%s&limit=%s&startDT=%s&endDT=%s'
                 % (refdes1, refdes2, method1, method2, stream1, stream2,
                    params1, params2, limit, start_time, end_time))

        _, timeout, timeout_read = get_uframe_info()
        url = "/".join([current_app.config['UFRAME_URL'], query])
        current_app.logger.debug("***:" + url)
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            msg = map_common_error_message(response.text, response.text)
            return msg, 500
        else:
            return response.json(), response.status_code
    except Exception as e:
        return str(e), 500


@auth.login_required
@api.route('/get_csv/<string:stream>/<string:ref>/<string:start_time>/<string:end_time>/<string:dpa_flag>', methods=['GET'])
def get_csv(stream, ref, start_time, end_time, dpa_flag):
    mooring, platform, instrument = ref.split('-', 2)
    stream_type, stream = stream.split('_', 1)

    stream_type = stream_type.replace('-','_')
    stream = stream.replace('-','_')

    # figures out if its in a date time range
    end_time = validate_date_time(start_time, end_time)

    try:
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
    mooring, platform, instrument = ref.split('-', 2)
    stream_type, stream = stream.split('_', 1)

    stream_type = stream_type.replace('-','_')
    stream = stream.replace('-','_')

    # figures out if its in a date time range
    end_time = validate_date_time(start_time, end_time)

    try:
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
    mooring, platform, instrument = ref.split('-', 2)
    stream_type, stream = stream.split('_', 1)

    stream_type = stream_type.replace('-','_')
    stream = stream.replace('-','_')

    try:
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
        join_name ='_'.join([str(instrument), str(stream)])

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
                dpa_flag = "0"
            ed_date = validate_date_time(st_date, ed_date)
            data, status_code = get_uframe_plot_contents_chunked(mooring, platform, instrument, stream_type, stream, st_date, ed_date, dpa_flag, parameter_ids)
        else:
            message = 'Failed to make plot - start end dates not applied'
            current_app.logger.exception(message)
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
            test_request_xvar = junk.encode('ascii','ignore')
            if type(test_request_xvar) == type(''):
                if ',' in test_request_xvar:
                    chunk_request_var = test_request_xvar.split(',',1)
                    if len(chunk_request_var) > 0:
                        request_xvar = chunk_request_var[0]
                else:
                    request_xvar = test_request_xvar
        else:
            message = 'Failed to make plot - no xvar provided in request'
            current_app.logger.exception(message)
            raise Exception(message)
        if not request_xvar:
            message = 'Failed to make plot - unable to process xvar provided in request'
            current_app.logger.exception(message)
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
        # I NEED to CHECK FOR DUPLICATE TIMES !!!!! NOT YET DONE!!!!
        # Start stop times may result in over laps on original data set. (see function above)
        # May be an issue, requires further enquiry
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
        current_app.logger.exception('\n* (pass) exception: ' + str(err.message))


# @auth.login_required
@api.route('/get_profiles/<string:stream>/<string:instrument>', methods=['GET'])
def get_profiles(stream, instrument):
    filename = '-'.join([stream, instrument, "profiles"])
    content_headers = {'Content-Type': 'application/json', 'Content-Disposition': "attachment; filename=%s.json" % filename}
    try:
        profiles = get_profile_data(instrument, stream)
    except Exception as e:
        return jsonify(error=e.message), 400, content_headers
    if profiles is None:
        return jsonify(), 204, content_headers
    return jsonify(profiles=profiles), 200, content_headers


#==============================================================================================
#==============================================================================================
# @auth.login_required
@api.route('/get_data/<string:instrument>/<string:stream>/<string:yvar>/<string:xvar>', methods=['GET'])
def get_data_api(stream, instrument, yvar, xvar):
    # return if error
    debug = False
    try:
        if debug:
            print '\n debug -- Entered controller route: get_data'
            print '\n debug -- instrument: %r ' % instrument
            print '\n debug -- stream: %r ' % stream
            print '\n debug -- yvar: ', yvar
            print '\n debug -- xvar: ', xvar
        xvar = xvar.split(',')
        yvar = yvar.split(',')
        #instrument = instrument.split(',')
        #title = get_display_name_by_rd(instrument[0])
        if instrument and instrument is not None and len(instrument) > 8:
            title = get_display_name_by_rd(instrument)
        else:
            title = instrument
        if debug:
            print '\n debug -- Title: ', title
            print '\n debug -- Calling get_simple_data...'
            print '\n debug -- stream: ', stream
        resp_data, units = get_simple_data(stream, instrument, yvar, xvar)
        if debug:
            print '\n debug -- Exit get_simple_data...'
            print '\n debug -- len(resp_date): ', len(resp_data)
            print '\n debug -- len(units): ', len(units)
            print '\n debug -- title: ', title
            print '\n debug -- units: ', units
        if debug:
            print '\n debug -- Exit controller route: get_data'
        return jsonify(data=resp_data, units=units, title=title)

    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- exception: ', message
        #return jsonify(error='%s' % str(err.message)), 500
        return bad_request(message)


#@auth.login_required
@api.route('/plot/<string:instrument>/<string:stream>', methods=['GET'])
def get_svg_plot(instrument, stream):
    # from ooiservices.app.uframe.controller import split_stream_name
    # Ok first make a list out of stream and instrument
    debug = False
    if debug:
        print '\n debug -- =============================================='
        print '\n debug -- =============================================='
        print '\n debug -- Entered /plot - get_svg_plot...'
        print '\n debug -- instrument: ', instrument
        print '\n debug -- stream: ', stream

    instrument = instrument.split(',')
    #instrument.append(instrument[0])

    stream = stream.split(',')
    #stream.append(stream[0])

    plot_format = request.args.get('format', 'svg')
    # time series vs profile
    plot_layout = request.args.get('plotLayout', 'timeseries')
    if debug: print '\n debug -- plot_layout: ', plot_layout

    xvar = request.args.get('xvar', 'time')
    yvar = request.args.get('yvar', None)

    # There can be multiple variables so get into a list
    xvar = xvar.split(',')
    yvar = yvar.split(',')

    if len(instrument) == len(stream):
        pass # everything the same
    else:
        instrument = [instrument[0]]
        stream = [stream[0]]
        yvar = [yvar[0]]
        xvar = [xvar[0]]

    # create bool from request
    # use_line = to_bool(request.args.get('line', True))
    use_scatter = to_bool(request.args.get('scatter', True))
    use_event = to_bool(request.args.get('event', True))
    qaqc = int(request.args.get('qaqc', 0))

    # Get Events!
    events = {}
    """
    if use_event:
        try:
            response = get_events_by_ref_des(instrument[0])
            events = json.loads(response.data)
        except Exception as err:
            current_app.logger.exception(str(err.message))
            return jsonify(error=str(err.message)), 400
    """

    profileid = request.args.get('profileId', None)

    # need a yvar for sure
    if yvar is None:
        return jsonify(error='Error: yvar is required'), 400

    height = float(request.args.get('height', 100))  # px
    width = float(request.args.get('width', 100))  # px

    # do conversion of the data from pixels to inches for plot
    height_in = height / 96.
    width_in = width / 96.

    # get the data from uFrame
    if debug:
        print '\n Get data from uframe...'
        print '\n debug -- plot_layout: ', plot_layout
    try:
        if plot_layout == "depthprofile":
            data = get_process_profile_data(stream[0], instrument[0], yvar[0], xvar[0])
        else:
            if len(instrument) == 1:
                if debug: print '\n debug -- Branch 1...'
                data = get_data(stream[0], instrument[0], yvar, xvar)
                if not data or data is None:
                    message = 'No data returned for stream %s and instrument %s, y-var: %s and x-var: %s' % \
                              (stream[0], instrument[0], yvar, xvar)
                    raise Exception(message)
            elif len(instrument) > 1:  # Multiple datasets
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
        current_app.logger.exception(str(err))
        return jsonify(error=str(err)), 400

    if not data:
        return jsonify(error='No data returned for %s' % plot_layout), 400


    # return if error
    if 'error' in data or 'Error' in data:
        return jsonify(error=data['error']), 400

    if debug: print '\n debug -- Have data to plot...'
    # generate plot
    some_tuple = ('a', 'b')
    if str(type(data)) == str(type(some_tuple)) and plot_layout == "depthprofile":
        return jsonify(error='tuple data returned for %s' % plot_layout), 400
    if isinstance(data, dict):
        # get title
        if debug: print '\n debug -- (dict) using rd %r to get title or long display name...' % instrument[0]
        # Note: If instrument reference designator is not found in the vocabulary, the reference designator is returned.
        # (This provides a clear indication the instrument has NOT been added to the vocabulary and the COL folks
        # and data team will want to address why it is missing from the vocabulary.)
        title = get_display_name_by_rd(instrument[0])
        if len(title) > 50:
            title = ''.join(title.split('-')[0:-1]) + '\n' + title.split('-')[-1]

        data['title'] = title
        data['height'] = height_in
        data['width'] = width_in
    else:
        for idx, streamx in enumerate(stream):
            if debug: print '\n debug -- (idx loop) using rd %s to get title or long display name...', instrument[0]
            title = get_display_name_by_rd(instrument[idx])
            if len(title) > 50:
                title = ''.join(title.split('-')[0:-1]) + '\n' + title.split('-')[-1]
            data[idx]['title'] = title
            data[idx]['height'] = height_in
            data[idx]['width'] = width_in

    if debug:
        print '\n Preparing plot options...'
        print '\n Before generate plot, data[title]: ', data['title']
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
        buf = generate_plot(data, plot_options)

        content_header_map = {
            'svg' : 'image/svg+xml',
            'png' : 'image/png'
        }

        return buf.read(), 200, {'Content-Type': content_header_map[plot_format]}
    except Exception as err:
        message = 'Error generating {0} plot: {1}'.format(plot_options['plot_layout'], str(err.message))
        current_app.logger.exception(str(err.message))
        return jsonify(error=message), 400


def get_uframe_stream_contents_chunked(mooring, platform, instrument, stream_type, stream,
                                       start_time, end_time, dpa_flag):
    """ Gets the bounded stream contents, start_time and end_time need to be datetime objects.
    """
    debug = False
    try:
        if debug:
            print '\n debug -- ********************************************************************'
            print '\n debug -- Entered get_uframe_stream_contents_chunked...'
            print '\n debug -- dps_flag: ', dpa_flag
        """
        if dpa_flag == '0':
            query = '?beginDT=%s&endDT=%s&user=download' % (start_time, end_time)
        else:
            query = '?beginDT=%s&endDT=%s&user=download&execDPA=true' % (start_time, end_time)
        """
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
                content_length = content_length + CHUNK_SIZE
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
                # all the data is in the resonse return it as normal
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

            return json.loads(dataBlock),200

    except Exception,e:
        #return json.loads(dataBlock), 200
        return internal_server_error('uframe connection unstable.'),500


def get_uframe_plot_contents_chunked(mooring, platform, instrument, stream_type, stream,
                                     start_time, end_time, dpa_flag, parameter_ids):
    """ Gets the bounded stream contents, start_time and end_time need to be datetime objects
    """
    debug = False
    query = ''
    dataBlock = ''
    rd = None
    try:
        if debug:
            print '\n debug --------------------------------------------------------------'
            print '\n debug -- Entered get_uframe_plot_contents_chunked...'
        rd = '-'.join([mooring, platform, instrument])
        if dpa_flag == '0' and len(parameter_ids) < 1:
            if debug: print '\n debug -- Branch A...'
            query = '?beginDT=%s&endDT=%s&limit=%s&user=plotting' % (start_time, end_time, current_app.config['DATA_POINTS'])
        elif dpa_flag == '1' and len(parameter_ids) < 1:
            if debug: print '\n debug -- Branch B...'
            query = '?beginDT=%s&endDT=%s&limit=%s&user=plotting&execDPA=true' % \
                    (start_time, end_time, current_app.config['DATA_POINTS'])
        elif dpa_flag == '0' and len(parameter_ids) > 0:
            if debug: print '\n debug -- Branch C...MODIFIED'
            query = '?beginDT=%s&endDT=%s&limit=%s&parameters=%s&user=plotting' % \
                    (start_time, end_time, current_app.config['DATA_POINTS'], ','.join(parameter_ids))
        elif dpa_flag == '1' and len(parameter_ids) > 0:
            if debug: print '\n debug -- Branch D...'
            query = '?beginDT=%s&endDT=%s&limit=%s&parameters=%s&user=plotting&execDPA=true' % \
              (start_time, end_time, current_app.config['DATA_POINTS'], ','.join(map(str, parameter_ids)))
            # (start_time, end_time, current_app.config['DATA_POINTS'], ','.join(parameter_ids))
        else:
            if debug: print '\n debug -- Branch E...query not defined...'

        GA_URL = current_app.config['GOOGLE_ANALYTICS_URL']+'&ec=plot&ea=%s&el=%s' % \
                 ('-'.join([mooring, platform, instrument, stream_type, stream]), '-'.join([start_time, end_time]))

        UFRAME_DATA = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE']
        url = "/".join([UFRAME_DATA, mooring, platform, instrument, stream_type, stream + query])
        current_app.logger.debug("***: " + url)

        TOO_BIG = 1024 * 1024 * 15 # 15MB
        CHUNK_SIZE = 1024 * 32   #...KB
        TOTAL_SECONDS = current_app.config['UFRAME_PLOT_TIMEOUT']
        dataBlock = ""
        #response = ""
        idx = 0
        t0 = time.time()  # counter

        try:
            with closing(requests.get(url, stream=True)) as response:
                content_length = 0
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    content_length = content_length + CHUNK_SIZE
                    t1 = time.time()
                    total = t1-t0
                    idx += 1
                    if content_length > TOO_BIG:
                        #return 'Data request too large, greater than 15MB', 500
                        message = 'Data request too large, greater than 15MB.'
                        if debug: print '\n debug -- error message: ', message
                        raise Exception(message)
                    if total > TOTAL_SECONDS:
                        #return 'Data request time out', 500
                        message = 'Data request timeout.'
                        if debug: print '\n debug -- error message: ', message
                        raise Exception(message)

                    dataBlock += chunk

                if debug:
                    print '\n debug Step A...'
                    print '\n debug Step A -- type(dataBlock): ', str(type(dataBlock))
                idx_c = dataBlock.rfind('}\n]')
                if debug: print '\n debug Step B...'
                if idx_c == -1:
                    # This is a failure...
                    if debug: print '\n debug Step C...'
                    if debug: print '\n debug Step C -- type(dataBlock): ', str(type(dataBlock))
                    if not dataBlock or dataBlock is None or len(dataBlock) == 0:
                        message = 'No data returned from uframe for request.'
                        if debug: print '\n debug -- error message (not dataBlock or dataBlock is None): ', message
                        raise Exception(message)
                    result = json.loads(dataBlock)
                    #print '\n failure result?: ', result
                    current_app.logger.info(result)
                    # Look for failure...
                    # {u'requestUUID': u'49b32b32-cd04-4a32-8929-0b3e676c4dfe',
                    # u'message': u'Unexpected internal error during request'}
                    if 'message' in result and 'requestUUID' in result:
                        #message = 'uframe error message: ' + result['message'] + ', requestUUID: ' + result['requestUUID']
                        message = 'uframe error message: ' + str(result)
                        raise Exception(message)

                    #dataBlock += ']'
                    #if debug: print '\n debug Step C -- type(dataBlock) after...len(dataBlock): ', len(dataBlock)
                else:
                    if debug:
                        print '\n debug Step D...'
                        print '\n debug -- idx_c != -1: ', idx_c
                # What does this provide regarding google analytics?
                #urllib2.urlopen(GA_URL)
                if debug:
                    print '\n debug Step E...'
                    print '\n debug Step E dataBlock: ', str(type(dataBlock))
                    #print '\n debug Step E dataBlock: ', dataBlock
                result = json.loads(dataBlock)
                if debug: print '\n debug Step F...'
                return json.loads(dataBlock), 200

            if debug: print '\n debug -***** Step 1 -- get_uframe_plot_contents_chunked returning...'
            #raise Exception('No data returned...')

        except Exception as err:
            raise Exception(str(err))

        if debug: print '\n debug -***** Step 2 -- get_uframe_plot_contents_chunked returning...'
        #raise Exception('No data returned...')
        return None, 400

    except ConnectionError:
        message = 'Error: ConnectionError getting uframe plot contents chunked for reference designator: %s' % rd
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Error: Timeout getting uframe plot contents chunked for reference designator: %s' % rd
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as e:
        #msg = map_common_error_message(dataBlock, str(e))
        #return msg, 500
        raise Exception(str(e))