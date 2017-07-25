#!/usr/bin/env python


def get_help_data_12576():
    """
    Sensor Inventory help.
    Data store of information to be presented when a help request is made for port 12576.
    Returns a list of dictionaries associated with various requests supported on that port.
    """
    help_data = \
        [
            {
                'root': 'sensor/inv',
                'endpoint': 'sensor/inv',
                'method': 'GET',
                'permission_required': False,
                'description': 'Get platforms (subsites). Returns a list of available subsites from the sensor inventory.',
                'data_required': False,
                'data_format': None,
                'samples': [{
                            'sample_request': 'sensor/inv',
                            'sample_response': [ "CE01ISSM", "CE01ISSP", "CE02SHBP",
                                                 "CP01CNSM", "CP02PMCI", "CP02PMCO",
                                                 "GA01SUMO", "GI01SUMO", "GP02HYPM", "GP03FLMA",
                                                 "GS01SUMO", "RS01SBPS", "RS03CCAL", "RS03ECAL", "SSRSPACC" ]
                            }]
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
                'samples': [{
                            'sample_request': 'sensor/inv/CE01ISSM',
                            'sample_response': [ "MFC31", "MFD35", "MFD37", "RID16", "SBC11", "SBD17" ]
                            }]
            },
            {
                'root': 'sensor/inv',
                'endpoint': 'sensor/inv/{subsite}/{node}',
                'method': 'GET',
                'permission_required': False,
                'description': 'Get sensors for a subsite-node. Returns a list of sensors for a subsite and node from the sensor inventory.',
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
                'samples': [{
                            'sample_request': 'sensor/inv/CE01ISSM/MFD35',
                            'sample_response': [ "00-DCLENG000", "01-VEL3DD000", "02-PRESFA000", "04-ADCPTM000",
                                                 "05-PCO2WB000", "06-PHSEND000" ]
                            }]
            },
            {
                'root': 'sensor/inv',
                'endpoint': 'sensor/inv/{subsite}/{node}/{sensor}',
                'method': 'GET',
                'permission_required': False,
                'description': 'Get all instrument methods. Returns a list of stream methods for a sensor.',
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
                'samples': [{
                            'sample_request': 'sensor/inv/CE01ISSM/MFC31/00-CPMENG000',
                            'sample_response': [ "telemetered" ]
                            }]
            },
            {
                'root': 'sensor/inv',
                'endpoint': 'sensor/inv/{subsite}/{node}/{sensor}/metadata',
                'method': 'GET',
                'permission_required': False,
                'description': 'Get instrument metadata. Returns a metadata dictionary with the parameters and times for a sensor.',
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
                'description': 'Get instrument metadata times. Returns a list of dictionaries, each containing the stream name, method and begin and end times for a sensor.',
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
                        { 'name': 'partition',
                          'type': 'bool',
                          'description': '[Optional] Provide additional time partition information.',
                          'valid_values': None,
                          'default': None
                        }
                ],
                'samples': [{
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
                            'sample_request': 'sensor/inv/CE01ISSM/MFC31/00-CPMENG000/metadata/times?partition=True',
                            'sample_response': [ {
                                                  "stream" : "cg_cpm_eng_cpm",
                                                  "method" : "telemetered",
                                                  "count" : 1,
                                                  "bin" : 3649363200,
                                                  "store" : "cass",
                                                  "endTime" : "2015-08-25T00:36:10.708Z",
                                                  "beginTime" : "2015-08-25T00:36:10.708Z"
                                                } ]
                            }]
            },
            {
                'root': 'sensor/inv',
                'endpoint': 'sensor/inv/{subsite}/{node}/{sensor}/<method>',
                'method': 'GET',
                'permission_required': False,
                'description': 'Get instrument methods. Returns a list of available streams for an instrument and method.',
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
                'samples': [{
                            'sample_request': 'sensor/inv/CE01ISSM/MFC31/00-CPMENG000/telemetered',
                            'sample_response': [ "cg_cpm_eng_cpm" ]
                            }]
            },
            {
                'root': 'sensor/inv',
                'endpoint': 'sensor/inv/{subsite}/{node}/{sensor}/{method}/{stream}',
                'method': 'GET',
                'permission_required': False,
                'description': 'Get data for a reference designator from a specific stream.',
                'data_required': True,
                'data_format': [
                        {'name': 'subsite',
                          'type': 'str',
                          'description': 'The subsite portion of the reference designator.',
                          'valid_values': None,
                          'default': None
                        },
                        {'name': 'node',
                          'type': 'str',
                          'description': 'The node portion of the reference designator.',
                          'valid_values': None,
                          'default': None
                        },
                        {'name': 'sensor',
                          'type': 'str',
                          'description': 'The sensor portion of the reference designator.',
                          'valid_values': None,
                          'default': None
                        },
                        {'name': 'method',
                          'type': 'str',
                          'description': 'Stream acquisition method (i.e. \'telemetered\', \'streamed\', etc.)',
                          'valid_values': None,
                          'default': None
                        },
                        {'name': 'stream',
                          'type': 'str',
                          'description': 'Stream name.',
                          'valid_values': None,
                          'default': None
                        },
                        {'name': 'user',
                          'type': 'str',
                          'description': 'The OOI user requesting the data.',
                          'valid_values': None,
                          'default': None
                        },
                        {'name': 'limit',
                          'type': 'int',
                          'description': '[Optional] The upper limit of json records to be returned. ' +
                                         '(Example: &limit=1000) If limit=-1 a netcdf object is returned. ' +
                                         'If limit is not provided, netcdf object information/links are provided ' +
                                         'for the OOI opendap server. ',
                          'valid_values': None,
                          'default': None
                        },
                        {'name': 'parameters',
                          'type': 'str',
                          'description': '[Optional] Comma separated parameter(s); used to identify response data ' +
                                         ' by parameters. (Example: &parameters=2926,7)',
                          'valid_values': None,
                          'default': None
                        },
                        {'name': 'email',
                          'type': 'str',
                          'description': '[Optional] Valid email address (registered in system) for ' +
                                         'email notification when request completes.',
                          'valid_values': None,
                          'default': None
                        },
                        {'name': 'include_provenance',
                          'type': 'bool',
                          'description': '[Optional] Indicate whether or not to include provenance; default is False.',
                          'valid_values': None,
                          'default': None
                        },
                        {'name': 'include_annotations',
                          'type': 'bool',
                          'description': '[Optional] Indicate whether or not to include annotations; default is False.',
                          'valid_values': None,
                          'default': None
                        }
                ],
                'samples': [{
                            'sample_request': 'sensor/inv/CE01ISSM/MFC31/00-CPMENG000/telemetered/cg_cpm_eng_cpm?user=foo',
                            'sample_response':
                                {"requestUUID":"8ade93a8-1ea8-48ff-a3ea-46b12bd3db75",
                                 "outputURL":"https://opendap-test.oceanobservatories.org/thredds/catalog/ooinet-dev-03/foo/20170525T163138-CE01ISSM-MFC31-00-CPMENG000-telemetered-cg_cpm_eng_cpm/catalog.html",
                                 "allURLs":["https://opendap-test.oceanobservatories.org/thredds/catalog/ooinet-dev-03/foo/20170525T163138-CE01ISSM-MFC31-00-CPMENG000-telemetered-cg_cpm_eng_cpm/catalog.html",
                                 "https://opendap.oceanobservatories.org/ooinet-dev-03/async_results/foo/20170525T163138-CE01ISSM-MFC31-00-CPMENG000-telemetered-cg_cpm_eng_cpm"],
                                 "sizeCalculation":1000,
                                 "timeCalculation":60,
                                 "numberOfSubJobs":1}
                            },
                            {
                               'sample_request': 'http://uframe-3-test.intra.oceanobservatories.org:12576/sensor/inv/' +
                                                 'GA01SUMO/RII11/02-CTDMOQ017/' +
                                                 'telemetered/ctdmo_ghqr_imodem_instrument?' +
                                                 'beginDT=2017-05-18T15:07:00.000Z&endDT=2017-05-25T15:07:00.000Z' +
                                                 '&limit=1000&parameters=2926,7&user=plotting',
                               'sample_response': [
                                                      {
                                                        "ctdmo_seawater_pressure_qc_results": 29,
                                                        "ctdmo_seawater_pressure_qc_executed": 29,
                                                        "pk": {
                                                          "node": "RII11",
                                                          "stream": "ctdmo_ghqr_imodem_instrument",
                                                          "subsite": "GA01SUMO",
                                                          "deployment": 3,
                                                          "time": 3704108851.0,
                                                          "sensor": "02-CTDMOQ017",
                                                          "method": "telemetered"
                                                        },
                                                        "ctdmo_seawater_pressure": 503.5411462319808,
                                                        "time": 3704108851.0
                                                      },
                                                      {
                                                        "ctdmo_seawater_pressure_qc_results": 29,
                                                        "ctdmo_seawater_pressure_qc_executed": 29,
                                                        "pk": {
                                                          "node": "RII11",
                                                          "stream": "ctdmo_ghqr_imodem_instrument",
                                                          "subsite": "GA01SUMO",
                                                          "deployment": 3,
                                                          "time": 3704109301.0,
                                                          "sensor": "02-CTDMOQ017",
                                                          "method": "telemetered"
                                                        },
                                                        "ctdmo_seawater_pressure": 503.45232172670586,
                                                        "time": 3704109301.0
                                                      }
                                                    ]
                            }]
            },
            {
                'root': 'sensor/inv',
                'endpoint': 'sensor/inv/toc',
                'method': 'GET',
                'permission_required': False,
                'description': 'Get toc. Returns a dictionary of parameters_by_stream, parameter_definitions and ' +
                               'list of instruments (The sample response content is abbreviated.)',
                'data_required': False,
                'data_format': None,
                'samples': [{
                            'sample_request': 'sensor/inv/toc',
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
                }]
            }
    ]
    return help_data
