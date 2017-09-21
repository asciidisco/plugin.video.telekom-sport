# -*- coding: utf-8 -*-
# Module: Session
# Author: asciidisco
# Created on: 24.07.2017
# License: MIT https://goo.gl/xF5sC4

"""ADD ME"""

try:
    import cPickle as pickle
except ImportError:
    import pickle
from os import path, remove
from requests import session, utils
from bs4 import BeautifulSoup


class Session(object):
    """ADD ME"""

    def __init__(self, constants, util, settings):
        """ADD ME"""
        self.constants = constants
        self.utils = util
        self.settings = settings
        self.session_file = self.utils.get_addon_data().get('cookie_path')
        self._session = self.load_session()

    def get_session(self):
        """ADD ME"""
        return self._session

    def clear_session(self):
        """ADD ME"""
        if path.isfile(self.session_file):
            remove(self.session_file)

    def save_session(self):
        """ADD ME"""
        with open(self.session_file, 'w') as handle:
            pickle.dump(
                utils.dict_from_cookiejar(self._session.cookies),
                handle)

    def load_session(self):
        """ADD ME"""
        _session = session()
        _session.headers.update({
            'User-Agent': self.utils.get_user_agent(),
            'Accept-Encoding': 'gzip'
        })
        if path.isfile(self.session_file):
            with open(self.session_file, 'r') as handle:
                _cookies = utils.cookiejar_from_dict(pickle.load(handle))
                _session.cookies = _cookies
        return _session

    def login(self, user, password):
        """ADD ME"""
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
        res = _session.get(self.constants.get_login_link())
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
            data=payload)
        soup = BeautifulSoup(login_res.text, 'html.parser')
        success = 'Sport' in soup.find('title').get_text()
        if success:
            self.save_session()
            return True
        else:
            return False

    def logout(self):
        """ADD ME"""
        self.clear_session()

    def switch_account(self):
        """ADD ME"""
        self.clear_session()
        self.settings.set_credentials()
