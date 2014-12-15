#!/usr/bin/env python
'''
ooiservices.adaptor.rest.py

RestAdaptor
'''

from ooiservices.model.adaptor.base import BaseAdaptor
from flask import Response, jsonify, json
import requests

class RestAdaptor(BaseAdaptor):
    '''
    An adaptor that provides a rest based interface for json documents
    '''
    interface_name = None
    def __init__(self, interface_name):

        self.interface_name = interface_name
        try:
            self.get_settings()
        except Exception as e:
            raise Exception('RestAdaptor __init__ exception: %s' % e)

    def create(self, doc, query):
        '''
        Creates the document at rest endpoint; return id (success) or None (failure)
        '''
        pass

    def read(self, id, query):
        '''
        Reads the document from the rest endpoint; returns json (date or error message)
        '''
        try:
            result = self.url_get(id, query)
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

    def update(self, doc, query):
        '''
        Updates the specified document at rest endpoint; return status = {True | False}
        '''
        pass

    def delete(self, id):
        '''
        Deletes the specified document at rest endpoint; return status = {True | False}
        '''
        return  True

    # helper methods
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
            if not self.base_url:
                raise Exception('base_url empty')
            if self.timeout_connect < 3:
                raise Exception('timeout_connect value (%d) less than 3; increase' % self.timeout_connect)
            if self.timeout_read < 1:
                raise Exception('timeout_read value shall be greater tha 1; increase')

        except Exception as e:
            raise Exception('%s' % e)
        return

    def read_config(self):
        '''
        read section from config.yml for named interface; perform cursory checks on variables and values
        '''
        from ooiservices.config import settings
        if self.interface_name not in settings:
            raise Exception('%s section not provided in config.yml' % self.interface_name)

        settings = settings[self.interface_name]
        if not settings:
            raise Exception('%s section empty in config.yml' % self.interface_name)

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


