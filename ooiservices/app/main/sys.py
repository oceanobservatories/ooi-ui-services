#!/usr/bin/env python
'''
Routes for end to end testing, can only be called when in test mode.

'''
__author__ = 'M@Campbell'

from flask import jsonify, current_app, request
from ooiservices.app.main import api
from celery.task.control import discard_all
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
    @method GET:
        Returns this list of flask cache keys and their
        time to live (TTL)
        :return: JSON

    @method DELETE:
        Send a delete request passing in the name of the
        cache key that needs to be deleted.
        :return: JSON
    '''
    if request.method == 'GET':
        # setup the container for the list of current cache items
        flask_cache = []

        # issue the command to get the list from redis
        pipe_output = subprocess.Popen(['redis-cli', 'keys', '*'],
                                       stdout=subprocess.PIPE)
        output, err = pipe_output.communicate()

        # the output is a string, so lets load it into the array
        flask_cache = output.split('\n')

        # we don't want to provide system keys, remove non "flask_cache"
        temp_list = []
        for cache_key in flask_cache:
            if 'flask_cache' in cache_key:
                temp_list.append({'key': cache_key,
                                  'name': cache_key.split('_')[2]
                                  })

        # assign the list to the main bin
        flask_cache = temp_list

        # lets get the TTL of each of the keys
        for cache_key in flask_cache:
            pipe_output = subprocess.Popen(['redis-cli', 'TTL',
                                            cache_key['key']],
                                           stdout=subprocess.PIPE)
            output, err = pipe_output.communicate()
            cache_key['TTL'] = output.split('\n')[0]

        # clear out this for garbage collection of flask_cache ref
        temp_list = None
        flask_cache.sort(key=lambda x: (x['key']))

        return jsonify({'results': flask_cache})

    elif request.method == 'DELETE':
        try:
            # grab the key, lets give it a more readable reference
            redis_key = key

            # perform the delete operation on the target host's redis server
            pipe_output = subprocess.Popen(['redis-cli', 'del', redis_key],
                                           stdout=subprocess.PIPE)
            output, err = pipe_output.communicate()

            # we'll discard all previous celery jobs, so new ones can be queued up.
            # Note, this does NOT issue a cache reload.  It simply removes any
            # backloged tasks.
            if output == 1:
                discard_all()

            return jsonify({'results': int(output)}), 200

        except Exception as e:
            return jsonify({'error': 'Exception in cache delete. %s' % e}), 500
