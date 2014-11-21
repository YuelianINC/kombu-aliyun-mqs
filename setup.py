#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Last modified: Zhong Gaohao (pkuember@gmail.com)

from setuptools import setup, find_packages


setup(
    name='kombu-aliyun-mqs',
    version='0.1',
    packages=find_packages(),
    author='Zhong Gaohao',
    author_email='pkuember@gmail.com',
    url='https://https://github.com/YuelianINC/kombu-aliyun-mqs',
    description='aliyun mqs ',
    #long_description=open('README.md').read(),
    license='Apache2',
    requires=[
        'kombu',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: System :: Installation/Setup'
    ],
    include_package_data=True,
    zip_safe=False
)