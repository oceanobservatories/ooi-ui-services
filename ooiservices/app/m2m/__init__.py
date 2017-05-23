#!/usr/bin/env python
'''
M2M app blueprint.

'''

__author__ = 'DanMarrggghhhh'

from flask import Blueprint

m2m = Blueprint('m2m', __name__)

from ooiservices.app.m2m import routes, exceptions, help, help_tools, \
    help_data, help_data_12575, help_data_12576, help_data_12577, help_data_12580, help_data_12586, \
    help_data_12587_asset, help_data_12587_events
