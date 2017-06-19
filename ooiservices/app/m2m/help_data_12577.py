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
                        'samples': [{
                                    'sample_request': 'alertfilters/inv',
                                    'sample_response': [ "CE01ISSM", "CE01ISSP"]
                                    }]
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
                        'samples': [{
                                    'sample_request': 'alertfilters/inv/CE01ISSM',
                                    'sample_response': [ "SBD17" ]
                                    }]
                    },
                    {
                        'root': 'alertfilters/inv',
                        'endpoint': 'alertfilters/inv/{subsite}/{node}',
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
                        'samples': [{
                                    'sample_request': 'alertfilters/inv/CE01ISSM/SBD17',
                                    'sample_response': [ "01-MOPAK0000" ]
                                    }]
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
                        'samples': [{
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
                        'samples': [{
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
                        'samples': [{
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
                                    }]
                    },
                    {
                        'root': 'alertalarms',
                        'endpoint': 'alertalarms',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Returns a list of alerts and alarms across all subsites. ' +
                                       '(Some sample response content abbreviated.) Numerous optional filters.',
                        'data_required': False,
                        'data_format': [
                                {'name': 'acknowledged',
                                 'type': 'str',
                                 'description': '[Optional] Enumeration value to filter results ' +
                                                'by acknowledged status.',
                                 'valid_values': ['true', 'false', 'all'],
                                 'default': None
                                },
                                {'name': 'results',
                                 'type': 'int',
                                 'description': '[Optional] Filter response result with upper limit ' +
                                                 'for values to be returned. (positive integer)',
                                 'valid_values': None,
                                 'default': None
                                },
                                {'name': 'sortorder',
                                 'type': 'str',
                                 'description': '[Optional] Filter response results in ascending or ' +
                                                 'descending order. The default is descending order.',
                                 'valid_values': ['dsc', 'asc'],
                                 'default': 'dsc'
                                }
                        ],
                        'samples': [{
                                    'sample_request': 'alertalarms',
                                    'sample_response': [ {
                                                          "severity" : 1,
                                                          "method" : None,
                                                          "message" : "Stream statuses: degraded: 1",
                                                          "id" : None,
                                                          "type" : "ASSET_STATUS",
                                                          "time" : 1.49610252096E12,
                                                          "maxMessageLenght" : 4096,
                                                          "storeTime" : 1496102530200,
                                                          "acknowledgeTime" : None,
                                                          "acknowledgedBy" : None,
                                                          "acknowledged" : False,
                                                          "deployment" : None,
                                                          "associatedId" : None,
                                                          "eventCount" : 1,
                                                          "omsEventId" : None,
                                                          "omsGroup" : None,
                                                          "omsPlatformId" : None,
                                                          "omsComponent" : None,
                                                          "omsPlatformClass" : None,
                                                          "omsFirstTimeTimestamp" : None,
                                                          "assetStatus" : "degraded",
                                                          "node" : "PC01B",
                                                          "subsite" : "CE04OSPS",
                                                          "sensor" : "05-ZPLSCB102",
                                                          "eventId" : 6865817
                                                        }]
                                    },
                                    {
                                    'sample_request': 'alertalarms?results=2&acknowledged=true',
                                    'sample_response': [ {
                                                          "severity" : -1,
                                                          "method" : None,
                                                          "message" : "Stream statuses: failed: 1",
                                                          "id" : None,
                                                          "type" : "ASSET_STATUS",
                                                          "time" : 1.496016060937E12,
                                                          "maxMessageLenght" : 4096,
                                                          "storeTime" : 1496016070167,
                                                          "acknowledgeTime" : 1496102470174,
                                                          "acknowledgedBy" : "uframe",
                                                          "acknowledged" : True,
                                                          "deployment" : None,
                                                          "associatedId" : None,
                                                          "eventCount" : 1,
                                                          "omsEventId" : None,
                                                          "omsGroup" : None,
                                                          "omsPlatformId" : None,
                                                          "omsComponent" : None,
                                                          "omsPlatformClass" : None,
                                                          "omsFirstTimeTimestamp" : None,
                                                          "assetStatus" : "failed",
                                                          "node" : "PC01B",
                                                          "subsite" : "CE04OSPS",
                                                          "sensor" : "05-ZPLSCB102",
                                                          "eventId" : 6865811
                                                        }, {
                                                          "severity" : -1,
                                                          "method" : None,
                                                          "message" : "Stream statuses: failed: 1, notTracked: 1",
                                                          "id" : None,
                                                          "type" : "ASSET_STATUS",
                                                          "time" : 1.496012463445E12,
                                                          "maxMessageLenght" : 4096,
                                                          "storeTime" : 1496012470254,
                                                          "acknowledgeTime" : 1496030470221,
                                                          "acknowledgedBy" : "uframe",
                                                          "acknowledged" : True,
                                                          "deployment" : None,
                                                          "associatedId" : None,
                                                          "eventCount" : 1,
                                                          "omsEventId" : None,
                                                          "omsGroup" : None,
                                                          "omsPlatformId" : None,
                                                          "omsComponent" : None,
                                                          "omsPlatformClass" : None,
                                                          "omsFirstTimeTimestamp" : None,
                                                          "assetStatus" : "failed",
                                                          "node" : "PC03A",
                                                          "subsite" : "RS03AXPS",
                                                          "sensor" : "4B-PHSENA302",
                                                          "eventId" : 6865810
                                                        } ]
                                    }]
                    },
                    {
                        'root': 'alertalarms',
                        'endpoint': 'alertalarms/{eventId}',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Returns a single alert or alarm for the eventId provided.',
                        'data_required': True,
                        'data_format': [
                                {'name': 'eventId',
                                 'type': 'int',
                                 'description': 'The alarm eventId value.',
                                 'valid_values': None,
                                 'default': None
                                }
                        ],
                        'samples': [{
                                    'sample_request': 'alertalarms/6865817',
                                    'sample_response': [ {
                                                          "severity" : 1,
                                                          "method" : None,
                                                          "message" : "Stream statuses: degraded: 1",
                                                          "id" : None,
                                                          "type" : "ASSET_STATUS",
                                                          "time" : 1.49610252096E12,
                                                          "maxMessageLenght" : 4096,
                                                          "storeTime" : 1496102530200,
                                                          "acknowledgeTime" : None,
                                                          "acknowledgedBy" : None,
                                                          "acknowledged" : False,
                                                          "deployment" : None,
                                                          "associatedId" : None,
                                                          "eventCount" : 1,
                                                          "omsEventId" : None,
                                                          "omsGroup" : None,
                                                          "omsPlatformId" : None,
                                                          "omsComponent" : None,
                                                          "omsPlatformClass" : None,
                                                          "omsFirstTimeTimestamp" : None,
                                                          "assetStatus" : "degraded",
                                                          "node" : "PC01B",
                                                          "subsite" : "CE04OSPS",
                                                          "sensor" : "05-ZPLSCB102",
                                                          "eventId" : 6865817
                                                        }]
                                    }]
                    },
                    {
                        'root': 'alertalarms',
                        'endpoint': 'alertalarms/inv',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Get list of unique subsites with alerts or alarms. ' +
                                       'Optional filter by acknowledgment status.',
                        'data_required': False,
                        'data_format': [{'name': 'acknowledged',
                                         'type': 'str',
                                         'description': '[Optional] Enumeration value to filter results ' +
                                                        'by acknowledged status. Default is all.',
                                         'valid_values': ['true', 'false', 'all'],
                                         'default': None
                                        }],
                        'samples': [{
                                    'sample_request': 'alertalarms/inv',
                                    'sample_response': [ "RS03ASHS", "GI01SUMO", "CE02SHBP", "CE01ISSM"]
                                    }]
                    },
                    {
                        'root': 'alertalarms',
                        'endpoint': 'alertalarms/inv/{subsite}',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'For the subsite provided, get list of unique node(s) ' +
                                       'with alerts and/or alarms. Optional filter by acknowledgment status.',
                        'data_required': True,
                        'data_format': [
                                { 'name': 'subsite',
                                  'type': 'str',
                                  'description': 'The subsite portion of the reference designator.',
                                  'valid_values': None,
                                  'default': None
                                },
                                {'name': 'acknowledged',
                                 'type': 'str',
                                 'description': '[Optional] Enumeration value to filter results ' +
                                                'by acknowledged status. Default is all.',
                                 'valid_values': ['true', 'false', 'all'],
                                 'default': None
                                }
                        ],
                        'samples': [{
                                    'sample_request': 'alertalarms/inv/RS03ASHS',
                                    'sample_response': [ "MJ03B" ]
                                    }]
                    },
                    {
                        'root': 'alertalarms',
                        'endpoint': 'alertalarms/inv/{subsite}/{node}',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'For the subsite and node provided, get list of unique sensor(s) ' +
                                       'with alerts and/or alarms. Optional filter by acknowledgment status.',
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
                                {'name': 'acknowledged',
                                 'type': 'str',
                                 'description': '[Optional] Enumeration value to filter results ' +
                                                'by acknowledged status. Default is all.',
                                 'valid_values': ['true', 'false', 'all'],
                                 'default': None
                                }
                        ],
                        'samples': [{
                                    'sample_request': 'alertalarms/inv/RS03ASHS/MJ03B',
                                    'sample_response': [ "07-TMPSFA301" ]
                                    }]
                    },
                    {
                        'root': 'alertalarms',
                        'endpoint': 'alertalarms/inv/{subsite}/{node}/{sensor}',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'For the subsite, node and sensor provided, get list of ' +
                                       'alerts and/or alarms. Optional filter by acknowledgment status.',
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
                                {'name': 'acknowledged',
                                 'type': 'str',
                                 'description': '[Optional] Enumeration value to filter results ' +
                                                'by acknowledged status. Default is all.',
                                 'valid_values': ['true', 'false', 'all'],
                                 'default': None
                                }
                        ],
                        'samples': [{
                                    'sample_request': 'alertalarms/inv/RS03ASHS/MJ03B/07-TMPSFA301?acknowledged=true',
                                    'sample_response': [ {
                                                          "severity" : -1,
                                                          "method" : None,
                                                          "message" : "Stream statuses: failed: 1",
                                                          "id" : None,
                                                          "type" : "ASSET_STATUS",
                                                          "time" : 1.490303941683E12,
                                                          "maxMessageLenght" : 4096,
                                                          "storeTime" : 1490303955867,
                                                          "acknowledgeTime" : 1495783154043,
                                                          "acknowledgedBy" : "uframe",
                                                          "acknowledged" : True,
                                                          "deployment" : None,
                                                          "associatedId" : None,
                                                          "eventCount" : 1,
                                                          "omsEventId" : None,
                                                          "omsGroup" : None,
                                                          "omsPlatformId" : None,
                                                          "omsComponent" : None,
                                                          "omsPlatformClass" : None,
                                                          "omsFirstTimeTimestamp" : None,
                                                          "assetStatus" : "failed",
                                                          "node" : "MJ03B",
                                                          "subsite" : "RS03ASHS",
                                                          "sensor" : "07-TMPSFA301",
                                                          "eventId" : 6864312
                                                        } ]
                                    }]
                    }
                ]
    return help_data
