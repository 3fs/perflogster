#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='perflogster',
    version='0.0.2',
    description='Custom performance log parser',
    author='3fs',
    url='https://github.com/3fs/perflogster',
    download_url='https://github.com/3fs/perflogster/releases/tag/0.0.2',
    packages=[
        'perflogster'
    ],
    zip_safe=False,
    license='GPL3',
    test_suite='tests',
)
