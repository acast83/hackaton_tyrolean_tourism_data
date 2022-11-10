import os

VERSION = [1, 0, 0]
__VERSION__ = '.'.join(map(str, VERSION))

from setuptools import setup

long_description = 'tshared'

setup(
    name='tshared',
    version=__VERSION__,
    packages=[
              'tshared',
              'tshared.models',
              'tshared.lookups',
              'tshared.utils',
              ],
    url='',
    license='',
    author='Digital Cube doo',
    author_email='info@digitalcube.rs',
    description='tshared',
    long_description=long_description,

    install_requires=[

    ]
)

