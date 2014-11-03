from ooiservices.controller.base import BaseController
from ooiservices.model.platform import PlatformModel
from flask.ext.restful import Resource

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
    
    class List(Resource):
        plat = PlatformModel()
        
        def get(self):
            return self.plat.read()
        
        def post(self):
            args = request.form
            return self.plat.read()