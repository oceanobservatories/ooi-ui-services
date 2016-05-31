#!/usr/bin/env python
'''
uframe endpoints
'''
# base
from flask import jsonify, request, current_app, make_response, Response, send_file
from ooiservices.app import cache, db
from ooiservices.app.uframe import uframe as api
from ooiservices.app.models import DisabledStreams
from ooiservices.app.uframe.vocab import get_display_name_by_rd, get_long_display_name_by_rd
from ooiservices.app.uframe.vocab import get_parameter_name_by_parameter as get_param_names
from ooiservices.app.uframe.vocab import get_stream_name_by_stream as get_stream_name
from ooiservices.app.main.authentication import auth
from ooiservices.app.main.errors import internal_server_error, bad_request
# data imports
from ooiservices.app.uframe.data import get_data, get_simple_data, find_parameter_ids, get_multistream_data
from ooiservices.app.uframe.plotting import generate_plot
from ooiservices.app.uframe.assetController import get_events_by_ref_des
from ooiservices.app.uframe.events import get_events

from urllib import urlencode
from datetime import datetime
from dateutil.parser import parse as parse_date
import json
import numpy as np
import pytz
from contextlib import closing
import time
import urllib2
from copy import deepcopy
from operator import itemgetter
from bs4 import BeautifulSoup
import urllib
import os.path
import requests
import requests.adapters
import requests.exceptions
from requests.exceptions import ConnectionError, Timeout

#for image processing
import PIL
from PIL import Image
from StringIO import StringIO

__author__ = 'Andy Bird'

requests.adapters.DEFAULT_RETRIES = 2
CACHE_TIMEOUT = 172800
COSMO_CONSTANT = 2208988800


def dfs_streams():
    """ Compile a list of streams from uframe data.
    """
    try:
        retval = []
        streams = []
        toc = process_uframe_toc()
        if toc is None:
            message = 'The uframe toc response is empty, unable to return stream information.'
            raise Exception(message)

        # For each instrument, prepare parameters dictionary
        for instrument in toc:
            parameters_dict = parameters_in_instrument(instrument['instrument_parameters'])
            streams = data_streams_in_instrument(instrument, parameters_dict, streams)

        # try to use the event list cache first, if not loaded...load the event cache.
        cached = cache.get('event_list')
        if cached:
            event_list = cached
        else:
            get_events()
            event_list = cache.get('event_list')

        for stream in streams:
            try:
                data_dict = dict_from_stream(*stream)
            except Exception as e:
                message = 'Failed to process streams to dict; %s' % e.message
                current_app.logger.exception(message)
                continue
            if request.args.get('reference_designator'):
                if request.args.get('reference_designator') != data_dict['reference_designator']:
                    continue
            if data_dict:
                retval.append(data_dict)

        # Populate event information in response dictionaries
        for stream in retval:
            response = get_events_by_ref_des(event_list, stream['reference_designator'])
            events = json.loads(response.data)
            for event in events['events']:
                if event['eventClass'] == '.DeploymentEvent' and event['tense'] == 'PRESENT':
                    stream['depth'] = event['depth']
                    stream['lat_lon'] = event['lat_lon']
                    stream['cruise_number'] = event['cruise_number']
                    stream['deployment_number'] = event['deployment_number']

        return retval
    except Exception as err:
        message = '[dfs_streams] Exception: %s' % str(err)
        current_app.logger.info(message)
        raise Exception(message)


def parameters_in_instrument(parameters):
    """ Process an instrument's parameters when parameter shape is 'scalar' or 'function'.
    """
    parameters_dict = {}

    for parameter in parameters:
        if parameter['shape'].lower() in ['scalar', 'function']:
            tmp_stream = parameter['stream']
            if tmp_stream not in parameters_dict.iterkeys():
                parameters_dict[parameter['stream']] = []
                parameters_dict[parameter['stream']+'_variable_type'] = []
                parameters_dict[parameter['stream']+'_units'] = []
                parameters_dict[parameter['stream']+'_variables_shape'] = []
                parameters_dict[parameter['stream']+'_pdId'] = []

            parameters_dict[parameter['stream']].append(parameter['particleKey'])
            parameters_dict[parameter['stream']+'_variable_type'].append(parameter['type'].lower())
            parameters_dict[parameter['stream']+'_units'].append(parameter['units'])
            parameters_dict[parameter['stream']+'_variables_shape'].append(parameter['shape'].lower())
            parameters_dict[parameter['stream']+'_pdId'].append(parameter['pdId'].lower())

    return parameters_dict


def data_streams_in_instrument(instrument, parameters_dict, streams):
    """ Format data tuples to be processing in function 'dict_from_stream'.
    """
    for data_stream in instrument['streams']:
        try:
            if data_stream['stream']:
                tmp_stream = str(data_stream['stream'])
                if tmp_stream not in parameters_dict:
                    print '\n %s not in parameters_dict.' % tmp_stream
                    continue

                # Create stream tuple (order is important; used in  dict_from_stream)
                stream = (
                        instrument['mooring_code'],
                        instrument['platform_code'],
                        instrument['instrument_code'],
                        data_stream['method'].replace("_","-"),
                        data_stream['stream'].replace("_","-"),
                        instrument['reference_designator'],
                        data_stream['beginTime'],
                        data_stream['endTime'],
                        parameters_dict[tmp_stream],
                        parameters_dict[tmp_stream+'_variable_type'],
                        parameters_dict[tmp_stream+'_units'],
                        parameters_dict[tmp_stream+'_variables_shape'],
                        parameters_dict[tmp_stream+'_pdId']
                        )
                streams.append(stream)
        except KeyError as e:
            print '[data_streams_in_instrument] Error parsing stream on key: %s' % str(e)

    return streams


def split_stream_name(ui_stream_name):
    """ Splits the hypenated reference designator and stream type into a tuple of
    (mooring, platform, instrument, stream_type, stream)
    """
    mooring, platform, instrument = ui_stream_name.split('-', 2)
    instrument, stream_type, stream = instrument.split('_', 2)
    stream_type = stream_type.replace("-","_")
    stream = stream.replace("-","_")
    return (mooring, platform, instrument, stream_type, stream)


def combine_stream_name(mooring, platform, instrument, stream_type, stream):
    first_part = '-'.join([mooring, platform, instrument])
    all_of_it = '_'.join([first_part, stream_type, stream])
    return all_of_it


def iso_to_timestamp(iso8601):
    dt = parse_date(iso8601)
    t = (dt - datetime(1970, 1, 1, tzinfo=pytz.utc)).total_seconds()
    return t


def dict_from_stream(mooring, platform, instrument, stream_type, stream, reference_designator,
                     beginTime, endTime, variables, variable_type, units, variables_shape, parameter_id):
    """ Prepare a data dictionary from input data, where input data is constructed in data_streams_in_instrument.
    """
    try:
        stream_name = '_'.join([stream_type, stream])
        ref = '-'.join([mooring, platform, instrument])
        data_dict = {}
        data_dict['start'] = beginTime
        data_dict['end'] = endTime
        data_dict['reference_designator'] = reference_designator
        data_dict['stream_type'] = stream_type
        data_dict['stream_name'] = stream_name
        data_dict['stream_display_name'] = get_stream_name(stream_name)
        data_dict['variables'] = []
        data_dict['variable_types'] = {}
        data_dict['units'] = {}
        data_dict['variables_shape'] = {}
        data_dict['array_name'] = get_display_name_by_rd(ref[:2])
        data_dict['assembly_name'] = get_display_name_by_rd(ref[:14])
        data_dict['site_name'] = get_display_name_by_rd(ref[:8])
        data_dict['display_name'] = get_display_name_by_rd(ref)
        data_dict['long_display_name'] = get_long_display_name_by_rd(ref)
        data_dict['platform_name'] = get_display_name_by_rd(ref[:8])
        data_dict['download'] = {
                                 "csv" : "/".join(['api/uframe/get_csv', stream_name, ref]),
                                 "json" : "/".join(['api/uframe/get_json', stream_name, ref]),
                                 "netcdf" : "/".join(['api/uframe/get_netcdf', stream_name, ref]),
                                 "profile" : "/".join(['api/uframe/get_profiles', stream_name, ref])
                                }
        data_dict['variables'] = variables
        data_dict['variable_type'] = variable_type
        data_dict['units'] = units
        data_dict['variables_shape'] = variables_shape
        data_dict['parameter_id'] = parameter_id

        display_names = []
        for variable in variables:
            display_names.append(get_param_names(variable))

        data_dict['parameter_display_name'] = display_names
        if data_dict['display_name'] is None:
            data_dict['display_name'] = reference_designator
        return data_dict

    except Exception as err:
        message = '[dict_from_stream] exception : %s' % str(err)
        current_app.logger.info(message)
        return {}


def _create_image_entry(url):
    """ Decode a url into its metadata.
    """
    # Get the filename and other metadata
    filename = url.split('/')[-1]
    ref_date = filename.split('.png')[0].split('_')

    dt = urllib.unquote(ref_date[1]).decode('utf8')
    dt = dt.replace(',', '.')

    thumbnail = filename.replace('.png', '_thumbnail.png')

    item = {"url": url,
            "filename": filename,
            "reference_designator": str(ref_date[0]),
            "datetime": dt,
            "thumbnail": thumbnail}
    return item


def _get_folder_list(url,search_filter):
    """ Get url folder link list.
    """
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    ss = soup.findAll('a')
    url_list = []
    for s in ss:
        if 'href' in s.attrs:
            if search_filter in s.attrs['href']:
                url_list.append(url.split('contents.html')[0]+s.attrs['href'])
    return url_list


def _compile_cam_images():
    """ Loop over a directory list to get the images available (url>ref>year>month>day>image).
    """
    url = current_app.config['IMAGE_CAMERA_STORE']
    r = requests.get(url)

    soup = BeautifulSoup(r.content, "html.parser")
    ss = soup.findAll('a')
    data_image_list = []

    for s in ss:
        if 'href' in s.attrs:
            if '-CAMDS' in s.attrs['href']:
                #print s.attrs['href']
                d_url = url+s.attrs['href']
                url_list = _get_folder_list(d_url,'contents.html')
                #year
                for d_url in url_list:
                    url_list1 = _get_folder_list(d_url,'contents.html')
                    #month
                    for d_url1 in url_list1:
                        #day
                        url_list2 = _get_folder_list(d_url1,'contents.html')
                        for d_url2 in url_list2:
                            #image
                            url_list3 = _get_folder_list(d_url2,'.png')
                            #print "\t",len(url_list3)," images..."
                            for im_url in url_list3:
                                data_image_list.append(im_url)

    current_app.logger.debug("Found" + str(len(data_image_list)) + " images")

    image_dict = []
    for data_image_url in data_image_list:
        image_dict.append(_create_image_entry(data_image_url))

    completed= []
    #ADD THE IMAGES to the folder CACHE
    for image_item in image_dict:
        try:
            new_filename = image_item['filename'].split('.')[0]+"_thumbnail.png"
            new_filepath = current_app.config['IMAGE_STORE']+"/"+new_filename

            # Check its not already added and doesnt already exist, if so download it.
            if image_item['url'] not in completed and not os.path.isfile(new_filepath) :
                response = requests.get(image_item['url'])
                img = Image.open(StringIO(response.content))
                thumb = img.copy()
                maxsize = (200, 200)
                thumb.thumbnail(maxsize, PIL.Image.ANTIALIAS)
                thumb.save(new_filepath)
                completed.append(image_item['url'])
        except Exception,e:
            print "Error:",str(e)
            continue

    #return dict
    return image_dict


# @auth.login_required
@api.route('/get_cam_image/<string:image_id>.png', methods=['GET'])
def get_uframe_cam_image(image_id):
    try:
        filename = os.getcwd()+"/"+current_app.config['IMAGE_STORE']+"/"+image_id+'_thumbnail.png'
        filename = filename.replace(',','%2C')
        print filename
        if not os.path.isfile(filename):
            filename = current_app.config['IMAGE_STORE']+'/imageNotFound404.png'
        return send_file(filename,
                         attachment_filename='cam_image.png',
                         mimetype='image/png')
    except Exception, e:
        return jsonify(error="image not found"), 404


# @auth.login_required
@api.route('/get_cam_images')
def get_uframe_cam_images():
    '''
    get cam images
    '''
    try:
        cached = cache.get('cam_images')
        will_reset_cache = False
        if request.args.get('reset') == 'true':
            will_reset_cache = True

        will_reset = request.args.get('reset')
        if cached and not(will_reset_cache):
            data = cached
        else:
            data = _compile_cam_images()

            if "error" not in data:
                cache.set('cam_images', data, timeout=CACHE_TIMEOUT)

        return jsonify({"cam_images":data})
    except requests.exceptions.ConnectionError as e:
        error = "Error: Cannot connect to uframe.  %s" % str(e)
        print error
        return make_response(error, 500)

def _create_entry(url, ext):
    """ Create the JSON object for this file.

    Get the filename and other metadata
       ZPL .raw = CE02SHBP-MJ01C-07-ZPLSCB101_OOI-D20150802-T230543.raw
       HYD .mseed = OO-HYEA2--YDH.2015-09-03T23:55:06.365250.mseed
       CAMDS .png = CE02SHBP-MJ01C-08-CAMDSB107_20150818T214937,543Z.png
       OBS .mseed = OO-HYSB1--BHE.2015-09-03T23:54:37.100000.mseed
       CAMHD .mov = CAMHDA301-20151119T210000Z.mov
       CAMHS .mp4 = CAMHDA301-20151119T210000Z.mp4

    """
    filename = url.split('/')[-1]
    if ext == '.png':
        ref = filename.split(ext)[0].split('_')
        dt = urllib.unquote(ref[1]).decode('utf8')
        dt = dt.replace(',', '.')

    elif ext == '.raw':
        ref = filename.split(ext)[0].split('_OOI-D')
        date = ref[1] + 'Z'
        dt = urllib.unquote(date).decode('utf8')

    elif ext == '.mseed':
        ref = filename.split(ext)[0].split('.')
        if len(ref) == 3:
            date = ref[1] + 'Z'
            dt = urllib.unquote(date).decode('utf8')
        else:
            split = ref[0].split('-')
            date = '-'.join([split[-3], split[-2], split[-1]]) + 'Z'
            dt = urllib.unquote(date).decode('utf8')
    elif ext == '.mov' or ext == '.mp4':
        ref = filename.split(ext)[0].split('-')
        date = ref[1]
        dt = urllib.unquote(date).decode('utf8')

    item = {"url": url,
            "filename": urllib.unquote(filename).decode('utf8'),
            "datetime": dt.replace("-", "").replace(":", "")}

    return item


def _compile_large_format_files(test_ref_des=None, test_date_str=None):
    """ Loop over a directory list to get the files available (url>ref>year>month>day>image)

    Optional arguments are for testing ONLY:
        ref_des: Pass in a reference designator to only retrieve those results
        date_str: Pass in a date string (yyyy-mm-dd) to only get data from a specific day
    """
    testing = False
    if test_ref_des is not None and test_date_str is not None:
        testing = True
        # Get the date we're looking for
        date = test_date_str.split('-')
        test_year = date[0]
        test_month = date[1]
        test_day = date[2]

    url = current_app.config['IMAGE_CAMERA_STORE']
    r = requests.get(url)

    soup = BeautifulSoup(r.content, "html.parser")
    ss = soup.findAll('a')

    filetypes_to_check = ['-HYD', '-OBS', '-CAMDS', '-CAMHD', '-ZPL']
    extensions_to_check = ['.mseed', '.png', '.mp4', '.mov', '.raw']

    # Go fetch whatever data has already been cached
    data_dict = {}
    if cache.get('large_format') is not None:
        data_dict = cache.get('large_format')

    # Get the current date to use to check against the data on HYRAX server
    current_year = datetime.utcnow().strftime('%Y')
    current_month = datetime.utcnow().strftime('%m')
    current_day = datetime.utcnow().strftime('%d')

    # Ok let's walk the HYRAX server directory structure {ref-des > year > month > day}
    for s in ss:
        if 'href' in s.attrs:
            # REF DES
            if any(filetype in s.attrs['href'] for filetype in filetypes_to_check):
                ref_des = s.attrs['href'].split('/')[0]
                if (testing and test_ref_des != ref_des):
                    continue
                current_app.logger.debug(ref_des)
                if ref_des not in data_dict:
                    data_dict[ref_des] = {}
                ref_url = url+s.attrs['href']
                url_list = _get_folder_list(ref_url, 'contents.html')

                # YEAR
                for year_url in url_list:
                    year = year_url.split('/contents.html')[0].split('/')[-1]
                    if (testing and test_year != year):
                        continue
                    if year not in data_dict[ref_des]:
                        data_dict[ref_des][year] = {}
                    elif year != current_year:  # Move onto next year, this one's old!
                        continue
                    url_list1 = _get_folder_list(year_url, 'contents.html')

                    # MONTH
                    for month_url in url_list1:
                        month = month_url.split('/contents.html')[0].split('/')[-1]
                        if (testing and test_month != month):
                            continue
                        if month not in data_dict[ref_des][year]:
                            data_dict[ref_des][year][month] = {}
                        elif month != current_month:  # Move onto next month, this one's old!
                            continue
                        url_list2 = _get_folder_list(month_url, 'contents.html')

                        # DAY
                        for day_url in url_list2:
                            day = day_url.split('/contents.html')[0].split('/')[-1]
                            if (testing and test_day != day):
                                continue
                            if day not in data_dict[ref_des][year][month]:
                                data_dict[ref_des][year][month][day] = []
                            elif day != current_day:  # Move onto next day, this one's old!
                                continue

                            for ext in extensions_to_check:
                                # file
                                url_list3 = _get_folder_list(day_url, ext)
                                for im_url in url_list3:
                                    entry = _create_entry(im_url, ext)
                                    data_dict[ref_des][year][month][day].append(entry)

                # Update the cache in case the connection gets reset you don't want to lose anything
                cache.set('large_format', data_dict, timeout=CACHE_TIMEOUT)

    return data_dict


@api.route('/get_large_format_files_by_ref/<string:ref_des>/<string:date_str>')
def get_uframe_large_format_files_by_ref(ref_des, date_str):
    '''
    Walk the Hyrax server and parse out all available large format files
    '''

    filetypes_to_check = ['-HYD', '-OBS', '-CAMDS', '-CAMHD', '-ZPL']
    extensions_to_check = ['mseed', 'png', 'mp4', 'mov', 'raw']

    site = ref_des[0:8]
    assembly = ref_des[9:14]
    instrument = ref_des[15:]

    date = date_str.split('-')
    if len(date) < 3:
        error = 'Date format not compliant, expecting ISO8601 (yyyy-mm-dd)'
        return make_response(error, 500)
    year = date[0]
    month = date[1]
    day = date[2]

    data_payload = site + '/' + assembly + '/' + instrument + '/'
    date_payload = str(year) + '/' + str(month) + '/' + str(day)

    url = current_app.config['IMAGE_CAMERA_STORE'] + data_payload + date_payload
    r = requests.get(url, verify=False)

    soup = BeautifulSoup(r.content, "html.parser")
    ss = soup.findAll('a')

    entry = {}
    entry_list = []
    for s in ss:
        entry_url = url+s.attrs['href'][1:]
        if entry_url.split('.')[-1] in extensions_to_check:
            entry['url'] = entry_url
            entry['datetime'] = date_str
            entry['filename'] = entry_url.split('/')[-1]
            entry_list.append(entry)

    response = {'data': entry_list}

    if len(entry_list) < 1:
        error = "Error: %s data not available for this date." % (ref_des)
        return make_response(error, 500)

    return jsonify(response)

@api.route('/get_large_format_files')
def get_uframe_large_format_files():
    """ Get all available large format files.
    """
    try:
        cached = cache.get('large_format')
        if cached:
            data = cached
        else:
            data = _compile_large_format_files()
            if "error" not in data:
                cache.set('large_format', data, timeout=CACHE_TIMEOUT)

        return jsonify(data)
    except requests.exceptions.ConnectionError as e:
        error = "Error: Cannot connect to uframe.  %s" % e
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
                        print "old:",dt_old,"\t","new:",dt_new
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


@api.route('/stream')
#@auth.login_required
def streams_list():
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
    # Get cached stream_list; if available continue, if not fetch.
    cached = cache.get('stream_list')
    if cached:
        retval = cached
    else:
        try:
            retval = dfs_streams()
        except Exception as err:
            message = err.message
            return bad_request(message)

        if 'error' not in retval:
            cache.set('stream_list', retval, timeout=CACHE_TIMEOUT)

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
                del obj['parameter_id']
                del obj['units']
                del obj['variable_type']
                del obj['variable_types']
                del obj['download']
                del obj['variables']
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
                    elif subset.lower() in str(item['platform_name']).lower():
                        ven_subset.append(item)
                    elif subset.lower() in str(item['assembly_name']).lower():
                        ven_subset.append(item)
                    elif subset.lower() in str(item['reference_designator']).lower():
                        ven_subset.append(item)
                    elif subset.lower() in str(item['stream_name']).lower():
                        ven_subset.append(item)
                    elif subset.lower() in str(item['parameter_display_name']).lower():
                        ven_subset.append(item)
                    elif subset.lower() in str(item['long_display_name']).lower():
                        ven_subset.append(item)
                retval = ven_subset
            else:
                for item in retval:
                    if subset.lower() in str(item['array_name']).lower():
                        return_list.append(item)
                    elif subset.lower() in str(item['site_name']).lower():
                        return_list.append(item)
                    elif subset.lower() in str(item['platform_name']).lower():
                        return_list.append(item)
                    elif subset.lower() in str(item['assembly_name']).lower():
                        return_list.append(item)
                    elif subset.lower() in str(item['reference_designator']).lower():
                        return_list.append(item)
                    elif subset.lower() in str(item['parameter_display_name']).lower():
                        return_list.append(item)
                    elif subset.lower() in str(item['stream_name']).lower():
                        return_list.append(item)
                    elif subset.lower() in str(item['long_display_name']).lower():
                        return_list.append(item)
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
        return result

    else:
        return jsonify(streams=retval)

@api.route('/disabled_streams', methods=['GET', 'POST'])
@api.route('/disabled_streams/<int:id>', methods=['DELETE'])
def disabled_streams(id=None):
    """ Process GET, POST and DELETE for disabled streams.

    @method GET:
        Returns the list of all the disabled streams from our database.

    @method POST:
        @params: ID
        Create a new 'disabled streams' in our local database.

    @method DELETE:
        @params: ID
        Delete a disabled streams identifier from our local database.
    """

    if request.method == 'GET':
        disabled_streams = DisabledStreams.query.all()
        return jsonify({'disabled_streams':
                        [disabled_stream.to_json() \
                         for disabled_stream in disabled_streams]})

    elif request.method == 'POST':
        try:
            # grab the json payload
            payload = json.loads(request.data)

            # create a new instance of the disabled streams with the data
            disabled_stream = DisabledStreams.from_json(payload)

            # add to the databse
            db.session.add(disabled_stream)
            db.session.commit()
            return jsonify({ 'disabled_streams': 'Stream Disabled!'}), 200
        except Exception as e:
            print type(e)
            # roll it back if there is a problem.
            db.session.rollback()
            db.session.commit()
            return make_response(e.message), 409

    elif request.method == 'DELETE':
        try:
            # get the item to delete
            disabled_stream = DisabledStreams.query.get_or_404(id)

            # obliterate it form the db
            db.session.delete(disabled_stream)
            db.session.commit()
            return jsonify({'message': 'Stream Enabled!'}), 200
        except Exception as e:
            # roll it back if there is a problem.
            db.session.rollback()
            db.session.commit()
            return jsonify({'message': 'Problem activating stream: %s'%e}), 409


@api.route('/antelope_acoustic/list', methods=['GET'])
def get_acoustic_datalist():
    """ Get all available acoustic data sets.
    """
    antelope_url = current_app.config['UFRAME_ANTELOPE_URL']
    r = requests.get(antelope_url)
    data = r.json()

    for ind, record in enumerate(data):
        data[ind]['filename'] = record['downloadUrl'].split("/")[-1]
        data[ind]['startTime'] = data[ind]['startTime'] - COSMO_CONSTANT
        data[ind]['endTime'] = data[ind]['endTime'] - COSMO_CONSTANT

    try:
        is_reverse = False
        if request.args.get('sort') and request.args.get('sort') != "":
            sort_by = request.args.get('sort')
            if request.args.get('order') and request.args.get('order') != "":
                order = request.args.get('order')
                if order == 'reverse':
                    is_reverse = True
        else:
            sort_by = 'endTime'
        data = sorted(data, key=itemgetter(sort_by), reverse=is_reverse)
    except (TypeError, KeyError):
        raise

    if request.args.get('startAt'):
        start_at = int(request.args.get('startAt'))
        count = int(request.args.get('count'))
        total = int(len(data))
        retval_slice = data[start_at:(start_at + count)]
        result = jsonify({"count": count,
                          "total": total,
                          "startAt": start_at,
                          "results": retval_slice})
        return result

    else:
        return jsonify(results=data)


# @auth.login_required
@api.route('/get_glider_tracks')
def get_uframe_glider_track():
    """ Get glider tracks.
    """
    try:
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
                cache.set('glider_tracks', data, timeout=CACHE_TIMEOUT)

        return jsonify({"gliders":data})
    except requests.exceptions.ConnectionError as e:
        error = "Error: Cannot connect to uframe.  %s" % e
        print error
        return make_response(error, 500)


def get_uframe_streams(mooring, platform, instrument, stream_type):
    """ Get a list of all the streams.
    """
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = '/'.join([uframe_url, mooring, platform, instrument, stream_type])
        current_app.logger.info("GET %s", url)
        response = requests.get(url, timeout=(timeout, timeout_read))
        return response
    except Exception as e:
        return internal_server_error('uframe connection cannot be made.' + str(e.message))


def get_uframe_stream(mooring, platform, instrument, stream):
    """ Get a list the reference designators for the streams.
    """
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, mooring, platform, instrument, stream])
        current_app.logger.info("GET %s", url)
        response = requests.get(url, timeout=(timeout, timeout_read))
        return response
    except Exception as e:
        #return internal_server_error('uframe connection cannot be made.' + str(e.message))
        return _response_internal_server_error(str(e))


@api.route('/get_instrument_metadata/<string:ref>', methods=['GET'])
def get_uframe_instrument_metadata(ref):
    """ Returns the uFrame metadata response for a given stream.
    """
    try:
        mooring, platform, instrument = ref.split('-', 2)
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, mooring, platform, instrument, 'metadata'])
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code == 200:
            data = response.json()
            return jsonify(metadata=data['parameters'])
        return jsonify(metadata={}), 404
    except Exception as e:
        return internal_server_error('uframe connection cannot be made.' + str(e.message))


@api.route('/get_metadata_parameters/<string:ref>', methods=['GET'])
def get_uframe_instrument_metadata_parameters(ref):
    """ Returns the uFrame metadata parameters for a given stream.
    """
    try:
        mooring, platform, instrument = ref.split('-', 2)
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, mooring, platform, instrument, 'metadata', 'parameters'])
        response = requests.get(url, timeout=(timeout, timeout_read))
        return response
    except:
        return _response_internal_server_error()


def _response_internal_server_error(msg=None):
    message = json.dumps('"error" : "uframe connection cannot be made."')
    if msg:
        message = json.dumps(msg)
    response = make_response()
    response.content = message
    response.status_code = 500
    response.headers["Content-Type"] = "application/json"
    return response


@auth.login_required
@api.route('/get_metadata_times/<string:ref>', methods=['GET'])
def get_uframe_stream_metadata_times(ref):
    """ Returns the uFrame time bounds response for a given stream.
    """
    mooring, platform, instrument = ref.split('-', 2)
    try:
        uframe_url, timeout, timeout_read = get_uframe_info()
        url = "/".join([uframe_url, mooring, platform, instrument, 'metadata','times'])
        #current_app.logger.info("GET %s", url)
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code == 200:
            return response
        return jsonify(times={}), 200
    except ConnectionError:
        message = 'ConnectionError for get uframe stream metadata times.'
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout for get uframe stream metadata times.'
        current_app.logger.info(message)
        raise Exception(message)
    except Exception as e:
        message = 'get uframe stream metadata times exception' + str(e.message)
        current_app.logger.info(message)
        return internal_server_error(message)


@auth.login_required
@api.route('/get_multistream/<string:stream1>/<string:stream2>/<string:instrument1>/<string:instrument2>/<string:var1>/<string:var2>', methods=['GET'])
def multistream_api(stream1, stream2, instrument1, instrument2, var1, var2):
    '''
    Service endpoint to get multistream interpolated data.
    Example request:
        http://localhost:4000/uframe/get_multistream/CP05MOAS-GL340-03-CTDGVM000/CP05MOAS-GL340-02-FLORTM000/telemetered_ctdgv_m_glider_instrument/
        telemetered_flort_m_glider_instrument/sci_water_pressure/sci_flbbcd_chlor_units?startdate=2015-05-07T02:49:22.745Z&enddate=2015-06-28T04:00:41.282Z
    '''
    try:
        resp_data, units = get_multistream_data(instrument1, instrument2, stream1, stream2, var1, var2)
    except Exception as err:
        return jsonify(error='%s' % str(err.message)), 400

    header1 = '-'.join([stream1.replace('_', '-'), instrument1.split('_')[0].replace('-', '_'), instrument1.split('_')[1].replace('-', '_')])
    header2 = '-'.join([stream2.replace('_', '-'), instrument2.split('_')[0].replace('-', '_'), instrument2.split('_')[1].replace('-', '_')])

    # Need to reformat the data a bit
    try:
        for ind, data in enumerate(resp_data[header2]):
            resp_data[header1][ind][var2] = data[var2]
        #title = PlatformDeployment._get_display_name(stream1)
        #subtitle = PlatformDeployment._get_display_name(stream2)
        # TODO Test remove use of PlatformDeployment and use vocabulary functions.
        title = get_display_name_by_rd(stream1)
        subtitle = get_display_name_by_rd(stream2)
    except IndexError:
        return jsonify(error='Data Array Length Error'), 500
    except KeyError:
        return jsonify(error='Missing Data in Data Repository'), 500

    return jsonify(data=resp_data[header1], units=units, title=title, subtitle=subtitle)


def get_uframe_multi_stream_contents(stream1_dict, stream2_dict, start_time, end_time):
    """ Gets the data from an interpolated multi stream request.

    For details on the UFrame API:
        https://uframe-cm.ooi.rutgers.edu/projects/ooi/wiki/Web_Interface

    Example request:
        http://uframe-test.ooi.rutgers.edu:12576/sensor?r=r1&r=r2&r1.refdes=CP05MOAS-GL340-03-CTDGVM000&
        r2.refdes=CP05MOAS-GL340-02-FLORTM000&r1.method=telemetered&r2.method=telemetered&r1.stream=ctdgv_m_glider_instrument&
        r2.stream=flort_m_glider_instrument&r1.params=PD1527&r2.params=PD1485&limit=1000&startDT=2015-05-07T02:49:22.745Z&endDT=2015-06-28T04:00:41.282Z
    """
    try:
        # Get the parts of the request from the input stream dicts
        refdes1 = stream1_dict['refdes']
        refdes2 = stream2_dict['refdes']

        method1 = stream1_dict['method']
        method2 = stream2_dict['method']

        stream1 = stream1_dict['stream']
        stream2 = stream2_dict['stream']

        params1 = stream1_dict['params']
        params2 = stream2_dict['params']

        limit = current_app.config['DATA_POINTS']

        #GA_URL = current_app.config['GOOGLE_ANALYTICS_URL']+'&ec=multistreamdata&ea=%s&el=%s' % \
        #         ('-'.join([refdes1+stream1, refdes1+stream2]), '-'.join([start_time, end_time]))

        query = ('sensor?r=r1&r=r2&r1.refdes=%s&r2.refdes=%s&r1.method=%s&r2.method=%s'
                 '&r1.stream=%s&r2.stream=%s&r1.params=%s&r2.params=%s&limit=%s&startDT=%s&endDT=%s'
                 % (refdes1, refdes2, method1, method2, stream1, stream2,
                    params1, params2, limit, start_time, end_time))

        _, timeout, timeout_read = get_uframe_info()
        url = "/".join([current_app.config['UFRAME_URL'], query])
        current_app.logger.debug("***:" + url)
        response = requests.get(url, timeout=(timeout, timeout_read))
        if response.status_code != 200:
            msg = map_common_error_message(response.text, response.text)
            return msg, 500
        else:
            return response.json(), response.status_code
    except Exception as e:
        return str(e), 500


def get_uframe_plot_contents_chunked(mooring, platform, instrument, stream_type, stream,
                                     start_time, end_time, dpa_flag, parameter_ids):
    """ Gets the bounded stream contents, start_time and end_time need to be datetime objects
    """
    try:
        if dpa_flag == '0' and len(parameter_ids) < 1:
            query = '?beginDT=%s&endDT=%s&limit=%s' % (start_time, end_time, current_app.config['DATA_POINTS'])
        elif dpa_flag == '1' and len(parameter_ids) < 1:
            query = '?beginDT=%s&endDT=%s&limit=%s&execDPA=true' % \
                    (start_time, end_time, current_app.config['DATA_POINTS'])
        elif dpa_flag == '0' and len(parameter_ids) > 0:
            query = '?beginDT=%s&endDT=%s&limit=%s&parameters=%s' % \
                    (start_time, end_time, current_app.config['DATA_POINTS'], ','.join(parameter_ids))
        elif dpa_flag == '1' and len(parameter_ids) > 0:
            query = '?beginDT=%s&endDT=%s&limit=%s&execDPA=true&parameters=%s' % \
                    (start_time, end_time, current_app.config['DATA_POINTS'], ','.join(map(str, parameter_ids)))

        GA_URL = current_app.config['GOOGLE_ANALYTICS_URL']+'&ec=plot&ea=%s&el=%s' % \
                 ('-'.join([mooring, platform, instrument, stream_type, stream]), '-'.join([start_time, end_time]))

        UFRAME_DATA = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE']
        url = "/".join([UFRAME_DATA, mooring, platform, instrument, stream_type, stream + query])
        current_app.logger.debug("***:" + url)

        TOO_BIG = 1024 * 1024 * 15 # 15MB
        CHUNK_SIZE = 1024 * 32   #...KB
        TOTAL_SECONDS = current_app.config['UFRAME_PLOT_TIMEOUT']
        dataBlock = ""
        response = ""
        idx = 0

        # counter
        t0 = time.time()

        with closing(requests.get(url, stream=True)) as response:
            content_length = 0
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                content_length = content_length + CHUNK_SIZE
                t1 = time.time()
                total = t1-t0
                idx += 1

                if content_length > TOO_BIG:
                    return 'Data request too large, greater than 15MB', 500

                if total > TOTAL_SECONDS:
                    return 'Data request time out', 500

                dataBlock += chunk

            idx_c = dataBlock.rfind('}\n]')

            if idx_c == -1:
                dataBlock += "]"
            urllib2.urlopen(GA_URL)
            return json.loads(dataBlock), 200

    except Exception as e:
        msg = map_common_error_message(dataBlock, str(e))
        return msg, 500


def map_common_error_message(response, default):
    """ This function parses the error response from uFrame into a meaningful message for the UI.
    """
    message = default
    if 'requestUUID' in response:
        UUID = response.split('requestUUID":')[1].split('"')[1]
        message = 'Error Occurred During Product Creation<br>UUID for reference: ' + UUID
    elif 'Failed to respond' in response:
        message = 'Internal System Error in Data Repository'

    return message


def get_uframe_stream_contents_chunked(mooring, platform, instrument, stream_type, stream,
                                       start_time, end_time, dpa_flag):
    """ Gets the bounded stream contents, start_time and end_time need to be datetime objects.
    """
    try:
        if dpa_flag == '0':
            query = '?beginDT=%s&endDT=%s' % (start_time, end_time)
        else:
            query = '?beginDT=%s&endDT=%s&execDPA=true' % (start_time, end_time)
        UFRAME_DATA = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE']

        url = "/".join([UFRAME_DATA, mooring, platform, instrument, stream_type, stream + query])
        current_app.logger.debug("***:%s" % url)

        TOO_BIG = 1024 * 1024 * 15 # 15MB
        CHUNK_SIZE = 1024 * 32   #...KB
        TOTAL_SECONDS = 20
        dataBlock = ""
        idx = 0

        #counter
        t0 = time.time()

        with closing(requests.get(url,stream=True)) as response:
            content_length = 0
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                content_length = content_length + CHUNK_SIZE
                t1 = time.time()
                total = t1-t0
                idx+=1
                if content_length > TOO_BIG or total > TOTAL_SECONDS:
                    #('uframe response to large.')
                    # break it down to the last know good spot
                    t00 = time.time()
                    idx_c = dataBlock.rfind('}, {')
                    dataBlock = dataBlock[:idx_c]
                    dataBlock+="} ]"
                    t11 = time.time()
                    totaln = t11-t00

                    print "size_limit or time reached",content_length/(1024 * 1024),total,totaln,idx
                    return json.loads(dataBlock),200
                # all the data is in the resonse return it as normal
                #previousBlock = dataBlock
                dataBlock+=chunk
            #print "transfer complete",content_length/(1024 * 1024),total

            #if str(dataBlock[-3:-1]) != '} ]':
            #    idx_c = dataBlock.rfind('}')
            #    dataBlock = dataBlock[:idx_c]
            #    dataBlock+="} ]"
            #    print 'uFrame appended Error Message to Stream',"\n",dataBlock[-3:-1]
            idx_c = dataBlock.rfind('} ]')
            if idx_c == -1:
                dataBlock+="]"

            return json.loads(dataBlock),200

    except Exception,e:
        #return json.loads(dataBlock), 200
        return internal_server_error('uframe connection unstable.'),500


def get_uframe_info():
    """ Returns uframe configuration information. (uframe_url, uframe timeout_connect and timeout_read.)
    """
    uframe_url = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_URL_BASE']
    timeout = current_app.config['UFRAME_TIMEOUT_CONNECT']
    timeout_read = current_app.config['UFRAME_TIMEOUT_READ']
    return uframe_url, timeout, timeout_read


def validate_date_time(start_time, end_time):
    '''
    uframe_data_request_limit = int(current_app.config['UFRAME_DATA_REQUEST_LIMIT'])/1440
    new_end_time_strp = datetime.datetime.strptime(start_time, "
                                                   ") + datetime.timedelta(days=uframe_data_request_limit)
    old_end_time_strp = datetime.datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S.%fZ")
    new_end_time = datetime.datetime.strftime(new_end_time_strp, "%Y-%m-%dT%H:%M:%S.%fZ")
    if old_end_time_strp > new_end_time_strp:
        end_time = new_end_time
    '''
    return end_time


@auth.login_required
@api.route('/get_csv/<string:stream>/<string:ref>/<string:start_time>/<string:end_time>/<string:dpa_flag>', methods=['GET'])
def get_csv(stream, ref, start_time, end_time, dpa_flag):
    mooring, platform, instrument = ref.split('-', 2)
    stream_type, stream = stream.split('_', 1)

    stream_type = stream_type.replace('-','_')
    stream = stream.replace('-','_')

    # figures out if its in a date time range
    end_time = validate_date_time(start_time, end_time)

    try:
        GA_URL = current_app.config['GOOGLE_ANALYTICS_URL']+'&ec=download_csv&ea=%s&el=%s' % \
                 ('-'.join([mooring, platform, instrument, stream]), '-'.join([start_time, end_time]))
        urllib2.urlopen(GA_URL)
    except KeyError:
        pass

    uframe_url, timeout, timeout_read = get_uframe_info()
    user = request.args.get('user', '')
    email = request.args.get('email', '')
    if dpa_flag == '0':
        query = '?beginDT=%s&endDT=%s&user=%s&email=%s' % (start_time, end_time, user, email)
    else:
        query = '?beginDT=%s&endDT=%s&execDPA=true&user=%s&email=%s' % (start_time, end_time, user, email)
    query += '&format=application/csv'

    url = "/".join([uframe_url, mooring, platform, instrument, stream_type, stream + query])
    current_app.logger.debug('***** url: ' + url)
    response = requests.get(url, timeout=(timeout, timeout_read))

    return response.text, response.status_code


@auth.login_required
@api.route('/get_json/<string:stream>/<string:ref>/<string:start_time>/<string:end_time>/<string:dpa_flag>/<string:provenance>/<string:annotations>', methods=['GET'])
def get_json(stream, ref, start_time, end_time, dpa_flag, provenance, annotations):
    mooring, platform, instrument = ref.split('-', 2)
    stream_type, stream = stream.split('_', 1)

    stream_type = stream_type.replace('-','_')
    stream = stream.replace('-','_')

    # figures out if its in a date time range
    end_time = validate_date_time(start_time, end_time)

    try:
        GA_URL = current_app.config['GOOGLE_ANALYTICS_URL']+'&ec=download_json&ea=%s&el=%s' % \
                 ('-'.join([mooring, platform, instrument, stream]), '-'.join([start_time, end_time]))
        urllib2.urlopen(GA_URL)
    except KeyError:
        pass

    uframe_url, timeout, timeout_read = get_uframe_info()
    user = request.args.get('user', '')
    email = request.args.get('email', '')
    if dpa_flag == '0':
        query = '?beginDT=%s&endDT=%s&include_provenance=%s&include_annotations=%s&user=%s&email=%s' % \
                (start_time, end_time, provenance, annotations, user, email)
    else:
        query = '?beginDT=%s&endDT=%s&include_provenance=%s&include_annotations=%s&execDPA=true&user=%s&email=%s' % \
                (start_time, end_time, provenance, annotations, user, email)
    query += '&format=application/json'

    url = "/".join([uframe_url, mooring, platform, instrument, stream_type, stream + query])
    current_app.logger.debug('***** url: ' + url)
    response = requests.get(url, timeout=(timeout, timeout_read))

    return response.text, response.status_code


@auth.login_required
@api.route('/get_netcdf/<string:stream>/<string:ref>/<string:start_time>/<string:end_time>/<string:dpa_flag>/<string:provenance>/<string:annotations>', methods=['GET'])
def get_netcdf(stream, ref, start_time, end_time, dpa_flag, provenance, annotations):
    mooring, platform, instrument = ref.split('-', 2)
    stream_type, stream = stream.split('_', 1)

    stream_type = stream_type.replace('-','_')
    stream = stream.replace('-','_')

    try:
        GA_URL = current_app.config['GOOGLE_ANALYTICS_URL']+'&ec=download_netcdf&ea=%s&el=%s' % \
                 ('-'.join([mooring, platform, instrument, stream]), '-'.join([start_time, end_time]))
        urllib2.urlopen(GA_URL)
    except KeyError:
        pass

    user = request.args.get('user', '')
    email = request.args.get('email', '')
    if dpa_flag == '0':
        query = '?beginDT=%s&endDT=%s&include_provenance=%s&include_annotations=%s&user=%s&email=%s' % \
                (start_time, end_time, provenance, annotations, user, email)
    else:
        query = '?beginDT=%s&endDT=%s&include_provenance=%s&include_annotations=%s&execDPA=true&user=%s&email=%s' % \
                (start_time, end_time, provenance, annotations, user, email)
    query += '&format=application/netcdf'
    uframe_url, timeout, timeout_read = get_uframe_info()
    url = "/".join([uframe_url, mooring, platform, instrument, stream_type, stream + query])
    response = requests.get(url, timeout=(timeout, timeout_read))

    return response.text, response.status_code


# @auth.login_required
@api.route('/get_data/<string:instrument>/<string:stream>/<string:yvar>/<string:xvar>', methods=['GET'])
def get_data_api(stream, instrument, yvar, xvar):
    # return if error
    try:
        xvar = xvar.split(',')
        yvar = yvar.split(',')
        resp_data, units = get_simple_data(stream, instrument, yvar, xvar)
        instrument = instrument.split(',')
        title = get_display_name_by_rd(instrument[0])
    except Exception as err:
        return jsonify(error='%s' % str(err.message)), 500
    return jsonify(data=resp_data, units=units, title=title)


#@auth.login_required
@auth.login_required
@api.route('/plot/<string:instrument>/<string:stream>', methods=['GET'])
def get_svg_plot(instrument, stream):
    # from ooiservices.app.uframe.controller import split_stream_name
    # Ok first make a list out of stream and instrument
    instrument = instrument.split(',')
    #instrument.append(instrument[0])

    stream = stream.split(',')
    #stream.append(stream[0])

    plot_format = request.args.get('format', 'svg')
    # time series vs profile
    plot_layout = request.args.get('plotLayout', 'timeseries')
    xvar = request.args.get('xvar', 'time')
    yvar = request.args.get('yvar', None)

    # There can be multiple variables so get into a list
    xvar = xvar.split(',')
    yvar = yvar.split(',')

    if len(instrument) == len(stream):
        pass # everything the same
    else:
        instrument = [instrument[0]]
        stream = [stream[0]]
        yvar = [yvar[0]]
        xvar = [xvar[0]]

    # create bool from request
    # use_line = to_bool(request.args.get('line', True))
    use_scatter = to_bool(request.args.get('scatter', True))
    use_event = to_bool(request.args.get('event', True))
    qaqc = int(request.args.get('qaqc', 0))

    # Get Events!
    events = {}
    if use_event:
        try:
            response = get_events_by_ref_des(instrument[0])
            events = json.loads(response.data)
        except Exception as err:
            current_app.logger.exception(str(err.message))
            return jsonify(error=str(err.message)), 400

    profileid = request.args.get('profileId', None)

    # need a yvar for sure
    if yvar is None:
        return jsonify(error='Error: yvar is required'), 400

    height = float(request.args.get('height', 100))  # px
    width = float(request.args.get('width', 100))  # px

    # do conversion of the data from pixels to inches for plot
    height_in = height / 96.
    width_in = width / 96.

    # get the data from uFrame
    try:
        if plot_layout == "depthprofile":
            data = get_process_profile_data(stream[0], instrument[0], yvar[0], xvar[0])
        else:
            if len(instrument) == 1:
                data = get_data(stream[0], instrument[0], yvar, xvar)
            elif len(instrument) > 1:  # Multiple datasets
                data = []
                for idx, instr in enumerate(instrument):
                    stream_data = get_data(stream[idx], instr, [yvar[idx]], [xvar[idx]])
                    data.append(stream_data)

    except Exception as err:
        current_app.logger.exception(str(err.message))
        return jsonify(error=str(err.message)), 400

    if not data:
        return jsonify(error='No data returned for %s' % plot_layout), 400

    # return if error
    if 'error' in data or 'Error' in data:
        return jsonify(error=data['error']), 400

    # generate plot
    some_tuple = ('a', 'b')
    if str(type(data)) == str(type(some_tuple)) and plot_layout == "depthprofile":
        return jsonify(error='tuple data returned for %s' % plot_layout), 400
    if isinstance(data, dict):
        # get title
        title = get_display_name_by_rd(instrument[0])
        if len(title) > 50:
            title = ''.join(title.split('-')[0:-1]) + '\n' + title.split('-')[-1]

        data['title'] = title
        data['height'] = height_in
        data['width'] = width_in
    else:
        for idx, streamx in enumerate(stream):
            title = get_display_name_by_rd(instrument[idx])
            if len(title) > 50:
                title = ''.join(title.split('-')[0:-1]) + '\n' + title.split('-')[-1]
            data[idx]['title'] = title
            data[idx]['height'] = height_in
            data[idx]['width'] = width_in

    plot_options = {'plot_format': plot_format,
                    'plot_layout': plot_layout,
                    'use_scatter': use_scatter,
                    'events': events,
                    'profileid': profileid,
                    'width_in': width_in,
                    'use_qaqc': qaqc,
                    'st_date': request.args['startdate'],
                    'ed_date': request.args['enddate']}

    try:
        buf = generate_plot(data, plot_options)

        content_header_map = {
            'svg' : 'image/svg+xml',
            'png' : 'image/png'
        }

        return buf.read(), 200, {'Content-Type': content_header_map[plot_format]}
    except Exception as err:
        message = 'Error generating {0} plot: {1}'.format(plot_options['plot_layout'], str(err.message))
        current_app.logger.exception(str(err.message))
        return jsonify(error=message), 400


def get_process_profile_data(stream, instrument, xvar, yvar):
    """ NOTE: i have to swap the inputs (xvar, yvar) around at this point to get the plot to work....
    """
    try:
        join_name ='_'.join([str(instrument), str(stream)])

        mooring, platform, instrument, stream_type, stream = split_stream_name(join_name)
        parameter_ids, y_units, x_units = find_parameter_ids(mooring, platform, instrument, [yvar], [xvar])

        data = get_profile_data(mooring, platform, instrument, stream_type, stream, parameter_ids)
        if not data or data == None:
            raise Exception('profiles not present in data')
    except Exception as e:
        raise Exception('%s' % str(e.message))

    '''
    # check the data is in the first row
    if yvar not in data[0] or xvar not in data[0]:
        data = {'error':'requested fields not in data'}
        return data
    if 'profile_id' not in data[0]:
        data = {'error':'profiles not present in data'}
        return data
    '''

    y_data = []
    x_data = []
    time = []
    profile_id_list = []
    profile_count = -1

    for i, row in enumerate(data):
        if (row['profile_id']) >= 0:
            profile_id = int(row['profile_id'])
            if profile_id not in profile_id_list:
                y_data.append([])
                x_data.append([])
                time.append(float(row['pk']['time']))
                profile_id_list.append(profile_id)
                profile_count += 1
            try:
                y_data[profile_count].append(row[yvar])
                x_data[profile_count].append(row[xvar])
            except Exception as e:
                raise Exception('profiles not present in data')

    return {'x': x_data, 'y': y_data, 'x_field': xvar, "y_field": yvar, 'time': time}


def get_profile_data(mooring, platform, instrument, stream_type, stream, parameter_ids):
    """ Process uframe data into profiles.
    """
    try:
        data = []
        if 'startdate' in request.args and 'enddate' in request.args:
            st_date = request.args['startdate']
            ed_date = request.args['enddate']
            if 'dpa_flag' in request.args:
                dpa_flag = request.args['dpa_flag']
            else:
                dpa_flag = "0"
            ed_date = validate_date_time(st_date, ed_date)
            data, status_code = get_uframe_plot_contents_chunked(mooring, platform, instrument, stream_type, stream, st_date, ed_date, dpa_flag, parameter_ids)
        else:
            message = 'Failed to make plot - start end dates not applied'
            current_app.logger.exception(message)
            raise Exception(message)

        if status_code != 200:
            raise IOError("uFrame unable to get data for this request.")

        current_app.logger.debug('\n --- retrieved data from uframe for profile processing...')

        # Note: assumes data has depth and time is ordinal
        # Need to add assertions and try and exceptions to check data
        time = []
        depth = []

        request_xvar = None
        if request.args['xvar']:
            junk = request.args['xvar']
            test_request_xvar = junk.encode('ascii','ignore')
            if type(test_request_xvar) == type(''):
                if ',' in test_request_xvar:
                    chunk_request_var = test_request_xvar.split(',',1)
                    if len(chunk_request_var) > 0:
                        request_xvar = chunk_request_var[0]
                else:
                    request_xvar = test_request_xvar
        else:
            message = 'Failed to make plot - no xvar provided in request'
            current_app.logger.exception(message)
            raise Exception(message)
        if not request_xvar:
            message = 'Failed to make plot - unable to process xvar provided in request'
            current_app.logger.exception(message)
            raise Exception(message)

        for row in data:
            depth.append(int(row[request_xvar]))
            time.append(float(row['pk']['time']))

        matrix = np.column_stack((time, depth))
        tz = matrix
        origTz = tz
        INT = 10
        # tz length must equal profile_list length

        # maxi = np.amax(tz[:, 0])
        # mini = np.amin(tz[:, 0])
        # getting a range from min to max time with 10 seconds or milliseconds. I have no idea.
        ts = (np.arange(np.amin(tz[:, 0]), np.amax(tz[:, 0]), INT)).T

        # interpolation adds additional points on the line within f(t), f(t+1)  time is a function of depth
        itz = np.interp(ts, tz[:, 0], tz[:, 1])

        newtz = np.column_stack((ts, itz))
        # 5 unit moving average
        WINDOW = 5
        weights = np.repeat(1.0, WINDOW) / WINDOW
        ma = np.convolve(newtz[:, 1], weights)[WINDOW-1:-(WINDOW-1)]
        # take the diff and change negatives to -1 and postives to 1
        dZ = np.sign(np.diff(ma))

        # repeat for second derivative
        dZ = np.convolve(dZ, weights)[WINDOW-1:-(WINDOW-1)]
        dZ = np.sign(dZ)

        r0 = 1
        r1 = len(dZ) + 1
        dZero = np.diff(dZ)

        start = []
        stop = []
        # find where the slope changes
        dr = [start.append(i) for (i, val) in enumerate(dZero) if val != 0]
        if len(start) == 0:
            raise Exception('Unable to determine where slope changes.')

        for i in range(len(start)-1):
            stop.append(start[i+1])

        stop.append(start[0])
        start_stop = np.column_stack((start, stop))
        start_times = np.take(newtz[:, 0], start)
        stop_times = np.take(newtz[:, 0], stop)
        start_times = start_times - INT*2
        stop_times = stop_times + INT*2

        depth_profiles = []

        for i in range(len(start_times)):
            profile_id = i
            proInds = origTz[(origTz[:, 0] >= start_times[i]) & (origTz[:, 0] <= stop_times[i])]
            value = proInds.shape[0]
            z = np.full((value, 1), profile_id)
            pro = np.append(proInds, z, axis=1)
            depth_profiles.append(pro)

        depth_profiles = np.concatenate(depth_profiles)
        # I NEED to CHECK FOR DUPLICATE TIMES !!!!! NOT YET DONE!!!!
        # Start stop times may result in over laps on original data set. (see function above)
        # May be an issue, requires further enquiry
        profile_list = []
        for row in data:
            try:
                # Need to add epsilon. Floating point error may occur
                where = np.argwhere(depth_profiles == float(row['pk']['time']))
                index = where[0]
                rowloc = index[0]
                if len(where) and int(row[request_xvar]) == depth_profiles[rowloc][1]:
                    row['profile_id'] = depth_profiles[rowloc][2]
                    profile_list.append(row)
            except IndexError:
                row['profile_id'] = None
                profile_list.append(row)
            except Exception as err:
                raise Exception('%s' % str(err.message))

        # profile length should equal tz  length
        return profile_list

    except Exception as err:
        current_app.logger.exception('\n* (pass) exception: ' + str(err.message))


# @auth.login_required
@api.route('/get_profiles/<string:stream>/<string:instrument>', methods=['GET'])
def get_profiles(stream, instrument):
    filename = '-'.join([stream, instrument, "profiles"])
    content_headers = {'Content-Type': 'application/json', 'Content-Disposition': "attachment; filename=%s.json" % filename}
    try:
        profiles = get_profile_data(instrument, stream)
    except Exception as e:
        return jsonify(error=e.message), 400, content_headers
    if profiles is None:
        return jsonify(), 204, content_headers
    return jsonify(profiles=profiles), 200, content_headers


def make_cache_key():
    return urlencode(request.args)


def to_bool(value):
    """ Converts 'something' to boolean. Raises exception for invalid formats
           Possible True  values: 1, True, "1", "TRue", "yes", "y", "t"
           Possible False values: 0, False, None, [], {}, "", "0", "faLse", "no", "n", "f", 0.0, ...
    """
    if str(value).lower() in ("yes", "y", "true",  "t", "1"):
        return True
    if str(value).lower() in ("no",  "n", "false", "f", "0", "0.0", "", "none", "[]", "{}"):
        return False
    raise Exception('Invalid value for boolean conversion: ' + str(value))


def to_bool_str(value):
    """
       Converts 'something' to boolean. Raises exception for invalid formats
           Possible True  values: 1, True, "1", "TRue", "yes", "y", "t"
           Possible False values: 0, False, None, [], {}, "", "0", "faLse", "no", "n", "f", 0.0, ...
    """
    if str(value).lower() in ("yes", "y", "true",  "t", "1"):
        return "1"
    if str(value).lower() in ("no",  "n", "false", "f", "0", "0.0", "", "none", "[]", "{}"):
        return "0"
    raise Exception('Invalid value for boolean conversion: ' + str(value))


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# TOC routes and supporting functions
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
"""
# Development only.
@api.route('/get_structured_toc')
#@cache.memoize(timeout=1600)
def get_structured_toc():
    try:
        mooring_list = []
        mooring_key = []

        platform_list = []
        platform_key = []

        instrument_list = []
        instrument_key = []

        # Get toc data from uframe and process, returns data; if exception raise
        data = process_uframe_toc()

        # If no data return empty content immediately
        if data is None:
            return jsonify(toc={'moorings': mooring_list,
                            'platforms': platform_list,
                            'instruments': instrument_list
                            })

        # If data, Process uframe toc data for output
        for d in data:
            if d['reference_designator'] not in instrument_key:
                instrument_list.append({'array_code':d['reference_designator'][0:2],
                                        'display_name': d['instrument_display_name'],
                                        'mooring_code': d['mooring_code'],
                                        'platform_code': d['platform_code'],
                                        'instrument_code': d['platform_code'],
                                        'streams':d['streams'],
                                        'instrument_parameters':d['instrument_parameters'],
                                        'reference_designator':d['reference_designator']
                                     })

                instrument_key.append(d['reference_designator'])

            if d['mooring_code'] not in mooring_key:
                mooring_list.append({'array_code':d['reference_designator'][0:2],
                                     'mooring_code':d['mooring_code'],
                                     'platform_code':d['platform_code'],
                                     'display_name':d['mooring_display_name'],
                                     'geo_location':[],
                                     'reference_designator':d['mooring_code']
                                     })

                mooring_key.append(d['mooring_code'])

            if d['mooring_code']+d['platform_code'] not in platform_key:
                platform_list.append({'array_code':d['reference_designator'][0:2],
                                      'platform_code':d['platform_code'],
                                      'mooring_code':d['mooring_code'],
                                      'reference_designator':d['reference_designator'],
                                      'display_name': d['platform_display_name']
                                        })

                platform_key.append(d['mooring_code']+d['platform_code'])

        return jsonify(toc={'moorings': mooring_list,
                            'platforms': platform_list,
                            'instruments': instrument_list
                            })
    except Exception as e:
        message = str(e.message)
        current_app.logger.info(message)
        return internal_server_error(message)
"""

@api.route('/get_toc')
@cache.memoize(timeout=1600)
def get_toc():
    """ Get uframe toc data; process and return data list; if exception then raise.
    """
    try:
        data = process_uframe_toc()
        if data is None:
            data = []
        return jsonify(toc=data)
    except Exception as err:
        message = str(err.message)
        current_app.logger.info(message)
        return internal_server_error(message)


def get_uframe_toc_data():
    """ Get toc data from uframe; on exception raise. On success, return uframe toc data.
    """
    d = None
    try:
        uframe_url = current_app.config['UFRAME_URL'] + current_app.config['UFRAME_TOC']
        r = requests.get(uframe_url)
        if r.status_code == 200:
            d = r.json()
        return d

    except ConnectionError:
        message = 'ConnectionError for get uframe toc contents.'
        current_app.logger.info(message)
        raise Exception(message)
    except Timeout:
        message = 'Timeout for get uframe toc contents.'
        current_app.logger.info(message)
        raise Exception(message)
    except Exception:
        raise


def process_uframe_toc():
    """ Get toc content from uframe; if error raise. Continue processing based on toc content.
    """
    result = None
    try:
        d = get_uframe_toc_data()
        if d is not None:
            if isinstance(d, dict):
                result = get_uframe_toc(d)
            # TODO Deprecate once transition to new toc format has been completed.
            # TODO A log message here once previous toc is deprecated.
            else:
                result = old_get_uframe_toc(d)
        return result
    except Exception:
        raise


# [OLD FORMAT]
# TODO Deprecate once transition to new toc format has been completed.
@cache.memoize(timeout=1600)
def old_get_uframe_toc(d):
    """ Process uframe response from /sensor/inv/toc' for use in UI.
    """
    if d:
        for row in d:
            try:
                # FIX FOR THE WRONG WAY ROUND
                temp1 = row['platform_code']
                temp2 = row['mooring_code']
                row['mooring_code'] = temp1
                row['platform_code'] = temp2
                instrument_display_name = get_long_display_name_by_rd(row['reference_designator'])
                split_name = instrument_display_name.split(' - ')
                row['instrument_display_name'] = split_name[-1]
                row['mooring_display_name'] = split_name[0]
                row['platform_display_name'] = split_name[1]
            except:
                row['instrument_display_name'] = ""
                row['platform_display_name'] = ""
                row['mooring_display_name'] = ""
        return d
    else:
        return []


# [NEW FORMAT]
@cache.memoize(timeout=1600)
def get_uframe_toc(data):
    """ Process uframe response from /sensor/inv/toc into list of dictionaries for use in UI.

    The toc response has three [required] dictionaries:
        u'instruments', u'parameters_by_stream', u'parameter_definitions'.

    Process toc response into a a list of dictionaries, where dicts have the following format:
        [ {
            "instrument_code": "00-RTE000000",
            "instrument_display_name": "RTE00",
            "instrument_parameters": [
                {
                    "fillValue": "-9999999",
                    "particleKey": "time",
                    "pdId": "PD7",
                    "shape": "SCALAR",
                    "stream": "rte_o_dcl_instrument_recovered",
                    "type": "DOUBLE",
                    "units": "seconds since 1900-01-01",
                    "unsigned": false
                },
                . . .
            ],
            "mooring_code": "CP02PMCO",
            "mooring_display_name": "Coastal Pioneer Central Offshore Profiler Mooring",
            "platform_code": "SBS01",
            "platform_display_name": "Surface Buoy",
            "reference_designator": "CP02PMCO-SBS01-00-RTE000000",
            "streams": [
                {
                    "beginTime": "2014-04-13T13:40:55.951Z",
                    "count": 2795,
                    "endTime": "2014-11-06T22:26:48.041Z",
                    "method": "recovered_host",
                    "sensor": "CP02PMCO-SBS01-00-RTE000000",
                    "stream": "rte_o_dcl_instrument_recovered"
                }
            ]
        },
        . . .
        ]
    """
    error_debug = True  # This produces an informational message in ooiservice.log (default to True)
    error_messages = []
    required_components = ['instruments', 'parameters_by_stream', 'parameter_definitions']
    results = []
    try:
        if data:

            # Validate required components are provided in uframe toc data and not empty.
            for component in required_components:
                if component not in data:
                    message = 'The uframe toc data does not contain required component %s.' % component
                    current_app.logger.info(message)
                    raise Exception(message)
                if not data[component]:
                    message = 'The uframe toc data contains required component %s, but it is empty.' % component
                    current_app.logger.info(message)
                    raise Exception(message)

            # Get working dictionary of parameter definitions keyed by pdId.
            parameter_definitions_dict, all_pdids = get_toc_parameter_dict(data['parameter_definitions'])

            # Process all instruments to compile result
            instruments = data['instruments']
            parameters_by_streams = data['parameters_by_stream']
            for instrument in instruments:

                # Get reference designator and swap mooring and platform code
                rd = instrument['reference_designator']
                mooring = instrument['platform_code']
                platform = instrument['mooring_code']
                result = instrument
                result['mooring_code'] = mooring
                result['platform_code'] = platform

                # Get instrument_display_name, mooring_display_name, platform_display_name; add to result
                result['instrument_display_name'], \
                result['platform_display_name'], \
                result['mooring_display_name'] = get_names_for_toc(rd, mooring, platform)

                # Get "instrument_parameters" for instrument; if error return empty list and log errors.
                param_results, error_messages = get_instrument_parameters(instrument,
                                                                          parameters_by_streams,
                                                                          parameter_definitions_dict,
                                                                          error_messages)
                if param_results is None:
                    result['instrument_parameters'] = []
                    continue

                instrument_parameters = param_results
                result['instrument_parameters'] = instrument_parameters
                results.append(result)

            # Determine if error_messages received during processing; if so, write to log
            if error_debug:
                if error_messages:
                    error_message = 'Error messages in uframe toc content:\n'
                    for message in error_messages:
                        error_message += message + '\n'
                    current_app.logger.info(error_message)

            return results
        else:
            return []
    except Exception as err:
        message = '[get_uframe_toc] exception: %s' % str(err.message)
        current_app.logger.info(message)
        raise


def get_names_for_toc(rd, mooring, platform):
    """ Process display names for toc processing.

    Reference designator: 'GP03FLMB-RIS01-03-DOSTAD000' produces instrument_display_name:
    Global Station Papa Flanking Subsurface Mooring B - Mooring Riser - Dissolved Oxygen Stable Response
    """
    _instrument_display_name = ""
    _mooring_display_name = ""
    _platform_display_name = ""
    try:
        instrument_display_name = get_long_display_name_by_rd(rd)
        if ' - ' in instrument_display_name:
            split_name = instrument_display_name.split(' - ')
            _instrument_display_name = split_name[-1]
            _mooring_display_name = split_name[0]
            _platform_display_name = split_name[1]
        elif '-' in rd:
            mooring, platform, instr = rd.split('-', 2)
            _mooring_display_name = get_display_name_by_rd(mooring)
            tmp_platform = '-'.join([mooring, platform])
            _platform_display_name = get_display_name_by_rd(tmp_platform)
            _instrument_display_name = get_display_name_by_rd(rd)

        return _instrument_display_name, _mooring_display_name, _platform_display_name
    except:
        return "", "", ""


def get_instrument_parameters(instrument, parameters_by_stream, parameter_definitions_dict, error_messages):
    """ For an instrument, return instrument parameters list and error_messages list.

    TODO: Add error processing for following:
        if 'streams' not in instrument:
            if not instrument['streams']:
    """
    errors = False
    rd = None
    try:
        rd = instrument['reference_designator']

        # For each instrument, get instrument_parameters for all streams
        instrument_parameters = []

        # Get all stream names for instrument
        tmp_stream_names = get_stream_names(instrument['streams'])
        for stream_name in tmp_stream_names:

            # Determine stream name has parameter data; if not, error_message
            if stream_name not in parameters_by_stream:
                message = 'Stream %s not provided in parameters_by_stream; used by instrument %s' % (stream_name, rd)
                error_messages.append(message)
                errors = True
                continue

            # Get pdIds for stream from dict 'parameters_by_stream'
            tmp_pdids = parameters_by_stream[stream_name]
            for pdid in tmp_pdids:

                # Determine if pdid in definitions dictionary, if not then error_message
                if pdid not in parameter_definitions_dict:
                    message = 'A pdId %s used by instrument %s ' % (pdid, rd)
                    message += ' not provided in uframe toc \'parameter_definitions\.'
                    error_messages.append(message)
                    errors = True
                    continue

                # If parameter definition is empty, error_message
                if not parameter_definitions_dict[pdid]:
                    message = 'A pdId %s used by instrument %s ' % (pdid, rd)
                    message += ' provided in uframe toc \'parameter_definitions\ is empty.'
                    error_messages.append(message)
                    errors = True
                    continue

                # Get pdid parameter definition
                tmp_param = (parameter_definitions_dict[pdid]).copy()
                tmp_param['stream'] = stream_name

                # Add stream name to parameter dictionary (data enrichment for UI)
                instrument_parameters.append(tmp_param)

        if errors:
            instrument_parameters = None

        return instrument_parameters, error_messages

    except Exception:
        message = 'Exception processing instrument parameters for %s.' % rd
        current_app.logger.info(message)
        return None, error_messages


def get_toc_parameter_dict(definitions):
    """ Process the uframe toc['parameter_definitions'] list into a list of dict keyed by pdId. Return dict and pdids.
    """
    result = {}
    pdids = []
    if not definitions:
        return {}
    for definition in definitions:
        pdid = definition['pdId']
        if pdid:
            if pdid not in pdids:
                definition['particleKey'] = definition['particle_key']
                del definition['particle_key']
                pdids.append(pdid)
                result[pdid] = definition
    return result, pdids


def get_stream_names(streams):
    """ For an instrument, process streams (list of dictionaries), create list of stream names.
    """
    stream_names = []
    if streams:
        for stream in streams:
            if stream['stream'] not in stream_names:
                stream_names.append(stream['stream'])
    return stream_names
