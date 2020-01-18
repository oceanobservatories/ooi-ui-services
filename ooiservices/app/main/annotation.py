#!/usr/bin/env python
"""
Annotation endpoints and supporting functions.
"""
__author__ = 'M@Campbell'


from datetime import datetime
import time
import requests
from requests.exceptions import (ConnectionError, Timeout)
from flask import (jsonify, request, current_app)
from dateutil.parser import parse as parse_date
from authentication import auth
from ooiservices.app.decorators import scope_required
from ooiservices.app.main import api
from ooiservices.app.uframe.config import (get_uframe_timeout_info, get_annotations_base_url, _uframe_headers)
from ooiservices.app.main.errors import bad_request
from ooiservices.app.uframe.common_tools import get_qcflags_map
import json


unix_epoch = parse_date('1970-01-01T00:00:00.000Z')


# Helper methods
def get_refdes(anno_record):
    """ Build and return a reference designator from the subsite, node and sensor fields in record supplied.
    """
    subsite = anno_record.get('subsite', None)
    node = anno_record.get('node', None)
    sensor = anno_record.get('sensor', None)
    if node is None:
        return subsite
    if sensor is None:
        return '-'.join((subsite, node))
    return '-'.join((subsite, node, sensor))


def get_refdes_parts(anno_record):
    """ Given an annotation record with a reference designator, return the corresponding subsite, node and sensor.
    """
    subsite = None
    node = None
    sensor = None
    refdes = anno_record.get('referenceDesignator')
    if '-' not in refdes:
        subsite = refdes
    else:
        parts = refdes.split('-', 2)
        if len(parts) > 0:
            subsite = parts[0]
        if len(parts) > 1:
            node = parts[1]
        if len(parts) > 2:
            sensor = parts[2]
    return subsite, node, sensor


def timestamp_to_millis(timestamp):
    """ Convert the timestamp (string or datetime) into integer milliseconds since 1970-1-1
    """
    if isinstance(timestamp, basestring):
        timestamp = parse_date(timestamp)
    if isinstance(timestamp, datetime):
        try:
            return int((timestamp - unix_epoch).total_seconds() * 1000)
        except ValueError:
            return None
        except Exception:
            return None


def millis_to_timestamp(millis):
    """ Convert milliseconds since 1970-1-1 to a python datetime object.
    """
    try:
        if (isinstance(millis, int) or isinstance(millis, long)) and millis > 0:
            #return datetime.utcfromtimestamp(millis / 1000.0)
            return millis
        else:
            return None
    except Exception as err:
        message = 'Exception: millis_to_timestamp(%r), %s' % (millis, str(err))
        current_app.logger.debug(message)
        return None


def remap_uframe_to_ui(anno_record, rd_type=None):
    """ Remap the annotation record with a reference designator and human-readable timestamps.
    """
    debug = False
    try:
        if debug:
            print '\n debug -- Entered remap_uframe_to_ui...'
            print '\n\t debug -- rd_type: ', rd_type
            print '\n\t debug -- anno_record: ', anno_record
        if rd_type == 'sensor':
            method = anno_record['method']
            stream = anno_record['stream']
            if debug:
                print '\n\t debug -- method: *%r*' % method
                print '\n\t debug -- stream: *%r*' % stream
            #method = '' if method is None else method.replace('_', '-')
            #stream = '' if stream is None else stream.replace('_', '-')
            if method and method is not None:
                method = str(method).replace('_', '-')
            if stream and stream is not None:
                stream = str(stream).replace('_', '-')
            if debug:
                print '\n\t debug -- method: *%r*' % method
                print '\n\t debug -- stream: *%r*' % stream
            if stream is not None and method is not None:
                if debug: print '\n\t debug -- Before join...'
                anno_record['stream_name'] = '_'.join((method, stream))
                if debug: print '\n\t debug -- stream_name: %r' % anno_record['stream_name']
            else:
                anno_record['stream_name'] = None
                if debug:
                    print '\n\t debug -- stream_name is None for a sensor!!!!  ***************'
                    print '\n\t debug -- method: %r' % method
                    print '\n\t debug -- stream: %r' % stream

        anno_record['referenceDesignator'] = get_refdes(anno_record)
        anno_record['beginDT'] = millis_to_timestamp(anno_record.get('beginDT'))
        anno_record['endDT'] = millis_to_timestamp(anno_record.get('endDT'))
        return anno_record
    except Exception as err:
        message = str(err)
        raise Exception(message)


def remap_ui_to_uframe(anno_record, rd_type=None):
    try:
        if rd_type == 'sensor':
            subsite, node, sensor = get_refdes_parts(anno_record)
            stream_name = anno_record['stream_name']
            if '_' in stream_name:
                method, stream = stream_name.split('_')
                method = method.replace('-', '_')
                stream = stream.replace('-', '_')
            else:
                method = None
                stream = None
            anno_record['subsite'] = subsite
            anno_record['node'] = node
            anno_record['sensor'] = sensor
            anno_record['beginDT'] = timestamp_to_millis(anno_record['beginDT'])
            anno_record['endDT'] = timestamp_to_millis(anno_record['endDT'])
            anno_record['method'] = method
            anno_record['stream'] = stream
            anno_record['@class'] = '.AnnotationRecord'
        elif rd_type == 'subsite':
            result = {}
            result['@class'] = '.AnnotationRecord'
            result['subsite'] = anno_record['subsite']
            result['beginDT'] = timestamp_to_millis(anno_record['beginDT'])
            result['endDT'] = timestamp_to_millis(anno_record['endDT'])
            result['referenceDesignator'] = anno_record['subsite']
            result['annotation'] = anno_record['annotation']
            result['method'] = anno_record['method']
            result['source'] = anno_record['source']
            result['qcFlag'] =  anno_record['qcFlag']
            result['exclusionFlag'] = anno_record['exclusionFlag']
            result['stream'] = None
            result['node'] = None
            result['sensor'] = None
            result['stream'] = None
            result['stream_name'] = None
            anno_record = result
        elif rd_type == 'node':
            result = {}
            result['@class'] = '.AnnotationRecord'
            result['referenceDesignator'] = anno_record['referenceDesignator']
            result['beginDT'] = timestamp_to_millis(anno_record['beginDT'])
            result['endDT'] = timestamp_to_millis(anno_record['endDT'])
            result['annotation'] = anno_record['annotation']
            result['method'] = anno_record['method']
            result['source'] = anno_record['source']
            result['qcFlag'] =  anno_record['qcFlag']
            result['exclusionFlag'] = anno_record['exclusionFlag']
            result['subsite'] = anno_record['subsite']
            result['node'] = anno_record['node']
            result['sensor'] = None
            result['stream'] = None
            result['stream_name'] = None
            anno_record = result

        anno_record['@class'] = '.AnnotationRecord'
        return anno_record
    except Exception as err:
        message = str(err)
        raise Exception(message)


def validate_anno_record(anno_record):
    required_fields = {'referenceDesignator', 'annotation', 'beginDT', 'endDT', 'source'}
    return len(required_fields.difference(anno_record)) == 0


@api.route('/annotation', methods=['GET'])
def get_annotations():
    """ Fetch all annotations associated with the specified Reference Designator,
    delivery method, stream name and time bounds; return JSON Response containing all found annotations

    http://host:12580/anno/find?refdes=CE01ISSP-SP001-02-DOSTAJ000&method=telemetered
    &stream=dosta_abcdjm_cspp_instrument&beginDT=1482200000000&endDT=1482300000000
    [
        {
          "@class" : ".AnnotationRecord",
          "annotation" : "This is a test",
          "method" : "telemetered",
          "id" : 1,
          "source" : "user=aTestuser",
          "node" : "SP001",
          "stream" : "dosta_abcdjm_cspp_instrument",
          "sensor" : "02-DOSTAJ000",
          "beginDT" : 1482202000000,
          "endDT" : 1482204000000,
          "subsite" : "CE01ISSP",
          "exclusionFlag" : true
        }
    ]

    Example of params being sent to filter data:
    {
        "beginDT": 1397776652029,
        "endDT": 1398988704162,
        "method": "telemetered",
        "refdes": "CE01ISSP-SP001-02-DOSTAJ000",
        "stream": "dosta_abcdjm_cspp_instrument"
    }
    Sample uframe request:
    http://uframe:12580/anno/find?beginDT=1417796700008
    &endDT=1471258860094&method=telemetered&stream=fdchp_a_dcl_instrument&refdes=GS01SUMO-SBD12-08-FDCHPA000
    """
    debug = False

    try:
        method_stream = request.args.get('stream_name')
        if method_stream is not None:
            method, stream = method_stream.split('_')
            method = method.replace('-', '_')
            stream = stream.replace('-', '_')
        else:
            return jsonify({'annotations': []}), 204
        startdate = timestamp_to_millis(request.args.get('startdate'))
        # Make the end date not the stream end time but rather the current request time
        enddate = timestamp_to_millis(time.mktime(datetime.utcnow().timetuple())*1000)
        refdes = request.args.get('reference_designator')
        if debug: print '\n debug -- refdes: %r' % refdes
        rd_type = get_rd_type(str(refdes))
        if debug: print '\n debug -- rd_type: ', rd_type
        url = '/'.join((get_annotations_base_url(), 'find'))
        params = {
            'refdes': refdes,
            'method': method,
            'stream': stream,
            'beginDT': startdate,
            'endDT': enddate
        }
        if debug: print '\n debug -- params: %r' % params
        # Using default request timeouts, get annotations from uframe with parameters
        timeout, timeout_read = get_uframe_timeout_info()
        if debug: print '\n debug -- url: ', url
        r = requests.get(url, timeout=(timeout, timeout_read), params=params)
        data = r.json()
        if debug: print '\n debug -- data length: ', len(data)
        if r.status_code == 200:
            if debug: print '\n debug -- Good status code...'
            result = [remap_uframe_to_ui(record, rd_type) for record in data]
            if debug: print '\n debug -- result: ', result
            return jsonify({'annotations': result}), 201
        else:
            return jsonify(data), r.status_code

    except Exception as err:
        message = 'Could not obtain annotation(s): ' + str(err)
        return bad_request(message)


def process_annotation_response(response):
    return response.text, response.status_code, dict(response.headers)


@api.route('/annotation', methods=['POST'])
@auth.login_required
@scope_required('annotate')
def create_annotation():
    """ Create a new annotation object; response specifying success or failure.
    """
    try:
        data = request.get_json()
        rd = str(data['referenceDesignator'])
        rd_type = get_rd_type(rd)
        if rd_type == 'sensor':
            if 'parameters' in data and ((not data['parameters']) or (data['parameters'] is None)):
                data['parameters'] = None
            else:
                data['parameters'] = get_parameters(data['parameters'][:])
        if 'source' not in data:
            data['source'] = None
        if 'exclusionFlag' not in data:
            data['exclusionFlag'] = False
        elif data['exclusionFlag'] is None:
            data['exclusionFlag'] = False
        data = remap_ui_to_uframe(data, rd_type)
        if validate_anno_record(data):
            timeout, timeout_read = get_uframe_timeout_info()
            response = requests.post(get_annotations_base_url(), json=data, timeout=(timeout, timeout_read))
            if response.status_code != 201:
                message = 'Failed to create new annotation'
                if response.text:
                    temp = json.loads(response.text)
                    if 'message' in temp:
                        message += '; %s' % str(temp['message'])
                raise Exception(message)
            return response.text, response.status_code, dict(response.headers)
            #return process_annotation_response(requests.post(get_annotations_base_url(), json=data, timeout=10))
        else:
            message = 'Required information not specified for create annotation.'
            return bad_request(message)
    except Exception as err:
        message = str(err)
        return bad_request(message)


@api.route('/annotation/<string:annotation_id>', methods=['PUT'])
@auth.login_required
@scope_required('annotate')
def edit_annotation(annotation_id):
    """ Update an existing annotation.
    """
    debug = False
    try:
        # Get request data.
        data = request.get_json()

        # Get referenceDesignator and determine if subsite, susbite-node or subsite-node-sensor.
        rd = str(data['referenceDesignator'])
        rd_type = get_rd_type(rd)
        if rd_type == 'sensor':
            if debug: print '\n debug -- parameters: %r' % data['parameters']
            if 'parameters' in data and (not data['parameters'] or data['parameters']is None):
                data['parameters'] = None
            else:
                data['parameters'] = get_parameters(data['parameters'][:])

        data = remap_ui_to_uframe(data, rd_type)
        if 'source' not in data:
            data['source'] = None
        if validate_anno_record(data):
            url = '/'.join((get_annotations_base_url(), annotation_id))
            timeout, timeout_read = get_uframe_timeout_info()
            response = requests.put(url, json=data, timeout=(timeout, timeout_read))
            if response.status_code != 200:
                message = 'Failed to update annotation'
                if response.text:
                    temp = json.loads(response.text)
                    if 'message' in temp:
                        message += '; %s' % str(temp['message'])
                raise Exception(message)
            return response.text, response.status_code, dict(response.headers)
            #return process_annotation_response(requests.put(url, json=data, timeout=10))
        else:
            message = 'Required information not specified to update annotation.'
            return bad_request(message)
    except ValueError as err:
        message = 'Could not update annotation: ' + str(err)
        return bad_request(message)
    except Exception as err:
        message = 'Failed to update annotation: ' + str(err)
        return bad_request(message)


def get_rd_type(rd):
    try:
        rd_type = None
        if rd and rd is not None:
            len_rd = len(str(rd))

            if len_rd == 8:
                rd_type = 'subsite'
            elif len_rd == 14:
                rd_type = 'node'
            elif len_rd > 14 and len(rd) <= 27:
                rd_type = 'sensor'

        if rd_type is None:
            message = 'Unknown or malformed reference designator (%s).' % rd
            raise Exception(message)
        return rd_type
    except Exception as err:
        message = str(err)
        raise Exception(message)


def get_parameters(params):
    debug = False
    parameters = []
    try:
        if debug: print '\n debug -- get_parameters -- params: %r' % params
        if params and params is not None:
            if debug: print '\n debug -- Have params: %r' % params
            params = str(params)
            if debug: print '\n debug -- Have str(params): %r' % params
            str_list = params.split(",")
            if debug: print '\n debug -- After split: %r' % str_list
            if str_list and str_list is not None:
                for p in str_list:
                    if p and p is not None and p != 'null':
                        if debug: print '\n debug -- p: %r' % p
                        parameters.append(int(p))
        return parameters
    except Exception as err:
        message = str(err)
        raise Exception(message)


@api.route('/annotation/delete/<int:id>', methods=['GET'])
@auth.login_required
@scope_required('annotate')
def delete_annotation(id):
    try:
        timeout, timeout_read = get_uframe_timeout_info()
        url = '/'.join((get_annotations_base_url(), str(id)))
        response = requests.delete(url, headers=_uframe_headers(), timeout=(timeout, timeout_read))
        if response.status_code != 200:
            message = 'Failed to delete annotation id %d: %d ' % (id, response.status_code)
            raise Exception(message)
        return response.text, response.status_code, dict(response.headers)
    except ValueError as err:
        message = 'Could not delete annotation id %d: %s ' % (id, str(err))
        return bad_request(message)
    except ConnectionError:
        message = 'ConnectionError deleting annotation id %d.' % id
        return bad_request(message)
    except Timeout:
        message = 'Timeout deleting annotation id %d.' % id
        return bad_request(message)
    except Exception as err:
        message = str(err.message)
        return bad_request(message)


# Return a list of all valid qcflag values for annotations.
@api.route('/annotation/qcflags', methods=['GET'])
def get_annotation_qcflags():
    try:
        qcflags = get_qcflags_map()
        return jsonify({'qcflags': qcflags}), 200
    except Exception as err:
        message = str(err.message)
        return bad_request(message)