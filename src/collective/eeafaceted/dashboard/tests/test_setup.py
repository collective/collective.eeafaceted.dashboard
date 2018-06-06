# -*- coding: utf-8 -*-
from imio.dashboard.testing import IntegrationTestCase
from plone import api


class TestInstall(IntegrationTestCase):
    """Test installation of imio.dashboard into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if imio.dashboard is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('imio.dashboard'))

    def test_uninstall(self):
        """Test if imio.dashboard is cleanly uninstalled."""
        self.installer.uninstallProducts(['imio.dashboard'])
        self.assertFalse(self.installer.isProductInstalled('imio.dashboard'))

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that IImioDashboardLayer is registered."""
        from imio.dashboard.interfaces import IImioDashboardLayer
        from plone.browserlayer import utils
        self.assertIn(IImioDashboardLayer, utils.registered_layers())
