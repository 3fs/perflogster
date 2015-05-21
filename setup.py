#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='perf-logster',
    version='0.0.1',
    description='Custom performance log parser',
    author='3fs',
    url='https://github.com/3fs/perf-logster',
    packages=[
        'perf_logster'
    ],
    zip_safe=False,
    license='GPL3',
    test_suite='tests',
)
