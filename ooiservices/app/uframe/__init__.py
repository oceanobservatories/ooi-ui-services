#!/usr/bin/env python
"""
uframe blueprint.

"""

__author__ = 'M@Campbell'

from flask import Blueprint

uframe = Blueprint('uframe', __name__)

from ooiservices.app.uframe import controller, data, assets, events, subscribe, \
    vocab, config, asset_tools,  event_tools, events_validate_fields, events_create_update, \
    deployment_tools, assets_validate_fields, common_tools, assets_create_update, common_convert, \
    cruise_tools, toc_tools, cruises
