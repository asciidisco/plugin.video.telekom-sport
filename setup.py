# -*- coding: utf-8 -*-
# Module: default
# Author: asciidisco
# Created on: 24.07.2017
# License: MIT https://goo.gl/xF5sC4

"""Setup"""

import os
import re
import sys
from setuptools import find_packages, setup

AUTHOR_EMAIL = 'public@asciidisco.com'
URL = 'https://github.com/asciidisco/plugin.video.telekom-sport'
REQUIRED_PYTHON_VERSION = (2, 7)
PACKAGES = find_packages()
INSTALL_DEPENDENCIES = []
SETUP_DEPENDENCIES = []
TEST_DEPENDENCIES = [
    'nose',
    'Kodistubs',
    'httpretty',
    'mock',
]
EXTRA_DEPENDENCIES = {
    'dev': [
        'nose',
        'flake8',
        'codeclimate-test-reporter',
        'pylint',
        'mccabe',
        'pycodestyle',
        'pyflakes',
        'Kodistubs',
        'httpretty',
        'mock',
        'requests',
        'beautifulsoup4',
        'pyDes',
    ]
}


def get_addon_data():
    """Loads the Kodi plugin data from addon.xml"""
    root_dir = os.path.dirname(os.path.abspath(__file__))
    pathname = os.path.join(root_dir, 'addon.xml')
    with open(pathname, 'rb') as addon_xml:
        author = re.search(
            r'(?<!xml )provider-name="(.+?)"',
            addon_xml.read()).group(1)
        name = re.search(
            r'(?<!xml )name="(.+?)"',
            addon_xml.read()).group(1)
        version = re.search(
            r'(?<!xml )version="(.+?)"',
            addon_xml.read()).group(1)
        desc = re.search(
            r'(?<!xml )description lang="en_GB">(.+?)<',
            addon_xml.read()).group(1)
        return {
            'author': author,
            'name': name,
            'version': version,
            'desc': desc,
        }


if sys.version_info < REQUIRED_PYTHON_VERSION:
    sys.exit('Python >= 2.7 is required. Your version:\n' + sys.version)

ADDON_DATA = get_addon_data()

setup(
    name=ADDON_DATA.get('name'),
    version=ADDON_DATA.get('version'),
    author=ADDON_DATA.get('author'),
    author_email=AUTHOR_EMAIL,
    description=ADDON_DATA.get('desc'),
    packages=PACKAGES,
    include_package_data=True,
    install_requires=INSTALL_DEPENDENCIES,
    setup_requires=SETUP_DEPENDENCIES,
    tests_require=TEST_DEPENDENCIES,
    extras_require=EXTRA_DEPENDENCIES,
    test_suite='nose.collector',
)
