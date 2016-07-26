#!/usr/bin/env python
"""
uframe blueprint.

"""

__author__ = 'M@Campbell'

from flask import Blueprint

uframe = Blueprint('uframe', __name__)

from ooiservices.app.uframe import controller, assetController, data, assets, events, subscribe, \
    vocab, asset_tools, config, events_storage, events_unspecified, events_atvendor, events_asset_status, \
    events_retirement, events_integration, events_location, events_cruise_info, event_tools, deployment_tools
