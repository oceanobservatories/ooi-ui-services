#!/usr/bin/env python

"""
Asset Management - Assets: Support functions for asset cache.
"""
__author__ = 'Edna Donoughe'

from flask import current_app
from ooiservices.app.uframe.config import get_cache_timeout
from ooiservices.app import cache
from copy import deepcopy
#CACHE_TIMEOUT = 172800


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
                cache.set('asset_list', asset_cache, timeout=get_cache_timeout())

                # Update assets_dict cache ('assets_dict')
                assets_dict_cache = cache.get('assets_dict')
                if assets_dict_cache:
                    if id in assets_dict_cache:
                        assets_dict_cache[id] = deepcopy(asset)
                        cache.set('assets_dict', assets_dict_cache, timeout=get_cache_timeout())

        return
    except Exception as err:
        message = str(err)
        raise Exception(message)

def get_assets_dict():
    try:
        assets_dict = cache.get('assets_dict')
        return assets_dict
    except:
        return None


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
                cache.set('asset_list', asset_list, timeout=get_cache_timeout())
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
                    cache.set('assets_dict', assets_dict_cache, timeout=get_cache_timeout())
    except Exception as err:
        message = str(err)
        raise Exception(message)


def asset_cache_refresh(id, asset, rd):
    """ Update asset cache.
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

                        #------------
                        # update asset in 'asset_list' cache.
                        item.update(asset)
                        cache.set('asset_list', asset_cache, timeout=get_cache_timeout())

                        # Update assets_dict cache ('assets_dict')
                        assets_dict_cache = cache.get('assets_dict')
                        if assets_dict_cache:
                            if id in assets_dict_cache:
                                assets_dict_cache[id] = deepcopy(asset)
                                cache.set('assets_dict', assets_dict_cache, timeout=get_cache_timeout())
                        #------------
                        found_asset = True
                        break

                # If not in cache, add asset to cache.
                if not found_asset:
                    asset_list.append(asset)
                    cache.set('asset_list', asset_list, timeout=get_cache_timeout())
                    asset_cache = cache.get('asset_list')
                    if asset_cache:
                        if len(asset_cache) == len(asset_list):
                            add_success = True

                    if add_success:
                        # Add asset to assets_dict cache ('assets_dict')
                        assets_dict_cache = cache.get('assets_dict')
                        if assets_dict_cache:
                            assets_dict_cache[id] = asset
                            cache.set('assets_dict', assets_dict_cache, timeout=get_cache_timeout())

        return
    except Exception as err:
        message = str(err)
        raise Exception(message)


def get_asset_list_cache():
    """ Get 'asset_list' cache.
    """
    try:
        asset_list = cache.get('asset_list')
        if not asset_list or asset_list is None:
            message = 'Failed to get value for asset_list cache.'
            raise Exception(message)

        return asset_list
    except Exception as err:
        message = str(err)
        current_app.logger.info(message)
        return None


