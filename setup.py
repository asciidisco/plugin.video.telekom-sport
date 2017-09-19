# -*- coding: utf-8 -*-
# Module: default
# Author: asciidisco
# Created on: 24.07.2017
# License: MIT https://github.com/asciidisco/plugin.video.telekom-sport/master/LICENSE

"""Kodi plugin for Telekom Sport (https://telekomsport.de)"""

import re
import os
import shutil
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

this_dir = os.path.dirname(os.path.abspath(__file__))


def get_version():
    with open(os.path.join(this_dir, 'addon.xml'), 'rb') as addon_xml:
        return re.search(r'(?<!xml )version="(.+?)"', addon_xml.read()).group(1)


setup(
    name='Telekom Sport',
    version=get_version(),
    description='Kodi plugin for Telekom Sport',
    author='asciidisco',
    author_email='public@asciidisco.com',
    url='https://github.com/asciidisco/plugin.video.telekom-sport',
    license='MIT',
    py_modules=[],
    zip_safe=False)
