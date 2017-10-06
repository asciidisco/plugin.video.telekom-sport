# -*- coding: utf-8 -*-
# Module: Cache
# Author: asciidisco
# Created on: 24.07.2017
# License: MIT https://goo.gl/WA1kby

"""Caching facade for KODIs window API"""

try:
    import cPickle as pickle
except ImportError:
    import pickle
import xbmcgui


class Cache(object):
    """Caching facade for KODIs window API"""

    def __init__(self):
        """Setup in memory cache & stores window instance in memory"""
        self.setup_memcache()

    def setup_memcache(self):
        """Setup in memory cache"""
        window = self.__get_window_instance()
        try:
            cached_items = pickle.loads(window.getProperty('memcache'))
        except EOFError:
            cached_items = {}
        if len(cached_items) < 1:
            window.setProperty('memcache', pickle.dumps({}))
        return cached_items

    def has_cached_item(self, cache_id):
        """
        Checks if an item exists in the mem cache

        :param cache_id: ID of the cached item
        :type cache_id: str.
        :returns:  bool -- Matching item found
        """
        window = self.__get_window_instance()
        cached_items = pickle.loads(window.getProperty('memcache'))
        return cache_id in cached_items.keys()

    def get_cached_item(self, cache_id):
        """
        Returns a cached item

        :param cache_id: ID of the cached item
        :type cache_id: str.
        :returns:  mixed -- Cached item
        """
        window = self.__get_window_instance()
        cached_items = pickle.loads(window.getProperty('memcache'))
        if self.has_cached_item(cache_id) is not True:
            return None
        return cached_items[cache_id]

    def add_cached_item(self, cache_id, contents):
        """
        Adds an item to the cache

        :param cache_id: ID of the item to be cached
        :type cache_id: str.
        :param contents: Contents to be cached
        :type contents: mixed
        """
        window = self.__get_window_instance()
        cached_items = pickle.loads(window.getProperty('memcache'))
        cached_items.update({cache_id: contents})
        window.setProperty('memcache', pickle.dumps(cached_items))

    @classmethod
    def __get_window_instance(cls):
        """
        Returns the current window instance from KODI

        :returns: xmbcguiWindow -- Window instance
        """
        return xbmcgui.Window(xbmcgui.getCurrentWindowId())
