#from setuptools import *
from distutils.core import setup

setup(
    name='att_event_engine',
    version='0.8.1',
    packages=['att_event_engine'],
    install_requires='paho-mqtt',
    url='',
    license='copyright AllThingsTalk',
    author='Jan Bogaerts',
    author_email='jb@allthingsTalk.com',
    description='A library for creating event driven applications running on the ATT cloud'
)
