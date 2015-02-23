#!/usr/bin/env python
'''
API v1.0 List

'''
__author__ = 'M@Campbell'

from flask import jsonify, request, current_app, url_for, make_response
from ooiservices.app.main import api
from ooiservices.app import db, cache
from authentication import auth
from ooiservices.app.models import PlatformDeployment, InstrumentDeployment
from ooiservices.app.models import Stream, StreamParameter, Organization, Instrumentname
from ooiservices.app.uframe.controller import get_data
import json
import yaml
from wtforms import ValidationError
from netCDF4 import num2date, date2index

import matplotlib
import matplotlib.pyplot as plt
import io
import numpy as np
import time
import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
import prettyplotlib as ppl

axis_font = {'fontname': 'Calibri',
                     'size': '14',
                     'color': 'black',
                     'weight': 'bold',
                     'verticalalignment': 'bottom'}

title_font = {'fontname': 'Arial',
                      'size': '18',
                      'color': 'black',
                      'weight': 'bold',
                      'verticalalignment': 'bottom'}

@api.route('/platform_deployments')
def get_platform_deployments():
    if 'array_id' in request.args:
        platform_deployments = \
        PlatformDeployment.query.filter_by(array_id=request.args['array_id']).order_by(PlatformDeployment.reference_designator).all()
    elif 'search' in request.args:
        platform_deployments = PlatformDeployment.query.whoosh_search(request.args['search'])
    else:
        platform_deployments = PlatformDeployment.query.all()
    return jsonify({ 'platform_deployments' : [platform_deployment.to_json() for platform_deployment in platform_deployments] })

@api.route('/platform_deployments/<string:id>')
def get_platform_deployment(id):
    platform_deployment = PlatformDeployment.query.filter_by(reference_designator=id).first_or_404()
    return jsonify(platform_deployment.to_json())

@api.route('/streams')
def get_streams():
    streams = Stream.query.all()
    return jsonify({ 'streams' : [stream.to_json() for stream in streams] })

@api.route('/streams/<string:id>')
def get_stream(id):
    stream = Stream.query.filter_by(stream_name=id).first_or_404()
    return jsonify(stream.to_json())

@api.route('/parameters')
def get_parameters():
    parameters = StreamParameter.query.all()
    return jsonify({ 'parameters' : [parameter.to_json() for parameter in parameters] })

@api.route('/parameters/<string:id>')
def get_parameter(id):
    parameter = StreamParameter.query.filter_by(stream_parameter_name=id).first_or_404()
    return jsonify(parameter.to_json())

@api.route('/organization', methods=['GET'])
def get_organizations():
    organizations = [o.serialize() for o in Organization.query.all()]
    return jsonify(organizations=organizations)

@api.route('/organization/<int:id>', methods=['GET'])
def get_organization_by_id(id):
    org = Organization.query.filter(Organization.id==id).first()
    if not org:
        return '{}', 204
    response = org.serialize()
    return jsonify(**response)

@api.route('/platformlocation', methods=['GET'])
def get_platform_deployment_geojson_single():
    geo_locations = {}
    if len(request.args) > 0:
        if ('reference_designator' in request.args):
            if len(request.args['reference_designator']) < 100:
                reference_designator = request.args['reference_designator']
                geo_locations = PlatformDeployment.query.filter(PlatformDeployment.reference_designator == reference_designator).all()
    else:
        geo_locations = PlatformDeployment.query.all()
    if len(geo_locations) == 0:
        return '{}', 204
    return jsonify({ 'geo_locations' : [{'id' : geo_location.id, 'reference_designator' : geo_location.reference_designator, 'geojson' : geo_location.geojson} for geo_location in geo_locations] })

def get_display_name_by_rd(reference_designator):
    if len(reference_designator) <= 14:
        platform_deployment_filtered = PlatformDeployment.query.filter_by(reference_designator=reference_designator).first_or_404()
        display_name = platform_deployment_filtered.proper_display_name
        if platform_deployment_filtered is None:
            return None
    elif len(reference_designator) == 27:
        platform_deployment = PlatformDeployment.query.filter_by(reference_designator=reference_designator[:14]).first()
        if platform_deployment is None:
            return None
        platform_display_name = platform_deployment.proper_display_name
        instrument_class = reference_designator[18:18+5]
        instrument_name = Instrumentname.query.filter_by(instrument_class=instrument_class).first()
        if 'ENG' in instrument_class or instrument_class == '00000':
            instrument_name = 'Engineering'
        elif instrument_name is None:
            instrument_name = reference_designator[18:]
        else:
            instrument_name = instrument_name.display_name

        display_name = ' - '.join([platform_display_name, instrument_name])
    else:
        return None
    return display_name

@api.route('/display_name', methods=['GET'])
def get_display_name():
    # 'CE01ISSM-SBD17'
    reference_designator = request.args.get('reference_designator')
    if not reference_designator:
        return '{}', 204

    display_name = get_display_name_by_rd(reference_designator)
    if display_name is None:
        return '{}', 204

    return jsonify({ 'proper_display_name' : display_name })

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
