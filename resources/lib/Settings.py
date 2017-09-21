# -*- coding: utf-8 -*-
# Module: Utils
# Author: asciidisco
# Created on: 24.07.2017
# License: MIT https://goo.gl/xF5sC4

"""ADD ME"""

import base64
import uuid
import time
import xbmc
import pyDes


class Settings(object):
    """ADD ME"""

    def __init__(self, utils, dialogs, constants):
        """ADD ME"""
        self.utils = utils
        self.dialogs = dialogs
        self.constants = constants
        self.addon_id = self.constants.get_addon_id()

    def uniq_id(self, delay=1):
        """ADD ME"""
        mac_addr = self.__get_mac_address(delay=delay)
        if ':' in mac_addr and delay == 2:
            return uuid.uuid5(uuid.NAMESPACE_DNS, str(mac_addr)).bytes
        else:
            error_msg = '[%s] error: failed to get device id (%s)'
            self.utils.log(error_msg % (self.addon_id, str(mac_addr)))
            self.dialogs.show_storing_credentials_failed()
            return False

    def encode(self, data):
        """ADD ME"""
        key_handle = pyDes.triple_des(
            key=self.uniq_id(delay=2),
            mode=pyDes.CBC,
            pad='\0\0\0\0\0\0\0\0',
            padmode=pyDes.PAD_PKCS5)
        encrypted = key_handle.encrypt(
            data=data)
        return base64.b64encode(s=encrypted)

    def decode(self, data):
        """ADD ME"""
        key_handle = pyDes.triple_des(
            key=self.uniq_id(delay=2),
            mode=pyDes.CBC,
            pad='\0\0\0\0\0\0\0\0',
            padmode=pyDes.PAD_PKCS5)
        decrypted = key_handle.decrypt(
            data=base64.b64decode(s=data))
        return decrypted

    def has_credentials(self):
        """ADD ME"""
        addon = self.utils.get_addon()
        user = addon.getSetting('email')
        password = addon.getSetting('password')
        return user != '' or password != ''

    def set_credentials(self):
        """ADD ME"""
        addon = self.utils.get_addon()
        user = self.dialogs.show_email_dialog()
        password = self.dialogs.show_password_dialog()
        addon.setSetting('email', self.encode(user))
        addon.setSetting('password', self.encode(password))
        return (user, password)

    def get_credentials(self):
        """ADD ME"""
        addon = self.utils.get_addon()
        user = addon.getSetting('email')
        password = addon.getSetting('password')
        return (self.decode(user), self.decode(password))

    @classmethod
    def __get_mac_address(cls, delay):
        """ADD ME"""
        mac_addr = xbmc.getInfoLabel('Network.MacAddress')
        # hack response busy
        i = 0
        while ':' not in mac_addr and i < 3:
            i += 1
            time.sleep(delay)
            mac_addr = xbmc.getInfoLabel('Network.MacAddress')
        return mac_addr
