#!/usr/bin/env python
'''
M2M app blueprint.

'''

__author__ = 'DanM'

from flask import Blueprint

m2m = Blueprint('m2m', __name__)

from ooiservices.app.m2m import routes, exceptions, common, help, help_tools, \
    help_data, help_data_12575, help_data_12576, help_data_12577, help_data_12578, \
    help_data_12580, help_data_12586, help_data_12587_asset, help_data_12587_events, \
    help_data_12587_status, help_data_12590, help_data_12591
