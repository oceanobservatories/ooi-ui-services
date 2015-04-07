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
            return jsonify(error=e.message), 500

    streams = dfs_streams()

    retval = []
    for stream in streams:
        try:
            data_dict = dict_from_stream(*stream)
        except Exception as e:
            continue
        if request.args.get('reference_designator'):
            if request.args.get('reference_designator') != data_dict['reference_designator']:
                continue

        retval.append(data_dict)

    return jsonify(streams=retval)


@cache.memoize(timeout=3600)
def get_uframe_moorings():
    '''
    Lists all the streams
    '''
    try:
        UFRAME_DATA = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE']
        current_app.logger.info("GET %s", UFRAME_DATA)
        timeout = current_app.config['UFRAME_TIMEOUT_CONNECT']
        timeout_read = current_app.config['UFRAME_TIMEOUT_READ']
        response = requests.get(UFRAME_DATA, timeout=(timeout, timeout_read))
        return response
    except:
        return internal_server_error('uframe connection cannot be made.')


@cache.memoize(timeout=3600)
def get_uframe_platforms(mooring):
    '''
    Lists all the streams
    '''
    try:
        UFRAME_DATA = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE'] + '/' + mooring
        current_app.logger.info("GET %s", UFRAME_DATA)
        timeout = current_app.config['UFRAME_TIMEOUT_CONNECT']
        timeout_read = current_app.config['UFRAME_TIMEOUT_READ']
        response = requests.get(UFRAME_DATA, timeout=(timeout, timeout_read))
        return response
    except:
        return internal_server_error('uframe connection cannot be made.')

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

@cache.memoize(timeout=3600)
def get_uframe_instruments(mooring, platform):
    '''
    Lists all the streams
    '''
    try:
        UFRAME_DATA = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE'] + '/' + mooring + '/' + platform
        current_app.logger.info("GET %s", UFRAME_DATA)
        timeout = current_app.config['UFRAME_TIMEOUT_CONNECT']
        timeout_read = current_app.config['UFRAME_TIMEOUT_READ']
        response = requests.get(UFRAME_DATA, timeout=(timeout, timeout_read))
        return response
    except:
        return internal_server_error('uframe connection cannot be made.')


@cache.memoize(timeout=3600)
def get_uframe_stream_types(mooring, platform, instrument):
    '''
    Lists all the streams
    '''
    try:
        UFRAME_DATA = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE']
        current_app.logger.info("GET %s", '/'.join([UFRAME_DATA, mooring, platform, instrument]))
        url = '/'.join([UFRAME_DATA, mooring, platform, instrument])
        timeout = current_app.config['UFRAME_TIMEOUT_CONNECT']
        timeout_read = current_app.config['UFRAME_TIMEOUT_READ']
        response = requests.get(url, timeout=(timeout, timeout_read))
        return response
    except Exception, err:
        return internal_server_error('uframe connection cannot be made. error: %s' % err.message)


@cache.memoize(timeout=3600)
def get_uframe_streams(mooring, platform, instrument, stream_type):
    '''
    Lists all the streams
    '''
    try:
        UFRAME_DATA = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE']

        url = '/'.join([UFRAME_DATA, mooring, platform, instrument, stream_type])
        timeout = current_app.config['UFRAME_TIMEOUT_CONNECT']
        timeout_read = current_app.config['UFRAME_TIMEOUT_READ']
        response = requests.get(url, timeout=(timeout, timeout_read))
        current_app.logger.info("GET %s", '/'.join([UFRAME_DATA, mooring, platform, instrument, stream_type]))
        return response
    except:
        return internal_server_error('uframe connection cannot be made.')


@cache.memoize(timeout=3600)
def get_uframe_stream(mooring, platform, instrument, stream):
    '''
    Lists the reference designators for the streams
    '''
    try:
        UFRAME_DATA = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE']
        current_app.logger.info("GET %s", "/".join([UFRAME_DATA,mooring, platform, instrument, stream]))
        url = "/".join([UFRAME_DATA,mooring, platform, instrument, stream])
        timeout = current_app.config['UFRAME_TIMEOUT_CONNECT']
        timeout_read = current_app.config['UFRAME_TIMEOUT_READ']
        response = requests.get(url, timeout=(timeout, timeout_read))
        return response
    except:
        return internal_server_error('uframe connection cannot be made.')

@api.route('/get_toc')
@cache.memoize(timeout=3600)
def get_toc():
    '''
    Returns a table of contents based on the uFrame contents
    '''

    example_toc_response = {
      "arrays": [
                  {
                    "id":"CP",
                    "display_name":"CP",
                    "geojson":""
                  },
                  {
                    "id":"CE",
                    "display_name":"CE",
                    "geojson":"",
                  }
                ],
      "moorings":[
                    {
                     "id":"05MOAS",
                     "array_id":"CP",
                     "display_name":"05 mobile assest",
                     "geojson":"",
                     },
                 ],
      "platforms":[
                    {
                      "id":"GL004",
                      "mooring_id":"SMMFD35",
                      "display_name":"Coastal Pioneer glider 004",
                      "geojson":"",
                    },
                  ],
      "instruments":
        [
          {
            "geojson":"<point/line>",
            "array_id":"CP",
            "platform_id":"CP01",
            "mooring_id":"SMMFD35",
            "display_name":"",
            "instrument_id":"00-ENG000000",
            "ref_des":"CP-05MOAS-GL004-00-ENG000000",
            "instrument_parameters": [
                                      "message_sent_timestamp",
                                      "bad_records",
                                      "internal_timestamp",
                                      "driver_timestamp",
                                      "preferred_timestamp",
                                      "header_timestamp"
                                      ],
            "streams": [
              {
                "beginTime": "2014-11-06T20:34:31.666Z",
                "count": 1734,
                "endTime": "2014-12-14T21:04:36.668Z",
                "method": "telemetered",
                "sensor": "CP01CNSM-MFD35-00-DCLENG000",
                "stream": "cg_dcl_eng_dcl_cpu_uptime"
              },
              {
                "beginTime": "2014-11-06T20:34:31.886Z",
                "count": 1734,
                "endTime": "2014-12-14T21:04:36.941Z",
                "method": "telemetered",
                "sensor": "CP01CNSM-MFD35-00-DCLENG000",
                "stream": "cg_dcl_eng_dcl_dlog_mgr"
              }]
          }
        ]
    }
    UFRAME_DATA = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE']

    try:
        url = "/".join([UFRAME_DATA])
        response = requests.get(url)
        if response.status_code == 200:
            moorings = response.json()

            toc = {}
            mooring_list = []
            platform_list = []
            instrument_list = []

            for mooring in moorings:
                mooring_list.append({'reference_designator': mooring,
                                     'array_code': mooring[:2],
                                     'display_name': get_display_name_by_rd(mooring),
                                     'geo_location': {'coordinates':[0,0],'type':'Point'}
                                     })

            # for mooring in moorings:
                url = "/".join([UFRAME_DATA, mooring])
                response = requests.get(url)
                if response.status_code == 200:
                    platforms = response.json()


                    for platform in platforms:
                        pd = PlatformDeployment.query.filter_by(reference_designator="-".join([mooring, platform])).first()
                        pos = 'null'
                        if pd:
                            print pd
                            print pd.geojson
                            pos = pd.geojson

                        platform_list.append({'reference_designator': "-".join([mooring, platform]),
                                              'mooring_code': mooring,
                                              'platform_code': platform,
                                              'display_name': get_display_name_by_rd("-".join([mooring, platform])),
                                              # 'geo_location': {'coordinates':[0,0],'type':'Point'}
                                              'geo_location': pos
                                              })

                    # for platform in platforms:
                        url = "/".join([UFRAME_DATA, mooring, platform])
                        response = requests.get(url)
                        if response.status_code == 200:
                            instruments = response.json()



                            for instrument in instruments:
                                url = "/".join([UFRAME_DATA, mooring, platform, instrument, 'metadata'])
                                response = requests.get(url)
                                if response.status_code == 200:
                                    instrument_metadata = response.json()
                                    instrument_parameters = instrument_metadata['parameters']
                                    parameters = []
                                    for ip in instrument_parameters:
                                        pk = ip['particleKey']
                                        parameters.append(pk)

                                    instrument_streams = instrument_metadata['times']

                                    instrument_list.append({'mooring_code': mooring,
                                                            'platform_code': platform,
                                                            'instrument_code': instrument,
                                                            'reference_designator': "-".join([mooring, platform, instrument]),
                                                            'display_name': get_display_name_by_rd("-".join([mooring, platform, instrument])),
                                                            'instrument_parameters': parameters,
                                                            'streams': instrument_streams
                                                            })


                                    # Build the TOC
                                    #toc["-".join([mooring, platform, instrument])] = {'mooring':mooring, 'platform':platform, 'instrument':instrument, 'instrument_parameters': parameters, 'streams': instrument_times}
                    arrays = Array.query.all()
                    toc['arrays'] = [array.to_json() for array in arrays]
                    toc['moorings'] = mooring_list
                    toc['platforms'] = platform_list
                    toc['instruments'] = instrument_list

            return jsonify(toc=toc)
        return jsonify(toc={}), 404

    except Exception as ex:
        return internal_server_error('uframe connection cannot be made.' + str(ex.message))

@api.route('/get_instrument_metadata/<string:ref>', methods=['GET'])
@cache.memoize(timeout=3600)
def get_uframe_instrument_metadata(ref):
    '''
    Returns the uFrame metadata response for a given stream
    '''    
    try:
        mooring, platform, instrument = ref.split('-', 2)

        UFRAME_DATA = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE']
        url = "/".join([UFRAME_DATA, mooring, platform, instrument, 'metadata'])        
  
        response = requests.get(url)      
        if response.status_code == 200:
            data = response.json()
            return jsonify(metadata=data['parameters'])
        return jsonify(metadata={}), 404
    except Exception,e:        
        return internal_server_error('uframe connection cannot be made.')

@auth.login_required
@api.route('/get_metadata_times/<string:ref>', methods=['GET'])
@cache.memoize(timeout=3600)
def get_uframe_stream_metadata_times(ref):
    '''
    Returns the uFrame time bounds response for a given stream
    '''
    mooring, platform, instrument = ref.split('-', 2)
    try:
        UFRAME_DATA = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE']
        response = requests.get("/".join([UFRAME_DATA, mooring, platform, instrument, 'metadata','times']))
        if response.status_code == 200:
            return response
        return jsonify(times={}), 200
    except:
        return internal_server_error('uframe connection cannot be made.')

@cache.memoize(timeout=3600)
def get_uframe_stream_contents(mooring, platform, instrument, stream_type, stream, start_time, end_time, dpa_flag):
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
        # print url
        response =  requests.get(url)
        if response.status_code != 200:
            #print response.text
            pass
        return response
    except:
        return internal_server_error('uframe connection cannot be made.')


def validate_date_time(start_time,end_time):
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
@api.route('/get_netcdf/<string:stream>/<string:ref>', methods=['GET'])
def get_netcdf(stream, ref):
    mooring, platform, instrument = ref.split('-', 2)
    stream_type, stream = stream.split('_', 1)
    UFRAME_DATA = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE']
    url = '/'.join([UFRAME_DATA, mooring, platform, instrument, stream_type, stream])
    NETCDF_LINK = url+'?format=application/netcdf'

    timeout = current_app.config['UFRAME_TIMEOUT_CONNECT']
    timeout_read = current_app.config['UFRAME_TIMEOUT_READ']
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
    return jsonify(**get_data(stream, instrument, yvar, xvar))


@auth.login_required
@api.route('/plot/<string:instrument>/<string:stream>', methods=['GET'])
def get_svg_plot(instrument, stream):
    plot_format = request.args.get('format', 'svg')

    # time series vs profile
    plot_layout = request.args.get('plotLayout', 'timeseries')
    xvar = request.args.get('xvar', 'time')
    yvar = request.args.get('yvar', None)

    # There can be multiple variables so get into a list
    xvar = xvar.split(',')
    yvar = yvar.split(',')

    # create bool from request
    use_line = to_bool(request.args.get('line', True))
    use_scatter = to_bool(request.args.get('scatter', True))

    # get titles and labels
    title = request.args.get('title', '%s Data' % stream)
    profileid = request.args.get('profileId', None)    

    # need a yvar for sure
    if yvar is None:
        return jsonify(error='Error: yvar is required'), 400

    height = float(request.args.get('height', 100))  # px
    width = float(request.args.get('width', 100))  # px

    # do conversion of the data from pixels to inches for plot
    height_in = height / 96.
    width_in = width / 96.

    # get the data
    if plot_layout in ["timeseries", "ts_diagram"]:
        data = get_data(stream, instrument, yvar, xvar)
    elif plot_layout == "depthprofile":
        # if yvar != 'pressure':
        #    return jsonify(error='invalid profile request'), 400
        data = get_process_profile_data(stream, instrument, yvar[0], xvar[0])

    data['title'] = title
    data['height'] = height_in
    data['width'] = width_in

    # return if error
    if 'error' in data:
        return jsonify(error=data['error']), 400

    # generate plot
    buf = generate_plot(data,
                        plot_format,
                        plot_layout,
                        use_line,
                        use_scatter,
                        profileid,
                        width_in = width_in)

    content_header_map = {
        'svg' : 'image/svg+xml',
        'png' : 'image/png'
    }

    return buf.read(), 200, {'Content-Type': content_header_map[plot_format]}


def get_process_profile_data(stream, instrument, yvar, xvar):
    data = get_profile_data(instrument, stream)
    # check the data is in the first row
    '''
    if yvar not in data[0] or xvar not in data[0]:
        data = {'error':'requested fields not in data'}
        return data
    if 'profile_id' not in data[0]:
        data = {'error':'profiles not present in data'}
        return data
    '''

    y_data = []
    x_data = []
    profile_id_list = []

    profile_count = -1

    for i, row in enumerate(data):
        if (row['profile_id']) >= 0:
            profile_id = int(row['profile_id'])

            if profile_id not in profile_id_list:
                y_data.append([])
                x_data.append([])
                profile_id_list.append(profile_id)
                profile_count += 1

            try:
                y_data[profile_count].append(row[yvar])
                x_data[profile_count].append(row[xvar])
            except Exception:
                return {'error': 'profiles not present in data, maybe a bug?'}

    return {'x': x_data, 'y': y_data, 'x_field': xvar, "y_field": yvar}


def get_profile_data(instrument, stream):
    '''
    process uframe data into profiles
    '''
    data = []
    # dt_bounds = ''
    # instrument = instrument.replace('-','/',2)
    # url = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE'] +'/' + instrument+ "/telemetered/"+stream + "/" + dt_bounds
    # response = requests.get(url)
    mooring, platform, instrument, stream_type, stream = split_stream_name('_'.join([instrument, stream]))
    if 'startdate' in request.args and 'enddate' in request.args:
        st_date = request.args['startdate']
        ed_date = request.args['enddate']
        if 'dpa_flag' in request.args:
            dpa_flag = request.args['dpa_flag']
        else:    
            dpa_flag = "0"
        ed_date = validate_date_time(st_date,ed_date)
        response = get_uframe_stream_contents(mooring, platform, instrument, stream_type, stream, st_date, ed_date, dpa_flag)
    else:
        current_app.logger.exception('Failed to make plot')
        return {'error': 'start end dates not applied:'}

    if response.status_code != 200:
        raise IOError("Failed to get data from uFrame")
    data = response.json()
    # Note: assumes data has depth and time is ordinal
    # Need to add assertions and try and exceptions to check data

    time = []
    depth = []

    for row in data:
        depth.append(int(row[request.args['xvar']]))
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
            if len(where) and int(row[request.args['xvar']]) == depth_profiles[rowloc][1]:
                row['profile_id'] = depth_profiles[rowloc][2]
                profile_list.append(row)

        except IndexError:
            row['profile_id'] = None
            profile_list.append(row)
    # profile length should equal tz  length
    return profile_list


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
