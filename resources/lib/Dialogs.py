# -*- coding: utf-8 -*-
# Module: Utils
# Author: asciidisco
# Created on: 24.07.2017
# License: MIT https://goo.gl/WA1kby


"""Displays localized dialogs for Kodi"""

import xbmcgui


class Dialogs(object):
    """Displays localized dialogs for Kodi"""

    def __init__(self, utils):
        """Injects the utils instance

        :param utils: Plugin utils
        :type utils: resources.lib.Utils
        """
        self.utils = utils

    def show_password_dialog(self):
        """
        Shows password input

        :returns:  string - Password characters
        """
        dlg = xbmcgui.Dialog()
        return dlg.input(
            self.utils.get_local_string(string_id=32004),
            type=xbmcgui.INPUT_ALPHANUM,
            option=xbmcgui.ALPHANUM_HIDE_INPUT)

    def show_email_dialog(self):
        """
        Shows email input

        :returns:  string - Email characters
        """
        dlg = xbmcgui.Dialog()
        return dlg.input(
            self.utils.get_local_string(string_id=32005),
            type=xbmcgui.INPUT_ALPHANUM)

    def show_not_available_dialog(self):
        """
        Shows "video not playable/available" modal

        :returns:  bool - Dialog shown
        """
        addon_data = self.utils.get_addon_data()
        dlg = xbmcgui.Dialog()
        return dlg.ok(
            addon_data.get('plugin'),
            self.utils.get_local_string(string_id=32009))

    def show_login_failed_notification(self):
        """
        Shows login failed notification for 5 sec

        :returns:  bool - Notification shown
        """
        dialog = xbmcgui.Dialog()
        dialog.notification(
            self.utils.get_local_string(string_id=32006),
            self.utils.get_local_string(string_id=32007),
            xbmcgui.NOTIFICATION_ERROR, 5000)

    def show_storing_credentials_failed(self):
        """
        Shows "storing credentials failed" modal

        :returns:  bool - Dialog shown
        """
        dialog = xbmcgui.Dialog()
        dialog.ok(
            self.utils.get_addon_data().get('plugin'),
            self.utils.get_local_string(32008))
