#!/usr/bin/env python
'''
uframe endpoints
'''
# base
from flask import jsonify, request, current_app
from ooiservices.app.m2m import m2m as api
from ooiservices.app.main.authentication import auth
from ooiservices.app.main.errors import internal_server_error
from ooiservices.app.decorators import scope_required
from ooiservices.app.main.authentication import auth


# data imports
from ooiservices.app.uframe.data import get_data

import requests
import urllib2


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
@scope_required('data_manager')
@api.route('/get_data/', methods=['GET'])
def get_data():
    uframe_req = request.args.get('uframe').replace('(','?')
    uframe_req = uframe_req.replace(')','&')
    uframe_url, timeout, timeout_read = get_uframe_info()
    print uframe_req, '~~~~~~'
    if uframe_url not in uframe_req and 'uframe' not in uframe_req:
        return "Not a valid uFrame Location"
    try:
        response = requests.get(uframe_req, timeout=(timeout, timeout_read))
    except Exception as e:
        return internal_server_error('uframe connection cannot be made.' + str(e.message))

    return response.text

