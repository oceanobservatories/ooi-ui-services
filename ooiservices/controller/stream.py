#!/usr/bin/env python
'''
ooiservices.controller.stream

StreamObjectController
StreamListController
'''

from ooiservices.controller.base import ObjectController, ListController
from ooiservices.model.stream import StreamModel
from ooiservices.config import ERDDAPURL
from ooiservices import app
from flask import request
from flask.ext.restful import Resource

import re
import time
import requests

CACHE_UPDATE = None
META_OUTLINE = None

class StreamController(ObjectController):

    model = StreamModel()

    def __init__(self):
        ObjectController.__init__(self)

    def get(self,id):
        result = self.model.read(id)
        if not result:
            return self.response_HTTP204()
        return result

class StreamListController(ListController):

    model = StreamModel()

    def get(self):
        args = request.args
        if args:
            result = self.process_args(self.model, args,'stream_id')
        else:
            result = self.model.read()
        if not result:
            return self.response_HTTP204()
        return result