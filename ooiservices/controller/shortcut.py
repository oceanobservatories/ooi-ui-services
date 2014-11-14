#!/usr/bin/env python
'''
ooiservices.controller.shortcut

A static JSON file for filling out the UI in the interim
'''

from ooiservices.controller.base import BaseController
from flask.ext.restful import Resource
from ooiservices.util.generate_json_from_db import generate
from ooiservices.util.parse_erddap_endpoints import get_times_for_stream
import json

class ShortcutController(Resource):

    def get(self):
        return generate()

class TimeController(Resource):

    def get(self, ref, stream):
        return get_times_for_stream(ref, stream)

