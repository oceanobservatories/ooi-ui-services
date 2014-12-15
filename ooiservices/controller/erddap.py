#!/usr/bin/env python
'''
ooiservices.controller.erddap.py

ErddapController

'''

from ooiservices.controller.base import ObjectController
from ooiservices.controller.base import ListController
from ooiservices.model.adaptor.erddap import ErddapModel

__author__ = "Edna Donoughe"

class ErddapObjectController(ObjectController):

    def __init__(self):
        ObjectController.__init__(self)
        try:
            self.model = ErddapModel()
        except Exception as e:
            raise Exception('erddap controller __init__: %s' % e)

    def get(self, id):
        try:
            result = self.model.read(id)
            if not result:
                result = self.response_HTTP204()
        except:
            result = self.response_HTTP500()
        return result

    def put(self, obj):
        raise NotImplementedError('erddap ObjectController put - Not Implemented')

    def delete(self, id):
        result = None
        try:
            if id:
                result = self.model.delete(id)
                if not result:
                    result = self.response_HTTP204()
        except Exception as e:
            #print '%s' % e
            result = self.response_HTTP500()
        return result

class ErddapListController(ListController):

    def __init__(self):
        ListController.__init__(self)
        self.model = ErddapModel()

    def get(self):
        raise NotImplementedError('erddap ListController get - Not Implemented')
