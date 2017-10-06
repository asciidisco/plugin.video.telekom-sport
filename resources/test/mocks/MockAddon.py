# -*- coding: utf-8 -*-
# Module: MockAddon
# Author: asciidisco
# Created on: 24.07.2017
# License: MIT https://goo.gl/xF5sC4

"""Mock for Kodi Addon instance"""


class MockAddon(object):
    """Mock for Kodi Addon instance"""

    @classmethod
    def getSetting(cls, name):
        """ADD ME"""
        if name == 'use_inputstream':
            return 'false'
        if name == 'email':
            return 'foo@bar.de'
        if name == 'password':
            return 'FooBar'

    @classmethod
    def getLocalizedString(cls, a):
        """ADD ME"""
        return 'Foo'.encode('utf-8')

    @classmethod
    def getAddonInfo(cls, a):
        """ADD ME"""
        return 'a'
