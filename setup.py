# -*- coding: utf-8 -*-
"""Installer for the collective.eeafaceted.dashboard package."""

from setuptools import find_packages
from setuptools import setup


long_description = (
    open('README.rst').read() + '\n' + open('CHANGES.rst').read() + '\n')


setup(
    name='collective.eeafaceted.dashboard',
    version='0.5',
    description="This package is the glue between different packages "
                "offering a usable and integrated dashboard application",
    long_description=long_description,
    # Get more from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Framework :: Plone :: 5.0",
        "Framework :: Plone :: 5.1",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ],
    keywords='Python Zope Plone',
    author='IMIO',
    author_email='dev@imio.be',
    url='http://pypi.python.org/pypi/collective.eeafaceted.dashboard',
    license='GPL V2',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['collective', 'collective.eeafaceted'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'Products.ZCatalog',
        'plone.api',
        # version 1.0.3+ manage correctly orphans
        'plone.batching > 1.0.4',
        'setuptools',
        'collective.compoundcriterion',
        'collective.documentgenerator',
        'collective.eeafaceted.collectionwidget>0.9',
        'collective.eeafaceted.z3ctable>1.0',
        'eea.facetednavigation>=10.0',
        'imio.prettylink',
        'z3c.unconfigure',
    ],
    extras_require={
        'test': [
            'plone.app.dexterity',
            'plone.app.testing',
            'plone.app.relationfield',
            'plone.app.robotframework[debug]',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
