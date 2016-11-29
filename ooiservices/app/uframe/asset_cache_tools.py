#!/usr/bin/env python

"""
Asset Management - Assets: Support functions for asset cache.
"""
__author__ = 'Edna Donoughe'


from ooiservices.app import cache
from ooiservices.app.uframe.toc_tools import _compile_asset_rds
from copy import deepcopy
import datetime as dt
CACHE_TIMEOUT = 172800


# Get assets_rd cache for asset reference designators.
def get_asset_rds_cache():
    asset_rds = None
    time = True
    try:
        asset_rds_cached = cache.get('asset_rds')
        if asset_rds_cached:
            asset_rds = asset_rds_cached
        elif not asset_rds_cached or asset_rds_cached is None:
            try:
                if time:
                    print '\nCompiling asset reference designators...'
                    asset_rds_start = dt.datetime.now()
                    print '\t-- Start time: ', asset_rds_start
                asset_rds, rds_wo_assets = _compile_asset_rds()
                if time:
                    asset_rds_end = dt.datetime.now()
                    print '\t-- End time: ', asset_rds_end
                    print '\t-- Time to get asset reference designators: %s' % str(asset_rds_end - asset_rds_start)
                    print 'Completed compiling asset reference designators...'
            except Exception as err:
                message = 'Error processing _compile_asset_rds: ', err.message
                raise Exception(message)
            # Cache asset_rds
            if not asset_rds or asset_rds is None:
                message = 'Unable to process uframe assets; error creating asset_rds.'
                raise Exception(message)
            #if asset_rds and asset_rds is not None:
            cache.set('asset_rds', asset_rds, timeout=CACHE_TIMEOUT)
        return asset_rds
    except Exception as err:
        message = str(err)
        raise Exception(message)

# Update asset reference designator cache.
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