#!/usr/bin/env python
'''
uframe controller

'''
__author__ = 'M@Campbell'

from flask import jsonify, request, current_app, url_for
from ooiservices.app.main import api
from ooiservices.app import db
from ooiservices.app.main.authentication import auth

from ooiservices.app.uframe.data import gen_data

@api.route('/get_data')
def get_data():
    start_time = request.args.get('start_time', '2015-01-01')
    end_time = request.args.get('end_time', '2015-01-01T01:00')
    norm = request.args.get('norm', 13)
    std_dev = request.args.get('std', 3)
    sampling_rate = request.args.get('sampling_rate', 1)
    response = gen_data(start_time, end_time, sampling_rate, norm, std_dev)
    return jsonify(**response)