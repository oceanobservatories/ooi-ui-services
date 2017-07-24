#!/usr/bin/env python
"""
Annotation endpoints and supporting functions.
"""
__author__ = 'M@Campbell'


from datetime import datetime
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


def remap_uframe_to_ui(anno_record):
    """ Remap the annotation record with a reference designator and human-readable timestamps.
    """
    try:
        method = anno_record['method']
        stream = anno_record['stream']
        method = '' if method is None else method.replace('_', '-')
        stream = '' if stream is None else stream.replace('_', '-')
        anno_record['stream_name'] = '_'.join((method, stream))
        anno_record['referenceDesignator'] = get_refdes(anno_record)
        anno_record['beginDT'] = millis_to_timestamp(anno_record.get('beginDT'))
        anno_record['endDT'] = millis_to_timestamp(anno_record.get('endDT'))
        return anno_record
    except Exception as err:
        message = str(err)
        raise Exception(message)


def remap_ui_to_uframe(anno_record):
    try:
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
        method, stream = method_stream.split('_')
        method = method.replace('-', '_')
        stream = stream.replace('-', '_')
        startdate = timestamp_to_millis(request.args.get('startdate'))
        enddate = timestamp_to_millis(request.args.get('enddate'))
        refdes = request.args.get('reference_designator')
        url = '/'.join((get_annotations_base_url(), 'find'))
        params = {
            'refdes': refdes,
            'method': method,
            'stream': stream,
            'beginDT': startdate,
            'endDT': enddate
        }
        if debug:
            print '\n debug -- GET annotations...'
            print '\n debug -- url: ', url
            print '\n debug -- params: ', params
        # Using default request timeouts, get annotations from uframe with parameters
        timeout, timeout_read = get_uframe_timeout_info()
        r = requests.get(url, timeout=(timeout, timeout_read), params=params)
        data = r.json()
        if debug: print '\n debug -- uframe GET output: ', json.dumps(data, indent=4, sort_keys=True)
        if r.status_code == 200:
            result = [remap_uframe_to_ui(record) for record in data]
            if debug: print '\n debug -- ui GET output: ', result
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
    debug = False
    try:
        if debug: print '\n debug -- Create annotation...'
        data = request.get_json()
        if debug: print '\n debug -- Request data: ', data
        if 'source' not in data:
            data['source'] = None
        if 'parameters' in data and not data['parameters']:
            data['parameters'] = None
        '''
        if debug:
            print '\n debug -- (before) data: ', data
            data = {'beginDT': '2017-04-11T13:43:39.000Z',
                    'stream_name': 'telemetered_flord-g-ctdbp-p-dcl-instrument',
                    'endDT': '2017-06-14T13:43:00.000Z',
                    'parameters': None,
                    'referenceDesignator': 'GA01SUMO-RII11-02-FLORDG032',
                    'comment': 'test',
                    'annotation': 'test',
                    'source': 'admin@ooi.rutgers.edu',
                    'instrument_name': '',
                    'method': 'telemetered_flord-g-ctdbp-p-dcl-instrument'}
        '''
        '''
        if debug: print '\n debug -- (hard coded) data: ', data
        # Partial seconds.
        print '\n debug -- (before) data: ', data
        data = {'beginDT': '2016-06-01T12:40:04.108Z',
                'stream_name': 'telemetered_metbk-a-dcl-instrument',
                'endDT': '2017-04-09T14:12:04.000Z',
                'parameters': None,
                'referenceDesignator': 'GI01SUMO-SBD11-06-METBKA000',
                'comment': 'Force test create annotation. (partial seconds)',
                'annotation': 'Force test create annotation. (partial seconds)',
                'source': 'admin@ooi.rutgers.edu',
                'instrument_name': 'XHXHXHXHXHXHX',
                'method': 'telemetered-XHXHXHXHXHXHX'}
        '''
        if debug: print '\n debug -- (before) data: ', data
        data = remap_ui_to_uframe(data)
        if debug: print '\n debug -- (after) data: ', data
        if validate_anno_record(data):
            if debug: print '\n debug -- valid anno record data...'
            timeout, timeout_read = get_uframe_timeout_info()
            response = requests.post(get_annotations_base_url(), json=data, timeout=(timeout, timeout_read))
            if debug:
                print '\n debug -- response.status_code: ', response.status_code
                print '\n debug -- response.text: ', json.loads(response.text)
            if response.status_code != 201:
                message = 'Failed to create new annotation'
                if response.text:
                    temp = json.loads(response.text)
                    if debug:
                        print '\n debug -- temp: ', temp
                        print '\n debug -- type(temp): ', type(temp)
                    if 'message' in temp:
                        if debug: print '\n debug -- temp[message]: ', temp['message']
                        message += '; %s' % str(temp['message'])
                raise Exception(message)
            return response.text, response.status_code, dict(response.headers)
            #return process_annotation_response(requests.post(get_annotations_base_url(), json=data, timeout=10))
        else:
            message = 'Required information not specified for create annotation.'
            return bad_request(message)
    except Exception as err:
        message = str(err)
        if debug: print '\n debug -- exception: ', message
        return bad_request(message)


@api.route('/annotation/<string:annotation_id>', methods=['PUT'])
@auth.login_required
@scope_required('annotate')
def edit_annotation(annotation_id):
    """ Update an existing annotation.
    """
    try:
        data = request.get_json()
        if 'parameters' in data and not data['parameters']:
            data['parameters'] = None
        data = remap_ui_to_uframe(data)
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


# The request method should be changed to be 'DELETE' rather than 'GET'.
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