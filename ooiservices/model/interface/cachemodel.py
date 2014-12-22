#!/usr/bin/env python
'''
ooiservices.model.cachemodel.py

CacheModel
'''

from ooiservices.model.base import BaseModel
import memcache

__author__ = "Edna Donoughe"

class CacheModel(BaseModel):

    def __init__(self):
        '''
        read cache config settings and initialize instance variables; initialize memcache client
        '''
        try:
            self.get_settings()
            self.client = self.get_client()
            if not self.client:
                raise Exception('CacheModel: failed to initialize memcache.Client: %s' % e)

        except Exception:
            raise Exception('CacheModel: __init__ error: %s' % e)

    # CRUD methods
    def create(self, obj):
        '''
        create key in cache. If key (provided in obj) is not in cache, then add to cache
        '''
        result = None
        key, value = self.get_key_value(obj)
        if key:
            # if already in cache, this is update, not create; do client.get(key)? TBD
            tmp = self.client.set(key, value, self.expiry)
            if tmp:
                result = 1
        return result

    def read(self, key):
        '''
        read key from cache. if key is in cache, return value; otherwise return None
        '''
        value = None
        if key:
            key = str(key)
            value = self.client.get(key)
        return value

    def update(self, obj):
        '''
        update cache using key and value provided in obj; if key == None, result = None
        if key does not exist, return result == 0 (do not create); if update successful, result == 1
        Note: only update value if key exists, if key does not exist, do not create - instead return None
        '''
        result = None
        key, value = self.get_key_value(obj)
        if key:
            tmp = self.client.get(key)
            if tmp:
                self.client.set(key, value, self.expiry)
                result = 1
            else:
                result = 0
        return result

    def delete(self, key):
        '''
        delete key from cache; success == 1, failure == 0; if key invalid or not found, result == None
        '''
        result = None
        if key:
            key = str(key)
            # determine if key exists in cache before delete
            tmp = self.client.get(key)
            if tmp:
                self.client.delete(key)
                result = 1
            else:
                result = 0
        return result

    #- - - - - - - - - - - - - - - - - -
    # helper methods
    #- - - - - - - - - - - - - - - - - -
    def get_client(self):
        try:
            mc = memcache.Client([(self.host, self.port)], debug=self.debug)
        except:
            mc = None
        return mc

    def get_key_value(self,obj):
        '''
        get key and value from input obj dictionary; return key, value where key returned as a str
        '''
        key = None
        value = None
        if 'key' in obj and 'value' in obj:
            key = obj['key']
            value = obj['value']
        return str(key), value

    def get_settings(self):
        '''
        read config and provide validated instance variables; validate and constraint settings (TBD)
        '''
        try:
            settings = self.read_config()
            self.port     = settings['port']     # (int)
            self.host     = settings['host']     # (str)
            self.expiry   = settings['expiry']   # (int)
            self.debug    = settings['debug']    # (int)
            self.min_compress_len = settings['min_compress_len'] # (int)

        except Exception as e:
            raise Exception('%s' % e)

        return

    def read_config(self):
        '''
        read cache section from config.yml; process and validate content from config
        '''
        from ooiservices.config import settings
        if 'cache' not in settings:
            raise Exception('cache section not provided in config.yml')

        settings = settings['cache']
        if not settings:
            raise Exception('cache section empty in config.yml')

        # dictionary of each required config var and type
        vars = {'port': 'int', 'host': 'str', 'expiry': 'int', 'min_compress_len': 'int', 'debug': 'int'}

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