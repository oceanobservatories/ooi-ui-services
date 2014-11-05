#!/usr/bin/env python
'''
ooiservices.controller.platform.py

PlatformController

'''

from ooiservices.controller.base import BaseController
from ooiservices.model.platform import PlatformModel
from flask.ext.restful import Resource
from flask import request

#TODO: BaseController already does this
#from ooiservices.model.base import BaseModel

__author__ = "Brian McKenna"

class PlatformController(BaseController):
    
    #    def _model(adapter):
    #        return BaseModel() # TODO
    
    plat = PlatformModel()
    
    def __init__(self):
        BaseController.__init__(self)

    class List(Resource):
        plat = PlatformModel()
        
        def get(self):
            result = self.plat.read()
            formatted_result = self.plat.filter_ooi_platforms(result)
            return formatted_result
