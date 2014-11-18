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
api.add_resource(ArrayListController, '/array')
api.add_resource(ArrayObjectController, '/array/<string:id>')

api.add_resource(PlatformListController, '/platform')
api.add_resource(PlatformObjectController, '/platform/<string:id>')

api.add_resource(InstrumentListController, '/instrument')
api.add_resource(InstrumentObjectController, '/instrument/<string:id>')