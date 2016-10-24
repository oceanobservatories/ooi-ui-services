#!/usr/bin/env python

"""
Asset Management - Assets: Support for cache related functions.
"""
__author__ = 'Edna Donoughe'

from flask import current_app
from ooiservices.app import cache
from ooiservices.app.uframe.toc_tools import _compile_asset_rds
from ooiservices.app.uframe.common_tools import (is_instrument, is_platform, is_mooring)
from ooiservices.app.uframe.deployment_tools import _compile_rd_assets
from copy import deepcopy
CACHE_TIMEOUT = 172800


def _get_rd_assets():
    """ Get 'rd_assets', if not available get and set cache; return 'rd_assets' dictionary.
    """
    rd_assets = {}
    try:
        # Get 'rd_assets' if cached
        rd_assets_cached = cache.get('rd_assets')
        if rd_assets_cached:
            rd_assets = rd_assets_cached
        # Get 'rd_assets' - compile them
        else:
            try:
                rd_assets = _compile_rd_assets()
            except Exception as err:
                message = 'Error processing _compile_rd_assets: ', err.message
                current_app.logger.warning(message)
            # Cache rd_assets
            if rd_assets:
                cache.set('rd_assets', rd_assets, timeout=CACHE_TIMEOUT)
        return rd_assets

    except Exception as err:
        message = 'Exception processing _get_rd_assets: %s' % str(err)
        current_app.logger.info(message)
        return {}


def get_asset_deployment_data(rd):
    """ Get deployment specific information for a reference designator. Returns dictionary from cache.
    """
    result = {}
    try:
        # Validate reference designator
        if not is_instrument(rd) and not is_mooring(rd) and not is_platform(rd):
            message = 'The reference designator provided (%s) is not a mooring, platform, or instrument.' % rd
            message += 'unable to provide asset deployment info.'
            raise Exception(message)

        # Verify rd_assets cache available, if raise exception.
        rd_assets = _get_rd_assets()
        if not rd_assets:
            message = 'The \'rd_assets\' cache is empty; unable to provide asset deployment info for %s.' % rd
            print '\n Error: ', message
            raise Exception(message)

        # Get information required from rd_assets.
        if rd in rd_assets:
            result = rd_assets[rd]
        return result

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return {}


def get_asset_deployment_info(asset_id, rd):
    """ Use rd to fetch dict from 'rd_assets' cache. Process dict and create result info. On error, log and return {}.

    The result dict value returned is described in get_asset_deployment_detail function.
    """
    result = {}
    try:
        # Get asset and deployment data for reference designator.
        data = get_asset_deployment_data(rd)

        # If data is returned, process into result and return. On error, log and return empty dict {}.
        if data:
            # Get specific info for asset id from data
            result = get_asset_deployment_detail(asset_id, data, rd)

        return result

    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return {}


def get_asset_deployment_detail(id, data, rd=None):
    """ Using deployment info in data, process and return specific details. (Only instruments)
    {
        "deployments": [4,3,2,1],
        "current_deployment": 4,
        # Multiple entries as follows, one for each deployment in 'deployments' list #
        "4": {
              "asset_ids": [
                1799,
                3085,
                3628
              ],
              "asset_ids_by_type": {
                "mooring": [
                  3085
                ],
                "node": [
                  3628
                ],
                "sensor": [
                  1799
                ]
              },
              "beginDT": 1439850000000,
              "endDT": null,
              "location": {
                "depth": 0.0,
                "latitude": 44.65602,
                "location": [
                  -124.09524,
                  44.65602
                ],
                "longitude": -124.09524,
                "orbitRadius": 0.0
              }
            }
    }

    """
    try:
        # Determine if asset_id in data['asset_ids'], if not log and return empty dict.
        if id not in data['asset_ids']:
            if rd is not None:
                message = 'Unable to find asset id %s for %s in rd_assets entry.' % (str(id), rd)
            else:
                message = 'Unable to find asset id %s in rd_assets entry.' % str(id)
            raise Exception(message)
        result = data.copy()
        del result['asset_ids']
        del result['asset_ids_by_type']
        return result
    except Exception as err:
        message = str(err)
        print '\tNote: %s' % message
        #current_app.logger.info(message)
        return {}


def get_rd_from_rd_assets(rd):
    result = None
    try:
        # Determine if deployment events are available for this reference designator.
        rd_assets = cache.get('rd_assets')
        if not rd_assets:
            return result
        if rd not in rd_assets:
            return result

        # Get all deployment maps for reference designator
        result = rd_assets[rd]
        return result
    except Exception as err:
        message = str(err)
        raise Exception(message)


def get_asset_rds_cache():
    asset_rds = None
    try:
        cached = cache.get('asset_rds')
        if cached:
            asset_rds = cached
        else:
            try:
                asset_rds, rds_wo_assets = _compile_asset_rds()
            except Exception as err:
                message = 'Error processing _compile_asset_rds: ', err.message
                raise Exception(message)
            # Cache rd_assets
            if asset_rds:
                cache.set('asset_rds', asset_rds, timeout=CACHE_TIMEOUT)
        return asset_rds

    except Exception as err:
        message = str(err)
        raise Exception(message)


def asset_rds_cache_update(dict_asset_ids):
    if dict_asset_ids:
        cache.set('asset_rds', dict_asset_ids, timeout=CACHE_TIMEOUT)


def refresh_asset_cache(id, asset, action, remote_id=None):
    """ Perform asset cache add or update depending on action provided.
    """
    try:
        if action == 'create':
            asset_cache_add(id, asset)
        elif action == 'update':
            update_asset_cache(id, asset, remote_id)
        else:
            message = 'Failed to refresh asset cache, unknown action(\'%s\').' % action
            raise Exception(message)
    except Exception as err:
        message = str(err)
        raise Exception(message)


def update_asset_cache(id, asset, remote_id=None):
    """ Update an asset stored in cache.
    """
    try:
        # Update asset cache ('asset_list')
        asset_cache = cache.get('asset_list')
        if asset_cache:
            found_asset = False
            for item in asset_cache:
                if item['id'] == id:
                    item.update(asset)
                    found_asset = True
                    break

            if found_asset:
                #cache.delete('asset_list')
                cache.set('asset_list', asset_cache, timeout=CACHE_TIMEOUT)

                # Update assets_dict cache ('assets_dict')
                assets_dict_cache = cache.get('assets_dict')
                if assets_dict_cache:
                    if id in assets_dict_cache:
                        assets_dict_cache[id] = deepcopy(asset)
                        cache.set('assets_dict', assets_dict_cache, timeout=CACHE_TIMEOUT)

        return
    except Exception as err:
        message = str(err)
        raise Exception(message)


def asset_cache_add(id, asset):
    """ Add an asset to asset_list and assets_dict cache.
    """
    try:
        # Add asset to asset cache ('asset_list')
        asset_cache = cache.get('asset_list')
        add_success = False
        if asset_cache:
            asset_list = asset_cache
            if isinstance(asset_list, list):
                found_asset = False
                for item in asset_cache:
                    if item['id'] == id:
                        del item
                        found_asset = True
                        break
                if found_asset:
                    message = '[asset_cache_add] asset already in cache, cannot create (use update).'
                    raise Exception(message)
                asset_list.append(asset)
                cache.set('asset_list', asset_list, timeout=CACHE_TIMEOUT)
                asset_cache = cache.get('asset_list')
                if asset_cache:
                    if len(asset_cache) == len(asset_list):
                        add_success = True

        if add_success:
            # Add asset to assets_dict cache ('assets_dict')
            assets_dict_cache = cache.get('assets_dict')
            if assets_dict_cache:
                if id not in assets_dict_cache:
                    assets_dict_cache[id] = asset
                    cache.set('assets_dict', assets_dict_cache, timeout=CACHE_TIMEOUT)
    except Exception as err:
        message = str(err)
        raise Exception(message)


def asset_cache_refresh(id, asset, rd):
    """ Add an asset to asset_list and assets_dict cache.
    """
    try:
        # Add asset to asset cache ('asset_list')
        asset_cache = cache.get('asset_list')
        add_success = False
        if asset_cache:
            asset_list = asset_cache
            if isinstance(asset_list, list):
                found_asset = False

                # If in cache, update asset in 'asset_list' cache.
                for item in asset_cache:
                    if item['id'] == id:
                        #del item
                        #------------
                        # update asset in 'asset_list' cache.
                        item.update(asset)
                        cache.set('asset_list', asset_cache, timeout=CACHE_TIMEOUT)

                        # Update assets_dict cache ('assets_dict')
                        assets_dict_cache = cache.get('assets_dict')
                        if assets_dict_cache:
                            if id in assets_dict_cache:
                                assets_dict_cache[id] = deepcopy(asset)
                                cache.set('assets_dict', assets_dict_cache, timeout=CACHE_TIMEOUT)
                        #------------
                        found_asset = True
                        break

                # If not in cache, add asset to cache.
                if not found_asset:
                    asset_list.append(asset)
                    cache.set('asset_list', asset_list, timeout=CACHE_TIMEOUT)
                    asset_cache = cache.get('asset_list')
                    if asset_cache:
                        if len(asset_cache) == len(asset_list):
                            add_success = True

                    if add_success:
                        # Add asset to assets_dict cache ('assets_dict')
                        assets_dict_cache = cache.get('assets_dict')
                        if assets_dict_cache:
                            assets_dict_cache[id] = asset
                            cache.set('assets_dict', assets_dict_cache, timeout=CACHE_TIMEOUT)

                        # Update cache 'asset_rds'.
                        cached = cache.get('asset_rds')
                        if cached:
                            asset_rds = cached
                            asset_rds[id] = rd
                            cache.set('asset_rds', asset_rds, timeout=CACHE_TIMEOUT)

        return

    except Exception as err:
        message = str(err)
        raise Exception(message)