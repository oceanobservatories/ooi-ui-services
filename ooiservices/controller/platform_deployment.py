#!/usr/bin/env python
'''
ooiservices.controller.platform_deployment

InstrumentController
'''
from flask import request
from ooiservices.controller.base import ObjectController, ListController
from ooiservices.model.platform_deployment import PlatformDeploymentModel



class PlatformDeploymentObjectController(ObjectController):

    platform = PlatformDeploymentModel()

    def __init__(self):
        ObjectController.__init__(self)

    def get(self, id):
        result = self.platform.read(id)
        if not result:
            return self.response_HTTP204()
        return result

    def put(self, id):
        args = request.args
        params = args.items()
        doc = {}
        if params:
            for item in params:
                doc[item[0]] = item[1]
        doc['id'] = id
        result = self.platform.update(doc)
        return result

    def delete(self, id):
        return self.platform.delete(id)

class PlatformDeploymentListController(ListController):

        model = PlatformDeploymentModel()

    def get(self):
        args = request.args
        if args:
            result = self.process_args(self.model, args,'array_id')
        else:
            result = self.model.read()
        if not result:
            return self.response_HTTP204()
        return result

