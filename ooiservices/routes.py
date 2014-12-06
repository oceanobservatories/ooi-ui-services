#!/usr/bin/env python
'''
ooiservices.routes

Routing for the service endpoints
'''
from flask import g
from flask.ext import restful
from ooiservices import app


api = restful.Api(app)

from ooiservices.controller.platform import PlatformObjectController, PlatformListController, initialize_model as initialize_platform
from ooiservices.controller.instrument import InstrumentObjectController, InstrumentListController, initialize_model as initialize_instrument
from ooiservices.controller.array import ArrayObjectController, ArrayListController, initialize_model as initialize_array
from ooiservices.controller.instrument_deployment import InstrumentDeploymentController, InstrumentDeploymentListController, initialize_model as initialize_instrument_deployment
from ooiservices.controller.platform_deployment import PlatformDeploymentController, PlatformDeploymentListController, initialize_model as initialize_platform_deployment


# initialize model
@app.before_request
def initialize_model():
    if not getattr(g, 'model_initialized', False):
        initialize_platform()
        initialize_instrument()
        initialize_array()
        initialize_instrument_deployment()
        initialize_platform_deployment()
        g.model_initialized = True


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

