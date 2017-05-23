#!/usr/bin/env python


def get_help_data_12576():
    """
    Sensor Inventory help.
    Data store of information to be presented when a help request is made for port 12576.
    Returns a list of dictionaries associated with various requests supported on that port.
    """
    help_data = [
                    {
                        'root': 'sensor/inv',
                        'endpoint': 'sensor/inv',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Returns a list of available subsites from the sensor inventory.',
                        'data_required': False,
                        'data_format': None,
                        'sample_request': 'sensor/inv',
                        'sample_response': [ "CE01ISSM", "CE01ISSP", "CE02SHBP",
                                             "CP01CNSM", "CP02PMCI", "CP02PMCO",
                                             "GA01SUMO", "GI01SUMO", "GP02HYPM", "GP03FLMA",
                                             "GS01SUMO", "RS01SBPS", "RS03CCAL", "RS03ECAL", "SSRSPACC" ]
                    },
                    {
                        'root': 'sensor/inv',
                        'endpoint': 'sensor/inv/{subsite}',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Returns a list of nodes for a subsite from the sensor inventory.',
                        'data_required': True,
                        'data_format': [
                                { 'name': 'subsite',
                                  'type': 'str',
                                  'description': 'The subsite portion of the reference designator.',
                                  'valid_values': None,
                                  'default': None
                                }
                        ],
                        'sample_request': 'sensor/inv/CE01ISSM',
                        'sample_response': [ "MFC31", "MFD35", "MFD37", "RID16", "SBC11", "SBD17" ]
                    },
                    {
                        'root': 'sensor/inv',
                        'endpoint': 'sensor/inv/{subsite}/{node}',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Returns a list of sensors for a subsite and node from the sensor inventory.',
                        'data_required': True,
                        'data_format': [
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
                                }
                        ],
                        'sample_request': 'sensor/inv/CE01ISSM/MFD35',
                        'sample_response': [ "00-DCLENG000", "01-VEL3DD000", "02-PRESFA000", "04-ADCPTM000",
                                             "05-PCO2WB000", "06-PHSEND000" ]
                    },
                    {
                        'root': 'sensor/inv',
                        'endpoint': 'sensor/inv/{subsite}/{node}/{sensor}',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Returns a list of stream methods for a sensor.',
                        'data_required': True,
                        'data_format': [
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
                                }
                        ],
                        'sample_request': 'sensor/inv/CE01ISSM/MFC31/00-CPMENG000',
                        'sample_response': [ "telemetered" ]
                    },
                    {
                        'root': 'sensor/inv',
                        'endpoint': 'sensor/inv/{subsite}/{node}/{sensor}/metadata',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Returns a metadata dictionary with the parameters and times for a sensor.',
                        'data_required': True,
                        'data_format': [
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
                                }
                        ]
                    },
                    {
                        'root': 'sensor/inv',
                        'endpoint': 'sensor/inv/{subsite}/{node}/{sensor}/metadata/times',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Returns a list of dictionaries, each containing the stream name, method and begin and end times for a sensor.',
                        'data_required': True,
                        'data_format': [
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
                                }
                        ],
                        'sample_request': 'sensor/inv/CE01ISSM/MFC31/00-CPMENG000/metadata/times',
                        'sample_response': [ {
                              "stream" : "cg_cpm_eng_cpm",
                              "method" : "telemetered",
                              "count" : 1,
                              "endTime" : "2015-08-25T00:36:10.708Z",
                              "beginTime" : "2015-08-25T00:36:10.708Z"
                            } ]
                    },
                    {
                        'root': 'sensor/inv',
                        'endpoint': 'sensor/inv/{subsite}/{node}/{sensor}/<method>',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Returns a list of available streams, by method, for an instrument.',
                        'data_required': True,
                        'data_format': [
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
                                { 'name': 'method',
                                  'type': 'str',
                                  'description': 'Stream acquisition method (i.e. \'telemetered\', \'streamed\', etc.)',
                                  'valid_values': None,
                                  'default': None
                                }
                        ],
                        'sample_request': 'sensor/inv/CE01ISSM/MFC31/00-CPMENG000/telemetered',
                        'sample_response': [ "cg_cpm_eng_cpm" ]
                    },
                    {
                        'root': 'sensor/inv',
                        'endpoint': 'sensor/inv/toc',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Returns a dictionary of parameters_by_stream, parameter_definitions and ' +
                                       'list of instruments (The sample response content is abbreviated.)',
                        'data_required': False,
                        'data_format': None,
                        'sample_request': 'sensor/inv',
                        'sample_response': {
                            "parameters_by_stream": {"adcp_config" : [ "PD7", "PD10", "PD11", "PD12"]},
                            "parameter_definitions": [ {
                                                        "pdId" : "PD1",
                                                        "particle_key" : "conductivity",
                                                        "type" : "FLOAT",
                                                        "unsigned" : False,
                                                        "shape" : "SCALAR",
                                                        "fill_value" : "-9999999",
                                                        "units" : "S m-1"
                                                      }, {
                                                        "pdId" : "PD2",
                                                        "particle_key" : "pressure",
                                                        "type" : "FLOAT",
                                                        "unsigned" : False,
                                                        "shape" : "SCALAR",
                                                        "fill_value" : "-9999999",
                                                        "units" : "dbar"
                                                      }],
                            "instruments": [{
                                        "reference_designator" : "CE02SHSM-SBD11-04-VELPTA000",
                                        "platform_code" : "CE02SHSM",
                                        "mooring_code" : "SBD11",
                                        "instrument_code" : "04-VELPTA000",
                                        "streams" : [ {
                                          "stream" : "velpt_ab_dcl_diagnostics_metadata",
                                          "method" : "telemetered",
                                          "count" : 392,
                                          "endTime" : "2017-04-10T12:03:01.000Z",
                                          "beginTime" : "2016-09-27T00:03:01.000Z"
                                        }, {
                                          "stream" : "velpt_ab_dcl_diagnostics",
                                          "method" : "telemetered",
                                          "count" : 39200,
                                          "endTime" : "2017-04-10T12:04:40.000Z",
                                          "beginTime" : "2016-09-27T00:03:01.000Z"
                                        }, {
                                          "stream" : "velpt_ab_dcl_instrument",
                                          "method" : "telemetered",
                                          "count" : 18825,
                                          "endTime" : "2017-04-10T23:45:00.000Z",
                                          "beginTime" : "2016-09-26T21:45:00.000Z"
                                        } ]
                                    }]
                        }
                    },
                ]
    return help_data
