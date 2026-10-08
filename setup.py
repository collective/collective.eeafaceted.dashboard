# -*- coding: utf-8 -*-
"""Installer for the collective.eeafaceted.dashboard package."""

from setuptools import find_packages
from setuptools import setup


long_description = open("README.rst").read() + "\n" + open("CHANGES.rst").read() + "\n"


setup(
    name="collective.eeafaceted.dashboard",
    version="0.23.3.dev0",
    description="This package is the glue between different packages "
    "offering a usable and integrated dashboard application",
    long_description=long_description,
    # Get more from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Development Status :: 6 - Mature",
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 6.2",
        "Framework :: Plone :: Addon",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.13",
    ],
    keywords="Python Zope Plone",
    author="IMIO",
    author_email="dev@imio.be",
    url="http://pypi.python.org/pypi/collective.eeafaceted.dashboard",
    license="GPL V2",
    packages=find_packages("src", exclude=["ez_setup"]),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.10",
    install_requires=[
        "Products.ZCatalog",
        "plone.api",
        # version 1.0.3+ manage correctly orphans
        "plone.batching > 1.0.4",
        "setuptools",
        "collective.behavior.talcondition",
        "collective.compoundcriterion",
        "collective.documentgenerator>=4.0",
        "collective.eeafaceted.collectionwidget>0.9",
        "collective.eeafaceted.z3ctable>1.0",
        "eea.facetednavigation>=16.0",
        "imio.prettylink",
        "plone.app.contenttypes",
        "plone.base",
        "z3c.unconfigure",
    ],
    extras_require={
        "test": [
            "plone.app.dexterity",
            "plone.app.testing",
            "plone.app.relationfield",
            "plone.app.robotframework[reload]",
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
