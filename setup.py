# -*- coding: utf-8 -*-
"""
Install file for lunchrobot.
"""
from setuptools import setup, find_packages

PACKAGES = find_packages()

SCRIPTS = []
EP = {}


def read_requirements(filename='requirements.txt'):
    req = []
    with open(filename, 'r') as f:
        for line in f:
            if not line.startswith('#') and not line.startswith('git'):
                req.append(line.strip('\n'))
    return req

requirements = read_requirements()


setup(name='lunchrobot',
      version='0.1.0',
      packages=PACKAGES,
      description='Uwolnij sie od zamawiania obiadu.',
      install_requires=requirements,
      include_package_data=True,
      scripts=SCRIPTS,
      entry_points=EP
)
