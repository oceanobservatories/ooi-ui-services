#!/usr/bin/env python
'''
uframe endpoints
'''
# base
from flask import jsonify, request, current_app, make_response, Response
from ooiservices.app import cache
from ooiservices.app.m2m import m2m as api
from ooiservices.app.models import PlatformDeployment
from ooiservices.app.main.routes import get_display_name_by_rd, get_long_display_name_by_rd,\
    get_platform_display_name_by_rd, get_parameter_name_by_parameter as get_param_names
from ooiservices.app.main.authentication import auth
from ooiservices.app.main.errors import internal_server_error
# data imports
from ooiservices.app.uframe.data import get_data, get_simple_data, find_parameter_ids, get_multistream_data
from ooiservices.app.uframe.plotting import generate_plot
from ooiservices.app.uframe.assetController import get_events_by_ref_des

from urllib import urlencode
from datetime import datetime
from dateutil.parser import parse as parse_date
import requests
import json
import numpy as np
import pytz
from contextlib import closing
import time
import urllib2
from copy import deepcopy
from operator import itemgetter


requests.adapters.DEFAULT_RETRIES = 2
CACHE_TIMEOUT = 86400

@api.route('/get_metadata/<string:ref>', methods=['GET'])
#@cache.memoize(timeout=3600)
def get_metadata(ref):
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
            
            return jsonify(data)
         
        return jsonify(metadata={}), 404
    except Exception as e:
        return internal_server_error('uframe connection cannot be made.' + str(e.message))


def get_uframe_info():
    '''
    returns uframe configuration information. (uframe_url, uframe timeout_connect and timeout_read.)
    '''
    uframe_url = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE']
    timeout = current_app.config['UFRAME_TIMEOUT_CONNECT']
    timeout_read = current_app.config['UFRAME_TIMEOUT_READ']
    return uframe_url, timeout, timeout_read

@auth.login_required
@api.route('/get_data/<string:ref>/<string:method>/<string:stream>/<string:start_time>/<string:end_time>', methods=['GET'])
def get_data(ref, method, stream, start_time, end_time):
     
    mooring, platform, instrument = ref.split('-', 2)

    method = method.replace('-','_')
    uframe_url, timeout, timeout_read = get_uframe_info()
    user = request.args.get('user', '')
    email = request.args.get('email', '')
    prov = request.args.get('provenance','false')
    pids = request.args.get('pid','')
    
    data_format = 'application/'+request.args.get('format', '')
    possible_data_format = ['application/netcdf','application/json','application/csv','application/tsv']
    if data_format not in possible_data_format:
        data_format = 'applciation/netcdf'

    limit = request.args.get('limit', 'NONE')
    if limit is 'NONE':
        query = '?beginDT=%s&endDT=%s&include_provenance=%s&include_annotations=true&user=%s&email=%s&format=%s&pid=%s' % (start_time, end_time, prov, user, email, data_format, pids)
    else:
        if int(limit) > 1001 or int(limit) <1:
            limit = 1000
        query = '?beginDT=%s&endDT=%s&include_provenance=%s&include_annotations=true&user=%s&email=%s&format=%s&limit=%s&pid=%s' % (start_time, end_time, prov, user, email, data_format,limit,pids)

    uframe_url, timeout, timeout_read = get_uframe_info()
    url = "/".join([uframe_url, mooring, platform, instrument, method, stream + query])
    current_app.logger.debug('***** url: ' + url)
    response = requests.get(url, timeout=(timeout, timeout_read))

    try:
        GA_URL = current_app.config['GOOGLE_ANALYTICS_URL']+'&ec=m2m&ea=%s&el=%s' % ('-'.join([mooring, platform, instrument, stream]), '-'.join([start_time, end_time]))
        urllib2.urlopen(GA_URL)
    except KeyError:
        pass
    
    
    return response.text, response.status_code


