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
import redis


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
@api.route('/cache_keys/<string:key>', methods=['GET'])
@api.route('/cache_keys/<string:key>', methods=['DELETE'])
@api.route('/cache_keys/<string:key>/<string:key_timeout>/<string:key_value>', methods=['POST'])
def cache_list(key=None, key_value=None, key_timeout=None):
    '''
    @method GET:
        Returns this list of flask cache keys and their
        time to live (TTL)
        :return: JSON

    @method DELETE:
        Send a delete request passing in the name of the
        cache key that needs to be deleted.
        :return: JSON

    @method PUT:
        Send a PUT request passing the key:value and timeout (seconds).
        :return JSON
    '''
    if request.method == 'GET':

        redis_connection = redis.Redis.from_url(current_app.config['REDIS_URL'])

        flask_cache = redis_connection.keys()

        # issue the command to get the list from redis
        # pipe_output = subprocess.Popen(['redis-cli', 'keys', '*'],
        #                                stdout=subprocess.PIPE)
        # output, err = pipe_output.communicate()

        # the output is a string, so lets load it into the array
        # flask_cache = output.split('\n')

        # we don't want to provide system keys, remove non "flask_cache"
        temp_list = []

        if key:
            for cache_key in flask_cache:
                if key in cache_key:
                    temp_list.append({'key': cache_key,
                                      'name': cache_key.split('_')[2]
                                      })
        else:
            for cache_key in flask_cache:
                if 'flask_cache' in cache_key or 'custom_cache' in cache_key:
                    temp_list.append({'key': cache_key,
                                      'name': cache_key.split('_')[2]
                                      })

        # assign the list to the main bin
        flask_cache = temp_list

        # lets get the TTL of each of the keys
        for cache_key in flask_cache:
            # pipe_output = subprocess.Popen(['redis-cli', 'TTL',
            #                                 cache_key['key']],
            #                                stdout=subprocess.PIPE)
            output = redis_connection.ttl(cache_key['key'])
            cache_key['TTL'] = output
            val = redis_connection.get(cache_key['key'])
            cache_key['value'] = val.lower()

        # clear out this for garbage collection of flask_cache ref
        temp_list = None
        flask_cache.sort(key=lambda x: (x['key']))

        return jsonify({'results': flask_cache})

    elif request.method == 'DELETE':
        try:
            # grab the key, lets give it a more readable reference
            redis_key = key

            # perform the delete operation on the target host's redis server
            redis_connection = redis.Redis.from_url(current_app.config['REDIS_URL'])

            redis_del = redis_connection.delete(redis_key)

            return jsonify({'results': redis_del}), 200

        except Exception as e:
            return jsonify({'error': 'Exception in cache delete. %s' % e}), 500

    elif request.method == 'POST':
        try:
            # perform the SETEX operation on the target host's redis server
            # Usage: SETEX metadatabanner 604800 "true"
            redis_connection = redis.Redis.from_url(current_app.config['REDIS_URL'])

            redis_setex = redis_connection.setex(key, int(key_timeout), key_value)

            return jsonify({'results': redis_setex}), 200

        except Exception as e:
            return jsonify({'error': 'Exception adding cache key. %s' % e}), 500
