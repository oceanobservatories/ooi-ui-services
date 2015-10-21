#!/usr/bin/env python
'''
M2M app blueprint.

'''

__author__ = 'DanMarrggghhhh'

from flask import Blueprint

m2m = Blueprint('m2m', __name__)

from ooiservices.app.m2m import routes
