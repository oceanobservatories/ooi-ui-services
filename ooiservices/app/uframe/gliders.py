#!/usr/bin/env python
"""
uframe endpoints for gliders.
"""
from flask import jsonify, request, current_app, make_response
from ooiservices.app import cache
from ooiservices.app.uframe.config import get_cache_timeout
from ooiservices.app.uframe import uframe as api

from datetime import datetime
import numpy as np
import time
import requests
import requests.adapters
import requests.exceptions
from requests.exceptions import (ConnectionError, Timeout)
from ooiservices.app.uframe.config import get_uframe_info

#CACHE_TIMEOUT = 172800
COSMO_CONSTANT = 2208988800


# @auth.login_required
@api.route('/get_glider_tracks')
def get_uframe_glider_track():
    """ Get glider tracks.
    """
    try:
        """
        cached = cache.get('glider_tracks')
        will_reset_cache = False
        will_update_using_cache = False

        if request.args.get('update') == 'true':
            #i.e "update only"
            will_update_using_cache = True
        if request.args.get('reset') == 'true':
            will_reset_cache = True
            will_update_using_cache = False

        if cached and not(will_reset_cache) and not (will_update_using_cache):
            data = cached
        else:
            data = _compile_glider_tracks(will_update_using_cache)

            if "error" not in data:
                cache.set('glider_tracks', data, timeout=get_cache_timeout())
        """
        data = None
        return jsonify({"gliders": data})
    except requests.exceptions.ConnectionError as e:
        error = "Error: Cannot connect to uframe.  %s" % e
        print error
        return make_response(error, 500)


def _check_for_gps_position_stream(glider_url,glider_stream,glider_method):
    """ Used to check if a desired stream is available.
    """
    url = glider_url+"/metadata"
    req_gps_info_list = requests.get(url)
    metadata = req_gps_info_list.json()
    time_list = metadata['times']
    param_list = metadata['parameters']

    selected_method = None
    selected_stream = None
    selected_times = None
    selected_depth = None

    for t in time_list:
        #use the selected one when found
        if glider_method == t['method'] and glider_stream == t['stream']:
            selected_method = t['method']
            selected_stream = t['stream']
            selected_times = {"begin_time": t["beginTime"],
                              "end_time": t["endTime"],
                              "last_updated": None,
                              "last_requested": None}
            break

    #WE ALWAYS NEED M_DEPTH - as its an ENG instrument
    for p in param_list:
        if p['stream'] == selected_stream:
            #identify depth
            if p['particleKey'] == "m_depth":
                selected_depth = p
            #available_depth_list = ['sci_water_pressure','m_pressure','m_depth','int_ctd_pressure']
            #if p['particleKey'] in available_depth_list:
            #    selected_depth = p
            #    break

    return selected_method,selected_stream,selected_times,selected_depth


def _select_glider_method(available_glider_methods):
    if "recovered_host" in available_glider_methods:
        return "recovered_host",True
    elif "telemetered" in available_glider_methods:
        return "telemetered",False
    return None,None


def _get_glider_track_data(glider_outline,glider_cache=None):
    """ Get the glider track information from uframe

        glider_outline: is the currently obtained gliders from uframe
        glider_cache  : are the cached gliders we already have in the store!
    """
    gliders_to_update = []
    glider_skips = []
    data_limit  = 1000

    if glider_cache is not None:
        #gets the gliders to skip and update. Updated gliders will use the last updated time to update the track from
        glider_skips, gliders_to_update = _get_existing_glider_ids_to_skip(glider_cache)

    t0 = time.time()
    for glider_track in glider_outline:
        try:

            if glider_track['depth'] is not None:
                data_request_str = "?limit="+ str(data_limit) + '&parameters='+glider_track['depth']['pdId']
            else:
                data_request_str = "?limit="+ str(data_limit)

                if glider_track['location'] in glider_skips:
                    #get the historic data, and add it to the glider info
                    for gl in glider_cache:
                        if glider_track['location'] == gl['location']:
                            existing_data = gl
                            if 'track' in existing_data:
                                glider_track['track'] = existing_data['track']
                            if 'metadata' in existing_data:
                                glider_track['metadata'] = existing_data['metadata']
                            if 'times' in existing_data:
                                glider_track['times'] = existing_data['times']
                            break

                else:
                    #if dont skip it, i.e not recovered then try processing it
                    #try and get some additional engineering data for the glider
                    glider_track = _get_additional_data(glider_track)

                    if glider_track['location'] not in gliders_to_update:
                        #if the glider is not in the update list get as much as we can
                        r = requests.get(glider_track['url']+data_request_str)
                        #loop through the returned data
                        track_data = _extract_glider_track_from_data(r.json(),glider_track['depth'])
                        glider_track['track'] = track_data
                        #when was the track updated
                        glider_track['times']['last_updated'] = str(datetime.utcnow())
                        #that last time of the track
                        glider_track['times']['last_requested'] = glider_track['track']['times'][-1] - COSMO_CONSTANT
                    else:
                        print "...exists already..update..."
                        #get the existing
                        existing_data = None
                        for gl in glider_cache:
                            if glider_track['location'] == gl['location']:
                                existing_data = gl
                                break

                        dt_old = datetime.strptime(existing_data['times']['end_time'], '%Y-%m-%dT%H:%M:%S.%fZ')
                        dt_new = datetime.strptime(glider_track['times']['end_time'], '%Y-%m-%dT%H:%M:%S.%fZ')
                        #print "old:",dt_old,"\t","new:",dt_new
                        #if the existing data, has the same stream metadata info just use the cache
                        if dt_old != dt_new: #and existing_data['track']['time'][-1] == glider_track['track']['time'][-1]:
                            #if they don't match, get the new data using the: old end, and the new end
                            start_req = "&startdt=" + existing_data['times']['end_time']
                            end_req = "&enddt="   + glider_track['times']['end_time']

                            r = requests.get(glider_track['url']+data_request_str+start_req+end_req)
                            track_data = _extract_glider_track_from_data(r.json(),glider_track['depth'])

                            #set, the track data to be the cache and add the new data in
                            glider_track['track'] = existing_data['track']
                            print "####### adding data......"

                            data_keys = ['depths','coordinates','times']

                            for key in glider_track['track'].keys():
                                if key in data_keys:
                                    try:
                                        glider_track['track'][key].extend(track_data[key])
                                    except Exception,e:
                                        raise KeyError('Error adding new track data to ('+key+')')
                        else:
                            #dont update the track use the cache
                            glider_track['track'] = existing_data['track']
                            glider_track['metadata'] = existing_data['metadata']
                            glider_track['times']['last_updated'] = existing_data['times']['last_updated']
                            glider_track['times']['last_requested'] = glider_track['track']['times'][-1] - COSMO_CONSTANT

            t1 = time.time()
            print t1-t0, " secs to complete..."
            return glider_outline
        except Exception as e:
            print e
            pass


def _get_existing_glider_ids_to_skip(glider_cache):
    """ Quick pass to identify glider entries that we can skip due to it being recovered.
        Also identifies gliders we wish we update, i.e telemetered gliders
    """
    locations_to_skip = []
    locations_to_update = []
    for g in glider_cache:
        #if its recovered we can skip it as
        #if not we should add the most up to date date for the track
        if g['is_recovered']:
            #add to the skip list and move on, as its recovered
            locations_to_skip.append(g['location'])
            continue

        #if there is no track or length (0) try and get it "all", using the default limit
        if 'track' not in g or g['track'] is None or len(g['track']) == 0:
            #if there was no data, dont do anything as we want another chance to get the data
            pass
        else:
            locations_to_update.append(g['location'])

    print "cache:",len(locations_to_update),len(locations_to_skip),len(glider_cache)
    return locations_to_skip,locations_to_update,


def _extract_glider_track_from_data(track_data, glider_depth=None):
    """ Loop through the response and create the line track.
    """
    lat_field = "latitude"
    lon_field = "longitude"
    bar_to_m = 0.09804139432

    coors = []
    dt = []
    depths = []
    glider_depth_units = None
    has_depth = False

    for row in track_data:
        try:

            has_lon   = not np.isnan(row[lon_field])
            if row[lon_field] >= 180 or row[lon_field] <= -180 :
                has_lon = False

            has_lat   = not np.isnan(row[lat_field])
            if row[lat_field] >= 90 or row[lat_field] <= -90:
                has_lat = False

            if glider_depth is not None:
                has_depth = not np.isnan(row[glider_depth['particleKey']])

            if has_lat and has_lon: #and has_depth and (float(row[depth_field]) != -999):
                #add position

                coors.append([row[lon_field], row[lat_field]])
                dt.append(row['pk']['time'])
                #add depth if available and not nan
                if (has_depth and
                    (float(row[glider_depth['particleKey']])) != -999 and
                     (float(row[glider_depth['particleKey']])) != float(glider_depth['fillValue'])):

                    if glider_depth['units'] == "bar":
                        depths.append(row[glider_depth['particleKey']] * bar_to_m)
                        glider_depth_units = "m"
                    elif glider_depth_units == "m":
                        depths.append(row[glider_depth['particleKey']])
                else:
                    depths.append(-999)

            return {"name":row['pk']['subsite']+"-"+row['pk']['node'],
                                     "reference_designator": row['pk']['subsite']+"-"+row['pk']['node']+"-"+row['pk']['sensor'],
                                     "type": "LineString",
                                     "coordinates" : coors,
                                     "times": dt,
                                     "units": glider_depth_units,
                                     "depths": depths}
        except Exception as e:
            #print e
            pass


def _get_additional_data(glider_track):
    """ Get additional data for a glider stream, [battery, vacuum, m_speed[] information.
    """
    #see if its recovered, create desired stream
    search_stream = None
    if glider_track['is_recovered'] == True:
        search_stream = "glider_eng_recovered"
        search_method = "recovered_host"
    else:
        search_stream = "glider_eng_telemetered"
        search_method = "telemetered"

    #check its available
    if search_stream in glider_track['available_streams']:
        #get the additional metadata fields
        url = glider_track['glider_metadata_url']+"/metadata"
        req_addit_info_list = requests.get(url)
        metadata = req_addit_info_list.json()
        param_list = metadata['parameters']

        #get the metadata for the extra fields
        metadata_field = []
        parameters = []   # for the '&parameters='
        param_request = '?limit=2'
        for p in param_list:
            if p['stream'] == search_stream:
                if p['particleKey'] == 'm_battery':
                    metadata_field.append(p)
                    parameters.append(p['pdId'])
                if p['particleKey'] == 'm_lithium_battery_relative_charge':
                    metadata_field.append(p)
                    parameters.append(p['pdId'])
                if p['particleKey'] == 'm_speed':
                    metadata_field.append(p)
                    parameters.append(p['pdId'])
                if p['particleKey'] == 'm_vacuum':
                    metadata_field.append(p)
                    parameters.append(p['pdId'])

        if len(parameters)>0:
            param_request += '&parameters='+",".join(parameters)

        additional_data_url = glider_track['glider_metadata_url'] + "/"+ search_method +"/"+ search_stream + param_request
        req_addit_info_data = requests.get(additional_data_url)
        if req_addit_info_data.status_code == 200:
            data = req_addit_info_data.json()
            #newest should be on the top
            data_entry = data[0]
            #get the time
            glider_track['metadata'] = {'time': data_entry['pk']['time']}
            #get the fields
            for field in metadata_field:
                if field['particleKey'] in data_entry.keys():
                    glider_track['metadata'][field['particleKey']] = field
                    glider_track['metadata'][field['particleKey']]['value'] = data_entry[field['particleKey']]

    return glider_track

def _compile_glider_tracks(update_tracks):
    """ We will always want the telemetered data, and the engineering stream if possible.
    """
    glider_ids = []
    glider_locations = []
    glider_info = []

    base_url, timeout, timeout_read = get_uframe_info()
    # Get the list of mobile assets
    try:
        r = requests.get(base_url)
    except Exception as err:
        message = 'Failed to retrieve glider data from uframe:\n\tUrl:\t%s\n\tError:\t%s' % (base_url, err.message)
        print 'Exception: ', message
        current_app.logger.info(message)
        raise

    all_platforms = r.json()
    skipped_glider = 0

    # Glider discovery
    for p in all_platforms:
        if "MOAS" in p:
            r_p = requests.get(base_url+"/"+p)
            try:
                p_p = r_p.json()
                for gl in p_p:
                    glider_location = "/"+p+"/"+gl
                    glider_url = base_url+glider_location

                    # Get the slider streams to see whats available
                    req_instrument_list = requests.get(glider_url)
                    available_instruments = req_instrument_list.json()

                    # Set some defaults, that will be overridden
                    glider_instrument = None
                    glider_stream = None
                    glider_method = None
                    glider_dates = None

                    # Assume its not recovered until we check the methods
                    is_recovered = False
                    # Check for eng instrument
                    if "00-ENG000000" in available_instruments:
                        glider_instrument = "00-ENG000000"
                    else:
                        skipped_glider+=1
                        #ONLY USE ENGINEERING STREAMS
                        continue
                        #use the first available insturment

                    glider_instrument = available_instruments[0]

                    # use the selected instrument to create the link, list the others to make them available
                    glider_location+="/"+glider_instrument
                    # update the url
                    glider_url = base_url+glider_location

                    # store the location to the metadata url
                    glider_metadata_url = glider_url
                    # get a list of the methods
                    req_method_list = requests.get(glider_url)
                    available_methods = req_method_list.json()
                    # if its not done get the best selected
                    if glider_method is None:
                        glider_method,is_recovered = _select_glider_method(available_methods)

                    # update the location and the url
                    glider_location+="/"+glider_method
                    glider_url = base_url+glider_location

                    req_stream_list = requests.get(glider_url)
                    available_streams = req_stream_list.json()
                    if glider_stream is None:
                        glider_stream = available_streams[0]
                    else:
                        available_streams.append(glider_stream)

                    # used to obtain the date metadata, also used to override the stream and method for glider info
                    glider_method, glider_stream,glider_dates,glider_depth = _check_for_gps_position_stream(glider_metadata_url,glider_stream,glider_method)

                    # update the location and the url with the stream
                    glider_location+="/"+glider_stream
                    glider_url = base_url+glider_location

                    glider_item = {"times" : glider_dates,
                                       "url" : glider_url,
                                       "location" : glider_location,
                                       'instrument' : glider_instrument,
                                       "method" : glider_method,
                                       "stream" : glider_stream,
                                       "depth" : glider_depth,
                                       "available_instruments" : available_instruments,
                                       "available_methods" : available_methods,
                                       "available_streams" : available_streams,
                                       "is_recovered" : is_recovered,
                                       "glider_metadata_url" : glider_metadata_url}

                    # update the content
                    glider_info.append(glider_item)
            except Exception,e:
                print "error:",str(e), p, r_p.content

    # The glider_info is the glider outline
    # Check for the update flag, will try and update only those available
    print "number of gliders:",len(glider_info)," skipped due to non ENG:",skipped_glider
    if update_tracks:
        print '\n glider_tracks: update_tracks is True'
        _get_glider_track_data(glider_info, cache.get('glider_tracks'))
    else:
        print '\n glider_tracks: update_tracks is False'
        _get_glider_track_data(glider_info)

    #if weve come this far, update the cache with any changes
    cache.set('glider_tracks',glider_info)

    # return it so we can see it
    return glider_info