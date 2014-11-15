#!/usr/bin/env python
'''
ooiservices.controller.platform.py

PlatformController

'''

from ooiservices.controller.base import ObjectController, ListController
from ooiservices.model.platform import PlatformModel
from flask.ext.restful import Resource
from flask import request

__author__ = "Brian McKenna"

class PlatformObjectController(ObjectController):

    plat = PlatformModel()

    def __init__(self):
        ObjectController.__init__(self)

    def get(self, id):
        result = self.plat.read(id)
        # TODO: return HTTP 204 if no result
        #Formats the json dict to be used by the view:
        formatted_result = self.plat.filter_ooi_platforms(result)
        if formatted_result is None:
            formatted_result = result
        return formatted_result

    def put(self, id):
        args = request.args
        params = args.items()
        doc = {}
        if params:
            for item in params:
                doc[item[0]] = item[1]
        doc['id'] = id
        result = self.plat.update(doc)
        return result

    def delete(self, id):
        return self.plat.delete(id)

class PlatformListController(ListController):

    plat = PlatformModel()

    def get(self):
        result = self.plat.read()
        #Formats the json dict to be used by the view:
        formatted_result = self.plat.filter_ooi_platforms(result)
        return formatted_result
