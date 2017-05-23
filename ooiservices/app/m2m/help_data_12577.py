#!/usr/bin/env python


def get_help_data_12577():
    """
    Alerts and Alarms help.
    Data store of information to be presented when a help request is made for port 12577.
    Returns a list of dictionaries associated with various requests supported on that port.
    """
    help_data = [
                    {
                        'root': 'alertfilters/inv',
                        'endpoint': 'alertfilters/inv',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Returns a list of subsites with alerts and/or alarm filters.',
                        'data_required': False,
                        'data_format': None,
                        'sample_request': 'alertfilters/inv',
                        'sample_response': [ "CE01ISSM", "CE01ISSP"]
                    },
                    {
                        'root': 'alertfilters/inv',
                        'endpoint': 'alertfilters/inv/{subsite}',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Returns a list of nodes with alerts and/or alarm filters.',
                        'data_required': True,
                        'data_format': [
                                { 'name': 'subsite',
                                  'type': 'str',
                                  'description': 'The subsite portion of the reference designator.',
                                  'valid_values': None,
                                  'default': None
                                }
                        ],
                        'sample_request': 'alertfilters/inv/CE01ISSM',
                        'sample_response': [ "SBD17" ]
                    },
                    {
                        'root': 'alertfilters/inv',
                        'endpoint': 'alertfilters/inv{subsite}/{node}',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Returns a list of sensors for a subsite and node with alerts and/or alarm filters.',
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
                        'sample_request': 'alertfilters/inv/CE01ISSM/SBD17',
                        'sample_response': [ "01-MOPAK0000" ]
                    },
                    {
                        'root': 'alertfilters/inv',
                        'endpoint': 'alertfilters/inv/{subsite}/{node}/{sensor}',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Returns a list of alerts and/or alarm filters for a subsite, node and sensor.',
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
                        'sample_request': 'alertfilters/inv/CE01ISSM/SBD17/01-MOPAK0000',
                        'sample_response': [
                                            {
                                              "@class" : ".AlertFilterRecord",
                                              "enabled" : True,
                                              "stream" : "mopak_o_dcl_accel",
                                              "referenceDesignator" : {
                                                "vocab" : {
                                                  "refdes" : "CE01ISSM-SBD17-01-MOPAK0000",
                                                  "instrument" : "3-Axis Motion Pack",
                                                  "tocL1" : "Coastal Endurance",
                                                  "tocL2" : "Oregon Inshore Surface Mooring",
                                                  "tocL3" : "Surface Buoy"
                                                },
                                                "node" : "SBD17",
                                                "full" : True,
                                                "sensor" : "01-MOPAK0000",
                                                "subsite" : "CE01ISSM"
                                              },
                                              "pdId" : "PD1595",
                                              "eventId" : 4,
                                              "alertMetadata" : {
                                                "severity" : 2,
                                                "description" : "test user defined alerts and alarms"
                                              },
                                              "alertRule" : {
                                                "filter" : "BETWEEN_EXCLUSIVE",
                                                "valid" : True,
                                                "lowVal" : 1.0,
                                                "highVal" : 1.5,
                                                "errMessage" : None
                                              },
                                              "eventReceiptDelta" : 5000
                                            }]
                    },
                    {
                        'root': 'alertfilters',
                        'endpoint': 'alertfilters',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Returns a list of alerts and alarms in the system.',
                        'data_required': False,
                        'data_format': None,
                        'sample_request': 'alertfilters',
                        'sample_response': [{
                                                  "@class" : ".AlertFilterRecord",
                                                  "enabled" : True,
                                                  "stream" : "ctdpf_j_cspp_instrument",
                                                  "referenceDesignator" : {
                                                    "vocab" : None,
                                                    "node" : "XX099",
                                                    "full" : True,
                                                    "sensor" : "01-CTDPFJ999",
                                                    "subsite" : "CE01ISSP"
                                                  },
                                                  "pdId" : "PD440",
                                                  "eventId" : 1,
                                                  "alertMetadata" : {
                                                    "severity" : 2,
                                                    "description" : "Rule 9"
                                                  },
                                                  "alertRule" : {
                                                    "filter" : "GREATER",
                                                    "valid" : True,
                                                    "lowVal" : 10.0,
                                                    "highVal" : 31.0,
                                                    "errMessage" : None
                                                  },
                                                  "eventReceiptDelta" : 0
                                                }]
                    },
                    {
                        'root': 'alertfilters',
                        'endpoint': 'alertfilters/{id}',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Get an alert or alarm filter by identifier.',
                        'data_required': True,
                        'data_format': [
                                { 'name': 'id',
                                  'type': 'int',
                                  'description': 'The identifier for an alert or alarm filter.',
                                  'valid_values': None,
                                  'default': None
                                }
                        ],
                        'sample_request': 'alertfilters/1',
                        'sample_response': {
                                              "@class" : ".AlertFilterRecord",
                                              "enabled" : True,
                                              "stream" : "ctdpf_j_cspp_instrument",
                                              "referenceDesignator" : {
                                                "vocab" : None,
                                                "node" : "XX099",
                                                "full" : True,
                                                "sensor" : "01-CTDPFJ999",
                                                "subsite" : "CE01ISSP"
                                              },
                                              "pdId" : "PD440",
                                              "eventId" : 1,
                                              "alertMetadata" : {
                                                "severity" : 2,
                                                "description" : "Rule 9"
                                              },
                                              "alertRule" : {
                                                "filter" : "GREATER",
                                                "valid" : True,
                                                "lowVal" : 10.0,
                                                "highVal" : 31.0,
                                                "errMessage" : None
                                              },
                                              "eventReceiptDelta" : 0
                                            }
                    }
                ]
    return help_data
