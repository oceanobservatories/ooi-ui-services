#!/usr/bin/env python


def get_help_data_12587_events():
    """
    Asset Management help - Category 'events'
    Data store of information to be presented when a help request is made for port 12587.
    Returns a list of dictionaries associated with various requests supported on that port.
    """
    help_data = [
        {
            'category': 'events',
            'root': 'events',
            'endpoint': 'events',
            'method': 'GET',
            'permission_required': False,
            'description': 'Get a list of all events. Sample response content abbreviated.',
            'data_required': False,
            'data_format': None,
            'samples': [{
                        'sample_request': 'events',
                        'sample_response': [{
                                              "@class" : ".CruiseInfo",
                                              "uniqueCruiseIdentifier" : "AR-04",
                                              "cruiseIdentifier" : None,
                                              "shipName" : "R/V Neil Armstrong",
                                              "editPhase" : "OPERATIONAL",
                                              "eventId" : 1,
                                              "assetUid" : None,
                                              "eventType" : "CRUISE_INFO",
                                              "eventName" : "AR-04",
                                              "eventStartTime" : 1463011200000,
                                              "eventStopTime" : 1464825600000,
                                              "notes" : "Pioneer 6 (rvdata)",
                                              "tense" : "UNKNOWN",
                                              "dataSource" : "Load from [CruiseInformation.xlsx]",
                                              "lastModifiedTimestamp" : 1495138206531
                                            }]
                        }]
        },
        {
            'category': 'events',
            'root': 'events',
            'endpoint': 'events/{id}',
            'method': 'GET',
            'permission_required': False,
            'description': 'Get event by identifier. ',
            'data_required': True,
            'data_format': [
                    { 'name': 'id',
                      'type': 'int',
                      'description': 'The event identifier.',
                      'valid_values': None,
                      'default': None
                    }
            ],
            'samples': [{
                        'sample_request': 'events/1',
                        'sample_response': {
                                              "@class" : ".CruiseInfo",
                                              "uniqueCruiseIdentifier" : "AR-04",
                                              "cruiseIdentifier" : None,
                                              "shipName" : "R/V Neil Armstrong",
                                              "editPhase" : "OPERATIONAL",
                                              "eventId" : 1,
                                              "assetUid" : None,
                                              "eventType" : "CRUISE_INFO",
                                              "eventName" : "AR-04",
                                              "eventStartTime" : 1463011200000,
                                              "eventStopTime" : 1464825600000,
                                              "notes" : "Pioneer 6 (rvdata)",
                                              "tense" : "UNKNOWN",
                                              "dataSource" : "Load from [CruiseInformation.xlsx]",
                                              "lastModifiedTimestamp" : 1495138206531
                                            }
                        }]
        },
        {
            'category': 'events',
            'root': 'events',
            'endpoint': 'events/deployment/inv',
            'method': 'GET',
            'permission_required': False,
            'description': 'Get a list of all unique subsites over all deployments. ',
            'data_required': False,
            'data_format': None,
            'samples': [{
                        'sample_request': 'events/deployment/inv',
                        'sample_response': ["CE01ISSM", "CE01ISSP", "CE02SHBP", "CE02SHSM"]
                        }]
        },
        {
            'category': 'events',
            'root': 'events',
            'endpoint': 'events/deployment/inv/{subsite}',
            'method': 'GET',
            'permission_required': False,
            'description': 'Get a list of all unique nodes for a specific subsite over all deployments. ',
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
                        'sample_request': 'events/deployment/inv/CE01ISSM',
                        'sample_response': ["MFC31", "MFD35", "MFD37", "RID16", "SBC11", "SBD17"]
                        }]
        },
        {
            'category': 'events',
            'root': 'events',
            'endpoint': 'events/deployment/inv/{subsite}/{node}',
            'method': 'GET',
            'permission_required': False,
            'description': 'Get a list of all unique sensors for a specific subsite and node ' +
                           'over all deployments.',
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
                        'sample_request': 'events/deployment/inv/CE01ISSM/MFC31',
                        'sample_response': ["00-CPMENG000"]
                        }]
        },
        {
            'category': 'events',
            'root': 'events',
            'endpoint': 'events/deployment/inv/{subsite}/{node}/{sensor}',
            'method': 'GET',
            'permission_required': False,
            'description': 'Get a list of all unique deployment numbers for a specified subsite, node ' +
                           'and sensor over all deployments.',
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
                'sample_request': 'events/deployment/inv/CE01ISSM/MFC31/00-CPMENG000',
                'sample_response': [1, 2, 3, 6, 7]
            }]
        },
        {
            'category': 'events',
            'root': 'events',
            'endpoint': 'events/deployment/inv/{subsite}/{node}/{sensor}/{deploymentNumber}',
            'method': 'GET',
            'permission_required': False,
            'description': 'Get a list of all unique deployment numbers for a specified subsite, node, ' +
                           'and sensor over all deployments. A deploymentNumber of -1 will return all ' +
                           'deployments for the reference designator.',
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
                    { 'name': 'deploymentNumber',
                      'type': 'int',
                      'description': 'The deployment number; -1 will return all deployments for ' +
                                     'the reference designator.',
                      'valid_values': None,
                      'default': None
                    }
            ],
            'samples': [{
                        'sample_request': 'events/deployment/inv/CE01ISSM/MFC31/00-CPMENG000/1',
                        'sample_response': [
                                {
                                  "@class" : ".XDeployment",
                                  "location" : {
                                    "depth" : 25.0,
                                    "location" : [ -124.0956, 44.65828 ],
                                    "latitude" : 44.65828,
                                    "longitude" : -124.0956,
                                    "orbitRadius" : None
                                  },
                                  "node" : None,
                                  "sensor" : {
                                    "@class" : ".XInstrument",
                                    "calibration" : [ ],
                                    "events" : [ ],
                                    "assetId" : 2664,
                                    "remoteResources" : [ ],
                                    "serialNumber" : "1",
                                    "name" : "1",
                                    "location" : None,
                                    "owner" : None,
                                    "description" : "Multi-Function Node Communications and Power Manager",
                                    "manufacturer" : "WHOI",
                                    "notes" : None,
                                    "uid" : "CGCON-MCPM03-00001",
                                    "editPhase" : "OPERATIONAL",
                                    "physicalInfo" : {
                                      "height" : -1.0,
                                      "width" : -1.0,
                                      "length" : -1.0,
                                      "weight" : -1.0
                                    },
                                    "assetType" : "Sensor",
                                    "mobile" : False,
                                    "modelNumber" : "CPM",
                                    "purchasePrice" : None,
                                    "purchaseDate" : None,
                                    "deliveryDate" : None,
                                    "depthRating" : None,
                                    "ooiPropertyNumber" : None,
                                    "ooiPartNumber" : None,
                                    "ooiSerialNumber" : None,
                                    "deliveryOrderNumber" : None,
                                    "institutionPropertyNumber" : None,
                                    "institutionPurchaseOrderNumber" : None,
                                    "shelfLifeExpirationDate" : None,
                                    "firmwareVersion" : None,
                                    "softwareVersion" : None,
                                    "powerRequirements" : None,
                                    "dataSource" : "BulkLoad from [sensor_bulk_load-AssetRecord.csv]",
                                    "lastModifiedTimestamp" : 1495455046865
                                  },
                                  "referenceDesignator" : "CE01ISSM-MFC31-00-CPMENG000",
                                  "editPhase" : "OPERATIONAL",
                                  "deploymentNumber" : 1,
                                  "versionNumber" : 1,
                                  "mooring" : {
                                    "@class" : ".XMooring",
                                    "events" : [ ],
                                    "assetId" : 138,
                                    "remoteResources" : [ ],
                                    "serialNumber" : "CE01ISSM-00001",
                                    "name" : "CE01ISSM-00001",
                                    "location" : None,
                                    "owner" : None,
                                    "description" : "Coastal Endurance Oregon Inshore Surface Mooring",
                                    "manufacturer" : "WHOI",
                                    "notes" : None,
                                    "uid" : "CGMCE-01ISSM-00001",
                                    "editPhase" : "OPERATIONAL",
                                    "physicalInfo" : {
                                      "height" : -1.0,
                                      "width" : -1.0,
                                      "length" : -1.0,
                                      "weight" : -1.0
                                    },
                                    "assetType" : "Mooring",
                                    "mobile" : False,
                                    "modelNumber" : "CE01ISSM",
                                    "purchasePrice" : 318795.53,
                                    "purchaseDate" : 1361145600000,
                                    "deliveryDate" : 1361145600000,
                                    "depthRating" : None,
                                    "ooiPropertyNumber" : None,
                                    "ooiPartNumber" : None,
                                    "ooiSerialNumber" : None,
                                    "deliveryOrderNumber" : None,
                                    "institutionPropertyNumber" : None,
                                    "institutionPurchaseOrderNumber" : None,
                                    "shelfLifeExpirationDate" : None,
                                    "firmwareVersion" : None,
                                    "softwareVersion" : None,
                                    "powerRequirements" : None,
                                    "dataSource" : "BulkLoad from [platform_bulk_load-AssetRecord.csv]",
                                    "lastModifiedTimestamp" : 1495455036366
                                  },
                                  "deployCruiseInfo" : {
                                    "@class" : ".CruiseInfo",
                                    "uniqueCruiseIdentifier" : "OC1404B",
                                    "cruiseIdentifier" : None,
                                    "shipName" : "R/V Oceanus",
                                    "editPhase" : "OPERATIONAL",
                                    "eventId" : 29,
                                    "assetUid" : None,
                                    "eventType" : "CRUISE_INFO",
                                    "eventName" : "OC1404B",
                                    "eventStartTime" : 1397520000000,
                                    "eventStopTime" : 1398038400000,
                                    "notes" : None,
                                    "tense" : "UNKNOWN",
                                    "dataSource" : "Load from [CruiseInformation.xlsx]",
                                    "lastModifiedTimestamp" : 1495455035279
                                  },
                                  "recoverCruiseInfo" : None,
                                  "deployedBy" : None,
                                  "recoveredBy" : None,
                                  "inductiveId" : None,
                                  "waterDepth" : 25.0,
                                  "ingestInfo" : [ ],
                                  "eventId" : 231,
                                  "assetUid" : None,
                                  "eventType" : "DEPLOYMENT",
                                  "eventName" : "CE01ISSM-MFC31-00-CPMENG000",
                                  "eventStartTime" : 1397767500000,
                                  "eventStopTime" : 1408228200000,
                                  "notes" : None,
                                  "tense" : "UNKNOWN",
                                  "dataSource" : "Load from [CE01ISSM_Deploy.xlsx]",
                                  "lastModifiedTimestamp" : 1495455063059
                                }]
            }]
        },
        {
            'category': 'events',
            'root': 'events',
            'endpoint': 'events/deployment/query',
            'method': 'GET',
            'permission_required': False,
            'description': 'Get all deployments for reference designator, whether platform, node ' +
                           'or instrument.',
            'data_required': True,
            'data_format': [
                    { 'name': 'refdes',
                      'type': 'str',
                      'description': 'A reference designator.',
                      'valid_values': None,
                      'default': None
                    },
                    { 'name': 'deploymentnum',
                      'type': 'int',
                      'description': '[Optional] Deployment number. Normally a positive integer. ' +
                                     'Default -1, selects all deployments.',
                      'valid_values': None,
                      'default': None
                    },
                    { 'name': 'beginDT',
                      'type': 'longint',
                      'description': '[Optional] Start time for filter.',
                      'valid_values': None,
                      'default': None
                    },
                    { 'name': 'endDT',
                      'type': 'longint',
                      'description': '[Optional] End time for filter.',
                      'valid_values': None,
                      'default': None
                    },
                    { 'name': 'notes',
                      'type': 'bool',
                      'description': '[Optional] Return notes field value; default is False',
                      'valid_values': None,
                      'default': None
                    }
            ],
            'samples': [{
                        'sample_request': 'events/deployment/query?refdes=CE01ISSM-MFC31&deploymentnum=1&notes=True',
                        'sample_response': [
                                    {
                                      "@class" : ".XDeployment",
                                      "location" : {
                                        "depth" : 25.0,
                                        "location" : [ -124.0956, 44.65828 ],
                                        "latitude" : 44.65828,
                                        "longitude" : -124.0956,
                                        "orbitRadius" : None
                                      },
                                      "node" : None,
                                      "sensor" : {
                                        "@class" : ".XInstrument",
                                        "calibration" : [ ],
                                        "events" : [ ],
                                        "assetId" : 2664,
                                        "remoteResources" : [ ],
                                        "serialNumber" : "1",
                                        "name" : "1",
                                        "location" : None,
                                        "owner" : None,
                                        "description" : "Multi-Function Node Communications and Power Manager",
                                        "manufacturer" : "WHOI",
                                        "notes" : "CE01ISSM-0000(1,2)-CPM3",
                                        "uid" : "CGCON-MCPM03-00001",
                                        "editPhase" : "OPERATIONAL",
                                        "physicalInfo" : {
                                          "height" : -1.0,
                                          "width" : -1.0,
                                          "length" : -1.0,
                                          "weight" : -1.0
                                        },
                                        "assetType" : "Sensor",
                                        "mobile" : False,
                                        "modelNumber" : "CPM",
                                        "purchasePrice" : None,
                                        "purchaseDate" : None,
                                        "deliveryDate" : None,
                                        "depthRating" : None,
                                        "ooiPropertyNumber" : None,
                                        "ooiPartNumber" : None,
                                        "ooiSerialNumber" : None,
                                        "deliveryOrderNumber" : None,
                                        "institutionPropertyNumber" : None,
                                        "institutionPurchaseOrderNumber" : None,
                                        "shelfLifeExpirationDate" : None,
                                        "firmwareVersion" : None,
                                        "softwareVersion" : None,
                                        "powerRequirements" : None,
                                        "dataSource" : "BulkLoad from [sensor_bulk_load-AssetRecord.csv]",
                                        "lastModifiedTimestamp" : 1495455046865
                                      },
                                      "referenceDesignator" : "CE01ISSM-MFC31-00-CPMENG000",
                                      "editPhase" : "OPERATIONAL",
                                      "deploymentNumber" : 1,
                                      "versionNumber" : 1,
                                      "mooring" : {
                                        "@class" : ".XMooring",
                                        "events" : [ ],
                                        "assetId" : 138,
                                        "remoteResources" : [ ],
                                        "serialNumber" : "CE01ISSM-00001",
                                        "name" : "CE01ISSM-00001",
                                        "location" : None,
                                        "owner" : None,
                                        "description" : "Coastal Endurance Oregon Inshore Surface Mooring",
                                        "manufacturer" : "WHOI",
                                        "notes" : None,
                                        "uid" : "CGMCE-01ISSM-00001",
                                        "editPhase" : "OPERATIONAL",
                                        "physicalInfo" : {
                                          "height" : -1.0,
                                          "width" : -1.0,
                                          "length" : -1.0,
                                          "weight" : -1.0
                                        },
                                        "assetType" : "Mooring",
                                        "mobile" : False,
                                        "modelNumber" : "CE01ISSM",
                                        "purchasePrice" : 318795.53,
                                        "purchaseDate" : 1361145600000,
                                        "deliveryDate" : 1361145600000,
                                        "depthRating" : None,
                                        "ooiPropertyNumber" : None,
                                        "ooiPartNumber" : None,
                                        "ooiSerialNumber" : None,
                                        "deliveryOrderNumber" : None,
                                        "institutionPropertyNumber" : None,
                                        "institutionPurchaseOrderNumber" : None,
                                        "shelfLifeExpirationDate" : None,
                                        "firmwareVersion" : None,
                                        "softwareVersion" : None,
                                        "powerRequirements" : None,
                                        "dataSource" : "BulkLoad from [platform_bulk_load-AssetRecord.csv]",
                                        "lastModifiedTimestamp" : 1495455036366
                                      },
                                      "deployCruiseInfo" : {
                                        "@class" : ".CruiseInfo",
                                        "uniqueCruiseIdentifier" : "OC1404B",
                                        "cruiseIdentifier" : None,
                                        "shipName" : "R/V Oceanus",
                                        "editPhase" : "OPERATIONAL",
                                        "eventId" : 29,
                                        "assetUid" : None,
                                        "eventType" : "CRUISE_INFO",
                                        "eventName" : "OC1404B",
                                        "eventStartTime" : 1397520000000,
                                        "eventStopTime" : 1398038400000,
                                        "notes" : "Endurance 1 (rvdata)",
                                        "tense" : "UNKNOWN",
                                        "dataSource" : "Load from [CruiseInformation.xlsx]",
                                        "lastModifiedTimestamp" : 1495455035279
                                      },
                                      "recoverCruiseInfo" : None,
                                      "deployedBy" : None,
                                      "recoveredBy" : None,
                                      "inductiveId" : None,
                                      "waterDepth" : 25.0,
                                      "ingestInfo" : [ ],
                                      "eventId" : 231,
                                      "assetUid" : None,
                                      "eventType" : "DEPLOYMENT",
                                      "eventName" : "CE01ISSM-MFC31-00-CPMENG000",
                                      "eventStartTime" : 1397767500000,
                                      "eventStopTime" : 1408228200000,
                                      "notes" : None,
                                      "tense" : "UNKNOWN",
                                      "dataSource" : "Load from [CE01ISSM_Deploy.xlsx]",
                                      "lastModifiedTimestamp" : 1495455063059
                                    }]
            }]
        },
        {
            'category': 'events',
            'root': 'events',
            'endpoint': 'events/cruise/inv',
            'method': 'GET',
            'permission_required': False,
            'description': 'Get a list of all unique cruise identifiers in the Asset Management.',
            'data_required': False,
            'data_format': None,
            'samples': [{
                        'sample_request': 'events/cruise/inv',
                        'sample_response': ["AR-03", "AR-04", "AR-07-01", "AR-08A", "AR-08B", "AR1-07"]
                        }]
        },
        {
            'category': 'events',
            'root': 'events',
            'endpoint': 'events/cruise/inv/{subsite}',
            'method': 'GET',
            'permission_required': False,
            'description': 'Get a a sorted list of all unique cruise identifiers in Asset Management ' +
                           'associated with a full or partial deployment subsite identifier.',
            'data_required': True,
            'data_format': [
                            { 'name': 'subsite',
                              'type': 'str',
                              'description': 'Full or partial subsite (i.e. \'CE01ISSM\' or \'CE\').',
                              'valid_values': None,
                              'default': None
                            }
            ],
            'samples': [{
                'sample_request': 'events/cruise/inv/CE',
                'sample_response': [ "AT37-03", "EK-1503", "EK-1506", "EK-1507", "EK-1508"]
            }]
        },
        {
            'category': 'events',
            'root': 'events',
            'endpoint': 'events/cruise/rec/{uniqueCruiseId}',
            'method': 'GET',
            'permission_required': False,
            'description': 'Get a single cruise info record using the unique cruise identifier.',
            'data_required': True,
            'data_format': [
                            { 'name': 'uniqueCruiseId',
                              'type': 'str',
                              'description': 'The unique cruise identifier.',
                              'valid_values': None,
                              'default': None
                            }
            ],
            'samples': [{
                'sample_request': 'events/cruise/rec/AR-03',
                'sample_response': {
                                      "@class" : ".CruiseInfo",
                                      "uniqueCruiseIdentifier" : "AR-03",
                                      "cruiseIdentifier" : None,
                                      "shipName" : "R/V Neil Armstrong ",
                                      "editPhase" : "OPERATIONAL",
                                      "eventId" : 6,
                                      "assetUid" : None,
                                      "eventType" : "CRUISE_INFO",
                                      "eventName" : "AR-03",
                                      "eventStartTime" : 1462147200000,
                                      "eventStopTime" : 1462752000000,
                                      "notes" : "Pioneer (rvdata)",
                                      "tense" : "UNKNOWN",
                                      "dataSource" : "Load from [CruiseInformation.xlsx]",
                                      "lastModifiedTimestamp" : 1495455035256
                                    }
                }]
            },
            {
                'category': 'events',
                'root': 'events',
                'endpoint': 'events/cruise/deployments/{uniqueCruiseId}',
                'method': 'GET',
                'permission_required': False,
                'description': 'Get a list of all deployments for a uniqueCruiseId.',
                'data_required': True,
                'data_format': [
                                { 'name': 'uniqueCruiseId',
                                  'type': 'str',
                                  'description': 'The unique cruise identifier.',
                                  'valid_values': None,
                                  'default': None
                                }],
                'samples': [{
                            'sample_request': 'events/cruise/deployments/AT-26-29',
                            'sample_response': [
                                {
                                  "@class" : ".XDeployment",
                                  "location" : {
                                    "depth" : 12.0,
                                    "location" : [ -89.3575, -54.40833 ],
                                    "latitude" : -54.40833,
                                    "longitude" : -89.3575,
                                    "orbitRadius" : None
                                  },
                                  "node" : None,
                                  "sensor" : {
                                    "@class" : ".XInstrument",
                                    "calibration" : [ ],
                                    "events" : [ ],
                                    "assetId" : 3084,
                                    "remoteResources" : [ ],
                                    "serialNumber" : "GS01SUMO-00001-DCL16",
                                    "name" : "GS01SUMO-00001-DCL16",
                                    "location" : None,
                                    "owner" : None,
                                    "description" : "Near Surface Instrument Frame Data Concentrator Logger",
                                    "manufacturer" : "WHOI",
                                    "notes" : None,
                                    "uid" : "R00065",
                                    "editPhase" : "OPERATIONAL",
                                    "physicalInfo" : {
                                      "height" : -1.0,
                                      "width" : -1.0,
                                      "length" : -1.0,
                                      "weight" : -1.0
                                    },
                                    "assetType" : "Sensor",
                                    "mobile" : False,
                                    "modelNumber" : "DCL",
                                    "purchasePrice" : None,
                                    "purchaseDate" : None,
                                    "deliveryDate" : None,
                                    "depthRating" : None,
                                    "ooiPropertyNumber" : None,
                                    "ooiPartNumber" : None,
                                    "ooiSerialNumber" : None,
                                    "deliveryOrderNumber" : None,
                                    "institutionPropertyNumber" : None,
                                    "institutionPurchaseOrderNumber" : None,
                                    "shelfLifeExpirationDate" : None,
                                    "firmwareVersion" : None,
                                    "softwareVersion" : None,
                                    "powerRequirements" : None,
                                    "dataSource" : "BulkLoad from [sensor_bulk_load-AssetRecord.csv]",
                                    "lastModifiedTimestamp" : 1495455048680
                                  },
                                  "referenceDesignator" : "GS01SUMO-RID16-00-DCLENG000",
                                  "editPhase" : "OPERATIONAL",
                                  "deploymentNumber" : 1,
                                  "versionNumber" : 1,
                                  "mooring" : {
                                    "@class" : ".XMooring",
                                    "events" : [ ],
                                    "assetId" : 42,
                                    "remoteResources" : [ ],
                                    "serialNumber" : "GS01SUMO-00001",
                                    "name" : "GS01SUMO-00001",
                                    "location" : None,
                                    "owner" : None,
                                    "description" : "Global Southern Ocean Apex Surface Mooring",
                                    "manufacturer" : "WHOI",
                                    "notes" : None,
                                    "uid" : "CGMGS-01SUMO-00001",
                                    "editPhase" : "OPERATIONAL",
                                    "physicalInfo" : {
                                      "height" : -1.0,
                                      "width" : -1.0,
                                      "length" : -1.0,
                                      "weight" : -1.0
                                    },
                                    "assetType" : "Mooring",
                                    "mobile" : False,
                                    "modelNumber" : "GS01SUMO",
                                    "purchasePrice" : None,
                                    "purchaseDate" : None,
                                    "deliveryDate" : None,
                                    "depthRating" : None,
                                    "ooiPropertyNumber" : None,
                                    "ooiPartNumber" : None,
                                    "ooiSerialNumber" : None,
                                    "deliveryOrderNumber" : None,
                                    "institutionPropertyNumber" : None,
                                    "institutionPurchaseOrderNumber" : None,
                                    "shelfLifeExpirationDate" : None,
                                    "firmwareVersion" : None,
                                    "softwareVersion" : None,
                                    "powerRequirements" : None,
                                    "dataSource" : "BulkLoad from [platform_bulk_load-AssetRecord.csv]",
                                    "lastModifiedTimestamp" : 1495455036018
                                  },
                                  "deployCruiseInfo" : {
                                    "@class" : ".CruiseInfo",
                                    "uniqueCruiseIdentifier" : "AT-26-29",
                                    "cruiseIdentifier" : None,
                                    "shipName" : "R/V Atlantis",
                                    "editPhase" : "OPERATIONAL",
                                    "eventId" : 9,
                                    "assetUid" : None,
                                    "eventType" : "CRUISE_INFO",
                                    "eventName" : "AT-26-29",
                                    "eventStartTime" : 1423699200000,
                                    "eventStopTime" : 1425513600000,
                                    "notes" : None,
                                    "tense" : "UNKNOWN",
                                    "dataSource" : "Load from [CruiseInformation.xlsx]",
                                    "lastModifiedTimestamp" : 1495455035260
                                  },
                                  "recoverCruiseInfo" : {
                                    "@class" : ".CruiseInfo",
                                    "uniqueCruiseIdentifier" : "NBP-15-11",
                                    "cruiseIdentifier" : None,
                                    "shipName" : "R/V Nathaniel B. Palmer",
                                    "editPhase" : "OPERATIONAL",
                                    "eventId" : 28,
                                    "assetUid" : None,
                                    "eventType" : "CRUISE_INFO",
                                    "eventName" : "NBP-15-11",
                                    "eventStartTime" : 1449446400000,
                                    "eventStopTime" : 1451865600000,
                                    "notes" : None,
                                    "tense" : "UNKNOWN",
                                    "dataSource" : "Load from [CruiseInformation.xlsx]",
                                    "lastModifiedTimestamp" : 1495455035278
                                  },
                                  "deployedBy" : None,
                                  "recoveredBy" : None,
                                  "inductiveId" : None,
                                  "waterDepth" : 4611.0,
                                  "ingestInfo" : [ ],
                                  "eventId" : 3534,
                                  "assetUid" : None,
                                  "eventType" : "DEPLOYMENT",
                                  "eventName" : "GS01SUMO-RID16-00-DCLENG000",
                                  "eventStartTime" : 1424293560000,
                                  "eventStopTime" : 1451215200000,
                                  "notes" : None,
                                  "tense" : "UNKNOWN",
                                  "dataSource" : "Load from [GS01SUMO_Deploy.xlsx]",
                                  "lastModifiedTimestamp" : 1495455092700
                                }]
                            }]
            }
    ]
    return help_data
