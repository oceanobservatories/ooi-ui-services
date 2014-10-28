from flask import request
from flask.ext.restful import Resource

from ooiservices.model.base import BaseModel

__author__ = "Brian McKenna"

class BaseController(Resource):

    """
    Implements Flask-RESTful Resource
    Provides HTTP methods GET/POST/DELETE/PUT
    
    Resources should be added to Flask app via:
        restful.Api.add_resource(FooController.List, '/foos')
        restful.Api.add_resource(FooController, '/foos/<string:id>')
    where:
        /foos accepts GET to return list of all objects and POST to create objects
        /foos/<id> acts on specific object and accepts GET/PUT/DELETE
    """

    def _model(adapter):
        """
        Implement _model to instantiate Model to be used by this controller
        """
        raise NotImplementedError()

    def __init__(self):
        """
        Controller requires a Model (providing the CRUD methods)
        Model requires an Adapter (providing persistence)
        - Adapter must be specified via configuration file (Application scoped)
        - Model instantiation must be provided by subclass using Adapter
        - HTTP methods are bound to the Model CRUD methods
        """

        super(Resource, self).__init__()

        # TODO get adapter from config
        adapter = None

        # instantiate model(adapter)
        model = _model(adapter)
        assert isinstance(model, BaseModel)

    def get(self, id):
        return 'GET OK - id: %s' % id

    def put(self, id):
        args = request.args
        return 'PUT OK - id: %s' % id

    def delete(self, id):
        return 'DELETE OK - id: %s' % id

    class List(Resource):

        def get(self):
            args = request.args
            return 'GET OK (list)'

        def post(self):
            args = request.form
            return 'POST OK'
