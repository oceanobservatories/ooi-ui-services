#!/usr/bin/env python
'''
Routes for end to end testing, can only be called when in test mode.

'''
__author__ = 'M@Campbell'

from flask import jsonify, current_app, request
from ooiservices.app.main import api
import urllib
import subprocess


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


@api.route('/cache_keys', methods=['GET'])
@api.route('/cache_keys/<string:key>', methods=['DELETE'])
def cache_list(key=None):
    '''
    @method GET: returns this list of flask cache keys and their
                 time to live (TTL)
    @method DELETE: Send a delete request passing in the name of the
                    cache key that needs to be deleted.
    '''
    if request.method == 'GET':
        # setup the container for the list of current cache items
        flask_cache = []

        # issue the command to get the list from redis
        pipe_output = subprocess.Popen(['redis-cli', 'scan', '0'],
                                       stdout=subprocess.PIPE)
        output, err = pipe_output.communicate()

        # the output is a string, so lets load it into the array based
        # on it's delimiter
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

        return jsonify({'results': flask_cache})

    elif request.method == 'DELETE':
        try:
            # grab the json and load the payload
            redis_key = key

            # for each item in the list, delete the cache
            pipe_output = subprocess.Popen(['redis-cli', 'del', redis_key],
                                           stdout=subprocess.PIPE)
            output, err = pipe_output.communicate()

            return jsonify({'results': int(output)}), 200

        except Exception as e:
            return jsonify({'error': 'Exception in cache delete. %s' % e}), 500
