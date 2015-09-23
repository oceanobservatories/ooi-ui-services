'''
uFrameEventCollection:
- Represents the latest attributes of the uframe endpoint.
- Important methods:
    to_json(id=None):
        Reaches out to uframe and gets either the complete list of events, or
        if an id is provided, an individual object.
    from_json():
        Prepares a JSON packet to be sent as either a POST or a PUT to uframe.
        There are some translation from what is sent from ooi ui, and what uframe
        is expecting.
        Please review method for further details.
'''

from flask import make_response, current_app
import requests
import sys

class UFrameEventsCollection(object):

    __endpoint__ = 'events'
    __uframe_url__ = ''
    #Create a json object that contains all uframe assets.
    #This will be the collection that will may be parsed.
    obj = None

    def __init__(self):
        object.__init__(self)
        pass


    def to_json(self,id=None):
        if id is not None:
            url = current_app.config['UFRAME_ASSETS_URL'] + '/%s/%s' % (self.__endpoint__, id)
        else:
            url = current_app.config['UFRAME_ASSETS_URL'] + '/%s' % self.__endpoint__

        try:
            payload = requests.get(url)
            return payload
        except Exception as e:
            return make_response("error: %s. UFrameEventsCollection.py. Line # %s" % (e,sys.exc_info()[2].tb_lineno ), 500)

    def from_json(self, json):
        event_class = json.get('class')
        reference_designator = json.get('referenceDesignator')
        deployment_number = json.get('deploymentNumber')
        deployment_name = json.get('deploymentName')
        deployment_depth = json.get('deploymentDepth')
        depthUnit_string = json.get('depthUnitString')
        deployment_doc_urls = json.get('deploymentDocUrls')
        deployment_location = json.get('deploymentLocation')
        cruise_number = json.get('cruiseNumber')
        location_lon_lat = json.get('locationLonLat')
        location_name = json.get('locationName')
        event_type = json.get('eventType')
        start_date = json.get('startDate')
        end_date = json.get('endDate')
        event_description = json.get('eventDescription')
        recorded_by = json.get('recordedBy')
        asset = json.get('asset')
        notes = json.get('notes')
        attachments = json.get('attachments')
        tense = json.get('tense')
        last_modified_timestamp = json.get('lastModifiedTimestamp')

        #Update deploymentLocation to send a float even if Lat/Lon is an int.
        if deployment_location is not None:
            deployment_location = [
                float(deployment_location[0]),
                float(deployment_location[1])
            ]

        formatted_return = {
            '@class' : event_class,
            'referenceDesignator': reference_designator,
            'deploymentNumber': deployment_number,
            'deploymentName': deployment_name,
            'deploymentDepth': deployment_depth,
            'depthUnitString': depthUnit_string,
            'deploymentDocUrls': deployment_doc_urls,
            'deploymentLocation': deployment_location,
            'cruiseNumber': cruise_number,
            'locationLonLat': location_lon_lat,
            'locationName': location_name,
            'eventType': event_type,
            'startDate': start_date,
            'endDate': end_date,
            'eventDescription': event_description,
            'recordedBy': recorded_by,
            'asset': asset,
            'notes': notes,
            'attachments': attachments,
            'tense': tense,
            'lastModifiedTimestamp': last_modified_timestamp
        }
        return formatted_return
