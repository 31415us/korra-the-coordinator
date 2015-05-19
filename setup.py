#! /usr/bin/python

from setuptools import setup

args = dict(
        name='korra',
        version='0.1',
        description='coordinates robot actions',
        packages=['korra'],
        install_requires=['pykka', 'molly', 'cvra_actuatorpub'],
        author='Pius von Daeniken',
        url='https://github.com/cvra/korra-the-coordinator'
)

setup(**args)
