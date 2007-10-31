#!/usr/bin/python

from distutils.core import setup

setup(name='scorpion_server',
      version='0.0.1',
      description='A simple web server using SSL and Basic auth.',
      author='Jeffrey Scudder',
      author_email='me@jeffscudder.com',
      url='...',
      packages=['scorpion_server'],
      package_dir = {'scorpion_server':'src/scorpion_server'})