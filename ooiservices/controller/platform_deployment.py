#!/usr/bin/env python
'''
ooiservices.controller.platform_deployment

InstrumentController
'''
from flask import request
from ooiservices.controller.base import ObjectController, ListController
from ooiservices.model.platform_deployment import PlatformDeploymentModel



class PlatformDeploymentController(ObjectController):
    model = None

    def get(self, id):
        result = self.array_model.read({'id' : id})
        if not result:
            return self.response_HTTP204()
        return result[0]

class PlatformDeploymentListController(ListController):
    model = None

    def get(self):
        result = self.array_model.read(request.args)
        return result

def initialize_model():
    '''
    Initializes the model for the controllers
    this function is to be called by app
    '''
    PlatformDeploymentController.array_model = PlatformDeploymentModel()
    PlatformDeploymentListController.array_model = PlatformDeploymentModel()

