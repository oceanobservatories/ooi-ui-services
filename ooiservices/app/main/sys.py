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


@api.route('/cache_keys', methods=['GET', 'POST'])
def cache_list():
    '''
    @method GET: returns this list of flask cache keys and their
                 time to live (TTL)
    @method POST: Submitting a post request with a list of keys
                  will delete each key in the list
                  Example: {delete: [<cache_item_1>, <cache_item_2>, ...]}
    '''
    if request.method == 'GET':
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
                temp_list.append({'key': cache_key})

        # assign the list to the main bin
        flask_cache = temp_list

        # lets get the TTL of each of the keys so we can see how long ago
        # they were created.
        for cache_key in flask_cache:
            pipe_output = subprocess.Popen(['redis-cli', 'TTL',
                                            cache_key['key']],
                                           stdout=subprocess.PIPE)
            output, err = pipe_output.communicate()
            cache_key['TTL'] = output.split('\n')[0]

        # clear out this for garbage collection of flask_cache ref
        temp_list = None

        return jsonify({'cache_list': flask_cache}), 200

    elif request.method == 'POST':
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
            return jsonify({'error': 'Exception in cache delete. %s' % e}), 500
