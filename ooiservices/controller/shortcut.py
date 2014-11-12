#!/usr/bin/env python
'''
ooiservices.controller.shortcut

A static JSON file for filling out the UI in the interim
'''

from ooiservices.controller.base import BaseController
from flask.ext.restful import Resource
from ooiservices.util.generate_json_from_db import generate
import json

class ShortcutController(Resource):

    def get(self):
        return generate()


