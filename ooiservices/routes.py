#!/usr/bin/env python
'''
ooiservices.routes

Routing for the service endpoints
'''
from flask.ext import restful
from ooiservices import app


api = restful.Api(app)

from ooiservices.controller.platform import PlatformObjectController, PlatformListController
from ooiservices.controller.instrument import InstrumentObjectController, InstrumentListController
from ooiservices.controller.array import ArrayObjectController, ArrayListController


# endpoints
api.add_resource(ArrayListController, '/arrays')
api.add_resource(ArrayObjectController, '/arrays/<string:id>')

api.add_resource(PlatformListController, '/platforms')
api.add_resource(PlatformObjectController, '/platforms/<string:id>')

api.add_resource(InstrumentListController, '/instruments')
api.add_resource(InstrumentObjectController, '/instruments/<string:id>')