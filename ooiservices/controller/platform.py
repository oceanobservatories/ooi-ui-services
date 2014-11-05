#!/usr/bin/env python
'''
ooiservices.controller.platform.py

PlatformController

'''

from ooiservices.controller.base import BaseController
from ooiservices.model.platform import PlatformModel
from flask.ext.restful import Resource
from flask import request

__author__ = "Brian McKenna"

class PlatformController(BaseController):
    
    plat = PlatformModel()
    
    def __init__(self):
        BaseController.__init__(self)

    def get(self, id):
        result = self.plat.read(id)
        #Formats the json dict to be used by the view:
        formatted_result = self.plat.filter_ooi_platforms(result)
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
   
    class List(Resource):
        plat = PlatformModel()
        
        def get(self):
            result = self.plat.read()
            #Formats the json dict to be used by the view:
            formatted_result = self.plat.filter_ooi_platforms(result)
            return formatted_result