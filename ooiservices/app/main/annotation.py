#!/usr/bin/env python
"""
Annotation endpoints

"""
from datetime import datetime

import requests
from flask import jsonify, request, current_app
from dateutil.parser import parse as parse_date

from authentication import auth
from ooiservices.app.decorators import scope_required
from ooiservices.app.main import api


__author__ = 'M@Campbell'


unix_epoch = parse_date('1970-01-01T00:00:00.000Z')


# Helper methods
def get_refdes(anno_record):
    """
    Build a reference designator from the subsite, node and sensor fields in supplied record
    :param anno_record: Input record
    :return: Reference Designator (string)
    """
    current_app.logger.debug('get_refdes(%r)', anno_record)
    subsite = anno_record.get('subsite', None)
    node = anno_record.get('node', None)
    sensor = anno_record.get('sensor', None)
    if node is None:
        return subsite
    if sensor is None:
        return '-'.join((subsite, node))
    return '-'.join((subsite, node, sensor))


def get_refdes_parts(anno_record):
    """
    Given an annotation record with a reference designator, return the corresponding subsite, node, sensor
    :param anno_record: Annotation Record
    :return: subsite, node, sensor
    """
    current_app.logger.debug('get_refdes_parts(%r)', anno_record)
    subsite = node = sensor = None
    refdes = anno_record.get('referenceDesignator')
    parts = refdes.split('-', 2)
    if len(parts) > 0:
        subsite = parts[0]
    if len(parts) > 1:
        node = parts[1]
    if len(parts) > 2:
        sensor = parts[2]
    return subsite, node, sensor


def timestamp_to_millis(timestamp):
    """
    Convert the timestamp (string or datetime) into integer milliseconds since 1970-1-1
    :param timestamp: timestamp to convert (string)
    :return: milliseconds
    """
    current_app.logger.debug('timestamp_to_millis(%r)', timestamp)
    if isinstance(timestamp, basestring):
        timestamp = parse_date(timestamp)
    if isinstance(timestamp, datetime):
        try:
            return int((timestamp - unix_epoch).total_seconds() * 1000)
        except ValueError:
            return None


def millis_to_timestamp(millis):
    """
    Convert milliseconds since 1970-1-1 to a python datetime object
    :param millis:
    :return:
    """
    current_app.logger.debug('millis_to_timestamp(%r)', millis)
    if isinstance(millis, int):
        return datetime.utcfromtimestamp(millis / 1000.0)


def remap_uframe_to_ui(anno_record):
    """
    Remap the annotation record with a reference designator and human-readable timestamps
    :param anno_record: record to be remapped
    :return: remapped record
    """
    current_app.logger.debug('remap_uframe_to_ui(%r)', anno_record)
    anno_record['referenceDesignator'] = get_refdes(anno_record)
    anno_record['beginDT'] = millis_to_timestamp(anno_record.get('beginDT'))
    anno_record['endDT'] = millis_to_timestamp(anno_record.get('endDT'))
    return anno_record


def remap_ui_to_uframe(anno_record):
    current_app.logger.debug('remap_ui_to_uframe(%r)', anno_record)
    subsite, node, sensor = get_refdes_parts(anno_record)
    anno_record['subsite'] = subsite
    anno_record['node'] = node
    anno_record['sensor'] = sensor
    anno_record['beginDT'] = timestamp_to_millis(anno_record['beginDT'])
    anno_record['endDT'] = timestamp_to_millis(anno_record['endDT'])
    return anno_record


def validate_anno_record(anno_record):
    current_app.logger.debug('validate_anno_record(%r)', anno_record)
    required_fields = {'referenceDesignator', 'annotation', 'beginDT', 'endDT'}
    return len(required_fields.difference(anno_record)) == 0


def get_annotations_base_url():
    return current_app.config['UFRAME_ANNOTATION_URL'] + current_app.config['UFRAME_ANNOTATION_BASE']


@api.route('/annotation', methods=['GET'])
def get_annotations():
    """
    Fetch all annotations associated with the specifed Reference Designator,
    delivery method, stream name and time bounds.
    :return: JSON Response containing all found annotations
    """
    method_stream = request.args.get('stream_name')
    method, stream = method_stream.split('_')
    stream = stream.replace('-', '_')
    startdate = timestamp_to_millis(request.args.get('startdate'))
    enddate = timestamp_to_millis(request.args.get('enddate'))
    refdes = request.args.get('reference_designator')

    try:
        url = '/'.join((get_annotations_base_url(), 'find'))

        params = {
            'refdes': refdes,
            'method': method,
            'stream': stream,
            'beginDT': startdate,
            'endDT': enddate
        }
        r = requests.get(url, params=params)
        data = r.json()
        if r.status_code == 200:
            return jsonify({'annotations': [remap_uframe_to_ui(record) for record in data]}), 201
        else:
            return jsonify(data), r.status_code

    except Exception, e:
        return jsonify({'error': "could not obtain annotation(s): "+str(e)}), 500


def process_annotation_response(response):
    return response.text, response.status_code, dict(response.headers)


@api.route('/annotation', methods=['POST'])
@auth.login_required
@scope_required('annotate')
def create_annotation():
    """
    Create a new annotation object
    :return: Response specifying success or failure
    """
    current_app.logger.debug('create_annotation: %r', request.data)
    try:
        data = request.get_json()
        data = remap_ui_to_uframe(data)
        if validate_anno_record(data):
            return process_annotation_response(requests.post(get_annotations_base_url(), json=data, timeout=10))
        else:
            return jsonify({'error': "required information not specified"}), 500
    except Exception, e:
        return jsonify({'error': "could not create annotation: "+str(e)}), 500


@api.route('/annotation/<string:annotation_id>', methods=['PUT'])
@auth.login_required
@scope_required('annotate')
def edit_annotation(annotation_id):
    """
    Update an existing annotation
    :param annotation_id:
    :return:
    """
    current_app.logger.debug('edit_annotation: %r', request.headers)
    try:
        data = request.get_json()
        data = remap_ui_to_uframe(data)
        if validate_anno_record(data):
            url = '/'.join((get_annotations_base_url(), annotation_id))
            return process_annotation_response(requests.put(url, json=data, timeout=10))
        else:
            return jsonify({'error': "required information not specified"}), 500
    except ValueError, e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': "could not update annotation: " + str(e)}), 500
