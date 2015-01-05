#!/usr/bin/env python
'''
ooiservices.routes

Routing for the service endpoints
'''
from flask import g, Response
from flask.ext import restful
from ooiservices import app
from config import extend_json


jsonp_api = restful.Api(app)
flask_api = restful.Api(app)

extend_json.support_jsonp(jsonp_api)

#jsonp classes
from ooiservices.controller.platform import PlatformObjectController, PlatformListController
from ooiservices.controller.instrument import InstrumentObjectController, InstrumentListController
from ooiservices.controller.array import ArrayObjectController, ArrayListController
from ooiservices.controller.erddap import ErddapObjectController
from ooiservices.controller.parameter import ParameterListController
from ooiservices.controller.stream import StreamObjectController, StreamListController
from ooiservices.controller.instrument_deployment import InstrumentDeploymentListController, InstrumentDeploymentObjectController
from ooiservices.controller.platform_deployment import PlatformDeploymentListController, PlatformDeploymentObjectController

#flask classes
from ooiservices.controller.user import UserAdd, UserLogin

# endpoints for jsonp (client side) requests.  Unsecure.  GET methods only.
jsonp_api.add_resource(ArrayListController, '/arrays')
jsonp_api.add_resource(ArrayObjectController, '/arrays/<string:id>')

jsonp_api.add_resource(PlatformListController, '/platforms')
jsonp_api.add_resource(PlatformObjectController, '/platforms/<string:id>')

jsonp_api.add_resource(InstrumentListController, '/instruments')
jsonp_api.add_resource(InstrumentObjectController, '/instruments/<string:id>')

jsonp_api.add_resource(InstrumentDeploymentListController, '/instrument_deployments')
jsonp_api.add_resource(InstrumentDeploymentObjectController, '/instrument_deployments/<string:id>')

jsonp_api.add_resource(PlatformDeploymentListController, '/platform_deployments')
jsonp_api.add_resource(PlatformDeploymentObjectController, '/platform_deployments/<string:id>')

jsonp_api.add_resource(StreamListController, '/streams')
jsonp_api.add_resource(StreamObjectController, '/streams/<string:id>')

jsonp_api.add_resource(ParameterListController, '/parameters')

jsonp_api.add_resource(ErddapObjectController, '/erddap/<string:id>')

# endpoints for Flask (server side) requests.  Secure. All supported methods.
#TODO, may need Brian M. to look at the logic of these routes.
flask_api.add_resource(UserAdd, '/user_add/<string:id>')
flask_api.add_resource(UserLogin, '/user/<string:id>')