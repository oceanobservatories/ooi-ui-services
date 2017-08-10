
"""
Data Availability routes.

Routes:

[GET]  /da/<string:rd>/<string:params>     # Get data availability for reference designator and optional params
"""
__author__ = 'Edna Donoughe'

from flask import request, jsonify, current_app
from ooiservices.app.main.authentication import auth
from ooiservices.app.decorators import scope_required
from ooiservices.app.main.errors import (bad_request, conflict, internal_server_error)
from ooiservices.app.uframe import uframe as api
from ooiservices.app.uframe.asset_tools import (verify_cache, _get_asset, _get_ui_asset_by_uid)
from ooiservices.app.uframe.event_tools import _get_events_by_id
from ooiservices.app.uframe.assets_create_update import (_create_asset, _update_asset)
from ooiservices.app.uframe.common_tools import (asset_edit_phase_values, boolean_values, get_asset_types_for_display,
                                                 get_supported_asset_types_for_display)
from ooiservices.app.uframe.uframe_tools import uframe_get_da_by_rd
from operator import itemgetter
import json

from ooiservices.app.uframe.asset_tools import assets_query_geojson


# Get data availability for reference designator.
@api.route('/available/<string:rd>', methods=['GET'])
def get_da_by_rd(rd):
    """ Get events for asset id. Optional type=[[event_type][,event_type, ...]]
    Sample requests:
        http://localhost:4000/uframe/da/CE02SHBP-LJ01D-06-CTDBPN106
    """
    try:
        # Get data availability for reference designator and optional params.
        # params = request.args.get('params')
        da = uframe_get_da_by_rd(rd, None)
        return jsonify(da)
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)
