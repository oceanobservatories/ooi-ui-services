from ooiservices.controller.base import BaseController
from ooiservices.model.platform import PlatformModel
from flask.ext.restful import Resource

#TODO: BaseController already does this
#from ooiservices.model.base import BaseModel

__author__ = "Brian McKenna"

class PlatformController(BaseController):

#    def _model(adapter):
#        return BaseModel() # TODO

    def __init__(self):
        super(BaseController, self).__init__()
    
    def get(self, id):
        plat = PlatformModel()
        return 'GET OK (%s)' % (plat.read(id))

    class List(Resource):
    
        def get(self):
            plat = PlatformModel()
            return 'GET OK (%s)' % (plat.read())
        
        def post(self):
            args = request.form
            return 'POST OK'