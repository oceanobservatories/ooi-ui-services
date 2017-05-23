#!/usr/bin/env python


def get_help_data_12580():
    """
    Annotation help.
    Data store of information to be presented when a help request is made for port 12580.
    Returns a list of dictionaries associated with various requests supported on that port.
    """
    qcflag_values = ['NOT_OPERATIONAL', 'NOT_AVAILABLE', 'PENDING_INGEST',
                     'NOT_EVALUATED', 'SUSPECT', 'FAIL', 'PASS']
    help_data = [
                    {
                        'root': 'anno/find',
                        'endpoint': 'anno/find',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Get all annotations for a specific time frame and for a known' +
                                       ' reference designator, stream and method. Parameter data required.',
                        'data_required': True,
                        'data_format': [
                                { 'name': 'beginDT',
                                  'type': 'longint',
                                  'description': 'Initial time for search.',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'endDT',
                                  'type': 'longint',
                                  'description': 'End time for search.',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'method',
                                  'type': 'str',
                                  'description': 'Stream method to search for.',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'refdes',
                                  'type': 'str',
                                  'description': 'Reference designator to search for.',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'stream',
                                  'type': 'str',
                                  'description': 'Stream name to search for.',
                                  'valid_values': None,
                                  'default': None
                                }
                            ],
                        'sample_request': 'http://uframe-test.intra.oceanobservatories.org:12580/anno/find',
                        'sample_data': {'beginDT': 1374274800000, 'endDT': 1481546694325, 'method': u'telemetered',
                                        'stream': u'flord_m_glider_instrument', 'refdes': u'GP05MOAS-GL365-01-FLORDM000'
                                    },
                        'sample_response': [
                            {
                                "@class": ".AnnotationRecord",
                                "annotation": "Create annotation for SSRSPACC-F10NA-F10-8",
                                "beginDT": 1491412013000,
                                "endDT": 1492468785000,
                                "exclusionFlag": False,
                                "id": 80,
                                "method": "streamed",
                                "node": "F10NA",
                                "parameters": [],
                                "qcFlag": None,
                                "sensor": "F10-8",
                                "source": "admin@ooi.rutgers.edu",
                                "stream": "shore_station_force_10_network_port_data",
                                "subsite": "SSRSPACC"
                            },
                            {
                                "@class": ".AnnotationRecord",
                                "annotation": "Create annotation for SSRSPACC-F10NA-F10-8",
                                "beginDT": 1491412013000,
                                "endDT": 1492468785000,
                                "exclusionFlag": False,
                                "id": 81,
                                "method": "streamed",
                                "node": "F10NA",
                                "parameters": [],
                                "qcFlag": None,
                                "sensor": "F10-8",
                                "source": "admin@ooi.rutgers.edu",
                                "stream": "shore_station_force_10_network_port_data",
                                "subsite": "SSRSPACC"
                            }
                        ]

                    },
                    {
                        'root': 'anno',
                        'endpoint': 'anno/{id}',
                        'method': 'PUT',
                        'permission_required': True,
                        'description': 'Update an annotation (by annotation id).',
                        'data_required': True,
                        'data_format':
                            [
                                { 'name': '@class',
                                  'type': 'str',
                                  'description': 'Constant value used by uframe. Use \'.AnnotationRecord\' for the value.',
                                  'valid_values': None,
                                  'default': '.AnnotationRecord'
                                },
                                { 'name': 'method',
                                  'type': 'str',
                                  'description': 'Stream acquisition method (i.e. \'telemetered\', \'streamed\', etc.)',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'annotation',
                                  'type': 'str',
                                  'description': 'Annotation description.',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'subsite',
                                  'type': 'str',
                                  'description': 'The subsite portion of the reference designator.',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'node',
                                  'type': 'str',
                                  'description': 'The node portion of the reference designator.',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'sensor',
                                  'type': 'str',
                                  'description': 'The sensor portion of the reference designator.',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'stream',
                                  'type': 'str',
                                  'description': 'The stream named to be used for updating the annotation.',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'source',
                                  'type': 'str',
                                  'description': 'The user id for user requesting the update.',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'qcFlag',
                                  'type': 'str',
                                  'description': 'Quality assurance value.',
                                  'valid_values': qcflag_values,     # List of valid values.
                                  'default': None
                                },
                                { 'name': 'parameters',
                                  'type': 'str',
                                  'description': 'List of one or more parameters to be annotated; default None.',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'beginDT',
                                  'type': 'longint',
                                  'description': 'Start time for annotation.',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'endDT',
                                  'type': 'longint',
                                  'description': 'End time for annotation.',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'exclusionFlag',
                                  'type': 'bool',
                                  'description': 'Boolean flag indicating whether data should be included or excluded.',
                                  'valid_values': None,
                                  'default': False
                                }
                            ],
                        'sample_request': 'anno/65',
                        'sample_data': {
                                        "node": "F10NA",
                                        "endDT": 1492117939000,
                                        "stream": "shore_station_force_10_network_port_data",
                                        "annotation": "M2M Update annotation for SSRSPACC-F10NA-F10-8 (verfied).",
                                        "@class": ".AnnotationRecord",
                                        "beginDT": 1491412013000,
                                        "parameters": None,
                                        "subsite": "SSRSPACC",
                                        "source": "admin@ooi.rutgers.edu",
                                        "exclusionFlag": False,
                                        "sensor": "F10-8",
                                        "method": "streamed"
                                        },
                        'sample_response': {
                                                "id": 65,
                                                "message": "Element updated successfully.",
                                                "statusCode": "OK"
                                            }
                    },
                    {
                        'root': 'anno',
                        'endpoint': 'anno',
                        'method': 'POST',
                        'permission_required': True,
                        'description': 'Create an annotation; upon success an annotation id is returned.',
                        'data_required': True,
                        'data_format':
                            [
                                { 'name': '@class',
                                  'type': 'str',
                                  'description': 'Constant value used by uframe. Use \'.AnnotationRecord\' for the value.',
                                  'valid_values': None,
                                  'default': '.AnnotationRecord'
                                },
                                { 'name': 'method',
                                  'type': 'str',
                                  'description': 'Stream acquisition method (i.e. \'telemetered\', \'streamed\', etc.)',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'annotation',
                                  'type': 'str',
                                  'description': 'Annotation description.',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'subsite',
                                  'type': 'str',
                                  'description': 'The subsite portion of the reference designator.',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'node',
                                  'type': 'str',
                                  'description': 'The node portion of the reference designator.',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'sensor',
                                  'type': 'str',
                                  'description': 'The sensor portion of the reference designator.',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'stream',
                                  'type': 'str',
                                  'description': 'The stream named to be used for creating the annotation.',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'source',
                                  'type': 'str',
                                  'description': 'The user id for user requesting the create annotation.',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'qcFlag',
                                  'type': 'str',
                                  'description': 'Quality assurance value.',
                                  'valid_values': qcflag_values,     # List of valid values.
                                  'default': None
                                },
                                { 'name': 'parameters',
                                  'type': 'str',
                                  'description': 'List of one or more parameters to be annotated; default None.',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'beginDT',
                                  'type': 'longint',
                                  'description': 'Start time for annotation.',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'endDT',
                                  'type': 'longint',
                                  'description': 'End time for annotation.',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'exclusionFlag',
                                  'type': 'bool',
                                  'description': 'Boolean flag indicating whether data should be included or excluded.',
                                  'valid_values': None,
                                  'default': False
                                }
                            ],
                        'sample_request': 'anno',
                        'sample_data': {
                                        "@class": ".AnnotationRecord",
                                        "method": "streamed",
                                        "annotation": "Create annotation for SSRSPACC-F10NA-F10-8",
                                        "node": "F10NA",
                                        "stream": "shore_station_force_10_network_port_data",
                                        "beginDT": 1491412013000,
                                        "endDT": 1492468785000,
                                        "subsite": "SSRSPACC",
                                        "sensor": "F10-8",
                                        "exclusionFlag": False,
                                        "source": "admin@ooi.rutgers.edu",
                                        "qcFlag": "SUSPECT",
                                        "parameters": None
                                        },
                        'sample_response': {
                                "id": 82,
                                "message": "Element created successfully.",
                                "statusCode": "CREATED"
                            }

                    }
                ]
    return help_data
