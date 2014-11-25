#!/usr/bin/env python
'''
ooiservices.model.erddap.py

ErddapModel
'''

from ooiservices.model.base import BaseModel
from ooiservices.model.cachemodel import CacheModel
from flask import request, Response, jsonify, json
import requests

__author__ = "Edna Donoughe"

class ErddapModel(BaseModel):

    def __init__(self):
        try:
            self.get_settings()
            self.cache_model = CacheModel()
        except Exception as e:
            raise Exception('erddap model __init_  exception: %s' % e)

    # CRUD methods
    def create(self, obj):  #key, value):
        '''
        do model specific create, if successful; add key and value to cache
        '''

        # TBD - do model specific create. (url?)
        # if model specific create is successful, add key, value to cache
        result = self.cache_model.create(obj)
        return result

    def read(self, id):
        '''
        read value for id from cache; if not in cache, perform read and if successful then cache it

        - if not in cache then retrieve value for id from url; if successful then add to cache
        - return json results in response message
        - If id not found, return HTTP204 response
        - If error adding to cache, return error message response
        - If exception, return exception message response
        '''
        # try to get value for id from cache; if in cache, return result in response
        result = self.cache_model.read(id)
        if result:
            print 'retrieve from cache'
            return Response(result,status=200,headers= {'Content-Type': 'text/html; charset=utf-8'},
                            content_type='text/html; charset=utf-8')

        # not in cache then retrieve value for id from url
        print 'retrieve with url'
        try:
            result = self.url_get(id, request.query_string)
            if not result:
                return self.response_HTTP404()
            if not result.data:
                return self.response_HTTP204()

        # http://docs.python-requests.org/en/latest/api/#requests.exceptions.HTTPError
        except requests.exceptions.ConnectionError:
            return jsonify({'error' : 'ConnectionError'})
        except requests.exceptions.RequestException:
            return jsonify({'error' : 'RequestException'})
        except requests.exceptions.HTTPError:
            return jsonify({'error' : 'HTTPError'})
        except requests.exceptions.URLRequired:
            return jsonify({'error' : 'URLRequired'})
        except requests.exceptions.TooManyRedirects:
            return jsonify({'error' : 'TooManyRedirects'})
        except requests.exceptions.ConnectTimeout:
            return jsonify({'error' : 'ConnectTimeout'})
        except requests.exceptions.ReadTimeout:
            return jsonify({'error' : 'ReadTimeout'})
        except:
            return self.response_HTTP500()
        return result

    def update(self, obj):
        '''
        do model specific update; if update successful, update cache using key and value provided in obj.
        '''
        raise NotImplementError('erddap model update Not Implemented')

    def delete(self, id):
        '''
        - Issue the delete, if successful, and id in cache, then also delete from cache; return success.
        - If error on delete, return error message response; do not delete from cache.
        - If delete successful and not in cache, return success.
        - If delete successful and in cache, delete from cache.
        - If error on delete from cache then report error message?

        delete id returns 204 if not found in cache to delete (todo - push delete through url as request)
        if successfully deleted from cache, result == 1
        '''
        result = None
        try:
            if id:
                # TBD - do model specific delete. (url?)
                result = self.cache_model.delete(id)
                if not result:
                    return self.response_HTTP204()
        except Exception, e:
            raise Exception('delete failed with exception: %s' % e)

        return result

    #- - - - - - - - - - - - - - - - - -
    # helper methods
    #- - - - - - - - - - - - - - - - - -
    def get_key_value(self,obj):
        '''
        get key and value from obj
        '''
        key = None
        value = None
        if 'key' in obj and 'value' in obj:
            key = str(obj['key'])
            value = obj['value']
        return key, value

    def url_get(self, id, query_string):
        '''
        forward request to target url since key not in cache; if successful then add to cache
        '''
        result = None
        try:
            if query_string:
                target_url = self.base_url + '?' + query_string
            else:
                target_url = self.base_url

            result = Response(requests.get(target_url,timeout=(self.timeout_connect, self.timeout_read)))
            if result:
                if result.data:
                    try:
                        json.loads(result.data)
                    except:
                        raise Exception('data received not in json format')

                    obj = {'key': str(id), 'value': result.data}
                    self.cache_model.create(obj)
                else:
                    result = self.response_HTTP204()
            else:
                result = self.response_HTTP204()

        except Exception as e:
            raise Exception('get_url: %s' % e)

        return result

    def get_settings(self):
        '''
        read config and provide validated instance variables (use of prefix TBD)
        '''
        try:
            settings = self.read_config()
            self.base_url = settings['base_url']                  # (str)
            self.timeout_connect = settings['timeout_connect']    # (int) connect timeout (should be greater than 3 secs)
            self.timeout_read    = settings['timeout_read']       # (int) read timeout (adjust to accommodate latency)

            # validate and constraint settings
            if self.timeout_connect < 3:
                raise Exception('timeout_connect value (%d) less than 3; increase' % self.timeout_connect)
            if self.timeout_read < 1:
                raise Exception('timeout_read value shall be greater tha 1; increase')

        except Exception as e:
            raise Exception('%s' % e)
        return

    def read_config(self):
        '''
        read erddap section from config.yml; perform cursory checks on variables and values
        '''
        from ooiservices.config import settings
        if 'erddap' not in settings:
            raise Exception('erddap section not provided in config.yml')

        settings = settings['erddap']
        if not settings:
            raise Exception('erddap section empty in config.yml')

        # dictionary of each required config var and type
        vars = {'base_url': 'str', 'timeout_connect': 'int', 'timeout_read': 'int'}

        # verify existence and type of each var provided in config (types: { str | int }
        for var in vars.keys():
            if var not in settings:
                raise Exception('required setting (%s) not provided in cache section of config' % var)

            # verify type of each var provided
            if vars[var] == 'str':
                if not isinstance(settings[var], str):
                    raise Exception('%s value not type str' % var)
                if settings[var] == 'None':
                    raise Exception('%s has invalid value \'None\'' % var)
            elif vars[var] == 'int':
                if not isinstance(settings[var], int):
                    raise Exception('%s value not type int' % var)
            else:
                raise Exception('unsupported type (%s) used (%s); ' % (vars[var], var))

        return settings

