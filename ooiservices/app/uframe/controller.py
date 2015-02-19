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

from ooiservices.app.uframe.data import gen_data, get_time_label, plot_scatter, _get_data_type, \
_get_annotation_content, make_cache_key, get_uframe_streams, get_uframe_stream, get_uframe_stream_contents
from ooiservices.app.main.errors import internal_server_error
from ooiservices.app.main.authentication import auth, verify_auth

import json
import datetime
import math
import csv
import io

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


