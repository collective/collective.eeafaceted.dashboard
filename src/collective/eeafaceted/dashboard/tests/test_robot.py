# -*- coding: utf-8 -*-
"""Robot suites of tests/robot, run with the layer of their file name.

ROBOT_PLONE_MAJOR (4 or 6) selects the UI keywords: robotsuite passes the
ROBOT_* environment variables to the suites as robot variables.
"""
from collective.eeafaceted.dashboard.testing import ACCEPTANCE
from plone.testing import layered

import os
import robotsuite
import unittest


try:
    from importlib.metadata import version
except ImportError:  # Python 2
    from pkg_resources import get_distribution

    def version(name):
        return get_distribution(name).version


# suites needing an optional integration layer, e.g. {'test_facetednav.robot': ADDONS_ACCEPTANCE}
SUITE_LAYERS = {}
# scenarios failing because of a known Plone 4 bug (MIGRATION.md Known issues): reported, not failing on
# Robot Framework 3 (Plone 4.3); Robot Framework 4+ (Plone 6) has no criticality, they must pass there
NONCRITICAL_TAGS = ['plone4-bug']


def test_suite():
    os.environ.setdefault('ROBOT_PLONE_MAJOR', version('Products.CMFPlone').split('.')[0])
    suite = unittest.TestSuite()
    robot_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'robot')
    for name in sorted(os.listdir(robot_dir)):
        if name.startswith('test_') and name.endswith('.robot'):
            suite.addTests([
                layered(robotsuite.RobotTestSuite(os.path.join('robot', name), noncritical=NONCRITICAL_TAGS),
                        layer=SUITE_LAYERS.get(name, ACCEPTANCE)),
            ])
    return suite
