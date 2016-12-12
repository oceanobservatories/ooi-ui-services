
"""
Asset Management - Status routes.

Routes:

[GET]  /status/arrays                               # Get status for all arrays.
[GET]  /status/sites/<string:array_rd>              # Get status for sites associated with an array.
[GET]  /status/platforms/<string:site_rd>           # Get status for platforms associated with a site.
[GET]  /status/instrument/<string:instrument_rd>    # Get instrument status.

"""
__author__ = 'Edna Donoughe'

from flask import jsonify, current_app
from ooiservices.app.main.errors import bad_request
from ooiservices.app.uframe import uframe as api
from ooiservices.app.uframe.status_tools import (_get_status_arrays, _get_status_sites,
                                                 _get_status_platforms, _get_status_instrument)


# Get status for all arrays.
@api.route('/status/arrays', methods=['GET'])
def get_status_arrays():
    """ Get status information for arrays.
    Sample request: http://localhost:4000/uframe/status/arrays
    """
    results = []
    try:
        data = _get_status_arrays()
        if data and data is not None:
            results = data
        return jsonify({'arrays': results})
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get status for sites associated with an array.
@api.route('/status/sites/<string:array_rd>', methods=['GET'])
def get_status_sites(array_rd):
    """ Get status for sites associated with an array.
    Sample request: http://localhost:4000/uframe/status/sites/CE
    """
    results = []
    try:
        data = _get_status_sites(array_rd)
        if data and data is not None:
            results = data
        return jsonify({'sites': results})
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get statuses for platforms associated with a site.
@api.route('/status/platforms/<string:site_rd>', methods=['GET'])
def get_status_platforms(site_rd):
    """ Get statuses for platforms associated with a site.
    Sample request: http://localhost:4000/uframe/status/platforms/CE01ISSM
    """
    results = []
    try:
        #data = _nav_get_platforms(site_rd)
        data = _get_status_platforms(site_rd)
        if data and data is not None:
            results = data
        return jsonify({'platforms': results})
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)


# Get instrument status.
@api.route('/status/instrument/<string:instrument_rd>', methods=['GET'])
def get_status_instrument(instrument_rd):
    """ Get instrument status.
    Sample request: http://localhost:4000/uframe/status/instrument/CE01ISSM-SBD17-03-DOSTAD000
    """
    results = []
    try:
        data = _get_status_instrument(instrument_rd)
        if data and data is not None:
            results = data
        return jsonify({'instrument': results})
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)

#======================================================
'''
# Get assets.
@api.route('/new_assets', methods=['GET'])
def new_get_assets():
    """ Get list of all uframe assets, optionally filtered by request,args criteria below, and formatted for UI display.

    Request arguments supported:
    1. request.arg:  'min'              (bool)  Sample request: http://localhost:4000/uframe/assets?min=true
    2. request.arg:  'sort'             (str)   Asset attribute name, for instance 'ref_des'.
    3. request.args: 'startAt', 'count' (int)   Point to begin slice and count to slice for assets list to return.
    4. request.arg:  'geoJSON'          (bool)  If true, show list of dicts for mooring and/or platform.
                                                Sample request: http://localhost:4000/uframe/assets?geoJSON=true
                                                Sample response:
                                                    {
                                                      "assets": [
                                                        {
                                                          "array_id": "CP",
                                                          "display_name": "Central Surface Mooring",
                                                          "geo_location": {
                                                            "coordinates": [
                                                              -70.7715,
                                                              40.1398
                                                            ],
                                                            "depth": 0.0
                                                          },
                                                          "maxdepth": 133.0,
                                                          "mindepth": 0.0,
                                                          "reference_designator": "CP01CNSM"
                                                        },
                                                        . . .
                                                    }
    """
    debug = True
    try:
        # Verify asset information available before continuing, if failure raise internal server error.
        try:
            data = verify_cache()
            if not data:
                message = 'Failed to get assets.'
                raise Exception(message)
        except Exception as err:
            message = str(err)
            current_app.logger.info(message)
            return internal_server_error(message)

        # Determine field to sort by, sort asset data (ooi-ui-services format. On bad field, raise exception.
        sort_by = ''
        try:
            if request.args.get('sort') and request.args.get('sort') != "":
                sort_by = str(request.args.get('sort'))
            else:
                sort_by = 'ref_des'
            data = sorted(data, key=itemgetter(sort_by))
        except Exception as err:
            message = 'Unknown element to sort assets by \'%s\'. %s' % (sort_by, str(err))
            current_app.logger.info(message)
            raise Exception(message)

        # If using minimized ('min') or use_min, then strip asset data
        if request.args.get('min') == 'True':
            for obj in data:
                if 'manufactureInfo' in obj:
                    del obj['manufactureInfo']
                if 'notes' in obj:
                    del obj['notes']
                if 'physicalInfo' in obj:
                    del obj['physicalInfo']
                if 'purchaseAndDeliveryInfo' in obj:
                    del obj['purchaseAndDeliveryInfo']
                if 'lastModifiedTimestamp' in obj:
                    del obj['lastModifiedTimestamp']
                if 'partData' in obj:
                    del obj['partData']
                if 'remoteResources' in obj:
                    del obj['remoteResources']

        # Create toc information using geoJSON=true
        geoJSON = False
        if request.args.get('geoJSON') and request.args.get('geoJSON') != "":
            geoJSON = True
        data = _get_assets(use_min=False, sort=None, geoJSON=geoJSON)

        # Both the startAt and count parameters must be provide to get a slice.
        if ( (request.args.get('startAt') and not request.args.get('count')) or
             (not request.args.get('startAt') and request.args.get('count')) ):
            message = 'Both \'startAt\' and \'count\' are required to provide a slice of response data.'
            raise Exception(message)

        if request.args.get('startAt') and request.args.get('count'):
            start_at = int(request.args.get('startAt'))
            count = int(request.args.get('count'))
            total = int(len(data))
            data_slice = data[start_at:(start_at + count)]
            result = jsonify({"count": count,
                              "total": total,
                              "startAt": start_at,
                              "assets": data_slice})
            return result

        result = jsonify({'assets': data})
        return result
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)
'''