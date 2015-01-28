#!/usr/bin/env python
'''
uframe endpoints

'''
__author__ = 'Andy Bird'

from flask import jsonify, request, current_app, url_for
from ooiservices.app.uframe import uframe as api
from ooiservices.app import db
from ooiservices.app.main.authentication import auth
from ooiservices.app.models import Array, PlatformDeployment, InstrumentDeployment
from ooiservices.app.models import Stream, StreamParameter, Organization, Instrumentname

from ooiservices.app.uframe.data import gen_data

import json
import datetime

def get_uframe_data():
    '''
    stub mock function to get some sample data
    '''
    json_data=open('ooiservices/tests/sampleData.json')
    data = json.load(json_data)
    return data

def get_data_type(data_input):
    '''
    gets the data type in a format google charts understands
    '''
    if data_input is float or data_input is int:
        return "number"
    elif data_input is str or data_input is unicode:
        return "string"
    else:
        return "unknown"

@api.route('/get_data',methods=['GET'])
def get_data():
    #get data from uframe
    data = get_uframe_data()
    hasAnnotation = False
    if 'annotation' in request.args:
        #generate annotation plot
        if request.args['annotation'] == "true":
            hasAnnotation = True        
  
    #got normal data plot
    #create the data fields,assumes the same data fields throughout
    d_row = data[0]
    data_fields = []
    data_field_list= []
    some_data = []
    #time minus ()
    cosmo_constant = 2208988800
    time_idx = -1   
    pref_timestamp = d_row["preferred_timestamp"]
    #ignore list for data fields
    ignore_list = ["preferred_timestamp","stream_name","driver_timestamp","quality_flag"]
    #figure out the header rows
    inital_fields = d_row.keys()
    #move timestamp to the front 
    inital_fields.insert(0, inital_fields.pop(inital_fields.index(pref_timestamp)))

    for field in inital_fields:
        if field in ignore_list:
            pass
        else:
            #map the data types to the correct data type for google charts
            if field == pref_timestamp:
                d_type = "datetime"
            else:             
                d_type = get_data_type(type(data[0][field]))   

            data_field_list.append(field)
            data_fields.append({"id": "",
                                "label": field,
                                "type":  d_type}) 

    if hasAnnotation:
        data_field_list.append("annotation")
        data_field_list.append("annotationText")
        data_fields.append({"label":"title1","type":  "string" , "role":"annotation"}) 
        data_fields.append({"label":"text1","type":  "string" , "role":"annotationText"}) 
    
    #figure out the data content 
    for d in data:
        c_r = []        
        for field in data_field_list:
            if field.endswith("_timestamp"):
                #create data time object
                c_dt = datetime.datetime.fromtimestamp(d[field] - cosmo_constant)                
                str_date = c_dt.isoformat()
                date_str = "Date("+str(c_dt.year)+","+str(c_dt.month)+","+str(c_dt.day)+","+str(c_dt.hour)+","+str(c_dt.minute)+","+str(c_dt.second)+")"
                c_r.append({"f":str_date,"v":date_str})            
                if field == pref_timestamp:
                    time_idx = len(c_r)-1                
            elif field == ("annotation"):
                if d['dofst_k_oxygen']>3277:                    
                    c_r.append({"v":"test"})  
                else:
                    c_r.append({"v":None})
            elif field == ("annotationText"):
                if d['dofst_k_oxygen']>3277:      
                    c_r.append({"v":"test"})  
                else:                        
                    c_r.append({"v":None})
            else:
                c_r.append({"v":d[field],"f":d[field]})
     
        some_data.insert(0,{"c":c_r}) 
    
    #genereate dict for the data thing
    resp_data = {'cols':data_fields,
                 'rows':some_data
                 #'size':len(some_data),
                 #'start_time' : datetime.datetime.fromtimestamp(data[0][pref_timestamp]).isoformat(),
                 #'end_time' : datetime.datetime.fromtimestamp(data[-1][pref_timestamp]).isoformat()
                 }        
            
    return jsonify(**resp_data)

@api.route('/platformlocation', methods=['GET'])
def get_platform_deployment_geojson_single():
    geo_locations = {}
    if len(request.args) > 0:
        if ('reference_designator' in request.args):
            if len(request.args['reference_designator']) < 100:
                reference_designator = request.args['reference_designator']
                geo_locations = PlatformDeployment.query.filter(PlatformDeployment.reference_designator == reference_designator).all()
    else:
        geo_locations = PlatformDeployment.query.all()
    if len(geo_locations) == 0:
        return '{}', 204
    return jsonify({ 'geo_locations' : [{'id' : geo_location.id, 'reference_designator' : geo_location.reference_designator, 'geojson' : geo_location.geojson} for geo_location in geo_locations] })

@api.route('/display_name', methods=['GET'])
def get_display_name():
    # 'CE01ISSM-SBD17'
    platform_deployment_filtered = None
    display_name = ''
    if len(request.args) > 0:
        if ('reference_designator' in request.args):
            if len(request.args['reference_designator']) < 100:
                reference_designator = request.args['reference_designator']
                platform_deployment_filtered = PlatformDeployment.query.filter_by(reference_designator=reference_designator).first_or_404()
                display_name = platform_deployment_filtered.proper_display_name
    if platform_deployment_filtered is None:
        return '{}', 204
    return jsonify({ 'proper_display_name' : display_name })