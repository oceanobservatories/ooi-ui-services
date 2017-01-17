#!/usr/bin/env python
"""
uframe blueprint.

"""

__author__ = 'M@Campbell'

from flask import Blueprint

uframe = Blueprint('uframe', __name__)

from ooiservices.app.uframe import controller, data, subscribe, vocab, config, common_tools, \
    uframe_tools, gliders, toc, toc_tools, streams, stream_tools, common_convert,\
    assets, asset_tools, assets_remote_resources, asset_cache_tools, assets_validate_fields, assets_create_update,\
    events, event_tools, events_validate_fields, events_create_update, \
    deployments, deployment_tools, cruises, cruise_tools, \
    status, status_tools, images, image_tools