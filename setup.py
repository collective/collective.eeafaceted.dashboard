"""Installer for the collective.eeafaceted.dashboard package."""

from setuptools import setup

long_description = open("README.rst").read() + "\n" + open("CHANGES.rst").read() + "\n"


setup(
    name="collective.eeafaceted.dashboard",
    version="1.0.0.dev0",
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
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
    ],
    keywords="Python Zope Plone",
    author="IMIO",
    author_email="dev@imio.be",
    url="http://pypi.python.org/pypi/collective.eeafaceted.dashboard",
    license="GPL V2",
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.10",
    install_requires=[
        "collective.beaker",
        "collective.behavior.talcondition",
        "collective.compoundcriterion",
        "collective.documentgenerator>=4.0",
        "collective.eeafaceted.collectionwidget>0.9",
        "collective.eeafaceted.z3ctable>1.0",
        "eea.facetednavigation>=16.0",
        "imio.helpers",
        "imio.prettylink",
        "plone.api",
        "plone.app.contenttypes",
        "plone.app.dexterity",
        "plone.app.portlets",
        "plone.app.uuid",
        "plone.app.vocabularies",
        "plone.autoform",
        "plone.base",
        "plone.locking",
        "plone.memoize",
        "plone.portlets",
        "Products.CMFCore",
        "z3c.form",
        "z3c.unconfigure",
        "Zope",
    ],
    extras_require={
        "test": [
            "lxml",
            "plone.app.relationfield",
            "plone.app.robotframework[reload]",
            "plone.app.testing",
            "plone.behavior",
            "plone.browserlayer",
            "plone.dexterity",
            "plone.indexer",
            "plone.testing",
            "robotsuite",
            "z3c.table",
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
