# -*- coding: utf-8 -*-
from collective.eeafaceted.dashboard.testing import IntegrationTestCase
from plone import api


class TestInstall(IntegrationTestCase):
    """Test installation of collective.eeafaceted.dashboard into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if collective.eeafaceted.dashboard is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('collective.eeafaceted.dashboard'))

    def test_uninstall(self):
        """Test if collective.eeafaceted.dashboard is cleanly uninstalled."""
        self.installer.uninstallProducts(['collective.eeafaceted.dashboard'])
        self.assertFalse(self.installer.isProductInstalled('collective.eeafaceted.dashboard'))

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that IImioDashboardLayer is registered."""
        from collective.eeafaceted.dashboard.interfaces import IFacetedDashboardLayer
        from plone.browserlayer import utils
        self.assertIn(IFacetedDashboardLayer, utils.registered_layers())
