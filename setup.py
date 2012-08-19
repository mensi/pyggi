# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='Pyggi',
    version='0.1',
    packages=[],
    include_package_data=False,
    install_requires=[
        'Flask>=0.7',
        'GitPython>=0.3',
    ],
    extras_require = {
        'Markdown': ['Markdown>=2.0.3'],
        'reST': ['docutils>=0.7'],
        'cache': ['python-memcached>=1.47'],
    },

    # package metadata
    author="Tobias Heinzen",
    author_email="tobias.heinzen@0xdeadbeef.ch",
    description="Pyggi - a lightweight git frontend",
    license="BSD"
)

