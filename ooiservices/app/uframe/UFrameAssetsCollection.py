'''
uFrameAssetCollection:
- Represents the latest attributes of the uframe endpoint.
- Important methods:
    to_json(id=None):
        Reaches out to uframe and gets either the complete list of assets, or
        if an id is provided, an individual object.
    from_json():
        Prepares a JSON packet to be sent as either a POST or a PUT to uframe.
        There are some translation from what is sent from ooi ui, and what
        uframe is expecting.
        Please review method for further details.
'''

from flask import make_response, current_app
import requests
import sys


class UFrameAssetsCollection(object):

    __endpoint__ = 'assets'
    # m@c: Updated 03/03/2015
    '''
    Create a json object that contains all uframe assets.
    This will be the collection that will may be parsed.
    '''
    obj = None

    def __init__(self):
        object.__init__(self)
        pass

    def to_json(self, id=None):
        if id is not None:
            url = current_app.config['UFRAME_ASSETS_URL']\
                + '/%s/%s' % (self.__endpoint__, id)
        else:
            url = current_app.config['UFRAME_ASSETS_URL']\
                + '/%s' % self.__endpoint__

        try:
            payload = requests.get(url)
            return payload
        except Exception as e:
            return make_response(
                "error: %s. UFrameAssetsCollection.py. Line # %s"
                % (e, sys.exc_info()[2].tb_lineno), 500)

    def from_json(self, json):
        '''
        Below section's keys are uFrame specific and shouldn't be modified
        unless necessary to support uframe updates.
        '''
        formatted_return = {
            '@class': json.get('asset_class'),
            'metaData': json.get('metaData'),
            'remoteDocuments': json.get('remoteDocuments'),
            'assetInfo': json.get('assetInfo'),
            'manufactureInfo': json.get('manufactureInfo'),
            'physicalInfo': json.get('physicalInfo'),
            'purchaseAndDeliveryInfo': json.get('purchaseAndDeliveryInfo'),
        }
        return formatted_return
