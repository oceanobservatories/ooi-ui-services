#!/usr/bin/env python
'''
uframe endpoints

'''
__author__ = 'Andy Bird'
#base
from flask import (jsonify, request, current_app, url_for, Flask, make_response,
                   url_for, Response)
from ooiservices.app import db, cache, celery
from ooiservices.app.uframe import uframe as api
from ooiservices.app.models import (Array, PlatformDeployment,
                                    InstrumentDeployment, Stream,
                                    StreamParameter, Organization,
                                    Instrumentname, Annotation)
from ooiservices.app.main.authentication import auth,verify_auth
from ooiservices.app.main.errors import internal_server_error
from urllib import urlencode
# data ones
from ooiservices.app.uframe.data import get_data, COSMO_CONSTANT
from ooiservices.app.uframe.plotting import generate_plot
from ooiservices.app.uframe.assetController import get_events_by_ref_des
from datetime import datetime
from dateutil.parser import parse as parse_date
import requests
# primarily for encoding coordinates to GeoJSON
from geojson import LineString
#additional ones
import json
import datetime
import math
import csv
import io
import numpy as np
import pytz
from ooiservices.app.main.routes import get_display_name_by_rd
from ooiservices.app.main.arrays import get_arrays, get_array
from contextlib import closing
import time 
from ooiservices.app.models import PlatformDeployment

def dfs_streams():
    response = get_uframe_moorings()
    if response.status_code != 200:
        current_app.logger.error("Failed to get a valid response from uframe")
        raise IOError('Failed to get response from uFrame')
    mooring_list = response.json()
    platforms = []
    for mooring in mooring_list:
        if 'VALIDATE' in mooring:
            continue  # Don't know what this is, but we don't want it
        response = get_uframe_platforms(mooring)
        if response.status_code != 200:
            continue
        
        platform_tmp = [(mooring, p) for p in response.json()]
        platforms.extend(platform_tmp)

    instruments = []
    for platform in platforms:
        response = get_uframe_instruments(*platform)
        if response.status_code != 200:
            continue
        instrument_tmp = [platform + (i,) for i in response.json()]
        instruments.extend(instrument_tmp)

    stream_types = []
    for instrument in instruments:
        response = get_uframe_stream_types(*instrument)
        if response.status_code != 200:
            continue

        stream_tmp = [instrument + (s,) for s in response.json()]
        stream_types.extend(stream_tmp)

    streams = []
    for stream_type in stream_types:
        response = get_uframe_streams(*stream_type)
        if response.status_code != 200:
            continue

        stream_tmp = [stream_type + (s,) for s in response.json()]
        streams.extend(stream_tmp)
    return streams


def split_stream_name(ui_stream_name):
    '''
    Splits the hypenated reference designator and stream type into a tuple of
    (mooring, platform, instrument, stream_type, stream)
    '''
    mooring, platform, instrument = ui_stream_name.split('-', 2)
    instrument, stream_type, stream = instrument.split('_', 2)
    return (mooring, platform, instrument, stream_type, stream)


def combine_stream_name(mooring, platform, instrument, stream_type, stream):
    first_part = '-'.join([mooring, platform, instrument])
    all_of_it = '_'.join([first_part, stream_type, stream])
    return all_of_it


def iso_to_timestamp(iso8601):
    dt = parse_date(iso8601)
    t = (dt - datetime(1970, 1, 1, tzinfo=pytz.utc)).total_seconds()
    return t

def dict_from_stream(mooring, platform, instrument, stream_type, stream):
    HOST = str(current_app.config['HOST'])
    PORT = str(current_app.config['PORT'])
    SERVICE_LOCATION = 'http://'+HOST+":"+PORT
    ref = mooring + "-" + platform + "-" + instrument
    response = get_uframe_stream_metadata_times(ref)    

    stream_name = '_'.join([stream_type, stream])
    ref = '-'.join([mooring, platform, instrument])
    if response.status_code != 200:
        raise IOError("Failed to get stream contents from uFrame")
    data = response.json()
    data_dict = {}
    #sort out the start and end times, as multiple times in a given metadata set
    if len(data) == 1:   
        data_dict['start'] = data[0]['beginTime']
        data_dict['end'] = data[0]['endTime']
    else:
        for times in data:
            if times['method'] == stream_type and times['stream'] == stream:               
                data_dict['start'] = times['beginTime']
                data_dict['end'] = times['endTime']

    data_dict['reference_designator'] = data[0]['sensor']
    data_dict['stream_name'] = stream_name
    data_dict['variables'] = []
    data_dict['variable_types'] = {}
    data_dict['units'] = {}
    data_dict['variables_shape'] = {}
    data_dict['display_name'] = get_display_name_by_rd(ref)
    data_dict['download'] = {
                             "csv":"/".join([SERVICE_LOCATION, 'uframe/get_csv', stream_name, ref]),
                             "json":"/".join([SERVICE_LOCATION, 'uframe/get_json', stream_name, ref]),
                             "netcdf":"/".join([SERVICE_LOCATION, 'uframe/get_netcdf', stream_name, ref]),
                             "profile":"/".join([SERVICE_LOCATION, 'uframe/get_profiles', stream_name, ref])
                            }
    '''
    d = get_uframe_instrument_metadata(ref)
    if d.status_code == 200:                    
        data1 = d.get_data()
        data1 = json.loads(data1)
        data1 = data1['metadata']
        if len(data)>0:            
            for field in data1:
                if field['particleKey'] not in data_dict['variables']: 
                    if field['shape'].lower() == 'scalar' or field['shape'].lower() == 'function':  
                        data_dict['variables'].append(field['particleKey'])
                        data_dict['variable_types'][field['particleKey']] = field['type'].lower()           
                        data_dict['units'][field['particleKey']] = field['units']
                        data_dict['variables_shape'][field['particleKey']]= field['shape'].lower()    
    '''
    d = get_uframe_instrument_metadata_parameters(ref)
    if d.status_code == 200:
        data1 = json.loads(d.content)
        if len(data1)>0:
            for field in data1:
                if field['particleKey'] not in data_dict['variables']:
                    if field['shape'].lower() == 'scalar' or field['shape'].lower() == 'function':
                        data_dict['variables'].append(field['particleKey'])
                        data_dict['variable_types'][field['particleKey']] = field['type'].lower()
                        data_dict['units'][field['particleKey']] = field['units']
                        data_dict['variables_shape'][field['particleKey']]= field['shape'].lower()
    return data_dict


@api.route('/stream')
#@auth.login_required
def streams_list():
    '''
    Accepts stream_name or reference_designator as a URL argument
    '''
    if request.args.get('stream_name'):
        try:
            dict_from_stream(request.args.get('stream_name'))
        except Exception as e:
            current_app.logger.exception('**** (1) exception: ' + e.message)
            return jsonify(error=e.message), 500
    try:
        streams = dfs_streams()
    except Exception as e:
        current_app.logger.exception('**** (2) exception: ' + e.message)
        return jsonify(error=e.message), 500

    retval = []
    for stream in streams:
        try:
            data_dict = dict_from_stream(*stream)
        except Exception as e:
            current_app.logger.exception('\n**** (3) exception: ' + e.message)
            continue
        if request.args.get('reference_designator'):
            if request.args.get('reference_designator') != data_dict['reference_designator']:
                continue

        retval.append(data_dict)

    return jsonify(streams=retval)


#@cache.memoize(timeout=3600)
def get_uframe_moorings():
    '''
    Lists all the streams
    '''
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        current_app.logger.info("GET %s", uframe_url)
        response = requests.get(uframe_url, timeout=(timeout, timeout_read))
        return response
    except Exception as e:
        return _response_internal_server_error()

#@cache.memoize(timeout=3600)
def get_uframe_platforms(mooring):
    '''
    Lists all the streams
    '''
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, mooring])
        current_app.logger.info("GET %s", uframe_url)
        response = requests.get(url, timeout=(timeout, timeout_read))
        return response
    except Exception as e:
        return _response_internal_server_error()

@auth.login_required
@api.route('/get_glider_track/<string:ref>')
def get_uframe_glider_track(ref):
    '''
    Given a reference designator, returns a GeoJSON LineString for glider
    tracks
    '''
    # we will always want the telemetered data, and the engineering stream
    # data should reside in the same place
    res = get_json('telemetered_glider_eng_telemetered', ref)
    try:
        if res.status_code == 200:
            res_arr = json.loads(res.data)['data']
            # load the JSON into a shapely LineString.
            track = LineString([(pt['m_gps_lon'], pt['m_gps_lat'])
                                for pt in res_arr if pt['m_gps_lon'] != 'NaN'
                                and pt['m_gps_lat'] != 'NaN'])
            # serialize the Python object of containing tracks to GeoJSON
            return Response(json.dumps(track),
                            mimetype='application/json')
        else:
            # if not a valid response, attempt to return the response as is.
            return Response(json.dumps({'type': "LineString",'coordinates':[],'note':'invalid status code'}),
                            mimetype='application/json')
            #return res.text, res.status_code, res.headers.items()
    except AttributeError:
        #return nothing
        return Response(json.dumps({'type': "LineString",'coordinates':[],'note':'AttributeError'}),
                            mimetype='application/json')

#@cache.memoize(timeout=3600)
def get_uframe_instruments(mooring, platform):
    '''
    Lists all the streams
    '''
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, mooring, platform])
        current_app.logger.info("GET %s", url)
        response = requests.get(url, timeout=(timeout, timeout_read))
        return response
    except Exception as e:
        #return internal_server_error('uframe connection cannot be made.' + str(e.message))
        return _response_internal_server_error()

#@cache.memoize(timeout=3600)
def get_uframe_stream_types(mooring, platform, instrument):
    '''
    Lists all the stream types
    '''
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = '/'.join([uframe_url, mooring, platform, instrument])
        current_app.logger.info("GET %s", url)
        response = requests.get(url, timeout=(timeout, timeout_read))
        return response
    except Exception as e:
        #return internal_server_error('uframe connection cannot be made. error: %s' %  + str(e.message))
        return _response_internal_server_error()

#@cache.memoize(timeout=3600)
def get_uframe_streams(mooring, platform, instrument, stream_type):
    '''
    Lists all the streams
    '''
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = '/'.join([uframe_url, mooring, platform, instrument, stream_type])
        current_app.logger.info("GET %s", url)
        response = requests.get(url, timeout=(timeout, timeout_read))
        return response
    except Exception as e:
        return internal_server_error('uframe connection cannot be made.' + str(e.message))


#@cache.memoize(timeout=3600)
def get_uframe_stream(mooring, platform, instrument, stream):
    '''
    Lists the reference designators for the streams
    '''
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, mooring, platform, instrument, stream])
        current_app.logger.info("GET %s", url)
        response = requests.get(url, timeout=(timeout, timeout_read))
        return response
    except Exception as e:
        #return internal_server_error('uframe connection cannot be made.' + str(e.message))
        return _response_internal_server_error()

def get_uframe_toc():
    uframe_url = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_TOC']
    r = requests.get(uframe_url)
    if r.status_code == 200:
        d =  r.json()
        for row in d:
            try:
                instrument_display_name = PlatformDeployment._get_display_name(row['reference_designator'])
                split_name = instrument_display_name.split(' - ')
                row['instrument_display_name'] = split_name[-1]
                row['platform_display_name'] = split_name[0]           
                row['mooring_display_name'] = split_name[1]
            except:
                row['instrument_display_name'] = ""
                row['platform_display_name'] = ""
                row['mooring_display_name'] = ""            
        return d
    else:
        return []


@api.route('/get_toc')
@cache.memoize(timeout=1600)
def get_toc():
    try:
        data = get_uframe_toc()
        return jsonify(toc=data)
    except Exception as e:
        return internal_server_error('uframe connection cannot be made.' + str(e.message))

@api.route('/get_instrument_metadata/<string:ref>', methods=['GET'])
#@cache.memoize(timeout=3600)
def get_uframe_instrument_metadata(ref):
    '''
    Returns the uFrame metadata response for a given stream
    '''    
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
#@cache.memoize(timeout=3600)
def get_uframe_instrument_metadata_parameters(ref):
    '''
    Returns the uFrame metadata parameters for a given stream
    '''
    try:
        mooring, platform, instrument = ref.split('-', 2)
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, mooring, platform, instrument, 'metadata', 'parameters'])
        #current_app.logger.info("GET %s", url)
        response = requests.get(url, timeout=(timeout, timeout_read))
        return response
    except:
        return _response_internal_server_error()

def _response_internal_server_error(msg=None):
    message = json.dumps('"error" : "uframe connection cannot be made."')
    if msg:
        message = json.dumps(msg)
    response = make_response()
    response.content = message
    response.status_code = 500
    response.headers["Content-Type"] = "application/json"
    return response

@auth.login_required
@api.route('/get_metadata_times/<string:ref>', methods=['GET'])
#@cache.memoize(timeout=3600)
def get_uframe_stream_metadata_times(ref):
    '''
    Returns the uFrame time bounds response for a given stream
    '''
    mooring, platform, instrument = ref.split('-', 2)
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, mooring, platform, instrument, 'metadata','times'])
        #current_app.logger.info("GET %s", url)
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code == 200:
            return response
        return jsonify(times={}), 200
    except Exception as e:
        return internal_server_error('uframe connection cannot be made.' + str(e.message))

#@cache.memoize(timeout=3600)
def get_uframe_stream_contents(mooring, platform, instrument, stream_type, stream, start_time, end_time, dpa_flag):
    """
    Gets the bounded stream contents, start_time and end_time need to be datetime objects; returns Respnse object.
    """
    try:        
        if dpa_flag == '0':
            query = '?beginDT=%s&endDT=%s' % (start_time, end_time)
        else:
            query = '?beginDT=%s&endDT=%s&execDPA=true' % (start_time, end_time)
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, mooring, platform, instrument, stream_type, stream + query])
        current_app.logger.debug('***** url: ' + url)
        response = requests.get(url, timeout=(timeout, timeout_read))
        if not response:
            raise Exception('No data available from uFrame for this request.')
        if response.status_code != 200:
            raise Exception('(%s) failed to retrieve stream contents from uFrame', response.status_code)
            #pass
        return response
    except Exception as e:
        return internal_server_error('uFrame connection cannot be made. ' + str(e.message))

def get_uframe_stream_contents_chunked(mooring, platform, instrument, stream_type, stream, start_time, end_time, dpa_flag):
    '''
    Gets the bounded stream contents, start_time and end_time need to be datetime objects
    '''
    try:        
        if dpa_flag == '0':
            query = '?beginDT=%s&endDT=%s' % (start_time, end_time)
        else:
            query = '?beginDT=%s&endDT=%s&execDPA=true' % (start_time, end_time)
        UFRAME_DATA = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE']
        url = "/".join([UFRAME_DATA,mooring, platform, instrument, stream_type, stream + query])     
        
        print "***:",url

        TOO_BIG = 1024 * 1024 * 15 # 15MB
        CHUNK_SIZE = 1024 * 32   #...KB
        TOTAL_SECONDS = 20
        dataBlock = ""
        idx = 0
      
        #counter
        t0 = time.time()

        with closing(requests.get(url,stream=True)) as response:
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
                    dataBlock+="}]" 
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

            return json.loads(dataBlock),200            
        
    except Exception,e: 
        #return json.loads(dataBlock), 200
        return internal_server_error('uframe connection unstable.'),500

def get_uframe_info():
    '''
    returns uframe configuration information. (uframe_url, uframe timeout_connect and timeout_read.)
    '''
    uframe_url = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE']
    timeout = current_app.config['UFRAME_TIMEOUT_CONNECT']
    timeout_read = current_app.config['UFRAME_TIMEOUT_READ']
    return uframe_url, timeout, timeout_read


def validate_date_time(start_time, end_time):
    uframe_data_request_limit = int(current_app.config['UFRAME_DATA_REQUEST_LIMIT'])/1440
    new_end_time_strp = datetime.datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S.%fZ") + datetime.timedelta(days=uframe_data_request_limit)
    old_end_time_strp = datetime.datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S.%fZ") 
    new_end_time = datetime.datetime.strftime(new_end_time_strp, "%Y-%m-%dT%H:%M:%S.%fZ")
    if old_end_time_strp > new_end_time_strp:
        end_time = new_end_time
    return end_time


@auth.login_required
@api.route('/get_csv/<string:stream>/<string:ref>/<string:start_time>/<string:end_time>/<string:dpa_flag>',methods=['GET'])
def get_csv(stream, ref,start_time,end_time,dpa_flag):
    mooring, platform, instrument = ref.split('-', 2)
    stream_type, stream = stream.split('_', 1)
    
    #figures out if its in a date time range
    end_time = validate_date_time(start_time, end_time)
    data = get_uframe_stream_contents(mooring, platform, instrument, stream_type, stream, start_time, end_time, dpa_flag)
    if data.status_code != 200:
        return data, data.status_code, dict(data.headers)

    output = io.BytesIO()
    data = data.json()
    f = csv.DictWriter(output, fieldnames = data[0].keys())
    f.writeheader()
    for row in data:
        f.writerow(row)

    filename = '-'.join([stream, ref])

    buf = output.getvalue()
    returned_csv = make_response(buf)
    returned_csv.headers["Content-Disposition"] = "attachment; filename=%s.csv" % filename
    returned_csv.headers["Content-Type"] = "text/csv"

    output.close()
    return returned_csv


@auth.login_required
@api.route('/get_json/<string:stream>/<string:ref>/<string:start_time>/<string:end_time>/<string:dpa_flag>',methods=['GET'])
def get_json(stream,ref,start_time,end_time,dpa_flag):
    mooring, platform, instrument = ref.split('-', 2)
    stream_type, stream = stream.split('_', 1)

    #figures out if its in a date time range
    end_time = validate_date_time(start_time, end_time)

    data = get_uframe_stream_contents(mooring, platform, instrument, stream_type, stream, start_time, end_time, dpa_flag)

    if data.status_code != 200:
        return data, data.status_code, dict(data.headers)
    response = '{"data":%s}' % data.content
    filename = '-'.join([stream,ref])
    returned_json = make_response(response)
    returned_json.headers["Content-Disposition"] = "attachment; filename=%s.json"%filename
    returned_json.headers["Content-Type"] = "application/json"
    return returned_json

@auth.login_required
@api.route('/get_netcdf/<string:stream>/<string:ref>/<string:start_time>/<string:end_time>/<string:dpa_flag>', methods=['GET'])
def get_netcdf(stream, ref,start_time,end_time,dpa_flag):
    mooring, platform, instrument = ref.split('-', 2)
    stream_type, stream = stream.split('_', 1)
    uframe_url, timeout, timeout_read = get_uframe_info()
    url = '/'.join([uframe_url, mooring, platform, instrument, stream_type, stream, start_time, end_time, dpa_flag])
    NETCDF_LINK = url+'?format=application/netcdf'
    response = requests.get(NETCDF_LINK, timeout=(timeout, timeout_read))
    if response.status_code != 200:
        return response.text, response.status_code

    filename = '-'.join([stream, ref])
    buf = response.content
    returned_netcdf = make_response(buf)
    returned_netcdf.headers["Content-Disposition"] = "attachment; filename=%s.nc" % filename
    returned_netcdf.headers["Content-Type"] = "application/x-netcdf"

    return returned_netcdf

@auth.login_required
@api.route('/get_data/<string:instrument>/<string:stream>/<string:yvar>/<string:xvar>', methods=['GET'])
def get_data_api(stream, instrument, yvar, xvar):
    # return if error
    try:
        resp_data = get_data(stream, instrument, yvar, xvar)
    except Exception as err:
        return jsonify(error='%s' % str(err.message)), 400

    return jsonify(resp_data)

@auth.login_required
@api.route('/plot/<string:instrument>/<string:stream>', methods=['GET'])
def get_svg_plot(instrument, stream):
    # from ooiservices.app.uframe.controller import split_stream_name

    # Ok first make a list out of stream and instrument
    instrument = instrument.split(',')
    #instrument.append(instrument[0])

    stream = stream.split(',')
    #stream.append(stream[0])

    plot_format = request.args.get('format', 'svg')
    # time series vs profile
    plot_layout = request.args.get('plotLayout', 'timeseries')
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

    # Get Events!
    events = {}
    if use_event:
        try:
            response = get_events_by_ref_des(instrument[0])
            events = json.loads(response.data)
        except Exception as err:
            current_app.logger.exception(str(err.message))
            return jsonify(error=str(err.message)), 400

    # get titles and labels
    title = request.args.get('title', '%s Data' % stream[0])
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
    try:
        if plot_layout == "depthprofile":
            data = get_process_profile_data(stream, instrument, yvar[0], xvar[0])
        else:
            if len(instrument) == 1:
                data = get_data(stream[0], instrument[0], yvar, xvar)
            elif len(instrument) > 1:  # Multiple datasets
                data = []
                for idx, instr in enumerate(instrument):
                    stream_data = get_data(stream[idx], instr, [yvar[idx]], [xvar[idx]])
                    data.append(stream_data)

    except Exception as err:
        current_app.logger.exception(str(err.message))
        return jsonify(error=str(err.message)), 400

    if not data:
        return jsonify(error='No data returned for %s' % plot_layout), 400

    # return if error
    if 'error' in data or 'Error' in data:
        return jsonify(error=data['error']), 400

    # generate plot
    some_tuple = ('a', 'b')
    if str(type(data)) == str(type(some_tuple)) and plot_layout == "depthprofile":
        return jsonify(error='tuple data returned for %s' % plot_layout), 400
    if isinstance(data, dict):
        data['title'] = title
        data['height'] = height_in
        data['width'] = width_in
    else:
        for idx, streamx in enumerate(stream):
            data[idx]['title'] = streamx
            data[idx]['height'] = height_in
            data[idx]['width'] = width_in

    buf = generate_plot(data,
                        plot_format,
                        plot_layout,
                        use_scatter,
                        events,
                        profileid,
                        width_in=width_in)

    content_header_map = {
        'svg' : 'image/svg+xml',
        'png' : 'image/png'
    }

    return buf.read(), 200, {'Content-Type': content_header_map[plot_format]}


def get_process_profile_data(stream, instrument, yvar, xvar):

    # get profile data
    try:
        data = get_profile_data(instrument, stream)
        if not data or data == None:
            raise Exception('profiles not present in data')
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


def get_profile_data(instrument, stream):
    '''
    process uframe data into profiles
    '''
    try:
        data = []
        mooring, platform, instrument, stream_type, stream = split_stream_name('_'.join([instrument, stream]))
        if 'startdate' in request.args and 'enddate' in request.args:
            st_date = request.args['startdate']
            ed_date = request.args['enddate']
            if 'dpa_flag' in request.args:
                dpa_flag = request.args['dpa_flag']
            else:
                dpa_flag = "0"
            ed_date = validate_date_time(st_date, ed_date)
            data, status_code = get_uframe_stream_contents_chunked(mooring, platform, instrument, stream_type, stream, st_date, ed_date, dpa_flag)
        else:
            message = 'Failed to make plot - start end dates not applied'
            current_app.logger.exception(message)
            raise Exception(message)

        if status_code != 200:
            raise IOError("uFrame unable to get data for this request.")

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
            #return {'error': 'Unable to determine where slope changes.'}
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
        current_app.logger.exception('\n***** (pass) exception: ' + str(err.message))
        pass

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

def make_cache_key():
    return urlencode(request.args)

def to_bool(value):
    """
       Converts 'something' to boolean. Raises exception for invalid formats
           Possible True  values: 1, True, "1", "TRue", "yes", "y", "t"
           Possible False values: 0, False, None, [], {}, "", "0", "faLse", "no", "n", "f", 0.0, ...
    """
    if str(value).lower() in ("yes", "y", "true",  "t", "1"):
        return True
    if str(value).lower() in ("no",  "n", "false", "f", "0", "0.0", "", "none", "[]", "{}"):
        return False
    raise Exception('Invalid value for boolean conversion: ' + str(value))
