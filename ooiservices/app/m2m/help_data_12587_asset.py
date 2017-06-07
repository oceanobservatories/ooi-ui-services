#!/usr/bin/env python


def get_help_data_12587_asset():
    """
    Asset Management help - Category 'asset'
    Data store of information to be presented when a help request is made for port 12587.
    Returns a list of dictionaries associated with various requests supported on that port.

    Note: Parameter serialnumber should be removed and/or deprecated as it is not supported on uframe
    or simply note working on uframe. (It is shown in the help right now.)
    """
    help_data = [
                    {
                        'root': 'asset',
                        'endpoint': 'asset',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Get a list of all asset records.',
                        'data_required': False,
                        'data_format': None,
                        'samples': [{
                                    'sample_request': 'asset',
                                    'sample_response': None
                                    }]
                    },
                    {
                        'root': 'asset',
                        'endpoint': 'asset/{id}',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Get asset information given its identifier. (id)',
                        'data_required': True,
                        'data_format': [
                                { 'name': 'id',
                                  'type': 'int',
                                  'description': 'The asset identifier. (id)',
                                  'valid_values': None,
                                  'default': None
                                }
                        ],
                        'samples': [{
                                    'sample_request': 'asset/10',
                                    'sample_response': {
                                                      "@class" : ".XMooring",
                                                      "events" : None,
                                                      "assetId" : 10,
                                                      "remoteResources" : [ ],
                                                      "serialNumber" : "SN0003",
                                                      "name" : "SN0003",
                                                      "location" : None,
                                                      "owner" : None,
                                                      "description" : "Cabled Oregon Slope Base Seafloor: Low Power Junction Box",
                                                      "manufacturer" : "UW-APL",
                                                      "notes" : None,
                                                      "uid" : "ATAPL-65310-010-0003",
                                                      "editPhase" : "OPERATIONAL",
                                                      "physicalInfo" : {
                                                        "height" : -1.0,
                                                        "width" : -1.0,
                                                        "length" : -1.0,
                                                        "weight" : -1.0
                                                      },
                                                      "assetType" : "Mooring",
                                                      "mobile" : False,
                                                      "modelNumber" : "RS01SLBS-LJ01A",
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
                                                      "lastModifiedTimestamp" : 1495138268172
                                                    }
                                    }]
                    },
                    {
                        'root': 'asset',
                        'endpoint': 'asset',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Get asset information given its identifier (id). ',
                        'data_required': True,
                        'data_format': [
                                { 'name': 'assetid',
                                  'type': 'int',
                                  'description': 'The asset identifier.',
                                  'valid_values': None,
                                  'default': None
                                }
                        ],
                        'samples': [{
                                    'sample_request': 'asset?assetid=10',
                                    'sample_response': {
                                                      "@class" : ".XMooring",
                                                      "events" : None,
                                                      "assetId" : 10,
                                                      "remoteResources" : [ ],
                                                      "serialNumber" : "SN0003",
                                                      "name" : "SN0003",
                                                      "location" : None,
                                                      "owner" : None,
                                                      "description" : "Cabled Oregon Slope Base Seafloor: Low Power Junction Box",
                                                      "manufacturer" : "UW-APL",
                                                      "notes" : None,
                                                      "uid" : "ATAPL-65310-010-0003",
                                                      "editPhase" : "OPERATIONAL",
                                                      "physicalInfo" : {
                                                        "height" : -1.0,
                                                        "width" : -1.0,
                                                        "length" : -1.0,
                                                        "weight" : -1.0
                                                      },
                                                      "assetType" : "Mooring",
                                                      "mobile" : False,
                                                      "modelNumber" : "RS01SLBS-LJ01A",
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
                                                      "lastModifiedTimestamp" : 1495138268172
                                                    }
                                    }]
                    },
                    {
                        'root': 'asset',
                        'endpoint': 'asset',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Get asset information by the unique identifier (UID). ',
                        'data_required': True,
                        'data_format': [
                                { 'name': 'uid',
                                  'type': 'str',
                                  'description': 'The asset unique identifier (uid).',
                                  'valid_values': None,
                                  'default': None
                                }
                        ],
                        'samples': [{
                                    'sample_request': 'asset?uid=ATAPL-65310-010-0003',
                                    'sample_response': {
                                              "@class" : ".XMooring",
                                              "events" : None,
                                              "assetId" : 10,
                                              "remoteResources" : [ ],
                                              "serialNumber" : "SN0003",
                                              "name" : "SN0003",
                                              "location" : None,
                                              "owner" : None,
                                              "description" : "Cabled Oregon Slope Base Seafloor: Low Power Junction Box",
                                              "manufacturer" : "UW-APL",
                                              "notes" : None,
                                              "uid" : "ATAPL-65310-010-0003",
                                              "editPhase" : "OPERATIONAL",
                                              "physicalInfo" : {
                                                "height" : -1.0,
                                                "width" : -1.0,
                                                "length" : -1.0,
                                                "weight" : -1.0
                                              },
                                              "assetType" : "Mooring",
                                              "mobile" : False,
                                              "modelNumber" : "RS01SLBS-LJ01A",
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
                                              "lastModifiedTimestamp" : 1495138268172
                                            }
                        }]
                    },
                    {
                        'root': 'asset',
                        'endpoint': 'asset',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Retrieve information for an asset given its serial number. ',
                        'data_required': True,
                        'data_format': [
                                { 'name': 'serialnumber',
                                  'type': 'str',
                                  'description': 'The asset serial number.',
                                  'valid_values': None,
                                  'default': None
                                }
                        ],
                        'samples': [{
                                    'sample_request': 'asset?serialnumber=SN0003',
                                    'sample_response': {
                                              "@class" : ".XMooring",
                                              "events" : None,
                                              "assetId" : 10,
                                              "remoteResources" : [ ],
                                              "serialNumber" : "SN0003",
                                              "name" : "SN0003",
                                              "location" : None,
                                              "owner" : None,
                                              "description" : "Cabled Oregon Slope Base Seafloor: Low Power Junction Box",
                                              "manufacturer" : "UW-APL",
                                              "notes" : None,
                                              "uid" : "ATAPL-65310-010-0003",
                                              "editPhase" : "OPERATIONAL",
                                              "physicalInfo" : {
                                                "height" : -1.0,
                                                "width" : -1.0,
                                                "length" : -1.0,
                                                "weight" : -1.0
                                              },
                                              "assetType" : "Mooring",
                                              "mobile" : False,
                                              "modelNumber" : "RS01SLBS-LJ01A",
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
                                              "lastModifiedTimestamp" : 1495138268172
                                            }
                                    }]
                    },
                    {
                        'root': 'asset/deployments',
                        'endpoint': 'asset/deployments',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Get deployment digests by the unique asset identifier (UID).',
                        'data_required': True,
                        'data_format': [
                                { 'name': 'uid',
                                  'type': 'str',
                                  'description': 'The asset unique identifier (uid).',
                                  'valid_values': None,
                                  'default': None
                                },
                                { 'name': 'editphase',
                                  'type': 'str',
                                  'description': 'Enumeration value.',
                                  'valid_values': ['ALL','EDIT', 'OPERATIONAL', 'STAGED'],
                                  'default': None
                                }
                        ],
                        'samples': [{
                                    'sample_request': 'asset/deployments/ATAPL-65244-060-0028?editphase=ALL',
                                    'sample_response':
                                        [{
                                          "depth" : 1518.0,
                                          "startTime" : 1406502900000,
                                          "node" : "MJ03C",
                                          "latitude" : 45.92617,
                                          "longitude" : -129.97901,
                                          "sensor" : "05-CAMDSB303",
                                          "subsite" : "RS03INT1",
                                          "eventId" : 4060,
                                          "editPhase" : "OPERATIONAL",
                                          "deploymentNumber" : 1,
                                          "versionNumber" : 1,
                                          "orbitRadius" : None,
                                          "waterDepth" : 1518.0,
                                          "deployCruiseIdentifier" : "TN-313",
                                          "recoverCruiseIdentifier" : None,
                                          "endTime" : 1436567198000,
                                          "mooring_uid" : "ATAPL-65244-060-0028",
                                          "node_uid" : None,
                                          "sensor_uid" : "ATAPL-58317-00002"
                                        },
                                        {
                                          "depth" : 1518.0,
                                          "startTime" : 1436567198000,
                                          "node" : "MJ03C",
                                          "latitude" : 45.92616,
                                          "longitude" : -129.97901,
                                          "sensor" : "05-CAMDSB303",
                                          "subsite" : "RS03INT1",
                                          "eventId" : 4066,
                                          "editPhase" : "OPERATIONAL",
                                          "deploymentNumber" : 2,
                                          "versionNumber" : 1,
                                          "orbitRadius" : None,
                                          "waterDepth" : 1518.0,
                                          "deployCruiseIdentifier" : "TN-326",
                                          "recoverCruiseIdentifier" : None,
                                          "endTime" : 1469491200000,
                                          "mooring_uid" : "ATAPL-65244-060-0028",
                                          "node_uid" : None,
                                          "sensor_uid" : "ATAPL-58317-00005"
                                        }]
                                    }]
                    },
                    {
                        'root': 'asset/cal',
                        'endpoint': 'asset/cal',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Get calibration information by the unique asset identifier (UID). ' +
                                       'Response output abbreviated for a single parameter.',
                        'data_required': True,
                        'data_format': [
                                        { 'name': 'uid',
                                          'type': 'str',
                                          'description': 'The asset unique identifier (uid).',
                                          'valid_values': None,
                                          'default': None
                                        }],
                        'samples':
                        [{
                            'sample_request': 'asset/cal?uid=CGINS-CTDMOH-13655',
                            'sample_response':
                                {
                                  "@class" : ".XInstrument",
                                  "calibration" :
                                              [ {
                                                "@class" : ".XCalibration",
                                                "name" : "CC_a0",
                                                "calData" : [ {
                                                              "@class" : ".XCalibrationData",
                                                              "value" : -1.401584E-4,
                                                              "comments" : None,
                                                              "eventId" : 28535,
                                                              "assetUid" : "CGINS-CTDMOH-13655",
                                                              "eventType" : "CALIBRATION_DATA",
                                                              "eventName" : "CC_a0",
                                                              "eventStartTime" : 1450310400000,
                                                              "eventStopTime" : None,
                                                              "notes" : None,
                                                              "tense" : "UNKNOWN",
                                                              "dataSource" : "CGINS-CTDMOH-13655__20151217_Cal_Info.xlsx",
                                                              "lastModifiedTimestamp" : 1495455123265
                                                            }, {
                                                              "@class" : ".XCalibrationData",
                                                              "value" : -9.51E-5,
                                                              "comments" : None,
                                                              "eventId" : 28582,
                                                              "assetUid" : "CGINS-CTDMOH-13655",
                                                              "eventType" : "CALIBRATION_DATA",
                                                              "eventName" : "CC_a0",
                                                              "eventStartTime" : 1490054400000,
                                                              "eventStopTime" : None,
                                                              "notes" : None,
                                                              "tense" : "UNKNOWN",
                                                              "dataSource" : "CGINS-CTDMOH-13655__20170321_Cal_Info.xlsx",
                                                              "lastModifiedTimestamp" : 1495455123342
                                                            } ]
                                              } ],
                                  "events" : [ ],
                                  "assetId" : 344,
                                  "remoteResources" : [ ],
                                  "serialNumber" : "37-13655",
                                  "name" : "37-13655",
                                  "location" : None,
                                  "owner" : None,
                                  "description" : "CTD Mooring (Inductive): CTDMO Series H",
                                  "manufacturer" : "Sea-Bird Electronics",
                                  "notes" : None,
                                  "uid" : "CGINS-CTDMOH-13655",
                                  "editPhase" : "OPERATIONAL",
                                  "physicalInfo" : {
                                    "height" : -1.0,
                                    "width" : -1.0,
                                    "length" : -1.0,
                                    "weight" : -1.0
                                  },
                                  "assetType" : "Sensor",
                                  "mobile" : False,
                                  "modelNumber" : "SBE 37-IM",
                                  "purchasePrice" : 7000.0,
                                  "purchaseDate" : 1435708800000,
                                  "deliveryDate" : 1435708800000,
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
                                  "lastModifiedTimestamp" : 1495455037605
                                }


                        }]
                    },
                    {
                        'root': 'asset/cal',
                        'endpoint': 'asset/cal',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Get calibration information by the asset identifier (assetId). ' +
                                       'Response output abbreviated for a single parameter.',
                        'data_required': True,
                        'data_format': [
                                        { 'name': 'assetid',
                                          'type': 'int',
                                          'description': 'The asset identifier (assetId).',
                                          'valid_values': None,
                                          'default': None
                                        }],
                        'samples':
                        [{
                            'sample_request': 'asset/cal?assetid=344',
                            'sample_response':
                                {
                                  "@class" : ".XInstrument",
                                  "calibration" :
                                              [ {
                                                "@class" : ".XCalibration",
                                                "name" : "CC_a0",
                                                "calData" : [ {
                                                              "@class" : ".XCalibrationData",
                                                              "value" : -1.401584E-4,
                                                              "comments" : None,
                                                              "eventId" : 28535,
                                                              "assetUid" : "CGINS-CTDMOH-13655",
                                                              "eventType" : "CALIBRATION_DATA",
                                                              "eventName" : "CC_a0",
                                                              "eventStartTime" : 1450310400000,
                                                              "eventStopTime" : None,
                                                              "notes" : None,
                                                              "tense" : "UNKNOWN",
                                                              "dataSource" : "CGINS-CTDMOH-13655__20151217_Cal_Info.xlsx",
                                                              "lastModifiedTimestamp" : 1495455123265
                                                            }, {
                                                              "@class" : ".XCalibrationData",
                                                              "value" : -9.51E-5,
                                                              "comments" : None,
                                                              "eventId" : 28582,
                                                              "assetUid" : "CGINS-CTDMOH-13655",
                                                              "eventType" : "CALIBRATION_DATA",
                                                              "eventName" : "CC_a0",
                                                              "eventStartTime" : 1490054400000,
                                                              "eventStopTime" : None,
                                                              "notes" : None,
                                                              "tense" : "UNKNOWN",
                                                              "dataSource" : "CGINS-CTDMOH-13655__20170321_Cal_Info.xlsx",
                                                              "lastModifiedTimestamp" : 1495455123342
                                                            } ]
                                              } ],
                                  "events" : [ ],
                                  "assetId" : 344,
                                  "remoteResources" : [ ],
                                  "serialNumber" : "37-13655",
                                  "name" : "37-13655",
                                  "location" : None,
                                  "owner" : None,
                                  "description" : "CTD Mooring (Inductive): CTDMO Series H",
                                  "manufacturer" : "Sea-Bird Electronics",
                                  "notes" : None,
                                  "uid" : "CGINS-CTDMOH-13655",
                                  "editPhase" : "OPERATIONAL",
                                  "physicalInfo" : {
                                    "height" : -1.0,
                                    "width" : -1.0,
                                    "length" : -1.0,
                                    "weight" : -1.0
                                  },
                                  "assetType" : "Sensor",
                                  "mobile" : False,
                                  "modelNumber" : "SBE 37-IM",
                                  "purchasePrice" : 7000.0,
                                  "purchaseDate" : 1435708800000,
                                  "deliveryDate" : 1435708800000,
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
                                  "lastModifiedTimestamp" : 1495455037605
                                }


                        }]

                    },
                    {
                        'root': 'asset/cal',
                        'endpoint': 'asset/cal',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Get a list of deployments with calibration information by the ' +
                                        'reference designator, using begin and end time to limit response output. ' +
                                       'Complete response output provided and includes one (1) deployment.',
                        'data_required': True,
                        'data_format': [
                                        { 'name': 'refdes',
                                          'type': 'str',
                                          'description': 'The asset reference designator.',
                                          'valid_values': None,
                                          'default': None
                                        },
                                        { 'name': 'beginDT',
                                          'type': 'longint',
                                          'description': '[Optional] Filter search using an initial time for search.',
                                          'valid_values': None,
                                          'default': None
                                        },
                                        { 'name': 'endDT',
                                          'type': 'longint',
                                          'description': '[Optional] Filter search using an end time for search.',
                                          'valid_values': None,
                                          'default': None
                                        }],
                        'samples':
                            [{
                            'sample_request': 'asset/cal?refdes=GS03FLMA-RIM01-02-CTDMOH051&beginDT=2016-01-17T19:42:00.000Z&endDT=2016-02-18T00:00:00.000Z',
                            'sample_response': [
                                                {
                                                  "@class" : ".XDeployment",
                                                  "location" : {
                                                    "depth" : 1501.0,
                                                    "location" : [ -89.55293, -54.12563 ],
                                                    "latitude" : -54.12563,
                                                    "longitude" : -89.55293,
                                                    "orbitRadius" : None
                                                  },
                                                  "node" : None,
                                                  "sensor" : {
                                                    "@class" : ".XInstrument",
                                                    "calibration" : [ {
                                                      "@class" : ".XCalibration",
                                                      "name" : "CC_a0",
                                                      "calData" : [ {
                                                        "@class" : ".XCalibrationData",
                                                        "value" : -1.401584E-4,
                                                        "comments" : None,
                                                        "eventId" : 28535,
                                                        "assetUid" : "CGINS-CTDMOH-13655",
                                                        "eventType" : "CALIBRATION_DATA",
                                                        "eventName" : "CC_a0",
                                                        "eventStartTime" : 1450310400000,
                                                        "eventStopTime" : None,
                                                        "notes" : None,
                                                        "tense" : "UNKNOWN",
                                                        "dataSource" : "CGINS-CTDMOH-13655__20151217_Cal_Info.xlsx",
                                                        "lastModifiedTimestamp" : 1495455123265
                                                      } ]
                                                    }, {
                                                      "@class" : ".XCalibration",
                                                      "name" : "CC_ptcb1",
                                                      "calData" : [ {
                                                        "@class" : ".XCalibrationData",
                                                        "value" : -7.5E-5,
                                                        "comments" : None,
                                                        "eventId" : 28537,
                                                        "assetUid" : "CGINS-CTDMOH-13655",
                                                        "eventType" : "CALIBRATION_DATA",
                                                        "eventName" : "CC_ptcb1",
                                                        "eventStartTime" : 1450310400000,
                                                        "eventStopTime" : None,
                                                        "notes" : None,
                                                        "tense" : "UNKNOWN",
                                                        "dataSource" : "CGINS-CTDMOH-13655__20151217_Cal_Info.xlsx",
                                                        "lastModifiedTimestamp" : 1495455123265
                                                      } ]
                                                    }, {
                                                      "@class" : ".XCalibration",
                                                      "name" : "CC_g",
                                                      "calData" : [ {
                                                        "@class" : ".XCalibrationData",
                                                        "value" : -0.9922154000000001,
                                                        "comments" : None,
                                                        "eventId" : 28539,
                                                        "assetUid" : "CGINS-CTDMOH-13655",
                                                        "eventType" : "CALIBRATION_DATA",
                                                        "eventName" : "CC_g",
                                                        "eventStartTime" : 1450310400000,
                                                        "eventStopTime" : None,
                                                        "notes" : None,
                                                        "tense" : "UNKNOWN",
                                                        "dataSource" : "CGINS-CTDMOH-13655__20151217_Cal_Info.xlsx",
                                                        "lastModifiedTimestamp" : 1495455123265
                                                      } ]
                                                    }, {
                                                      "@class" : ".XCalibration",
                                                      "name" : "CC_ptcb2",
                                                      "calData" : [ {
                                                        "@class" : ".XCalibrationData",
                                                        "value" : 0.0,
                                                        "comments" : None,
                                                        "eventId" : 28541,
                                                        "assetUid" : "CGINS-CTDMOH-13655",
                                                        "eventType" : "CALIBRATION_DATA",
                                                        "eventName" : "CC_ptcb2",
                                                        "eventStartTime" : 1450310400000,
                                                        "eventStopTime" : None,
                                                        "notes" : None,
                                                        "tense" : "UNKNOWN",
                                                        "dataSource" : "CGINS-CTDMOH-13655__20151217_Cal_Info.xlsx",
                                                        "lastModifiedTimestamp" : 1495455123265
                                                      } ]
                                                    }, {
                                                      "@class" : ".XCalibration",
                                                      "name" : "CC_h",
                                                      "calData" : [ {
                                                        "@class" : ".XCalibrationData",
                                                        "value" : 0.1440444,
                                                        "comments" : None,
                                                        "eventId" : 28543,
                                                        "assetUid" : "CGINS-CTDMOH-13655",
                                                        "eventType" : "CALIBRATION_DATA",
                                                        "eventName" : "CC_h",
                                                        "eventStartTime" : 1450310400000,
                                                        "eventStopTime" : None,
                                                        "notes" : None,
                                                        "tense" : "UNKNOWN",
                                                        "dataSource" : "CGINS-CTDMOH-13655__20151217_Cal_Info.xlsx",
                                                        "lastModifiedTimestamp" : 1495455123265
                                                      } ]
                                                    }, {
                                                      "@class" : ".XCalibration",
                                                      "name" : "CC_i",
                                                      "calData" : [ {
                                                        "@class" : ".XCalibrationData",
                                                        "value" : -1.411668E-4,
                                                        "comments" : None,
                                                        "eventId" : 28545,
                                                        "assetUid" : "CGINS-CTDMOH-13655",
                                                        "eventType" : "CALIBRATION_DATA",
                                                        "eventName" : "CC_i",
                                                        "eventStartTime" : 1450310400000,
                                                        "eventStopTime" : None,
                                                        "notes" : None,
                                                        "tense" : "UNKNOWN",
                                                        "dataSource" : "CGINS-CTDMOH-13655__20151217_Cal_Info.xlsx",
                                                        "lastModifiedTimestamp" : 1495455123265
                                                      } ]
                                                    }, {
                                                      "@class" : ".XCalibration",
                                                      "name" : "CC_a3",
                                                      "calData" : [ {
                                                        "@class" : ".XCalibrationData",
                                                        "value" : 2.076626E-7,
                                                        "comments" : None,
                                                        "eventId" : 28547,
                                                        "assetUid" : "CGINS-CTDMOH-13655",
                                                        "eventType" : "CALIBRATION_DATA",
                                                        "eventName" : "CC_a3",
                                                        "eventStartTime" : 1450310400000,
                                                        "eventStopTime" : None,
                                                        "notes" : None,
                                                        "tense" : "UNKNOWN",
                                                        "dataSource" : "CGINS-CTDMOH-13655__20151217_Cal_Info.xlsx",
                                                        "lastModifiedTimestamp" : 1495455123265
                                                      } ]
                                                    }, {
                                                      "@class" : ".XCalibration",
                                                      "name" : "CC_a2",
                                                      "calData" : [ {
                                                        "@class" : ".XCalibrationData",
                                                        "value" : -4.648632E-6,
                                                        "comments" : None,
                                                        "eventId" : 28549,
                                                        "assetUid" : "CGINS-CTDMOH-13655",
                                                        "eventType" : "CALIBRATION_DATA",
                                                        "eventName" : "CC_a2",
                                                        "eventStartTime" : 1450310400000,
                                                        "eventStopTime" : None,
                                                        "notes" : None,
                                                        "tense" : "UNKNOWN",
                                                        "dataSource" : "CGINS-CTDMOH-13655__20151217_Cal_Info.xlsx",
                                                        "lastModifiedTimestamp" : 1495455123265
                                                      } ]
                                                    }, {
                                                      "@class" : ".XCalibration",
                                                      "name" : "CC_ptcb0",
                                                      "calData" : [ {
                                                        "@class" : ".XCalibrationData",
                                                        "value" : 25.00462,
                                                        "comments" : None,
                                                        "eventId" : 28551,
                                                        "assetUid" : "CGINS-CTDMOH-13655",
                                                        "eventType" : "CALIBRATION_DATA",
                                                        "eventName" : "CC_ptcb0",
                                                        "eventStartTime" : 1450310400000,
                                                        "eventStopTime" : None,
                                                        "notes" : None,
                                                        "tense" : "UNKNOWN",
                                                        "dataSource" : "CGINS-CTDMOH-13655__20151217_Cal_Info.xlsx",
                                                        "lastModifiedTimestamp" : 1495455123265
                                                      } ]
                                                    }, {
                                                      "@class" : ".XCalibration",
                                                      "name" : "CC_a1",
                                                      "calData" : [ {
                                                        "@class" : ".XCalibrationData",
                                                        "value" : 3.106804E-4,
                                                        "comments" : None,
                                                        "eventId" : 28553,
                                                        "assetUid" : "CGINS-CTDMOH-13655",
                                                        "eventType" : "CALIBRATION_DATA",
                                                        "eventName" : "CC_a1",
                                                        "eventStartTime" : 1450310400000,
                                                        "eventStopTime" : None,
                                                        "notes" : None,
                                                        "tense" : "UNKNOWN",
                                                        "dataSource" : "CGINS-CTDMOH-13655__20151217_Cal_Info.xlsx",
                                                        "lastModifiedTimestamp" : 1495455123265
                                                      } ]
                                                    }, {
                                                      "@class" : ".XCalibration",
                                                      "name" : "CC_ptempa2",
                                                      "calData" : [ {
                                                        "@class" : ".XCalibrationData",
                                                        "value" : 1.000242E-6,
                                                        "comments" : None,
                                                        "eventId" : 28555,
                                                        "assetUid" : "CGINS-CTDMOH-13655",
                                                        "eventType" : "CALIBRATION_DATA",
                                                        "eventName" : "CC_ptempa2",
                                                        "eventStartTime" : 1450310400000,
                                                        "eventStopTime" : None,
                                                        "notes" : None,
                                                        "tense" : "UNKNOWN",
                                                        "dataSource" : "CGINS-CTDMOH-13655__20151217_Cal_Info.xlsx",
                                                        "lastModifiedTimestamp" : 1495455123265
                                                      } ]
                                                    }, {
                                                      "@class" : ".XCalibration",
                                                      "name" : "CC_ptempa1",
                                                      "calData" : [ {
                                                        "@class" : ".XCalibrationData",
                                                        "value" : -0.09096076,
                                                        "comments" : None,
                                                        "eventId" : 28557,
                                                        "assetUid" : "CGINS-CTDMOH-13655",
                                                        "eventType" : "CALIBRATION_DATA",
                                                        "eventName" : "CC_ptempa1",
                                                        "eventStartTime" : 1450310400000,
                                                        "eventStopTime" : None,
                                                        "notes" : None,
                                                        "tense" : "UNKNOWN",
                                                        "dataSource" : "CGINS-CTDMOH-13655__20151217_Cal_Info.xlsx",
                                                        "lastModifiedTimestamp" : 1495455123265
                                                      } ]
                                                    }, {
                                                      "@class" : ".XCalibration",
                                                      "name" : "CC_ptempa0",
                                                      "calData" : [ {
                                                        "@class" : ".XCalibrationData",
                                                        "value" : 168.1614,
                                                        "comments" : None,
                                                        "eventId" : 28559,
                                                        "assetUid" : "CGINS-CTDMOH-13655",
                                                        "eventType" : "CALIBRATION_DATA",
                                                        "eventName" : "CC_ptempa0",
                                                        "eventStartTime" : 1450310400000,
                                                        "eventStopTime" : None,
                                                        "notes" : None,
                                                        "tense" : "UNKNOWN",
                                                        "dataSource" : "CGINS-CTDMOH-13655__20151217_Cal_Info.xlsx",
                                                        "lastModifiedTimestamp" : 1495455123265
                                                      } ]
                                                    }, {
                                                      "@class" : ".XCalibration",
                                                      "name" : "CC_pa0",
                                                      "calData" : [ {
                                                        "@class" : ".XCalibrationData",
                                                        "value" : 0.213848,
                                                        "comments" : None,
                                                        "eventId" : 28561,
                                                        "assetUid" : "CGINS-CTDMOH-13655",
                                                        "eventType" : "CALIBRATION_DATA",
                                                        "eventName" : "CC_pa0",
                                                        "eventStartTime" : 1450310400000,
                                                        "eventStopTime" : None,
                                                        "notes" : None,
                                                        "tense" : "UNKNOWN",
                                                        "dataSource" : "CGINS-CTDMOH-13655__20151217_Cal_Info.xlsx",
                                                        "lastModifiedTimestamp" : 1495455123265
                                                      } ]
                                                    }, {
                                                      "@class" : ".XCalibration",
                                                      "name" : "CC_cpcor",
                                                      "calData" : [ {
                                                        "@class" : ".XCalibrationData",
                                                        "value" : -9.57E-8,
                                                        "comments" : None,
                                                        "eventId" : 28563,
                                                        "assetUid" : "CGINS-CTDMOH-13655",
                                                        "eventType" : "CALIBRATION_DATA",
                                                        "eventName" : "CC_cpcor",
                                                        "eventStartTime" : 1450310400000,
                                                        "eventStopTime" : None,
                                                        "notes" : None,
                                                        "tense" : "UNKNOWN",
                                                        "dataSource" : "CGINS-CTDMOH-13655__20151217_Cal_Info.xlsx",
                                                        "lastModifiedTimestamp" : 1495455123265
                                                      } ]
                                                    }, {
                                                      "@class" : ".XCalibration",
                                                      "name" : "CC_pa1",
                                                      "calData" : [ {
                                                        "@class" : ".XCalibrationData",
                                                        "value" : 0.01629888,
                                                        "comments" : None,
                                                        "eventId" : 28565,
                                                        "assetUid" : "CGINS-CTDMOH-13655",
                                                        "eventType" : "CALIBRATION_DATA",
                                                        "eventName" : "CC_pa1",
                                                        "eventStartTime" : 1450310400000,
                                                        "eventStopTime" : None,
                                                        "notes" : None,
                                                        "tense" : "UNKNOWN",
                                                        "dataSource" : "CGINS-CTDMOH-13655__20151217_Cal_Info.xlsx",
                                                        "lastModifiedTimestamp" : 1495455123265
                                                      } ]
                                                    }, {
                                                      "@class" : ".XCalibration",
                                                      "name" : "CC_pa2",
                                                      "calData" : [ {
                                                        "@class" : ".XCalibrationData",
                                                        "value" : -7.884311E-10,
                                                        "comments" : None,
                                                        "eventId" : 28567,
                                                        "assetUid" : "CGINS-CTDMOH-13655",
                                                        "eventType" : "CALIBRATION_DATA",
                                                        "eventName" : "CC_pa2",
                                                        "eventStartTime" : 1450310400000,
                                                        "eventStopTime" : None,
                                                        "notes" : None,
                                                        "tense" : "UNKNOWN",
                                                        "dataSource" : "CGINS-CTDMOH-13655__20151217_Cal_Info.xlsx",
                                                        "lastModifiedTimestamp" : 1495455123265
                                                      } ]
                                                    }, {
                                                      "@class" : ".XCalibration",
                                                      "name" : "CC_p_range",
                                                      "calData" : [ {
                                                        "@class" : ".XCalibrationData",
                                                        "value" : 5076.0,
                                                        "comments" : None,
                                                        "eventId" : 28569,
                                                        "assetUid" : "CGINS-CTDMOH-13655",
                                                        "eventType" : "CALIBRATION_DATA",
                                                        "eventName" : "CC_p_range",
                                                        "eventStartTime" : 1450310400000,
                                                        "eventStopTime" : None,
                                                        "notes" : None,
                                                        "tense" : "UNKNOWN",
                                                        "dataSource" : "CGINS-CTDMOH-13655__20151217_Cal_Info.xlsx",
                                                        "lastModifiedTimestamp" : 1495455123265
                                                      } ]
                                                    }, {
                                                      "@class" : ".XCalibration",
                                                      "name" : "CC_j",
                                                      "calData" : [ {
                                                        "@class" : ".XCalibrationData",
                                                        "value" : 3.022001E-5,
                                                        "comments" : None,
                                                        "eventId" : 28571,
                                                        "assetUid" : "CGINS-CTDMOH-13655",
                                                        "eventType" : "CALIBRATION_DATA",
                                                        "eventName" : "CC_j",
                                                        "eventStartTime" : 1450310400000,
                                                        "eventStopTime" : None,
                                                        "notes" : None,
                                                        "tense" : "UNKNOWN",
                                                        "dataSource" : "CGINS-CTDMOH-13655__20151217_Cal_Info.xlsx",
                                                        "lastModifiedTimestamp" : 1495455123265
                                                      } ]
                                                    }, {
                                                      "@class" : ".XCalibration",
                                                      "name" : "CC_ptca1",
                                                      "calData" : [ {
                                                        "@class" : ".XCalibrationData",
                                                        "value" : -2.481876,
                                                        "comments" : None,
                                                        "eventId" : 28573,
                                                        "assetUid" : "CGINS-CTDMOH-13655",
                                                        "eventType" : "CALIBRATION_DATA",
                                                        "eventName" : "CC_ptca1",
                                                        "eventStartTime" : 1450310400000,
                                                        "eventStopTime" : None,
                                                        "notes" : None,
                                                        "tense" : "UNKNOWN",
                                                        "dataSource" : "CGINS-CTDMOH-13655__20151217_Cal_Info.xlsx",
                                                        "lastModifiedTimestamp" : 1495455123265
                                                      } ]
                                                    }, {
                                                      "@class" : ".XCalibration",
                                                      "name" : "CC_ctcor",
                                                      "calData" : [ {
                                                        "@class" : ".XCalibrationData",
                                                        "value" : 3.25E-6,
                                                        "comments" : None,
                                                        "eventId" : 28575,
                                                        "assetUid" : "CGINS-CTDMOH-13655",
                                                        "eventType" : "CALIBRATION_DATA",
                                                        "eventName" : "CC_ctcor",
                                                        "eventStartTime" : 1450310400000,
                                                        "eventStopTime" : None,
                                                        "notes" : None,
                                                        "tense" : "UNKNOWN",
                                                        "dataSource" : "CGINS-CTDMOH-13655__20151217_Cal_Info.xlsx",
                                                        "lastModifiedTimestamp" : 1495455123265
                                                      } ]
                                                    }, {
                                                      "@class" : ".XCalibration",
                                                      "name" : "CC_wbotc",
                                                      "calData" : [ {
                                                        "@class" : ".XCalibrationData",
                                                        "value" : 1.5866E-7,
                                                        "comments" : None,
                                                        "eventId" : 28577,
                                                        "assetUid" : "CGINS-CTDMOH-13655",
                                                        "eventType" : "CALIBRATION_DATA",
                                                        "eventName" : "CC_wbotc",
                                                        "eventStartTime" : 1450310400000,
                                                        "eventStopTime" : None,
                                                        "notes" : None,
                                                        "tense" : "UNKNOWN",
                                                        "dataSource" : "CGINS-CTDMOH-13655__20151217_Cal_Info.xlsx",
                                                        "lastModifiedTimestamp" : 1495455123265
                                                      } ]
                                                    }, {
                                                      "@class" : ".XCalibration",
                                                      "name" : "CC_ptca0",
                                                      "calData" : [ {
                                                        "@class" : ".XCalibrationData",
                                                        "value" : 524250.7,
                                                        "comments" : None,
                                                        "eventId" : 28579,
                                                        "assetUid" : "CGINS-CTDMOH-13655",
                                                        "eventType" : "CALIBRATION_DATA",
                                                        "eventName" : "CC_ptca0",
                                                        "eventStartTime" : 1450310400000,
                                                        "eventStopTime" : None,
                                                        "notes" : None,
                                                        "tense" : "UNKNOWN",
                                                        "dataSource" : "CGINS-CTDMOH-13655__20151217_Cal_Info.xlsx",
                                                        "lastModifiedTimestamp" : 1495455123265
                                                      } ]
                                                    }, {
                                                      "@class" : ".XCalibration",
                                                      "name" : "CC_ptca2",
                                                      "calData" : [ {
                                                        "@class" : ".XCalibrationData",
                                                        "value" : 0.1338709,
                                                        "comments" : None,
                                                        "eventId" : 28581,
                                                        "assetUid" : "CGINS-CTDMOH-13655",
                                                        "eventType" : "CALIBRATION_DATA",
                                                        "eventName" : "CC_ptca2",
                                                        "eventStartTime" : 1450310400000,
                                                        "eventStopTime" : None,
                                                        "notes" : None,
                                                        "tense" : "UNKNOWN",
                                                        "dataSource" : "CGINS-CTDMOH-13655__20151217_Cal_Info.xlsx",
                                                        "lastModifiedTimestamp" : 1495455123265
                                                      } ]
                                                    } ],
                                                    "events" : [ ],
                                                    "assetId" : 344,
                                                    "remoteResources" : [ ],
                                                    "serialNumber" : "37-13655",
                                                    "name" : "37-13655",
                                                    "location" : None,
                                                    "owner" : None,
                                                    "description" : "CTD Mooring (Inductive): CTDMO Series H",
                                                    "manufacturer" : "Sea-Bird Electronics",
                                                    "notes" : None,
                                                    "uid" : "CGINS-CTDMOH-13655",
                                                    "editPhase" : "OPERATIONAL",
                                                    "physicalInfo" : {
                                                      "height" : -1.0,
                                                      "width" : -1.0,
                                                      "length" : -1.0,
                                                      "weight" : -1.0
                                                    },
                                                    "assetType" : "Sensor",
                                                    "mobile" : False,
                                                    "modelNumber" : "SBE 37-IM",
                                                    "purchasePrice" : 7000.0,
                                                    "purchaseDate" : 1435708800000,
                                                    "deliveryDate" : 1435708800000,
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
                                                    "lastModifiedTimestamp" : 1495455037605
                                                  },
                                                  "referenceDesignator" : "GS03FLMA-RIM01-02-CTDMOH051",
                                                  "editPhase" : "OPERATIONAL",
                                                  "deploymentNumber" : 2,
                                                  "versionNumber" : 1,
                                                  "mooring" : {
                                                    "@class" : ".XMooring",
                                                    "events" : [ ],
                                                    "assetId" : 191,
                                                    "remoteResources" : [ ],
                                                    "serialNumber" : "GS03FLMA-00002",
                                                    "name" : "GS03FLMA-00002",
                                                    "location" : None,
                                                    "owner" : None,
                                                    "description" : "Global Southern Ocean Flanking Subsurface Mooring A",
                                                    "manufacturer" : "WHOI",
                                                    "notes" : None,
                                                    "uid" : "CGMGS-03FLMA-00002",
                                                    "editPhase" : "OPERATIONAL",
                                                    "physicalInfo" : {
                                                      "height" : -1.0,
                                                      "width" : -1.0,
                                                      "length" : -1.0,
                                                      "weight" : -1.0
                                                    },
                                                    "assetType" : "Mooring",
                                                    "mobile" : False,
                                                    "modelNumber" : "GS03FLMA",
                                                    "purchasePrice" : 35611.94,
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
                                                    "lastModifiedTimestamp" : 1495455036550
                                                  },
                                                  "deployCruiseInfo" : {
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
                                                  "recoverCruiseInfo" : {
                                                    "@class" : ".CruiseInfo",
                                                    "uniqueCruiseIdentifier" : "NBP16-10",
                                                    "cruiseIdentifier" : None,
                                                    "shipName" : "R/V Nathaniel B. Palmer",
                                                    "editPhase" : "OPERATIONAL",
                                                    "eventId" : 61,
                                                    "assetUid" : None,
                                                    "eventType" : "CRUISE_INFO",
                                                    "eventName" : "NBP16-10",
                                                    "eventStartTime" : 1480032000000,
                                                    "eventStopTime" : 1481500800000,
                                                    "notes" : None,
                                                    "tense" : "UNKNOWN",
                                                    "dataSource" : "Load from [CruiseInformation.xlsx]",
                                                    "lastModifiedTimestamp" : 1495455035305
                                                  },
                                                  "deployedBy" : None,
                                                  "recoveredBy" : None,
                                                  "inductiveId" : None,
                                                  "waterDepth" : 4705.0,
                                                  "ingestInfo" : [ ],
                                                  "eventId" : 3744,
                                                  "assetUid" : None,
                                                  "eventType" : "DEPLOYMENT",
                                                  "eventName" : "GS03FLMA-RIM01-02-CTDMOH051",
                                                  "eventStartTime" : 1450381320000,
                                                  "eventStopTime" : 1480982400000,
                                                  "notes" : None,
                                                  "tense" : "UNKNOWN",
                                                  "dataSource" : "Load from [GS03FLMA_Deploy.xlsx]",
                                                  "lastModifiedTimestamp" : 1495455094570
                                                }]



                            }]

                    }

        ]

    return help_data
