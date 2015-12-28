#!/usr/bin/env python
'''
API v1.0 List

'''
__author__ = 'M@Campbell'

from flask import jsonify, request
from ooiservices.app.main import api
from ooiservices.app.models import Array, PlatformDeployment, Platformname
from ooiservices.app.models import VocabNames
from ooiservices.app.models import Stream, StreamParameter, \
    Organization, Instrumentname
# from netCDF4 import num2date, date2index


@api.route('/platform_deployments')
def get_platform_deployments():
    if 'array_id' in request.args:
        platform_deployments = \
            PlatformDeployment.query.filter_by(array_id=request.args['array_id'])\
            .order_by(PlatformDeployment.reference_designator).all()
    elif 'search' in request.args:
        platform_deployments = PlatformDeployment\
            .query.whoosh_search(request.args['search'])
    else:
        platform_deployments = PlatformDeployment.query.all()
    return jsonify({'platform_deployments': [platform_deployment.to_json()
                    for platform_deployment in platform_deployments]})


@api.route('/platform_deployments/<string:id>')
def get_platform_deployment(id):
    platform_deployment = PlatformDeployment.\
        query.filter_by(reference_designator=id).first_or_404()
    return jsonify(platform_deployment.to_json())


@api.route('/streams')
def get_streams():
    streams = Stream.query.all()
    return jsonify({'streams': [stream.to_json() for stream in streams]})


@api.route('/streams/<string:id>')
def get_stream(id):
    stream = Stream.query.filter_by(stream_name=id).first_or_404()
    return jsonify(stream.to_json())


@api.route('/parameters')
def get_parameters():
    parameters = StreamParameter.query.all()
    return jsonify({'parameters': [parameter.to_json()
                    for parameter in parameters]})


@api.route('/parameters/<string:id>')
def get_parameter(id):
    parameter = StreamParameter.\
        query.filter_by(stream_parameter_name=id).first_or_404()
    return jsonify(parameter.to_json())


@api.route('/organization', methods=['GET'])
def get_organizations():
    organizations = [o.serialize() for o in Organization.query.all()]
    return jsonify(organizations=organizations)


@api.route('/organization/<int:id>', methods=['GET'])
def get_organization_by_id(id):
    org = Organization.query.filter(Organization.id == id).first()
    if not org:
        return '{}', 204
    response = org.serialize()
    return jsonify(**response)


def _array_name(ref_des):
    ''' M@Campbell 12/21/2015 '''
    array_des = ref_des[:2]
    try:
        array = VocabNames.query.with_entities(VocabNames.level_one).\
            filter_by(reference_designator=array_des).first()
        if array is not None:
            return array.level_one
    except Exception as e:
        print 'Unhandled exception in:'\
            'ooiuiserivces.main.routes._array_name: %s.' % e


def _platform_name(ref_des):
    ''' M@Campbell 12/21/2015 '''
    platform_des = ref_des[:8]
    try:
        platform = VocabNames.query.with_entities(VocabNames.level_two).\
            filter_by(reference_designator=platform_des).first()
        if platform is not None:
            return platform.level_two
    except Exception as e:
        print 'Unhandled exception in:'\
            'ooiuiserivces.main.routes._platform_name: %s.' % e


def _assembly_name(ref_des):
    ''' M@Campbell 12/21/2015 '''
    assembly_des = ref_des[:14]
    try:
        assembly = VocabNames.query.with_entities(VocabNames.level_three).\
            filter_by(reference_designator=assembly_des).first()
        if assembly is not None:
            return assembly.level_three
    except Exception as e:
        print 'Unhandled exception in:'\
            'ooiuiserivces.main.routes._assembly_name: %s.' % e


def _instrument_name(ref_des):
    ''' M@Campbell 12/21/2015 '''
    instrument_des = ref_des[:27]
    try:
        instrument = VocabNames.query.with_entities(VocabNames.level_four).\
            filter_by(reference_designator=instrument_des).first()
        if instrument is not None:
            return instrument.level_four
    except Exception as e:
        print 'Unhandled exception in:'\
            'ooiuiserivces.main.routes._instrument_name: %s.' % e


def get_display_name_by_rd(reference_designator):
    if len(reference_designator) == 2:
        array = _array_name(reference_designator)
        return array

    if len(reference_designator) == 8:
        platform = _platform_name(reference_designator)
        return platform

    if len(reference_designator) == 14:
        assembly = _assembly_name(reference_designator)
        return assembly

    if len(reference_designator) == 27:
        instrument = _instrument_name(reference_designator)
        return instrument


def get_long_display_name_by_rd(reference_designator):
    try:
        display_name = VocabNames.query.\
            filter_by(reference_designator=reference_designator).first()

        if display_name is not None:
            display_name = ' '.join((display_name.level_one or "",
                                     display_name.level_two or "",
                                     display_name.level_three or "",
                                     display_name.level_four or ""))
        return display_name
    except Exception as e:
        print 'Unhandled exception in:'\
                'ooiservices.main.routes.get_long_display_name_by_rd: %s' % e



def get_platform_display_name_by_rd(reference_designator):
    platform = Platformname.query.filter_by(reference_designator=reference_designator[:14]).first()
    if platform is None:
        return None
    platform_display_name = platform.platform

    return platform_display_name


def get_parameter_name_by_parameter(stream_parameter_name):
    streamParameter = StreamParameter.query.filter_by(stream_parameter_name = stream_parameter_name).first()
    if streamParameter is None or streamParameter is []:
        return None

    stream_display_name = streamParameter.standard_name

    return stream_display_name


def get_stream_name_by_stream(stream):
    stream = Stream.query.filter_by(stream=stream).first()
    if stream is None or stream is []:
        return None

    stream_display_name = stream.concatenated_name

    return stream_display_name


@api.route('/display_name', methods=['GET'])
def get_display_name():
    # 'CE01ISSM-SBD17'
    reference_designator = request.args.get('reference_designator')
    if not reference_designator:
        return '{}', 204

    display_name = get_display_name_by_rd(reference_designator)
    if not display_name:
        return '{}', 204

    return jsonify({'proper_display_name': display_name})
