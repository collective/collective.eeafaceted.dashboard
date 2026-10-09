# -*- coding: utf-8 -*-
"""Base module for unittesting."""

from collective.eeafaceted.dashboard.utils import enableFacetedDashboardFor
from plone.app.robotframework.content import Content
from plone.app.robotframework.remote import RemoteLibraryLayer
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.robotframework.utils import disableCSRFProtection
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.testing import zope
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
from zope.viewlet.interfaces import IViewletManager

import collective.eeafaceted.dashboard
import unittest


class FacetedDashboardLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)
    products = ("Products.DateRecurringIndex",)

    def setUpZope(self, app, configurationContext):
        """Set up Zope."""
        # Load ZCML
        self.loadZCML(package=collective.eeafaceted.dashboard, name="testing.zcml")
        for p in self.products:
            zope.installProduct(app, p)

    def setUpPloneSite(self, portal):
        """Set up Plone."""
        # Install into Plone site using portal_setup
        applyProfile(portal, "collective.eeafaceted.dashboard:testing")

        # Login and create some test content
        setRoles(portal, TEST_USER_ID, ["Manager"])
        login(portal, TEST_USER_NAME)
        folder_id = portal.invokeFactory("Folder", "folder", title="Folder")
        portal[folder_id].reindexObject()

        # Commit so that the test browser sees these objects
        import transaction

        transaction.commit()

    def tearDownZope(self, app):
        """Tear down Zope."""
        for p in reversed(self.products):
            zope.uninstallProduct(app, p)


class DemoFacetedDashboardLayer(FacetedDashboardLayer):
    """ """

    def setUpPloneSite(self, portal):
        """Set up Plone."""
        super(DemoFacetedDashboardLayer, self).setUpPloneSite(portal)
        applyProfile(portal, "collective.eeafaceted.dashboard:demo")


FIXTURE = FacetedDashboardLayer(name="FIXTURE")

DEMO_FIXTURE = DemoFacetedDashboardLayer(name="DEMO_FIXTURE")

INTEGRATION = IntegrationTesting(bases=(FIXTURE,), name="INTEGRATION")

DEMO_INTEGRATION = IntegrationTesting(bases=(DEMO_FIXTURE,), name="DEMO_INTEGRATION")

FUNCTIONAL = FunctionalTesting(bases=(FIXTURE,), name="FUNCTIONAL")


class SetFieldValue(Content):
    def set_field_value(self, uid, field, value, field_type):
        """plone.app.robotframework 3.0.0 doesn't disable the CSRF protection here (as
        create_content does): plone.protect silently aborts the change (MIGRATION.md).
        """
        disableCSRFProtection()
        return super().set_field_value(uid, field, value, field_type)


# REMOTE_LIBRARY_BUNDLE_FIXTURE with the fixed "Set field value" keyword
REMOTE_LIBRARY_FIXTURE = RemoteLibraryLayer(
    bases=(PLONE_FIXTURE,),
    libraries=(SetFieldValue,) + REMOTE_LIBRARY_BUNDLE_FIXTURE.libraryBases[1:],
    name="DashboardRemoteLibrary:RobotRemote",
)


# robot scenarios (tests/robot): demo dashboard, served over HTTP
ACCEPTANCE = FunctionalTesting(
    bases=(DEMO_FIXTURE, REMOTE_LIBRARY_FIXTURE, zope.WSGI_SERVER_FIXTURE),
    name="ACCEPTANCE",
)


class IntegrationTestCase(unittest.TestCase):
    """Base class for integration tests."""

    layer = INTEGRATION

    def setUp(self):
        super(IntegrationTestCase, self).setUp()
        self.portal = self.layer["portal"]
        self.request = self.portal.REQUEST
        self.folder = self.portal.get("folder")
        enableFacetedDashboardFor(self.folder)
        self.faceted_table = self.folder.restrictedTraverse("faceted-table-view")

    # utils method to be put later in testing helpers
    def _get_viewlet_manager(self, context, manager_name):
        """ """
        view = BrowserView(context, self.request)
        viewlet_manager = getMultiAdapter(
            (context, self.request, view), IViewletManager, manager_name
        )
        viewlet_manager.update()
        return viewlet_manager

    def _get_viewlet(self, context, manager_name, viewlet_name):
        """ """
        viewlet_manager = self._get_viewlet_manager(context, manager_name)
        viewlet = viewlet_manager.get(viewlet_name)
        return viewlet


class FunctionalTestCase(unittest.TestCase):
    """Base class for functional tests."""

    layer = FUNCTIONAL
