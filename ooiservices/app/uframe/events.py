from flask import url_for, request, current_app, jsonify
from ooiservices.app.uframe import uframe as api
from ooiservices.app.main.authentication import auth
from ooiservices.app.uframe.UFrameEventsCollection import UFrameEventsCollection
from ooiservices.app.uframe.assetController import get_events_by_ref_des
from ooiservices.app.uframe.assetController import convert_lat_lon
from ooiservices.app.uframe.assetController import convert_date_time
from ooiservices.app.uframe.assetController import convert_water_depth
from ooiservices.app.uframe.assetController import _uframe_url
from ooiservices.app.uframe.assetController import _uframe_headers
from ooiservices.app.main.routes import get_display_name_by_rd
from ooiservices.app import cache
from operator import itemgetter
from copy import deepcopy
from netCDF4 import num2date

import json
import requests

#Default number of times to retry the connection:
requests.adapters.DEFAULT_RETRIES = 2
CACHE_TIMEOUT = 86400
### ---------------------------------------------------------------------------
### BEGIN Events CRUD methods.
### ---------------------------------------------------------------------------
#Read (list)
@api.route('/events', methods=['GET'])
def get_events():
    '''
    -- M@C 05/12/2015
    Added to support event query on stream data.
    '''
    try:
        '''
        Listing GET request of all events.  This method is cached for 1 hour.
        '''
        #set up all the contaners.
        data = {}

        #Manually set up the cache
        cached = cache.get('event_list')
        if cached:
            data = cached

        else:
            #create uframe instance, and fetch the data.
            uframe_obj = UFrameEventsCollection()
            payload = uframe_obj.to_json()
            data = payload.json()
            if payload.status_code != 200:
                return  jsonify({ "events" : payload.json()}), payload.status_code

            try:
                for row in data:
                    row['id'] = row.pop('eventId')
                    row['class'] = row.pop('@class')
                #parse the result and assign ref_des as top element.
            except (KeyError, TypeError, AttributeError):
                pass

            if "error" not in data:
                cache.set('event_list', data, timeout=CACHE_TIMEOUT)

        #data = sorted(data, key=itemgetter('id'))

        if request.args.get('search') and request.args.get('search') != "":
            return_list = []
            ven_set = []
            search_term = str(request.args.get('search')).split()
            search_set = set(search_term)
            for subset in search_set:
                if len(return_list) > 0:
                    if len(ven_set) > 0:
                        ven_set = deepcopy(ven_subset)
                    else:
                        ven_set = deepcopy(return_list)
                    ven_subset = []
                    for item in return_list:
                        if subset.lower() in str(item['class']).lower():
                            ven_subset.append(item)
                        elif subset.lower() in str(item['id']).lower():
                            ven_subset.append(item)
                        elif subset.lower() in str(item['startDate']).lower():
                            ven_subset.append(item)
                        elif subset.lower() in str(item['referenceDesignator']).lower():
                            ven_subset.append(item)
                    data = ven_subset
                else:
                    for item in data:
                        if subset.lower() in str(item['class']).lower():
                            return_list.append(item)
                        elif subset.lower() in str(item['id']).lower():
                            return_list.append(item)
                        elif subset.lower() in str(item['startDate']).lower():
                            return_list.append(item)
                        elif subset.lower() in str(item['referenceDesignator']).lower():
                            return_list.append(item)
                    data = return_list

        result = jsonify({ 'events' : data })
        return result

    except requests.exceptions.ConnectionError as e:
        error = "Error: Cannot connect to uframe.  %s" % e
        print error
        return make_response(error, 500)

#Read (object)
@api.route('/events/<int:id>', methods=['GET'])
def get_event(id):
    '''
    Object response for the GET(id) request.  This response is NOT cached.
    '''
    try:
        #set up all the contaners.
        data = {}
        asset_id = ""
        #create uframe instance, and fetch the data.
        uframe_obj = UFrameEventsCollection()
        payload = uframe_obj.to_json(id)
        data = payload.json()
        if payload.status_code != 200:
            return  jsonify({ "events" : payload.json()}), payload.status_code

        try:
            data['class'] = data.pop('@class')
            data['startDate'] = num2date(float(data['startDate'])/1000, units='seconds since 1970-01-01 00:00:00', calendar='gregorian')
            data['endDate'] = num2date(float(data['endDate'])/1000, units='seconds since 1970-01-01 00:00:00', calendar='gregorian')
        except (KeyError, TypeError):
            pass
        return jsonify(**data)

    except requests.exceptions.ConnectionError as e:
        error = "Error: Cannot connect to uframe.  %s" % e
        print error
        return make_response(error, 500)

#Create
@auth.login_required
@api.route('/events', methods=['POST'])
def create_event():
    '''
    Create a new event, the return will be right from uframe if all goes well.
    Either a success or an error message.
    Login required.
    '''
    try:
        data = json.loads(request.data)
        uframe_obj = UFrameEventsCollection()
        post_body = uframe_obj.from_json(data)
        uframe_events_url = _uframe_url(uframe_obj.__endpoint__)
        response = requests.post(uframe_events_url, data=json.dumps(post_body), headers=_uframe_headers())
        cache.delete('event_list')
        return response.text

    except requests.exceptions.ConnectionError as e:
        error = "Error: Cannot connect to uframe.  %s" % e
        print error
        return make_response(error, 500)

#Update
@auth.login_required
@api.route('/events/<int:id>', methods=['PUT'])
def update_event(id):
    '''
    Update an existing event, the return will be right from uframe if all goes well.
    Either a success or an error message.
    Login required.
    '''
    try:
        data = json.loads(request.data)
        uframe_obj = UFrameEventsCollection()
        put_body = uframe_obj.from_json(data)
        uframe_events_url = _uframe_url(uframe_obj.__endpoint__, id)
        response = requests.put(uframe_events_url, data=json.dumps(put_body), headers=_uframe_headers())
        cache.delete('event_list')
        return response.text

    except requests.exceptions.ConnectionError as e:
        error = "Error: Cannot connect to uframe.  %s" % e
        print error
        return make_response(error, 500)

#Delete
#Not supported

### ---------------------------------------------------------------------------
### END Events CRUD methods.
### ---------------------------------------------------------------------------
