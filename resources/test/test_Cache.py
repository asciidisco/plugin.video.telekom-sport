# -*- coding: utf-8 -*-
# Module: Cache
# Author: asciidisco
# Created on: 24.07.2017
# License: MIT https://goo.gl/xF5sC4

"""Tests for the `Cache` module"""

import unittest
import mock
from resources.lib.Cache import Cache
from resources.test.mocks.MockWindow import MockWindow
from resources.test.mocks.MockWindowException import MockWindowException

class CacheTestCase(unittest.TestCase):
    """Tests for the `Cache` module"""

    @mock.patch('xbmcgui.Window')
    def test_has_cached_item(self, mock_window):
        """ADD ME"""
        mock_window.return_value = MockWindow()
        cache = Cache()
        cache.setup_memcache()
        self.assertFalse(cache.has_cached_item('foo'))

    @mock.patch('xbmcgui.Window')
    def test_get_cached_item(self, mock_window):
        """ADD ME"""
        mock_window.return_value = MockWindow()
        cache = Cache()
        cache.setup_memcache()
        self.assertIsNone(cache.get_cached_item('foo'))

    @mock.patch('xbmcgui.Window')
    def test_get_cached_item(self, mock_window):
        """ADD ME"""
        mock_window.return_value = MockWindow()
        cache = Cache()
        cache.setup_memcache()
        self.assertIsNone(cache.get_cached_item('foo'))

    @mock.patch('xbmcgui.Window')
    def test_add_cached_item(self, mock_window):
        """ADD ME"""
        mock_window.return_value = MockWindow()
        cache = Cache()
        cache.setup_memcache()
        self.assertIsNone(cache.add_cached_item('foo', 'bar'))
        self.assertEquals(cache.get_cached_item('foo'), 'bar')

    @mock.patch('xbmcgui.Window')
    def test_setup_memcache(self, mock_window):
        """ADD ME"""
        mock_window.return_value = MockWindow()
        cache = Cache()
        cache.setup_memcache()
        self.assertIsNone(cache.add_cached_item('foo', 'bar'))
        cache.setup_memcache()
        self.assertEquals(cache.get_cached_item('foo'), 'bar')

    @mock.patch('xbmcgui.Window')
    def test_setup_memcache_erro(self, mock_window):
        """ADD ME"""
        mock_window.return_value = MockWindowException()
        cache = Cache()
        self.assertEquals(cache.setup_memcache(), {})
