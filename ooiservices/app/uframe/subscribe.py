#!/usr/bin/env python
'''
Subscription services for uframe.
'''

__author__ = 'M@Campbell'
__created__ = '11/04/2015'

from flask import request, current_app as app
from ooiservices.app.uframe import uframe as api
from ooiservices.app.main.authentication import auth

import requests
import requests.adapters
from requests.exceptions import ConnectionError, Timeout
from ooiservices.app.main.errors import bad_request
from ooiservices.app.main.alertsalarms_tools import get_uframe_info

requests.adapters.DEFAULT_RETRIES = 2

headers = {'Content-Type': 'application/json'}


@auth.login_required
@api.route('/subscription', methods=['GET'])
def get_subscription():

    try:
        # Get uframe connect and timeout information
        timeout, timeout_read = get_uframe_info()
        if request.args is not None:
            res = requests.get(
                app.config['UFRAME_SUBSCRIBE_URL']+'/subscription',
                params=request.args,
                timeout=(timeout, timeout_read))
        else:
            res = requests.get(
                app.config['UFRAME_SUBSCRIBE_URL']+'/subscription')
        return res.text, res.status_code

    except ConnectionError:
        message = 'ConnectionError getting subscription.'
        return bad_request(message)
    except Timeout:
        message = 'Timeout getting subscription.'
        return bad_request(message)
    except Exception as err:
        message = str(err)
        return bad_request(message)


@auth.login_required
@api.route('/subscription', methods=['POST'])
def create_subscription():
    try:
        # Get uframe connect and timeout information
        timeout, timeout_read = get_uframe_info()
        res = requests.post(
            app.config['UFRAME_SUBSCRIBE_URL']+'/subscription',
            data=request.data,
            headers=headers,
            timeout=(timeout, timeout_read))
        return res.text, res.status_code

    except ConnectionError:
        message = 'ConnectionError getting subscription.'
        return bad_request(message)
    except Timeout:
        message = 'Timeout getting subscription.'
        return bad_request(message)
    except Exception as err:
        message = str(err)
        return bad_request(message)


@auth.login_required
@api.route('/subscription/<int:id>', methods=['DELETE'])
def delete_subscription(id):
    try:
        # Get uframe connect and timeout information
        timeout, timeout_read = get_uframe_info()
        res = requests.delete(
            app.config['UFRAME_SUBSCRIBE_URL']+'/subscription/%s' % id,
            timeout=(timeout, timeout_read))
        return res.text, res.status_code

    except ConnectionError:
        message = 'ConnectionError getting subscription.'
        return bad_request(message)
    except Timeout:
        message = 'Timeout getting subscription.'
        return bad_request(message)
    except Exception as err:
        message = str(err)
        return bad_request(message)
