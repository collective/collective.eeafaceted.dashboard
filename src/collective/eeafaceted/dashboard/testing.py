# -*- coding: utf-8 -*-
"""Base module for unittesting."""

from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.testing import z2

import unittest

import collective.eeafaceted.dashboard
from collective.eeafaceted.dashboard.utils import enableFacetedDashboardFor


class FacetedDashboardLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)
    products = ('Products.DateRecurringIndex', )

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""
        # Load ZCML
        self.loadZCML(package=collective.eeafaceted.dashboard,
                      name='testing.zcml')
        for p in self.products:
            z2.installProduct(app, p)

    def setUpPloneSite(self, portal):
        """Set up Plone."""
        # Install into Plone site using portal_setup
        applyProfile(portal, 'collective.eeafaceted.dashboard:testing')

        # Login and create some test content
        setRoles(portal, TEST_USER_ID, ['Manager'])
        login(portal, TEST_USER_NAME)
        folder_id = portal.invokeFactory('Folder', 'folder', title='Folder')
        portal[folder_id].reindexObject()

        # Commit so that the test browser sees these objects
        import transaction
        transaction.commit()

    def tearDownZope(self, app):
        """Tear down Zope."""
        for p in reversed(self.products):
            z2.uninstallProduct(app, p)


class DemoFacetedDashboardLayer(FacetedDashboardLayer):
    """ """

    def setUpPloneSite(self, portal):
        """Set up Plone."""
        super(DemoFacetedDashboardLayer, self).setUpPloneSite(portal)
        applyProfile(portal, 'collective.eeafaceted.dashboard:demo')


FIXTURE = FacetedDashboardLayer(
    name="FIXTURE"
)

DEMO_FIXTURE = DemoFacetedDashboardLayer(
    name="DEMO_FIXTURE"
)

INTEGRATION = IntegrationTesting(
    bases=(FIXTURE,),
    name="INTEGRATION"
)


FUNCTIONAL = FunctionalTesting(
    bases=(FIXTURE,),
    name="FUNCTIONAL"
)


ACCEPTANCE = FunctionalTesting(bases=(DEMO_FIXTURE,
                                      REMOTE_LIBRARY_BUNDLE_FIXTURE,
                                      z2.ZSERVER_FIXTURE),
                               name="ACCEPTANCE")


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION

    def setUp(self):
        super(IntegrationTestCase, self).setUp()
        self.portal = self.layer['portal']
        self.request = self.portal.REQUEST
        self.folder = self.portal.get('folder')
        enableFacetedDashboardFor(self.folder)
        self.faceted_table = self.folder.restrictedTraverse('faceted-table-view')


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL
