#!/usr/bin/env python
'''
ooiservices/app/main/data.py

Support for generating sample data
'''

__author__ = 'Andy Bird'

from flask import jsonify, request, current_app, url_for, Flask, make_response
from ooiservices.app.uframe import uframe as api

import numpy as np
import calendar
import time
from dateutil.parser import parse
from datetime import datetime
from ooiservices.app.main.errors import internal_server_error
from ooiservices.app import cache
import requests

#ignore list for data fields
FIELDS_IGNORE = ["stream_name","quality_flag"]
COSMO_CONSTANT = 2208988800


def get_data(stream, instrument,field):
    #get data from uframe
    #-------------------
    # m@c: 02/01/2015
    #uframe url to get stream data from instrument:
    # /sensor/user/inv/<stream_name>/<instrument_name>
    #
    #-------------------
    #TODO: create better error handler if uframe is not online/responding
    data = []
    try:
        url = current_app.config['UFRAME_URL'] + '/sensor/m2m/inv/' + stream + '/' + instrument
        data = requests.get(url)
        data = data.json()        
    except Exception,e:
        return {'error':'uframe connection cannot be made:'+str(e)}

    if len(data)==0:
        return {'error':'non data available'}    

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
                 'dt_units':'seconds since 1900-01-01 00:00:00',
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
