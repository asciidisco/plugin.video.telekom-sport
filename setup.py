# -*- coding: utf-8 -*-
# Module: default
# Author: asciidisco
# Created on: 24.07.2017
# License: MIT https://github.com/asciidisco/plugin.video.telekom-sport/master/LICENSE

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
    ]
}

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

def get_author():
    """Loads the Kodi plugin author/provider"""
    with open(os.path.join(ROOT_DIR, 'addon.xml'), 'rb') as addon_xml:
        return re.search(r'(?<!xml )provider-name="(.+?)"', addon_xml.read()).group(1)

def get_name():
    """Loads the Kodi plugin name"""
    with open(os.path.join(ROOT_DIR, 'addon.xml'), 'rb') as addon_xml:
        return re.search(r'(?<!xml )name="(.+?)"', addon_xml.read()).group(1)

def get_version():
    """Loads the Kodi plugin version"""
    with open(os.path.join(ROOT_DIR, 'addon.xml'), 'rb') as addon_xml:
        return re.search(r'(?<!xml )version="(.+?)"', addon_xml.read()).group(1)

def get_description():
    """Loads the Kodi plugin description"""
    with open(os.path.join(ROOT_DIR, 'addon.xml'), 'rb') as addon_xml:
        return re.search(r'(?<!xml )description lang="en_GB">(.+?)<', addon_xml.read()).group(1)

if sys.version_info < REQUIRED_PYTHON_VERSION:
    sys.exit('Python >= 2.7 is required. Your version:\n' + sys.version)

setup(
    name=get_name(),
    version=get_version(),
    author=get_author(),
    author_email=AUTHOR_EMAIL,
    description=get_description(),
    packages=PACKAGES,
    include_package_data=True,
    install_requires=INSTALL_DEPENDENCIES,
    setup_requires=SETUP_DEPENDENCIES,
    tests_require=TEST_DEPENDENCIES,
    extras_require=EXTRA_DEPENDENCIES,
    test_suite='nose.collector',
)
