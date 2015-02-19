#!/usr/bin/env python
'''
uframe endpoints

'''
__author__ = 'Andy Bird'

from flask import jsonify, request, current_app, url_for, Flask, make_response
from ooiservices.app.uframe import uframe as api
from ooiservices.app import db, cache, celery
from ooiservices.app.main.authentication import auth
from ooiservices.app.models import Array, PlatformDeployment, InstrumentDeployment
from ooiservices.app.models import Stream, StreamParameter, Organization, Instrumentname
from ooiservices.app.models import Annotation
from urllib import urlencode
import requests
import json

#from ooiservices.app.uframe.data import get_data, gen_data, get_time_label, plot_scatter, _get_data_type, \
#_get_annotation_content, make_cache_key, get_uframe_streams, get_uframe_stream, get_uframe_stream_contents
from ooiservices.app.main.errors import internal_server_error
from ooiservices.app.main.authentication import auth, verify_auth

import json
import datetime
import math
import csv
import io
import numpy as np

#ignore list for data fields
FIELDS_IGNORE = ["stream_name","quality_flag"]
#time minus ()
COSMO_CONSTANT = 2208988800


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

    #with open('/tmp/response.json', 'w') as f:
    #    buf = streams.text.encode('UTF-8')
    #    f.write(buf)

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
@api.route('/get_data/<string:instrument>/<string:stream>/<string:field>',methods=['GET'])
def get_data_api(stream, instrument,field):
    return jsonify(**get_data(stream,instrument,field))

@auth.login_required
@api.route('/plot/<string:instrument>/<string:stream>', methods=['GET'])
def plotdemo(instrument, stream):
    plot_format = request.args.get('format', 'svg')
    xvar = request.args.get('xvar', 'internal_timestamp')
    yvar = request.args.get('yvar',None)
    title = request.args.get('title', '%s Data' % stream)
    xlabel = request.args.get('xlabel', 'X')
    ylabel = request.args.get('ylabel', yvar)
    if yvar is None:
        return 'Error: yvar is required', 400, {'Content-Type':'text/plain'}

    height = float(request.args.get('height', 100)) # px
    width = float(request.args.get('width', 100)) # px

    print height
    print width

    height_in = height / 96.
    width_in = width / 96.

    t0 = time.time()

    data = get_data(stream,instrument,yvar);

    x = data['x']
    y = data['y']

    fig, ax = ppl.subplots(1, 1, figsize=(width_in, height_in))

    kwargs = dict(linewidth=1.0,alpha=0.7)

    date_list = num2date(x, units='seconds since 1900-01-01 00:00:00', calendar='gregorian')
    plot_time_series(fig, ax, date_list, y,
                                     title=title,
                                     ylabel=ylabel,
                                     title_font=title_font,
                                     axis_font=axis_font,
                                     **kwargs)

    buf = io.BytesIO()
    content_header_map = {
        'svg' : 'image/svg+xml',
        'png' : 'image/png'
    }
    if plot_format not in ['svg', 'png']:
        plot_format = 'svg'
    plt.savefig(buf, format=plot_format)
    buf.seek(0)

    t1 = time.time()
    plt.clf()
    plt.cla()
    return buf.read(), 200, {'Content-Type':content_header_map[plot_format]}

@api.route('/get_profiles/<string:reference_designator>/<string:stream_name>')
def get_profiles(reference_designator, stream_name):

    data = get_data(reference_designator, stream_name)
    data = data.json()
    # Note: assumes data has depth and time is ordinal
    # Need to add assertions and try and exceptions to check data
    if 'pressure' not in data:
        return jsonify(error="This stream doesn't contain a depth context"), 400
    time = []
    depth = []
    preferred_timestamp = data[0]['preferred_timestamp']
        #preferred_timestamp = preferred_timestamp * 2208988800


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
    return  json.dumps(profile_list, indent=4)

import json
import datetime
import math
import csv
import io
import numpy as np

def get_data(stream, instrument,field):
    #get data from uframe
    #-------------------
    # m@c: 02/01/2015
    #uframe url to get stream data from instrument:
    # /sensor/user/inv/<stream_name>/<instrument_name>
    #
    #-------------------
    #TODO: create better error handler if uframe is not online/responding
    try:
        url = current_app.config['UFRAME_URL'] + '/sensor/user/inv/' + stream + '/' + instrument
        data = requests.get(url)
        data = data.json()
    except:
        return internal_server_error('uframe connection cannot be made.')

    hasStartDate = False
    hasEndDate = False

    if 'startdate' in request.args:
        st_date = datetime.datetime.strptime(request.args['startdate'], "%Y-%m-%d %H:%M:%S")
        hasStartDate = True

    if 'enddate' in request.args:
        ed_date = datetime.datetime.strptime(request.args['enddate'], "%Y-%m-%d %H:%M:%S")
        hasEndDate = True

    #got normal data plot
    #create the data fields,assumes the same data fields throughout
    d_row = data[0]
    ntp_offset = 22089888000 # See any documentation about NTP including RFC 5905
    #data store
    some_data = []

    pref_timestamp = d_row["preferred_timestamp"]
    #figure out the header rows
    inital_fields = d_row.keys()
    #move timestamp to the front
    inital_fields.insert(0, inital_fields.pop(inital_fields.index(pref_timestamp)))

    data_cols,data_field_list = _get_col_outline(data,pref_timestamp,inital_fields,field)

    x = [ d[pref_timestamp] for d in data ]
    y = [ d[field] for d in data ]

    #genereate dict for the data thing
    resp_data = {'x':x,
                 'y':y,
                 'data_length':len(x),
                 'x_field':pref_timestamp,
                 'y_field':field,
                 #'start_time' : datetime.datetime.fromtimestamp(data[0][pref_timestamp]).isoformat(),
                 #'end_time' : datetime.datetime.fromtimestamp(data[-1][pref_timestamp]).isoformat()
                 }

    #return jsonify(**resp_data)
    return resp_data

def gen_data(start_date, end_date, sampling_rate, mean, std_dev):
    '''
    Returns a dictionary that contains the x coordinate time and the y
    coordinate which is random data normally distributed about the mean with
    the specified standard deviation.
    '''
    time0 = calendar.timegm(parse(start_date).timetuple())
    time1 = calendar.timegm(parse(end_date).timetuple())

    dt = sampling_rate # obs per second
    x = np.arange(time0, time1, dt)
    y = np.random.normal(mean, std_dev, x.shape[0])
    xy = np.array([x,y])

    row_order_xy = xy.T


    iso0 = datetime.utcfromtimestamp(time0).isoformat()
    iso1 = datetime.utcfromtimestamp(time1).isoformat()

    return {'size' : x.shape[0], 'start_time':iso0, 'end_time':iso1, 'cols':['x','y'], 'rows':row_order_xy.tolist()}

@cache.memoize(timeout=3600)
def plot_time_series(fig, ax, x, y, fill=False, title='', ylabel='',
                         title_font={}, axis_font={}, **kwargs):

    if not title_font:
        title_font = title_font_default
    if not axis_font:
        axis_font = axis_font_default

    h = ppl.plot(ax, x, y, **kwargs)
    ppl.scatter(ax, x, y, **kwargs)
    get_time_label(ax, x)
    fig.autofmt_xdate()

    if ylabel:
        ax.set_ylabel(ylabel, **axis_font)
    if title:
        ax.set_title(title, **title_font)
    if 'degree' in ylabel:
        ax.set_ylim([0, 360])
    ax.grid(True)
    if fill:
        miny = min(ax.get_ylim())
        ax.fill_between(x, y, miny+1e-7, facecolor = h[0].get_color(), alpha=0.15)
    # plt.subplots_adjust(top=0.85)
    plt.tight_layout()

def get_time_label(ax, dates):
    '''
    Custom date axis formatting
    '''
    def format_func(x, pos=None):
        x = mdates.num2date(x)
        if pos == 0:
            fmt = '%Y-%m-%d %H:%M'
        else:
            fmt = '%H:%M'
        label = x.strftime(fmt)
        # label = label.rstrip("0")
        # label = label.rstrip(".")
        return label
    day_delta = (max(dates)-min(dates)).days

    if day_delta < 1:
        ax.xaxis.set_major_formatter(FuncFormatter(format_func))
    else:
        # pass
        major = mdates.AutoDateLocator()
        formt = mdates.AutoDateFormatter(major, defaultfmt=u'%Y-%m-%d')
        formt.scaled[1.0] = '%Y-%m-%d'
        formt.scaled[30] = '%Y-%m'
        formt.scaled[1./24.] = '%Y-%m-%d %H:%M:%S'
        # formt.scaled[1./(24.*60.)] = FuncFormatter(format_func)
        ax.xaxis.set_major_locator(major)
        ax.xaxis.set_major_formatter(formt)

def plot_scatter(fig, ax, x, y, title='', xlabel='', ylabel='',
                     title_font={}, axis_font={}, **kwargs):

        if not title_font:
            title_font = title_font_default
        if not axis_font:
            axis_font = axis_font_default

        ppl.scatter(ax, x, y, **kwargs)
        if xlabel:
            ax.set_xlabel(xlabel, labelpad=10, **axis_font)
        if ylabel:
            ax.set_ylabel(ylabel, labelpad=10, **axis_font)
        ax.set_title(title, **title_font)
        ax.grid(True)
        ax.set_aspect(1./ax.get_data_ratio())  # make axes square

def _get_data_type(data_input):
    '''
    gets the data type in a format google charts understands
    '''
    if data_input is float or data_input is int:
        return "number"
    elif data_input is str or data_input is unicode:
        return "string"
    else:
        return "unknown"

def _get_annotation(instrument_name, stream_name):
    annotations = Annotation.query.filter_by(instrument_name=instrument_name, stream_name=stream_name).all()
    return [annotation.to_json() for annotation in annotations]

def _get_col_outline(data,pref_timestamp,inital_fields,requested_field):
    '''
    gets the column outline for the google chart response, figures out what annotations are required where...
    '''
    data_fields = []
    data_field_list= []
    #used to cound the fields, used for annotations
    field_count = 1
    #loop and generate inital col dict
    for field in inital_fields:
        if field == pref_timestamp:
            d_type = "datetime"
        elif field in FIELDS_IGNORE or str(field).endswith('_timestamp'):
            continue
        else:
            if requested_field is not None:
                if field == requested_field:
                    d_type = _get_data_type(type(data[0][field]))
                else:
                    continue
            else:
                #map the data types to the correct data type for google charts
                d_type = _get_data_type(type(data[0][field]))

        data_field_list.append(field)
        data_fields.append({"id": "",
                            "label": field,
                            "type":  d_type})

    return data_fields,data_field_list

def _get_annotation_content(annotation_field, pref_timestamp, annotations_list, d, data_field):
    '''
    creates the annotation content for a given field
    '''
    #right now x and y are timeseries data
    for an in annotations_list:
        if an['field_x'] == pref_timestamp or an['field_y'] == data_field:
            # and and y value
            an_date_time = datetime.datetime.strptime(an['pos_x'], "%Y-%m-%dT%H:%M:%S")
            an_int_date_time = int(an_date_time.strftime("%s"))

            if int(d['fixed_dt']) == an_int_date_time:
                if annotation_field == "annotation":
                    return {"v":an["title"]}
                elif annotation_field == "annotationText":
                    return {"v":an['comment']}

    #return nothing
    return {"v":None,"f":None}

def make_cache_key():
    return urlencode(request.args)

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

