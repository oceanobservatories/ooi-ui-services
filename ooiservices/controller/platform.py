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
        super(BaseController, self).__init__()
    
    def get(self, id):
        return self.plat.read(id)
    
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
            return self.plat.read()
        
        def post(self):
            args = request.form
            return self.plat.read()