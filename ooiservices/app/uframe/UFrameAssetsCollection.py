'''
uFrameAssetCollection:
- Represents the latest attributes of the uframe endpoint.
- Important methods:
    to_json(id=None):
        Reaches out to uframe and gets either the complete list of assets, or
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

class UFrameAssetsCollection(object):

    #Define the connection

    __endpoint__ = 'assets'
    # m@c: Updated 03/03/2015
    class_type =  None
    meta_data = []
    asset_info = None
    manufacture_info = None
    notes = None
    asset_id = None
    attachments = []
    purchase_and_delivery_info = None
    physical_info = None
    identifier = None
    trace_id = None
    overwrite_allowed = False

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

            data = payload.json()
            return data
        except Exception as e:
            return make_response("error: %s. UFrameAssetsCollection.py. Line # %s" % (e,sys.exc_info()[2].tb_lineno ), 500)

    def from_json(self, json):
        # Below section is from UI
        class_type = json.get('asset_class')
        asset_info = json.get('assetInfo')
        manufacture_info = json.get('manufactureInfo')
        notes = json.get('notes')
        asset_id = json.get('id')
        attachments = json.get('attachments')
        purchase_and_delivery_info = json.get('purchaseAndDeliveryInfo')
        #coordinates = json.get('coordinates')
        #launch_date_time = json.get('launch_date_time')
        #water_depth = json.get('water_depth')
        #ref_des = json.get('ref_des')
        meta_data = json.get('metaData')
        ### These are not returned, for now they don't exist in uframe.
        identifier = json.get('identifier')
        trace_id = json.get('traceId')
        overwrite_allowed = json.get('overwriteAllowed')
        platform = json.get('platform')
        deployment_number = json.get('deployment_number')
        last_modified_imestamp = json.get("lastModifiedTimestamp")
        class_code = json.get("classCode")
        series_classification = json.get("seriesClassification")
        #####

        #Below section's keys are uFrame specific and shouldn't be modified
        #unless necessary to support uframe updates.
        formatted_return = {
                "@class": class_type,
                "assetId": asset_id,
                "metaData": meta_data,
                "assetInfo": asset_info,
                "manufacturerInfo": manufacture_info,
                "notes": notes,
                "attachments": attachments,
                "purchaseAndDeliveryInfo": purchase_and_delivery_info,
                "lastModifiedTimestamp": last_modified_imestamp,
                "classCode": class_code,
                "seriesClassification": series_classification
                }
        return formatted_return
