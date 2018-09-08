# -*- coding: utf-8 -*-
# Module: Session
# Author: asciidisco
# Created on: 24.07.2017
# License: MIT https://goo.gl/WA1kby

"""Stores, loads & builds up a request session object. Provides login"""

try:
    import cPickle as pickle
except ImportError:
    import pickle
from os import path, remove
from requests import session, utils
from bs4 import BeautifulSoup


class Session(object):
    """Stores, loads & builds up a request session object. Provides login"""

    def __init__(self, constants, util, settings):
        """
        Injects instances, sets session file & loads initial session

        :param constants: Constants instance
        :type constants: resources.lib.Constants
        :param util: Utils instance
        :type util: resources.lib.Utils
        :param settings: Settings instance
        :type settings: resources.lib.Settings
        """
        self.constants = constants
        self.utils = util
        self.settings = settings
        addon = self.utils.get_addon()
        verify_ssl = True if addon.getSetting('verifyssl') == 'True' else False
        self.session_file = self.utils.get_addon_data().get('cookie_path')
        self.verify_ssl = verify_ssl
        self._session = self.load_session()

    def get_session(self):
        """
        Returns the build up session object

        :returns:  requests.session -- Session object
        """
        return self._session

    def clear_session(self):
        """Clears the session, e.g. removes Cookie file"""
        if path.isfile(self.session_file):
            remove(self.session_file)

    def save_session(self):
        """Persists the session, e.g. generates Cookie file"""
        with open(self.session_file, 'w') as handle:
            pickle.dump(
                utils.dict_from_cookiejar(self._session.cookies),
                handle)

    def load_session(self):
        """
        Generates the build up session object,
        loads & deserializes Cookie file if exists

        :returns:  requests.session -- Session object
        """
        _session = session()
        _session.headers.update({
            'User-Agent': self.utils.get_user_agent(),
            'Accept-Encoding': 'gzip'
        })
        if path.isfile(self.session_file):
            with open(self.session_file, 'r') as handle:
                try:
                    _cookies = utils.cookiejar_from_dict(pickle.load(handle))
                except EOFError:
                    _cookies = utils.cookiejar_from_dict({})
                _session.cookies = _cookies
        return _session

    def login(self, user, password):
        """
        Logs in to the platform, fetches cookie headers and checks
        if the login succeeded

        :param user: Username/E-Mail
        :type user: string
        :param password: Password
        :type password: string
        :returns:  bool -- Login succeeded
        """
        payload = {}
        # check if the suer is already logged in
        check_res = self.get_session().get(self.constants.get_base_url())
        check_soup = BeautifulSoup(check_res.text, 'html.parser')
        if check_soup.find('a', class_='logout') is not None:
            return True
        # clear session
        self.clear_session()
        self._session = self.load_session()
        _session = self.get_session()
        # get contents of login page
        res = _session.get(
            self.constants.get_login_link(),
            verify=self.verify_ssl)
        login_page_html = res.text
        soup = BeautifulSoup(login_page_html, 'html.parser')
        # find all <input/> items in the login form & grep their data
        for item in soup.find(id='login').find_all('input'):
            if item.attrs.get('name') is not None:
                payload[item.attrs.get('name')] = item.attrs.get('value', '')
        # overwrite user & password fields with our settings data
        payload['pw_usr'] = user
        payload['pw_pwd'] = password
        # persist the session
        # payload['persist_session'] = 1
        # add empyt sumbit field (it is the value of the button in the page...)
        payload['pw_submit'] = ''
        # do the login & read the incoming html <title/>
        # attribute to determine of the login was successfull
        login_res = _session.post(
            self.constants.get_login_endpoint(),
            verify=self.verify_ssl,
            data=payload)
        soup = BeautifulSoup(login_res.text, 'html.parser')
        success = 'sport' in soup.find('title').get_text().lower()
        if success is True:
            self.save_session()
            return True
        return False

    def logout(self):
        """Clears the session"""
        self.clear_session()

    def switch_account(self):
        """Clears the session & opens up credentials dialogs"""
        self.clear_session()
        self.settings.set_credentials()
