# -*- coding: utf-8 -*-
# Module: MockAddon
# Author: asciidisco
# Created on: 24.07.2017
# License: MIT https://goo.gl/xF5sC4

"""Mock for Kodi Addon instance (Encrypted credentials)"""


class MockAddonEncrypted(object):
    """Mock for Kodi Addon instance (Encrypted credentials)"""

    @classmethod
    def getSetting(cls, name):
        """ADD ME"""
        if name == 'email':
            return 'lvZxwZ4WVUo='
        if name == 'password':
            return 'lvZxwZ4WVUo='

    @classmethod
    def getLocalizedString(cls, a):
        """ADD ME"""
        return 'Foo'.encode('utf-8')

    @classmethod
    def getAddonInfo(cls, a):
        """ADD ME"""
        return 'a'
