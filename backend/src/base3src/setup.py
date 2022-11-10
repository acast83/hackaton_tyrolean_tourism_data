import os

VERSION = [3, 1, 0]
__VERSION__ = '.'.join(map(str, VERSION))

from setuptools import setup

long_description = 'base3'

setup(
    name='base3',
    version=__VERSION__,
    packages=[
              'base3',
              ],
    url='',
    license='',
    author='Digital Cube doo',
    author_email='info@digitalcube.rs',
    description='base3',
    long_description=long_description,

    install_requires=[

    ]
)

