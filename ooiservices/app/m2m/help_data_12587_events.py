#!/usr/bin/env python


def get_help_data_12587_events():
    """
    Asset Management help - Category asset
    Data store of information to be presented when a help request is made for port 12587.
    Returns a list of dictionaries associated with various requests supported on that port.

    Note: Parameter serialnumber should be removed and/or deprecated as it is not supported on uframe
    or simply note working on uframe. (It is shown in the help right now.)
    """
    help_data = [
                    {
                        'category': 'events',
                        'root': 'events',
                        'endpoint': 'events',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Get all events.',
                        'data_required': False,
                        'data_format': None,
                        'sample_request': 'asset',
                        'sample_response': None
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
                    },
                    {
                        'category': 'events',
                        'root': 'events',
                        'endpoint': 'events',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Get events for an asset given its unique identifier (uid). ',
                        'data_required': True,
                        'data_format': [
                                { 'name': 'uid',
                                  'type': 'str',
                                  'description': 'The asset unique identifier (uid).',
                                  'valid_values': None,
                                  'default': None
                                }
                        ],
                        'sample_request': 'asset?uid=1',
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
                    },
                    {
                        'category': 'asset',
                        'root': 'asset',
                        'endpoint': 'asset',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Retrieve information for an asset given its unique identifier (UID). ',
                        'data_required': True,
                        'data_format': [
                                { 'name': 'uid',
                                  'type': 'str',
                                  'description': 'The asset unique identifier (uid).',
                                  'valid_values': None,
                                  'default': None
                                }
                        ],
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
                    },
                    {
                        'category': 'asset',
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
                    }

                ]
    return help_data
