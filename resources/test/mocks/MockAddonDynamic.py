# -*- coding: utf-8 -*-
# Module: MockAddon
# Author: asciidisco
# Created on: 24.07.2017
# License: MIT https://goo.gl/xF5sC4

"""Mock for Kodi Addon instance"""


class MockAddonDynamic(object):
    """Mock for Kodi Addon instance"""

    def __init__(self):
        """ADD ME"""
        self._data = {}

    def setSetting(self, name, value):
        """ADD ME"""
        self._data[name] = value

    def getSetting(self, name):
        """ADD ME"""
        return self._data.get(name)

    @classmethod
    def getLocalizedString(cls, a):
        """ADD ME"""
        return 'Foo'.encode('utf-8')

    @classmethod
    def getAddonInfo(cls, a):
        """ADD ME"""
        return 'a'
