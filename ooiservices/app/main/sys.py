#!/usr/bin/env python
'''
Routes for end to end testing, can only be called when in test mode.

'''
__author__ = 'M@Campbell'

from flask import jsonify, current_app, request
from ooiservices.app.main import api
import urllib
import subprocess
import json


@api.route('/list_routes', methods=['GET'])
def list_routes():
    """
    Create a list of (url, endpoint) tuples from app.url_map
    Used for performance testing
    :return:
    """
    routes = []
    for rule in current_app.url_map.iter_rules():
        if 'GET' in rule.methods:
            url = urllib.unquote("{}".format(rule))
            routes.append((url, rule.endpoint))

    if not routes:
        return '{}', 204

    return jsonify({'routes': routes})


@api.route('/get_cache_list', methods=['GET'])
# TODO: @scope_required('sys_admin')
def get_cache_list():
    # setup the container for the list of current cache items
    flask_cache = []

    # issue the command to get the list from redis
    pipe_output = subprocess.Popen(['redis-cli', 'scan', '0'],
                                   stdout=subprocess.PIPE)
    output, err = pipe_output.communicate()

    # the output is a string, so lets load it into the array based
    # in it's delimiter
    flask_cache = output.split('\n')

    # we don't want to provide system level redis keys, so iterate
    # over the list and only provide those that are prefixed
    # by 'flask_cache'
    temp_list = []
    for cache_key in flask_cache:
        if 'flask_cache' in cache_key:
            temp_list.append(cache_key)

    flask_cache = temp_list
    temp_list = None  # clear out this for garbage collection

    return jsonify({'response': flask_cache}), 200


@api.route('/delete_cache', methods=['POST'])
# TODO: @scope_required('sys_admin')
def delete_cache():
    '''
    Example Post:
        {delete: [<cache_item_1>, <cache_item_2>, ...]}

    Response Codes:
        1 = success
        0 = not success
    '''

    redis_response = 1

    try:
        # grab the json and load the payload
        redis_list = json.loads(request.data)

        # for each item in the list, delete the cache
        for cache_key in redis_list['delete']:
            pipe_output = subprocess.Popen(['redis-cli', 'del', cache_key],
                                           stdout=subprocess.PIPE)
            output, err = pipe_output.communicate()

            # figure out if the response is a great success
            # by multiplying the redis_response by the output
            # which will be a 1 for success and a 0 otherwise
            redis_response = redis_response*output

        return jsonify({'response': int(redis_response)}), 200

    except Exception as e:
        return jsonify({'error': 'Exception in cache deletion: %s' % e}), 500
