#!/usr/bin/env python


def get_help_data_12587_asset():
    """
    Asset Management help - Category asset
    Data store of information to be presented when a help request is made for port 12587.
    Returns a list of dictionaries associated with various requests supported on that port.

    Note: Parameter serialnumber should be removed and/or deprecated as it is not supported on uframe
    or simply note working on uframe. (It is shown in the help right now.)
    """
    help_data = [
                    {
                        'category': 'asset',
                        'root': 'asset',
                        'endpoint': 'asset',
                        'method': 'GET',
                        'permission_required': False,
                        'description': 'Get all asset records.',
                        'data_required': False,
                        'data_format': None,
                        'sample_request': 'asset',
                        'sample_response': None
                    },
                    {
                        'category': 'asset',
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
                    },
                    {
                        'category': 'asset',
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
                    },
                    {
                        'category': 'asset',
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
