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

requests.adapters.DEFAULT_RETRIES = 2

headers = {'Content-Type': 'application/json'}


@auth.login_required
@api.route('/subscription', methods=['GET'])
def get_subscription():
    res = requests.get(
        app.config['UFRAME_SUBSCRIBE_URL']+'/subscription',
        params=request.args)
    return res.text, res.status_code


@auth.login_required
@api.route('/subscription', methods=['POST'])
def create_subscription():
    res = requests.post(
        app.config['UFRAME_SUBSCRIBE_URL']+'/subscription',
        data=request.data,
        headers=headers)
    return res.text, res.status_code


@auth.login_required
@api.route('/subscription/<int:id>', methods=['DELETE'])
def delete_subscription(id):
    res = requests.delete(
        app.config['UFRAME_SUBSCRIBE_URL']+'/subscription/%s' % id)
    return res.text, res.status_code
