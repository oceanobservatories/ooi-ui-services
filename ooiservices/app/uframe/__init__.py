#!/usr/bin/env python
"""
uframe blueprint.

"""

__author__ = 'M@Campbell'

from flask import Blueprint

uframe = Blueprint('uframe', __name__)

# Remove development_tools before placing in git.
from ooiservices.app.uframe import controller, data, subscribe, vocab, config, common_tools, \
    uframe_tools, gliders, toc, toc_tools, streams, stream_tools, common_convert,\
    assets, asset_tools, assets_remote_resources, asset_cache_tools, assets_validate_fields, assets_create_update,\
    events, event_tools, events_validate_fields, events_create_update, \
    deployments, deployment_tools, cruises, cruise_tools, \
    status, status_tools, status_tools_mock, images, image_tools
