# -*- coding: utf-8 -*-
# Module: Settings
# Author: asciidisco
# Created on: 24.07.2017
# License: MIT https://goo.gl/xF5sC4

"""Tests for the `Settings` module"""

import unittest
import mock
from resources.lib.Utils import Utils
from resources.lib.Dialogs import Dialogs
from resources.lib.Settings import Settings
from resources.lib.Constants import Constants
from resources.test.mocks.MockAddon import MockAddon
from resources.test.mocks.MockAddonDynamic import MockAddonDynamic
from resources.test.mocks.MockAddonEncrypted import MockAddonEncrypted


class SettingsTestCase(unittest.TestCase):
    """Tests for the `Settings` module"""

    @mock.patch('xbmc.getInfoLabel')
    def test___get_mac_address(self, mock_getInfoLabel):
        """ADD ME"""
        mock_getInfoLabel.return_value = '00:80:41:ae:fd:7e'
        settings = Settings(
            utils=Utils(constants=Constants(), kodi_base_url=''),
            dialogs=Dialogs(utils=Utils(constants=Constants(), kodi_base_url='')),
            constants=Constants())
        self.assertEqual(
            first=settings._Settings__get_mac_address(),
            second='00:80:41:ae:fd:7e')

    @mock.patch('xbmc.getInfoLabel')
    def test___get_mac_address_malformed(self, mock_getInfoLabel):
        """ADD ME"""
        mock_getInfoLabel.return_value = '00-80-41-ae-fd-7e'
        settings = Settings(
            utils=Utils(constants=Constants(), kodi_base_url=''),
            dialogs=Dialogs(utils=Utils(constants=Constants(), kodi_base_url='')),
            constants=Constants())
        self.assertEqual(
            first=settings._Settings__get_mac_address(),
            second='00-80-41-ae-fd-7e')

    @mock.patch('xbmcaddon.Addon')
    @mock.patch('xbmc.getInfoLabel')
    def test_set_credentials_unencrypted(self, mock_getInfoLabel, mock_xbmcaddon):
        """ADD ME"""
        mock_getInfoLabel.return_value = '00:80:41:ae:fd:7e'
        mock_xbmcaddon.return_value = MockAddonDynamic()
        settings = Settings(
            utils=Utils(constants=Constants(), kodi_base_url=''),
            dialogs=Dialogs(utils=Utils(constants=Constants(), kodi_base_url='')),
            constants=Constants())
        self.assertEqual(
            first=settings.set_credentials(),
            second=('', ''))

    @mock.patch('xbmcaddon.Addon')
    @mock.patch('xbmc.getInfoLabel')
    def test_set_credentials_encrypted(self, mock_getInfoLabel, mock_xbmcaddon):
        """ADD ME"""
        mock_getInfoLabel.return_value = '00:80:41:ae:fd:7e'
        mock_addon = MockAddonDynamic()
        mock_addon.setSetting('encrypt_credentials', 'True')
        mock_xbmcaddon.return_value = mock_addon
        settings = Settings(
            utils=Utils(constants=Constants(), kodi_base_url=''),
            dialogs=Dialogs(utils=Utils(constants=Constants(), kodi_base_url='')),
            constants=Constants())
        self.assertEqual(
            first=settings.set_credentials(),
            second=('', ''))

    @mock.patch('xbmcaddon.Addon')
    def test_get_credentials_plain(self, mock_xbmcaddon):
        """ADD ME"""
        mock_xbmcaddon.return_value = MockAddon()
        settings = Settings(
            utils=Utils(constants=Constants(), kodi_base_url=''),
            dialogs=Dialogs(utils=Utils(constants=Constants(), kodi_base_url='')),
            constants=Constants())
        self.assertEqual(
            first=settings.get_credentials(),
            second=('foo@bar.de', 'FooBar'))

    @mock.patch('xbmcaddon.Addon')
    @mock.patch('xbmc.getInfoLabel')
    def test_get_credentials_encrypted(self, mock_getInfoLabel, mock_xbmcaddon):
        """ADD ME"""
        mock_getInfoLabel.return_value = '00:80:41:ae:fd:7e'
        mock_xbmcaddon.return_value = MockAddonEncrypted()
        settings = Settings(
            utils=Utils(constants=Constants(), kodi_base_url=''),
            dialogs=Dialogs(utils=Utils(constants=Constants(), kodi_base_url='')),
            constants=Constants())
        self.assertEqual(
            first=settings.get_credentials(),
            second=('foo', 'foo'))

    @mock.patch('xbmc.getInfoLabel')
    def test_encode(self, mock_getInfoLabel):
        """ADD ME"""
        mock_getInfoLabel.return_value = '00:80:41:ae:fd:7e'
        settings = Settings(
            utils=Utils(constants=Constants(), kodi_base_url=''),
            dialogs=Dialogs(utils=Utils(constants=Constants(), kodi_base_url='')),
            constants=Constants())
        self.assertEqual(
            first=settings.encode('foo'),
            second='lvZxwZ4WVUo=')

    @mock.patch('xbmc.getInfoLabel')
    def test_decode(self, mock_getInfoLabel):
        """ADD ME"""
        mock_getInfoLabel.return_value = '00:80:41:ae:fd:7e'
        settings = Settings(
            utils=Utils(constants=Constants(), kodi_base_url=''),
            dialogs=Dialogs(utils=Utils(constants=Constants(), kodi_base_url='')),
            constants=Constants())
        self.assertEqual(
            first=settings.decode('lvZxwZ4WVUo='),
            second='foo')

    @mock.patch('xbmcaddon.Addon')
    def test_has_credentials(self, mock_xbmcaddon):
        """ADD ME"""
        mock_xbmcaddon.return_value = MockAddon()
        settings = Settings(
            utils=Utils(constants=Constants(), kodi_base_url=''),
            dialogs=Dialogs(utils=Utils(constants=Constants(), kodi_base_url='')),
            constants=Constants())
        self.assertTrue(
            expr=settings.has_credentials())

    @mock.patch('xbmcaddon.Addon')
    def test_uniq_id(self, mock_xbmcaddon):
        """ADD ME"""
        mock_xbmcaddon.return_value = MockAddon()
        settings = Settings(
            utils=Utils(constants=Constants(), kodi_base_url=''),
            dialogs=Dialogs(utils=Utils(constants=Constants(), kodi_base_url='')),
            constants=Constants())
        self.assertEquals(
            first=settings.uniq_id(delay=1),
            second='UnsafeStaticSecret')
