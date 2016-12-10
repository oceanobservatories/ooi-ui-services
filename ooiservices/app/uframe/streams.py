#!/usr/bin/env python

"""
Support for uframe stream route(s), utilized for stream information.
"""
__author__ = 'Edna Donoughe'


from flask import (jsonify, request, current_app)
from ooiservices.app import cache
from ooiservices.app.uframe import uframe as api
from ooiservices.app.main.errors import (internal_server_error, bad_request)
from ooiservices.app.uframe.stream_tools import get_stream_list
from operator import itemgetter
from copy import deepcopy
from ooiservices.app.uframe.common_tools import iso_to_timestamp
from ooiservices.app.models import DisabledStreams


@api.route('/stream')
@cache.memoize(timeout=1600)
def get_streams_list():
    """ Get streams (list of dictionaries); used in the data catalog.

    List of request.args used in this function:
        'sort', 'order', 'min', 'concepts', 'search', 'startDate', 'endDate' and 'startAt'

    Sample response data (abbreviated):
    {
      "streams": [
        {
          "array_name": "Station Papa",
          "assembly_name": "Mooring Riser",
          "cruise_number": null,
          "deployment_number": 3,
          "depth": "NaN",
          "display_name": "Seawater pH",
          "download": {
            "csv": "api/uframe/get_csv/recovered-inst_phsen-abcdef-metadata/GP03FLMA-RIS01-04-PHSENF000",
            "json": "api/uframe/get_json/recovered-inst_phsen-abcdef-metadata/GP03FLMA-RIS01-04-PHSENF000",
            "netcdf": "api/uframe/get_netcdf/recovered-inst_phsen-abcdef-metadata/GP03FLMA-RIS01-04-PHSENF000",
            "profile": "api/uframe/get_profiles/recovered-inst_phsen-abcdef-metadata/GP03FLMA-RIS01-04-PHSENF000"
          },
          "end": "2040-02-05T12:25:32.000Z",
          "lat_lon": null,
          "long_display_name": "Station Papa Flanking Subsurface Mooring A - Mooring Riser - Seawater pH",
          "parameter_display_name": [
            "Time, UTC",
            "Port Timestamp, UTC",
            "Driver Timestamp, UTC",
            "Internal Timestamp, UTC",
            "Preferred Timestamp",
            "Record Type",
            . . .
          ],
          "parameter_id": [
            "pd7",
            "pd10",
            "pd11",
            "pd12",
            "pd16",
            "pd355",
            . . .
          ],
          "platform_name": "Flanking Subsurface Mooring A",
          "reference_designator": "GP03FLMA-RIS01-04-PHSENF000",
          "site_name": "Flanking Subsurface Mooring A",
          "start": "1904-01-01T18:50:57.000Z",
          "stream_display_name": null,
          "stream_name": "recovered-inst_phsen-abcdef-metadata",
          "stream_type": "recovered-inst",
          "units": [
            "seconds since 1900-01-01",
            "seconds since 1900-01-01",
            "seconds since 1900-01-01",
            "seconds since 1900-01-01",
            "1",
            "1",
            . . .
          ],
          "variable_type": [
            "double",
            "double",
            "double",
            "double",
            "string",
            "ubyte",
            . . .
          ],
          "variable_types": {},
          "variables": [
            "time",
            "port_timestamp",
            "driver_timestamp",
            "internal_timestamp",
            "preferred_timestamp",
            "record_type",
            . . .
          ],
          "variables_shape": [
            "scalar",
            "scalar",
            "scalar",
            "scalar",
            "scalar",
            "scalar",
            . . .
          ]
        },
    """
    retval = get_stream_list()
    if not retval or retval is None:
        message = 'The stream list did not return a value.'
        return internal_server_error(message)
    try:
        is_reverse = True
        if request.args.get('sort') and request.args.get('sort') != "":
            sort_by = request.args.get('sort')
            if request.args.get('order') and request.args.get('order') != "":
                order = request.args.get('order')
                if order == 'reverse':
                    is_reverse = False
        else:
            sort_by = 'end'
        retval = sorted(retval, key=itemgetter(sort_by), reverse=is_reverse)
    except (TypeError, KeyError) as e:
        return retval

    # lets create a container to work with
    temp_list = []

    # instantiate a disabled streams model cursor
    disabled_streams = DisabledStreams().query.all()

    # grab the json from the instance of all it's data
    disabled_streams = [disabled_stream.to_json() \
                        for disabled_stream in disabled_streams]

    # look over each of the items in the disabled streams
    '''
    @param search_terms:
        the list of strings that will be searched against
    @param data_set:
        the main data being parsed
    '''
    def _parse_lists(search_terms, data_set):
        included_streams = []

        '''
        @param term:
            The search term that will be checking aginst
        @param subset:
            The data being searched
        @param length:
            A very specific argument for choosing what part of the reference
            designator to use
        '''
        def _gen(term, subset, length):
            result = []
            for obj in subset:
                if obj['reference_designator'][:length] not in term:
                    result.append(obj)
            return result

        for stream in search_terms:

            # establish a match criteria, so we know at what level to delete
            match_on = len(stream['refDes'])

            # TODO: Refactor this to use a method
            if match_on == 2:
                if len(included_streams) is 0:
                    included_streams = _gen(stream['refDes'], data_set, match_on)
                else:
                    included_streams = _gen(stream['refDes'], included_streams, match_on)

            elif match_on == 8:
                if len(included_streams) is 0:
                    included_streams = _gen(stream['refDes'], data_set, match_on)
                else:
                    included_streams = _gen(stream['refDes'], included_streams, match_on)

            elif match_on == 11:
                if len(included_streams) is 0:
                    included_streams = _gen(stream['refDes'], data_set, match_on)
                else:
                    included_streams = _gen(stream['refDes'], included_streams, match_on)

            elif match_on == 27:
                if len(included_streams) is 0:
                    included_streams = _gen(stream['refDes'], data_set, match_on)
                else:
                    included_streams = _gen(stream['refDes'], included_streams, match_on)

        if len(included_streams) is 0:
            return data_set

        return included_streams

    retval = _parse_lists(disabled_streams, retval)

    # If 'min' is provided and enabled, the filter the data.
    if request.args.get('min') == 'True':
        for obj in retval:
            try:
                if 'parameter_id' in obj:
                    del obj['parameter_id']
                if 'units' in obj:
                    del obj['units']
                if 'variable_type' in obj:
                    del obj['variable_type']
                if 'variable_types' in obj:
                    del obj['variable_types']
                if 'download' in obj:
                    del obj['download']
                if 'variables' in obj:
                    del obj['variables']
                if 'variables_shape' in obj:
                    del obj['variables_shape']
            except KeyError as e:
                print e

    # If 'concepts' provided, then filter the data
    if request.args.get('concepts') and request.args.get('concepts') != "":
        return_list = []
        search_term = str(request.args.get('concepts')).split()
        search_set = set(search_term)
        for subset in search_set:
            for item in retval:
                if subset.lower() in str(item['reference_designator']).lower():
                    return_list.append(item)
        retval = return_list

    # If 'search' parameter(s) provided, then filter the data.
    if request.args.get('search') and request.args.get('search') != "":
        return_list = []
        search_term = str(request.args.get('search')).split()
        search_set = set(search_term)
        for subset in search_set:
            if len(return_list) > 0:
                ven_subset = []
                ven_set = deepcopy(retval)
                for item in ven_set:
                    if subset.lower() in str(item['array_name']).lower():
                        ven_subset.append(item)
                    elif subset.lower() in str(item['site_name']).lower():
                        ven_subset.append(item)
                    elif subset.lower() in str(item['assembly_name']).lower():
                        ven_subset.append(item)
                    elif subset.lower() in str(item['reference_designator']).lower():
                        ven_subset.append(item)
                    elif subset.lower() in str(item['stream_name']).lower():
                        ven_subset.append(item)
                    elif 'platform_name' in item:
                        if subset.lower() in str(item['platform_name']).lower():
                            ven_subset.append(item)
                    elif 'parameter_display_name' in item:
                        if subset.lower() in str(item['parameter_display_name']).lower():
                            ven_subset.append(item)
                    elif 'long_display_name' in item:
                        if subset.lower() in str(item['long_display_name']).lower():
                            ven_subset.append(item)
                    """
                    elif subset.lower() in str(item['platform_name']).lower():
                                ven_subset.append(item)
                    elif subset.lower() in str(item['parameter_display_name']).lower():
                        ven_subset.append(item)
                    elif subset.lower() in str(item['long_display_name']).lower():
                        ven_subset.append(item)
                    """
                retval = ven_subset
            else:
                for item in retval:
                    if subset.lower() in str(item['array_name']).lower():
                        return_list.append(item)
                    elif subset.lower() in str(item['site_name']).lower():
                        return_list.append(item)
                    elif subset.lower() in str(item['assembly_name']).lower():
                        return_list.append(item)
                    elif subset.lower() in str(item['reference_designator']).lower():
                        return_list.append(item)
                    elif subset.lower() in str(item['stream_name']).lower():
                        return_list.append(item)
                    elif 'platform_name' in item:
                        if subset.lower() in str(item['platform_name']).lower():
                            return_list.append(item)
                    elif 'parameter_display_name' in item:
                        if subset.lower() in str(item['parameter_display_name']).lower():
                            return_list.append(item)
                    elif 'long_display_name' in item:
                        if subset.lower() in str(item['long_display_name']).lower():
                                return_list.append(item)
                    """
                    elif subset.lower() in str(item['platform_name']).lower():
                        return_list.append(item)
                    elif subset.lower() in str(item['parameter_display_name']).lower():
                        return_list.append(item)
                    elif subset.lower() in str(item['long_display_name']).lower():
                        return_list.append(item)
                    """
                retval = return_list

    # If 'startDate' and 'endDate' provided, then use to filter the data.
    if request.args.get('startDate') and request.args.get('endDate') != "":
        # setup a temporary container for the result and convert the time
        return_val = []
        search_start_date = float(request.args.get('startDate'))/1000.0
        search_end_date = float(request.args.get('endDate'))/1000.0

        # loop over the current return value and begin parsing
        for obj in retval:
            obj_end_date = iso_to_timestamp(obj['end'])
            # add to the return_val if the obj has a end date
            # greater than or equal to 'startDate' and an end date
            # less than or equal to 'endDate'
            # ** we are only filtering by END date **
            if obj_end_date >= search_start_date and obj_end_date <= search_end_date:
                return_val.append(obj)

        # assign the new list to retval
        retval = return_val

    # If 'startAt' provided, then use to filter the data.
    if request.args.get('startAt'):
        start_at = int(request.args.get('startAt'))
        count = int(request.args.get('count'))
        total = int(len(retval))
        retval_slice = retval[start_at:(start_at + count)]
        result = jsonify({"count": count,
                            "total": total,
                            "startAt": start_at,
                            "streams": retval_slice})
        #return result
        return jsonify(streams=result)
    else:
        return jsonify(streams=retval)


@api.route('/build_stream_cache')
def build_stream_cache():
    """ Force stream cache build. (Streams currently (celery) set to build every hour on the hour.)
    Responses:
        Success:
        {
          "build_stream_cache": true
        }

        Failure:
        {
          "build_stream_cache": false
        }
    """
    success = False
    try:
        streams = get_stream_list(refresh=True)
        if streams and streams is not None and 'error' not in streams:
            stream_cache = cache.get('stream_list')
            if stream_cache and stream_cache is not None and "error" not in stream_cache:
                success = True
        return jsonify({'build_stream_cache': success}), 200
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return bad_request(message)