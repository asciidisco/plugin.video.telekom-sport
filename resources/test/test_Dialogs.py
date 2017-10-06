# -*- coding: utf-8 -*-
# Module: Dialogs
# Author: asciidisco
# Created on: 24.07.2017
# License: MIT https://goo.gl/xF5sC4

"""Tests for the `Dialogs` module"""

import unittest
import mock
from resources.lib.Utils import Utils
from resources.lib.Dialogs import Dialogs
from resources.lib.Constants import Constants

class DialogsTestCase(unittest.TestCase):
    """Tests for the `Dialogs` module"""

    def test_show_password_dialog(self):
        """ADD ME"""
        dialogs = Dialogs(utils=Utils(constants=Constants(), kodi_base_url=''))
        self.assertEqual(dialogs.show_password_dialog(), '')

    def test_show_email_dialog(self):
        """ADD ME"""
        dialogs = Dialogs(utils=Utils(constants=Constants(), kodi_base_url=''))
        self.assertEqual(dialogs.show_email_dialog(), '')

    def test_show_not_available_dialog(self):
        """ADD ME"""
        dialogs = Dialogs(utils=Utils(constants=Constants(), kodi_base_url=''))
        self.assertTrue(dialogs.show_not_available_dialog())

    def test_show_login_failed_notification(self):
        """ADD ME"""
        dialogs = Dialogs(utils=Utils(constants=Constants(), kodi_base_url=''))
        self.assertIsNone(dialogs.show_login_failed_notification())

    def test_show_storing_credentials_failed(self):
        """ADD ME"""
        dialogs = Dialogs(utils=Utils(constants=Constants(), kodi_base_url=''))
        self.assertIsNone(dialogs.show_storing_credentials_failed())
