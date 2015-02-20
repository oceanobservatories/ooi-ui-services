#!/usr/bin/env python
'''
uframe endpoints

'''
__author__ = 'Andy Bird'
#base
from flask import jsonify, request, current_app, url_for, Flask, make_response
from ooiservices.app import db, cache, celery
from ooiservices.app.uframe import uframe as api
from ooiservices.app.models import Array, PlatformDeployment, InstrumentDeployment,Stream, StreamParameter, Organization, Instrumentname,Annotation
from ooiservices.app.main.authentication import auth,verify_auth
from ooiservices.app.main.errors import internal_server_error
from urllib import urlencode
#data ones
from ooiservices.app.uframe.data import get_data, COSMO_CONSTANT
from ooiservices.app.uframe.plotting import generate_plot
import requests
#additional ones
import json
import datetime
import math
import csv
import io
import numpy as np

@api.route('/stream')
@auth.login_required
def streams_list():
    UFRAME_DATA = current_app.config['UFRAME_URL'] + '/sensor/m2m/inv'


    HOST = str(current_app.config['HOST'])
    PORT = str(current_app.config['PORT'])
    SERVICE_LOCATION = 'http://'+HOST+":"+PORT

    response = get_uframe_streams()
    if response.status_code != 200:
        return response
    streams = response.json()

    retval = []
    for stream in streams:
        if request.args.get('stream_name'):
            if request.args.get('stream_name') not in stream:
                continue
        response = get_uframe_stream(stream)
        if response.status_code != 200:
            return response
        refs = response.json()

        if request.args.get('reference_designator'):
            refs = [r for r in refs if request.args.get('reference_designator') in r]

        for ref in refs:
            data_dict = {}
            response = get_uframe_stream_contents(stream, ref)
            if response.status_code != 200:
                return response
            data =  response.json()
            preferred = data[0][u'preferred_timestamp']
            data_dict['start'] = data[0][preferred] - COSMO_CONSTANT
            data_dict['end'] = data[-1][preferred] - COSMO_CONSTANT
            data_dict['reference_designator'] = ref
            data_dict['csv_download'] = "/".join([SERVICE_LOCATION,'uframe/get_csv',stream,ref])
            data_dict['json_download'] = "/".join([SERVICE_LOCATION,'uframe/get_json',stream,ref])
            data_dict['netcdf_download'] = "/".join([SERVICE_LOCATION,'uframe/get_netcdf',stream,ref])
            data_dict['stream_name'] = stream
            data_dict['variables'] = data[1].keys()
            data_dict['variable_types'] = {k : type(data[1][k]).__name__ for k in data[1].keys() }
            data_dict['preferred_timestamp'] = data[0]['preferred_timestamp']
            retval.append(data_dict)

    return jsonify(streams=retval)

@cache.memoize(timeout=3600)
def get_uframe_streams():
    '''
    Lists all the streams
    '''
    try:
        UFRAME_DATA = current_app.config['UFRAME_URL'] + '/sensor/m2m/inv'
        response = requests.get(UFRAME_DATA)
        return response
    except:
        return internal_server_error('uframe connection cannot be made.')

@cache.memoize(timeout=3600)
def get_uframe_stream(stream):
    '''
    Lists the reference designators for the streams
    '''
    try:
        UFRAME_DATA = current_app.config['UFRAME_URL'] + '/sensor/m2m/inv'
        response = requests.get("/".join([UFRAME_DATA,stream]))
        return response
    except:
        return internal_server_error('uframe connection cannot be made.')

@cache.memoize(timeout=3600)
def get_uframe_stream_contents(stream, ref):
    '''
    Gets the stream contents
    '''
    try:
        UFRAME_DATA = current_app.config['UFRAME_URL'] + '/sensor/m2m/inv'
        response =  requests.get("/".join([UFRAME_DATA,stream,ref]))
        return response
    except:
        return internal_server_error('uframe connection cannot be made.')

@auth.login_required
@api.route('/get_csv/<string:stream>/<string:ref>',methods=['GET'])
def get_csv(stream,ref):
    data = get_uframe_stream_contents(stream,ref)
    if data.status_code != 200:
        return data.text, data.status_code, dict(data.headers)

    output = io.BytesIO()
    data = data.json()
    f = csv.DictWriter(output, fieldnames = data[0].keys())
    f.writeheader()
    for row in data:
        f.writerow(row)

    filename = '-'.join([stream,ref])

    buf = output.getvalue()
    returned_csv = make_response(buf)
    returned_csv.headers["Content-Disposition"] = "attachment; filename=%s.csv"%filename
    returned_csv.headers["Content-Type"] = "text/csv"

    output.close()
    return returned_csv

@auth.login_required
@api.route('/get_json/<string:stream>/<string:ref>',methods=['GET'])
def get_json(stream,ref):
    data = get_uframe_stream_contents(stream,ref)
    if data.status_code != 200:
        return data.text, data.status_code, dict(data.headers)
    response = '{"data":%s}' % data.content
    filename = '-'.join([stream,ref])
    returned_json = make_response(response)
    returned_json.headers["Content-Disposition"] = "attachment; filename=%s.json"%filename
    returned_json.headers["Content-Type"] = "application/json"
    return returned_json

@auth.login_required
@api.route('/get_netcdf/<string:stream>/<string:ref>',methods=['GET'])
def get_netcdf(stream,ref):
    UFRAME_DATA = current_app.config['UFRAME_URL'] + '/sensor/m2m/inv/%s/%s'%(stream,ref)
    NETCDF_LINK = UFRAME_DATA+'?format=application/netcdf3'

    response = requests.get(NETCDF_LINK)
    if response.status_code != 200:
        return response.text, response.status_code

    filename = '-'.join([stream,ref])
    buf = response.content
    returned_netcdf = make_response(buf)
    returned_netcdf.headers["Content-Disposition"] = "attachment; filename=%s.nc"%filename
    returned_netcdf.headers["Content-Type"] = "application/x-netcdf"

    return returned_netcdf


@auth.login_required
@api.route('/get_data/<string:instrument>/<string:stream>/<string:yvar>/<string:xvar>',methods=['GET'])
def get_data_api(stream, instrument,yvar):    
    return jsonify(**get_data(stream,instrument,yvar,xvar))

@auth.login_required
@api.route('/plot/<string:instrument>/<string:stream>', methods=['GET'])
def get_svg_plot(instrument, stream):
    plot_format = request.args.get('format', 'svg')
    #time series vs profile
    plot_layout = request.args.get('plotLayout', 'timeseries')
    xvar = request.args.get('xvar', 'internal_timestamp')
    yvar = request.args.get('yvar',None)
    #create bool from request
    use_line = to_bool(request.args.get('line',True))
    use_scatter = to_bool(request.args.get('scatter',True))
    #get titles and labels
    title = request.args.get('title', '%s Data' % stream)
    xlabel = request.args.get('xlabel', xvar)
    ylabel = request.args.get('ylabel', yvar)

    #need a yvar for sure
    if yvar is None:
        return jsonify(error='Error: yvar is required'), 400        

    height = float(request.args.get('height', 100)) # px
    width = float(request.args.get('width', 100)) # px

    #do conversion of the data from pixels to inches for plot
    height_in = height / 96.
    width_in = width / 96.

    #get the data
    if plot_layout == "timeseries":
        data = get_data(stream,instrument,yvar,xvar);
    elif plot_layout == "depthprofile":
        if yvar != 'pressure':
            return jsonify(error='invalid profile request'), 400            
        data = get_process_profile_data(stream,instrument,yvar,xvar);        

    #return if error
    if 'error' in data:
        return jsonify(error=data['error']), 400

    #generate plot
    buf = generate_plot(title,
                        xlabel,
                        ylabel,
                        data['x'],
                        data['y'],                        
                        xvar,
                        yvar,
                        height_in,
                        width_in,                        
                        plot_format,
                        plot_layout,
                        use_line,
                        use_scatter)

    content_header_map = {
        'svg' : 'image/svg+xml',
        'png' : 'image/png'
    }

    return buf.read(), 200, {'Content-Type':content_header_map[plot_format]}

def get_process_profile_data(stream,instrument,yvar,xvar):
    data = get_profile_data(instrument,stream)

    #check the data is in the first row
    if yvar not in data[0] or xvar not in data[0]:
        data = {'error':'requested fields not in data'}
        return data
    if 'profile_id' not in data[0]:
        data = {'error':'profiles not present in data'}
        return data

    y_data = []
    x_data = []
    profile_id_list = []

    profile_count = -1

    for i,row in enumerate(data): 
        if (row['profile_id']) >= 0:                        
            profile_id = int(row['profile_id'])    
            
            if profile_id not in profile_id_list:                
                y_data.append([])
                x_data.append([])
                profile_id_list.append(profile_id)
                profile_count+=1

            try:
                y_data[profile_count].append(row[yvar])
                x_data[profile_count].append(row[xvar])
            except Exception,e:                
                return {'error':'profiles not present in data,maybe a bug?'}
    
    return {'x':x_data,'y':y_data}

def get_profile_data(instrument,stream):
    '''
    process uframe data into profiles
    '''
    data = []
    try:
        url = current_app.config['UFRAME_URL'] + '/sensor/m2m/inv/' + stream + '/' + instrument
        data = requests.get(url)
        data = data.json()        
    except Exception,e:
        return jsonify(error='uframe connection cannot be made:'+str(e)), 400  
    # Note: assumes data has depth and time is ordinal
    # Need to add assertions and try and exceptions to check data

    if 'pressure' not in data[0]:
        return jsonify(error='no pressure data found'), 400  

    time = []
    depth = []
    preferred_timestamp = data[0]['preferred_timestamp']

    for row in data:
        depth.append(int(row['pressure']))
        time.append(float(row[preferred_timestamp]))

    matrix = np.column_stack((time, depth))
    tz = matrix
    origTz = tz
    INT = 10
    # tz length must equal profile_list length

    maxi = np.amax(tz[:,0])
    mini =np.amin(tz[:,0])
    #getting a range from min to max time with 10 seconds or milliseconds. I have no idea.
    ts =(np.arange(np.amin(tz[:,0]), np.amax(tz[:,0]), INT)).T

    #interpolation adds additional points on the line within f(t), f(t+1)  time is a function of depth
    itz = np.interp(ts,tz[:,0],tz[:,1])


    newtz= np.column_stack((ts, itz))
    # 5 unit moving average
    WINDOW = 5
    weights = np.repeat(1.0, WINDOW)/ WINDOW
    ma =np.convolve(newtz[:,1], weights)[WINDOW-1:-(WINDOW-1)]
    #take the diff and change negatives to -1 and postives to 1
    dZ = np.sign(np.diff(ma))

    # repeat for second derivative
    dZ = np.convolve(dZ, weights)[WINDOW-1:-(WINDOW-1)]
    dZ = np.sign(dZ)

    r0=1
    r1 = len(dZ)+1
    dZero = np.diff(dZ)

    start =[]
    stop =[]
    #find where the slope changes
    dr = [start.append(i)  for (i, val) in enumerate(dZero) if val !=0]

    for i in range(len(start)-1):
        stop.append(start[i+1])

    stop.append(start[0])
    start_stop = np.column_stack((start, stop))
    start_times = np.take(newtz[:,0], start)
    stop_times = np.take(newtz[:,0], stop)
    start_times = start_times - INT*2
    stop_times = stop_times + INT*2

    depth_profiles=[]

    for i in range(len(start_times)):
        profile_id=i
        proInds= origTz[(origTz[:,0] >= start_times[i]) & (origTz[:,0] <= stop_times[i])]
        value = proInds.shape[0]
        z = np.full((value,1), profile_id)
        pro = np.append(proInds, z, axis=1)
        depth_profiles.append(pro)

    depth_profiles = np.concatenate(depth_profiles)
    # I NEED to CHECK FOR DUPLICATE TIMES !!!!! NOT YET DONE!!!!
    # Start stop times may result in over laps on original data set. (see function above)
    # May be an issue, requires further enquiry
    profile_list= []
    for row in data:
        try:
            #Need to add epsilon. Floating point error may occur
            where = np.argwhere(depth_profiles == float(row['internal_timestamp']))
            index = where[0]
            rowloc = index[0]
            if len(where) and int(row['pressure']) ==  depth_profiles[rowloc][1]:
                row['profile_id']=depth_profiles[rowloc][2]
                profile_list.append(row)

        except IndexError:
            row['profile_id']= None
            profile_list.append(row)
    #profile length should equal tz  length
    return  profile_list


@auth.login_required
@api.route('/get_profiles/<string:instrument>/<string:stream>', methods=['GET'])
def get_profiles(instrument, stream):        
    return json.dumps(get_profile_data(instrument,stream))
    
def make_cache_key():
    return urlencode(request.args)

def to_bool(value):
    """
       Converts 'something' to boolean. Raises exception for invalid formats
           Possible True  values: 1, True, "1", "TRue", "yes", "y", "t"
           Possible False values: 0, False, None, [], {}, "", "0", "faLse", "no", "n", "f", 0.0, ...
    """
    if str(value).lower() in ("yes", "y", "true",  "t", "1"): return True
    if str(value).lower() in ("no",  "n", "false", "f", "0", "0.0", "", "none", "[]", "{}"): return False
    raise Exception('Invalid value for boolean conversion: ' + str(value))
