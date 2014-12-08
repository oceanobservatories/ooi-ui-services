#!/usr/bin/env python
'''
ooiservices.routes

Routing for the service endpoints
'''
from flask import g
from flask.ext import restful
from ooiservices import app


api = restful.Api(app)

from ooiservices.controller.platform import PlatformObjectController, PlatformListController
from ooiservices.controller.instrument import InstrumentObjectController, InstrumentListController
from ooiservices.controller.array import ArrayObjectController, ArrayListController
from ooiservices.controller.erddap import ErddapObjectController
from ooiservices.controller.parameter import ParameterListController
from ooiservices.controller.stream import StreamObjectController, StreamListController

# endpoints
api.add_resource(ArrayListController, '/arrays')
api.add_resource(ArrayObjectController, '/arrays/<string:id>')

api.add_resource(PlatformListController, '/platforms')
api.add_resource(PlatformObjectController, '/platforms/<string:id>')

api.add_resource(InstrumentListController, '/instruments')
api.add_resource(InstrumentObjectController, '/instruments/<string:id>')

api.add_resource(InstrumentDeploymentListController, '/instrument_deployments')
api.add_resource(InstrumentDeploymentController, '/instrument_deployments/<string:id>')

api.add_resource(PlatformDeploymentListController, '/platform_deployments')
api.add_resource(PlatformDeploymentController, '/platform_deployments/<string:id>')

api.add_resource(StreamListController, '/streams')
api.add_resource(StreamController, '/streams/<string:id>')

api.add_resource(ParameterListController, '/parameters')

api.add_resource(InstrumentListController, '/instrument')
api.add_resource(InstrumentObjectController, '/instrument/<string:id>')

api.add_resource(ErddapObjectController, '/erddap/<string:id>')

api.add_resource(StreamListController, '/stream')
api.add_resource(StreamObjectController, '/stream/<string:id>')