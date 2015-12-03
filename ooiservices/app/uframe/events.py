from flask import request, jsonify, make_response, current_app
from ooiservices.app.uframe import uframe as api
from ooiservices.app.main.authentication import auth
from ooiservices.app.decorators import scope_required
from ooiservices.app.uframe.assetController import get_events_by_ref_des
from ooiservices.app.uframe.assetController import _uframe_headers,\
    _compile_events
from ooiservices.app import cache
from copy import deepcopy

import json
import requests

requests.adapters.DEFAULT_RETRIES = 2
CACHE_TIMEOUT = 86400


'''
 BEGIN Events CRUD methods.
'''


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
        data = {}

        cached = cache.get('event_list')
        if cached:
            data = cached

        else:
            url = current_app.config['UFRAME_ASSETS_URL']\
                + '/%s' % 'events'

            payload = requests.get(url)

            data = payload.json()
            if payload.status_code != 200:
                return jsonify({"events": payload.json()}), payload.status_code

            data = _compile_events(data)

            if "error" not in data:
                cache.set('event_list', data, timeout=CACHE_TIMEOUT)

        if request.args.get('ref_des') and request.args.get('ref_des') != "":
            ref_des = request.args.get('ref_des')
            resp = get_events_by_ref_des(data, ref_des)
            return resp

        if request.args.get('search') and request.args.get('search') != "":
            return_list = []
            ven_set = []
            ven_subset = []
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
                        if subset.lower() in str(item['eventClass']).lower():
                            ven_subset.append(item)
                        elif subset.lower() in str(item['id']).lower():
                            ven_subset.append(item)
                        elif subset.lower() in str(item['startDate']).lower():
                            ven_subset.append(item)
                    data = ven_subset
                else:
                    for item in data:
                        if subset.lower() in str(item['eventClass']).lower():
                            return_list.append(item)
                        elif subset.lower() in str(item['id']).lower():
                            return_list.append(item)
                        elif subset.lower() in str(item['startDate']).lower():
                            return_list.append(item)
                    data = return_list

        result = jsonify({'events': data})
        return result

    except requests.exceptions.ConnectionError as e:
        error = "Error: Cannot connect to uframe.  %s" % e
        print error
        return make_response(error, 500)


@api.route('/events/<int:id>', methods=['GET'])
def get_event(id):
    '''
    Object response for the GET(id) request.  This response is NOT cached.
    '''
    try:
        data = {}
        url = current_app.config['UFRAME_ASSETS_URL']\
            + '/%s/%s' % ('events', id)
        payload = requests.get(url)
        data = payload.json()
        if payload.status_code != 200:
            return jsonify({"events": payload.json()}), payload.status_code

        try:
            data['eventClass'] = data.pop('@class')
        except (KeyError, TypeError):
            pass

        return jsonify(**data)

    except requests.exceptions.ConnectionError as e:
        error = "Error: Cannot connect to uframe.  %s" % e
        print error
        return make_response(error, 500)


@api.route('/events', methods=['POST'])
def create_event():
    '''
    Create a new event, the return will be right from uframe if all goes well.
    Either a success or an error message.
    Login required.
    '''
    try:
        data = json.loads(request.data)
        url = current_app.config['UFRAME_ASSETS_URL']\
            + '/%s/%s' % ('events', id)
        data['@class'] = data.pop('eventClass')
        response = requests.post(url,
                                 data=json.dumps(data),
                                 headers=_uframe_headers())
        cache.delete('event_list')
        return response.text, response.status_code

    except requests.exceptions.ConnectionError as e:
        error = "Error: Cannot connect to uframe.  %s" % e
        print error
        return make_response(error, 500)


@api.route('/events/<int:id>', methods=['PUT'])
def update_event(id):
    try:
        data = json.loads(request.data)
        url = current_app.config['UFRAME_ASSETS_URL']\
            + '/%s/%s' % ('events', id)
        data['@class'] = data.pop('eventClass')
        response = requests.put(url,
                                data=json.dumps(data),
                                headers=_uframe_headers())
        cache.delete('event_list')
        return response.text, response.status_code

    except requests.exceptions.ConnectionError as e:
        error = "Error: Cannot connect to uframe.  %s" % e
        print error
        return make_response(error, 500)


@api.route('/events/<int:id>', methods=['DELETE'])
def delete_event(id):
    '''
    Delete an existing event
    '''
    try:
        url = current_app.config['UFRAME_ASSETS_URL']\
            + '/%s/%s' % ('events', id)
        response = requests.delete(url,
                                   headers=_uframe_headers())
        cache.delete('event_list')
        return response.text, response.status_code

    except requests.exceptions.ConnectionError as e:
        error = "Error: Cannot connect to uframe.  %s" % e
        print error
        return make_response(error, 500)

'''
END Events CRUD methods.
'''
