# -*- coding: utf-8 -*-
# Module: Utils
# Author: asciidisco
# Created on: 24.07.2017
# License: MIT https://goo.gl/WA1kby

"""ADD ME"""

import xbmcgui


class Dialogs(object):
    """ADD ME"""

    def __init__(self, utils):
        """ADD ME"""
        self.utils = utils

    def show_password_dialog(self):
        """ADD ME"""
        dlg = xbmcgui.Dialog()
        return dlg.input(
            self.utils.get_local_string(string_id=32004),
            type=xbmcgui.INPUT_ALPHANUM,
            option=xbmcgui.ALPHANUM_HIDE_INPUT)

    def show_email_dialog(self):
        """ADD ME"""
        dlg = xbmcgui.Dialog()
        return dlg.input(
            self.utils.get_local_string(string_id=32005),
            type=xbmcgui.INPUT_ALPHANUM)

    def show_not_available_dialog(self):
        """ADD ME"""
        addon_data = self.utils.get_addon_data()
        dlg = xbmcgui.Dialog()
        return dlg.ok(
            addon_data.get('plugin'),
            self.utils.get_local_string(string_id=32009))

    def show_login_failed_notification(self):
        """ADD ME"""
        dialog = xbmcgui.Dialog()
        dialog.notification(
            self.utils.get_local_string(string_id=32006),
            self.utils.get_local_string(string_id=32007),
            xbmcgui.NOTIFICATION_ERROR, 5000)

    def show_storing_credentials_failed(self):
        """ADD ME"""
        dialog = xbmcgui.Dialog()
        dialog.ok(
            self.utils.get_addon_data().get('plugin'),
            self.utils.get_local_string(32008))
