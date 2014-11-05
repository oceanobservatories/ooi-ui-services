#!/usr/bin/env python
'''
ooiservices.routes

Routing for the service endpoints
'''
from flask.ext import restful
from ooiservices import app


api = restful.Api(app)
from ooiservices.controller.platform import PlatformController

# endpoints
api.add_resource(PlatformController.List, '/platforms')
api.add_resource(PlatformController, '/platforms/<string:id>')


