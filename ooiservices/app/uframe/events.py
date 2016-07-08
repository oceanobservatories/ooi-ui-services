from flask import jsonify, current_app
from ooiservices.app.uframe import uframe as api
#from ooiservices.app.main.authentication import auth
#from ooiservices.app.decorators import scope_required
#from ooiservices.app.uframe.assetController import get_events_by_ref_des
#from ooiservices.app.uframe.assetController import _uframe_headers, _compile_events
#from ooiservices.app import cache
#from copy import deepcopy

#import json
import requests
import requests.adapters
from requests.exceptions import ConnectionError, Timeout
from ooiservices.app.main.errors import (bad_request, internal_server_error)

requests.adapters.DEFAULT_RETRIES = 2
CACHE_TIMEOUT = 86400

# todo - rework when endpoint becomes available.
@api.route('/events', methods=['GET'])
def get_events():
    """ Get all events.
    """
    try:
        """
        Listing GET request of all events.  This method is cached for 1 hour.
        """
        data = {}

        """
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
        """
        result = jsonify({'events': data})
        return result

    except ConnectionError as err:
        message = "ConnectionError getting events from uframe;  %s" % str(err)
        current_app.logger.info(message)
        return internal_server_error(message)
    except Timeout as err:
        message = "Timeout getting events from uframe;  %s" % str(err)
        current_app.logger.info(message)
        return internal_server_error(message)
    except Exception as err:
        message = "Error getting events from uframe; %s" % str(err)
        current_app.logger.info(message)
        return internal_server_error(message)


# todo - rework when endpoint becomes available.
@api.route('/events/<int:id>', methods=['GET'])
def get_event(id):
    """ Object response for the GET(id) request.  This response is NOT cached.
    """
    try:
        data = {}
        """
        url = current_app.config['UFRAME_ASSETS_URL'] + '/%s/%s' % ('events', id)
        payload = requests.get(url)
        data = payload.json()
        if payload.status_code != 200:
            return jsonify({"events": payload.json()}), payload.status_code

        try:
            data['eventClass'] = data.pop('@class')
        except (KeyError, TypeError):
            pass

        return jsonify(**data)
        """
        return jsonify(data)

    except ConnectionError as err:
        message = "ConnectionError getting event %d from uframe;  %s" % (id, str(err))
        current_app.logger.info(message)
        return internal_server_error(message)
    except Timeout as err:
        message = "Timeout getting event %d from uframe;  %s" % (id, str(err))
        current_app.logger.info(message)
        return internal_server_error(message)
    except Exception as err:
        message = "Error getting event %d from uframe; %s" % (id, str(err))
        current_app.logger.info(message)
        return internal_server_error(message)


# todo - rework when endpoint becomes available.
@api.route('/events', methods=['POST'])
def create_event():
    """ Create a new event.
    The return will be right from uframe if all goes well.
    Either a success or an error message.
    Login required.
    """
    try:
        """
        data = json.loads(request.data)
        url = current_app.config['UFRAME_ASSETS_URL']\
            + '/%s/%s' % ('events', id)
        data['@class'] = data.pop('eventClass')
        response = requests.post(url,
                                 data=json.dumps(data),
                                 headers=_uframe_headers())
        cache.delete('event_list')
        return response.text, response.status_code
        """
        message = 'Create event not supported at this time.'
        return internal_server_error(message)

    except ConnectionError as err:
        message = "ConnectionError from uframe during create event;  %s" % str(err)
        current_app.logger.info(message)
        return internal_server_error(message)
    except Timeout as err:
        message = "Timeout from uframe during create event;  %s" % str(err)
        current_app.logger.info(message)
        return internal_server_error(message)
    except Exception as err:
        message = "Error from uframe during create event; %s" % str(err)
        current_app.logger.info(message)
        return internal_server_error(message)


# todo - rework when endpoint becomes available.
@api.route('/events/<int:id>', methods=['PUT'])
def update_event(id):
    """ Update an existing event.
    """
    try:
        """
        data = json.loads(request.data)
        url = current_app.config['UFRAME_ASSETS_URL']\
            + '/%s/%s' % ('events', id)
        data['@class'] = data.pop('eventClass')
        response = requests.put(url,
                                data=json.dumps(data),
                                headers=_uframe_headers())
        cache.delete('event_list')
        return response.text, response.status_code
        """
        message = 'Update event not supported at this time.'
        return internal_server_error(message)

    except ConnectionError as err:
        message = "ConnectionError from uframe during update event;  %s" % str(err)
        current_app.logger.info(message)
        return internal_server_error(message)
    except Timeout as err:
        message = "Timeout from uframe during update event;  %s" % str(err)
        current_app.logger.info(message)
        return internal_server_error(message)
    except Exception as err:
        message = "Error from uframe during update event; %s" % str(err)
        current_app.logger.info(message)
        return internal_server_error(message)


# todo - rework when endpoint becomes available.
@api.route('/events/<int:id>', methods=['DELETE'])
def delete_event(id):
    """ Delete an existing event.
    """
    try:
        """
        url = current_app.config['UFRAME_ASSETS_URL']\
            + '/%s/%s' % ('events', id)
        response = requests.delete(url,
                                   headers=_uframe_headers())
        cache.delete('event_list')
        return response.text, response.status_code
        """
        message = 'Delete event not supported at this time.'
        return internal_server_error(message)

    except ConnectionError as err:
        message = "ConnectionError from uframe during delete event;  %s" % str(err)
        current_app.logger.info(message)
        return internal_server_error(message)
    except Timeout as err:
        message = "Timeout from uframe during delete event;  %s" % str(err)
        current_app.logger.info(message)
        return internal_server_error(message)
    except Exception as err:
        message = "Error from uframe during delete event; %s" % str(err)
        current_app.logger.info(message)
        return internal_server_error(message)
