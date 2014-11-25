#!/usr/bin/env python
'''
ooiservices.model.erddap.py

ErddapModel
'''

from ooiservices.model.base import BaseModel
from ooiservices.model.cachemodel import CacheModel
from ooiservices.adaptor.rest import RestAdaptor
from flask import request, Response

__author__ = "Edna Donoughe"

class ErddapModel(BaseModel):
    '''
    Support erddap rest based interface; utilize RestAdaptor and CacheModel.
    TBD persistence added through additional SqlModel interface
    '''
    def __init__(self):
        self.init('erddap')

    def init(self, interface_name):
        try:
            self.cache_model = CacheModel()
            self.rest = RestAdaptor(interface_name)
        except Exception as e:
            raise Exception('erddap model __init_  exception: %s' % e)

    # CRUD methods
    def create(self, obj):
        '''
        do model specific create (rest.create), if successful; add key and value to cache
        '''
        # TBD self.rest.create(obj, query.string)
        result = self.cache_model.create(obj)
        return result

    def read(self, id):
        '''
        read value for id from cache; if not in cache, perform rest.read; if successful then cache it

        - if not in cache then retrieve value for id from rest endpoint; if successful then add to cache
        - return json results in response message
        - If id not found, return HTTP204 response
        - If error adding to cache, return error message response
        - If exception, return exception message response
        '''
        # try read from cache; if in cache, return result in response
        result = self.cache_model.read(id)
        if result:
            print 'retrieve from cache'
            return Response(result,status=200,headers= {'Content-Type': 'text/html; charset=utf-8'},
                            content_type='text/html; charset=utf-8')

        # not in cache then retrieve value for id from url
        print 'retrieve with url'
        try:
            result = self.rest.read(id, request.query_string)
            if not result:
                return self.response_HTTP404()
            if not result.data:
                return result   # result contains error response

            # update cache
            obj = {'key': str(id), 'value': result.data}
            self.cache_model.create(obj)

        except Exception as e:
            #print '%s' % e
            return self.response_HTTP500()  # custom error response?
        return result

    def update(self, obj):
        '''
        do model specific update (rest.update); if successful, update cache using key and value provided in obj.
        '''
        # TBD self.rest.update(obj, request.query_string)
        raise NotImplementError('erddap model update Not Implemented')

    def delete(self, id):
        '''
        - Issue the rest.delete, if successful, and id in cache, then also delete from cache; return success.
        - If error on delete, return error message response; do not delete from cache.
        - If delete successful and not in cache, return success.
        - If delete successful and in cache, delete from cache.
        - If error on delete from cache then report error message (what?)
        - If not found in cache to delete returns 204; if successful delete result == 1
        '''
        result = None
        try:
            if id:
                if self.rest.delete(id):
                    result = self.cache_model.delete(id)
                    if not result:
                        return self.response_HTTP204()
                else:
                    raise Exception('exception on delete id: %s' % str(id))
        except Exception, e:
            #print '%s' % e
            return self.response_HTTP500()  # custom error response?
        return result


