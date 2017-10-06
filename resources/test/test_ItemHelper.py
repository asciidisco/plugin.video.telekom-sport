# -*- coding: utf-8 -*-
# Module: ItemHelper
# Author: asciidisco
# Created on: 24.07.2017
# License: MIT https://goo.gl/xF5sC4

"""Tests for the `ItemHelper` module"""

import unittest
from resources.lib.Utils import Utils
from resources.lib.Constants import Constants
from resources.lib.ItemHelper import ItemHelper

class ItemHelperTestCase(unittest.TestCase):
    """Tests for the `ItemHelper` module"""

    def test_build_description_empty_item(self):
        """ADD ME"""
        item_helper = ItemHelper(
            constants=Constants(),
            utils=Utils(constants=Constants(), kodi_base_url=''))
        item = {}
        self.assertEqual(item_helper.build_description(item=item), ' ')

    def test_build_description_empty_bold_desc(self):
        """ADD ME"""
        item_helper = ItemHelper(
            constants=Constants(),
            utils=Utils(constants=Constants(), kodi_base_url=''))
        item = {'metadata': {'description_bold': 'Foo'}}
        self.assertEqual(item_helper.build_description(item=item), 'Foo :\nFoo ')

    def test_build_description_empty_reg_desc(self):
        """ADD ME"""
        item_helper = ItemHelper(
            constants=Constants(),
            utils=Utils(constants=Constants(), kodi_base_url=''))
        item = {'metadata': {'description_regular': 'Foo'}}
        self.assertEqual(item_helper.build_description(item=item), 'Foo:\nFoo ')

    def test_build_description_empty_boldreg_desc(self):
        """ADD ME"""
        item_helper = ItemHelper(
            constants=Constants(),
            utils=Utils(constants=Constants(), kodi_base_url=''))
        item = {'metadata': {'description_bold': 'Bar', 'description_regular': 'Foo'}}
        self.assertEqual(item_helper.build_description(item=item), 'Bar - Foo:\nFoo ')

    def test_build_epg_title(self):
        """ADD ME"""
        item_helper = ItemHelper(
            constants=Constants(),
            utils=Utils(constants=Constants(), kodi_base_url=''))
        item = {'home': {'name_full': 'foo'}, 'away': {'name_full': 'bar'}}
        self.assertEqual(item_helper.build_epg_title(details=item, match_time='12:00'), 'foo - bar (12:00 Uhr)')

    def test___build_match_title_short(self):
        """ADD ME"""
        item_helper = ItemHelper(
            constants=Constants(),
            utils=Utils(constants=Constants(), kodi_base_url=''))
        item = {'home': {'name_short': 'foo'}, 'away': {'name_short': 'bar'}}
        self.assertEqual(item_helper._ItemHelper__build_match_title_short(details=item), 'foo - bar')

    def test___build_match_title_full(self):
        """ADD ME"""
        item_helper = ItemHelper(
            constants=Constants(),
            utils=Utils(constants=Constants(), kodi_base_url=''))
        item = {'home': {'name_full': 'foo'}, 'away': {'name_full': 'bar'}}
        self.assertEqual(item_helper._ItemHelper__build_match_title_full(details=item), 'foo - bar')

    def test_datetime_from_utc(self):
        """ADD ME"""
        item_helper = ItemHelper(
            constants=Constants(),
            utils=Utils(constants=Constants(), kodi_base_url=''))
        item = {'scheduled_start': {'date': '1507232762'}}
        datetime = item_helper.datetime_from_utc(metadata=item)
        self.assertEqual(datetime[0], '05.10.2017')
        self.assertIn(':46', datetime[1])

    def test_datetime_from_utc_element(self):
        """ADD ME"""
        item_helper = ItemHelper(
            constants=Constants(),
            utils=Utils(constants=Constants(), kodi_base_url=''))
        item = {}
        element = {'scheduled_start': {'date': '1507232762'}}
        datetime = item_helper.datetime_from_utc(metadata=item, element=element)
        self.assertEqual(datetime[0], '05.10.2017')
        self.assertIn(':46', datetime[1])

    def test_datetime_from_utc_element_none(self):
        """ADD ME"""
        item_helper = ItemHelper(
            constants=Constants(),
            utils=Utils(constants=Constants(), kodi_base_url=''))
        item = {}
        element = None
        self.assertEqual(item_helper.datetime_from_utc(metadata=item, element=element), (None, None))

    def test___build_fallback_title(self):
        """ADD ME"""
        item_helper = ItemHelper(
            constants=Constants(),
            utils=Utils(constants=Constants(), kodi_base_url=''))
        item = {}
        element = None
        self.assertEqual(item_helper._ItemHelper__build_fallback_title(title='foo', metadata=item), 'foo')

    def test___build_fallback_title_fallback(self):
        """ADD ME"""
        item_helper = ItemHelper(
            constants=Constants(),
            utils=Utils(constants=Constants(), kodi_base_url=''))
        item = {'title': 'foo'}
        element = None
        self.assertEqual(item_helper._ItemHelper__build_fallback_title(title='', metadata=item), 'foo')
