#!/usr/bin/env python
'''
ooiservices.routes

Routing for the service endpoints
'''
from flask.ext import restful
from ooiservices import app


api = restful.Api(app)

from ooiservices.controller.platform import PlatformObjectController, PlatformListController

# endpoints
api.add_resource(PlatformListController, '/platforms')
api.add_resource(PlatformObjectController, '/platforms/<string:id>')


