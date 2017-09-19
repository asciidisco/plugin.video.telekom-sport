# -*- coding: utf-8 -*-
# Module: default
# Author: asciidisco
# Created on: 24.07.2017
# License: MIT https://github.com/asciidisco/plugin.video.telekom-sport/master/LICENSE

"""Kodi plugin for Telekom Sport (https://telekomsport.de)"""

import re
import os
import shutil
from setuptools import find_packages, setup, Command

here = os.path.abspath(os.path.dirname(__file__))

def get_version():
    with open(os.path.join(here, 'addon.xml'), 'rb') as addon_xml:
        return re.search(r'(?<!xml )version="(.+?)"', addon_xml.read()).group(1)


setup(
    name='Telekom Sport',
    version=get_version(),
    description='Kodi plugin for Telekom Sport',
    author='asciidisco',
    author_email='public@asciidisco.com',
    url='https://github.com/asciidisco/plugin.video.telekom-sport',
    license='MIT',
    packages=find_packages(exclude=('test',)),
    zip_safe=False)
