#!/usr/bin/env python
'''
uframe endpoints
'''
# base
from flask import jsonify, request, current_app
from ooiservices.app.m2m import m2m as api
from ooiservices.app.main.authentication import auth
from ooiservices.app.main.errors import internal_server_error
from ooiservices.app.models import User

import requests
import requests.adapters
import requests.exceptions
from requests.exceptions import ConnectionError, Timeout
from requests.utils import quote, unquote
import urllib2


requests.adapters.DEFAULT_RETRIES = 2
CACHE_TIMEOUT = 86400

data_types = {}
data_types['sensor_inv'] = 'UFRAME_URL_BASE'
data_types['sensor_inv_toc'] = 'UFRAME_TOC'


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
@api.route('/get_data', methods=['GET'])
def get_data():
    if User.api_verify_token(request.authorization['username'], request.authorization['password']):
        user_request = unquote(request.args.get('user_request', ''))

        try:
            uframe_url, timeout, timeout_read = get_uframe_info()
            user_url = "/".join([current_app.config['UFRAME_URL'], current_app.config[data_types[request.args.get('data_type', '')]], user_request])
            r = requests.get(user_url, timeout=(timeout, timeout_read))
            try:
                # Form the Google Analytics request
                if request.args.get('data_type', '') == 'sensor_inv':
                    user_request_list = user_request.split('/')
                    ga_data_string = '-'.join(
                        [
                            user_request_list[0],
                            user_request_list[1],
                            user_request_list[2],
                            user_request_list[3],
                            user_request_list[4].split('?')[0],
                        ]
                    )
                    ga_time_string = '-'.join(
                        [
                            user_request_list[4].split('beginDT=')[1].split('&')[0],
                            user_request_list[4].split('endDT=')[1].split('&')[0]
                        ]
                    )
                    ga_url = current_app.config['GOOGLE_ANALYTICS_URL']+'&ec=m2m&ea=%s&el=%s' % (ga_data_string, ga_time_string)
                    urllib2.urlopen(ga_url)
            except KeyError:
                pass
            return r.text, r.status_code
        except ConnectionError:
            message = 'ConnectionError for get uframe contents.'
            current_app.logger.info(message)
            raise Exception(message)
        except Timeout:
            message = 'Timeout for get uframe contents.'
            current_app.logger.info(message)
            raise Exception(message)
        except Exception:
            raise
    else:
        message = 'Authentication failed.'
        current_app.logger.info(message)
        return message, 401
