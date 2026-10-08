# -*- coding: utf-8 -*-
from collective.eeafaceted.collectionwidget.utils import getCollectionLinkCriterion
from collective.eeafaceted.dashboard import FacetedDashboardMessageFactory as _
from collective.eeafaceted.dashboard.testing import DEMO_INTEGRATION
from collective.eeafaceted.dashboard.testing import IntegrationTestCase
from eea.facetednavigation.interfaces import IFacetedLayout
from eea.facetednavigation.interfaces import IFacetedNavigable
from eea.facetednavigation.interfaces import IHidePloneLeftColumn
from plone.app.portlets.interfaces import IColumn
from plone.app.portlets.interfaces import IDashboard
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.base.interfaces import IBundleRegistry
from plone.base.utils import get_installer
from plone.behavior.interfaces import IBehavior
from plone.portlets.interfaces import IPortletType
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.component import queryUtility
from zope.i18n import translate


def registered_bundles():
    """Resource registry bundles, by name."""
    return getUtility(IRegistry).collectionOfInterface(
        IBundleRegistry, prefix="plone.bundles", check=False
    )


class TestInstall(IntegrationTestCase):
    """Test installation of collective.eeafaceted.dashboard into Plone."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.installer = get_installer(self.portal, self.layer["request"])

    def test_product_installed(self):
        """Test if collective.eeafaceted.dashboard is installed."""
        self.assertTrue(
            self.installer.is_product_installed("collective.eeafaceted.dashboard")
        )

    def test_uninstall(self):
        """Test if collective.eeafaceted.dashboard is cleanly uninstalled."""
        from collective.eeafaceted.dashboard.interfaces import IFacetedDashboardLayer
        from plone.browserlayer import utils

        self.installer.uninstall_product("collective.eeafaceted.dashboard")
        self.assertFalse(
            self.installer.is_product_installed("collective.eeafaceted.dashboard")
        )
        self.assertNotIn(IFacetedDashboardLayer, utils.registered_layers())
        self.assertNotIn("faceted-dashboard", registered_bundles())

    # browserlayer.xml
    def test_browserlayer(self):
        """Test that IImioDashboardLayer is registered."""
        from collective.eeafaceted.dashboard.interfaces import IFacetedDashboardLayer
        from plone.browserlayer import utils

        self.assertIn(IFacetedDashboardLayer, utils.registered_layers())

    # types.xml, types/DashboardPODTemplate.xml
    def test_types(self):
        fti = self.portal.portal_types.DashboardPODTemplate
        self.assertEqual(fti.meta_type, "Dexterity FTI")
        self.assertEqual(
            fti.klass,
            "collective.eeafaceted.dashboard.content.pod_template.DashboardPODTemplate",
        )
        self.assertEqual(
            fti.schema,
            "collective.eeafaceted.dashboard.content.pod_template.IDashboardPODTemplate",
        )
        self.assertEqual(fti.add_permission, "cmf.AddPortalContent")
        self.assertEqual(fti.default_view, "view")
        self.assertTrue(fti.global_allow)
        self.assertEqual(
            tuple(fti.behaviors),
            (
                "plone.app.dexterity.behaviors.metadata.IBasic",
                "plone.app.content.interfaces.INameFromTitle",
                "collective.behavior.talcondition.behavior.ITALCondition",
            ),
        )
        # every behavior exists
        self.assertEqual(
            [b for b in fti.behaviors if queryUtility(IBehavior, name=b) is None], []
        )
        # the add permission ("Add portal content") drives the add menu
        setRoles(self.portal, TEST_USER_ID, ["Member"])
        self.assertNotIn(
            "DashboardPODTemplate",
            [t.getId() for t in self.portal.allowedContentTypes()],
        )
        setRoles(self.portal, TEST_USER_ID, ["Contributor"])
        self.assertIn(
            "DashboardPODTemplate",
            [t.getId() for t in self.portal.allowedContentTypes()],
        )

    # portlets.xml
    def test_portlets(self):
        portlet_type = queryUtility(IPortletType, name="FacetedCollectionPortlet")
        self.assertEqual(portlet_type.addview, "FacetedCollectionPortlet")
        self.assertEqual(portlet_type.title, "Collection widget portlet")
        self.assertEqual(list(portlet_type.for_), [IColumn, IDashboard])

    # registry.xml
    def test_resources(self):
        bundles = registered_bundles()
        bundle = bundles["faceted-dashboard"]
        self.assertTrue(bundle.enabled)
        self.assertEqual(
            (bundle.jscompilation, bundle.csscompilation),
            (
                "++resource++collective.eeafaceted.dashboard/collective.eeafaceted.dashboard.js",
                "++resource++collective.eeafaceted.dashboard/collective.eeafaceted.dashboard.css",
            ),
        )
        # loaded after the eea.facetednavigation bundle it uses (Faceted.Events), deferred as it is
        self.assertEqual(bundle.depends, "faceted.view")
        self.assertIn(bundle.depends, bundles)
        self.assertTrue(bundle.load_defer)
        self.assertFalse(bundle.load_async)
        # every resource exists
        self.portal.restrictedTraverse(bundle.jscompilation)
        self.portal.restrictedTraverse(bundle.csscompilation)

    # locales
    def test_translations(self):
        self.assertEqual(
            translate(_("DashboardPODTemplate"), target_language="fr"),
            "Modèle de document POD pour tableau de bord",
        )
        self.assertEqual(
            translate(
                _("Only the first ${nb} items will be generated", mapping={"nb": 500}),
                target_language="fr",
            ),
            "Seuls les 500 premiers éléments seront pris en compte",
        )
        self.assertEqual(
            translate(
                "pretty_link",
                domain="collective.eeafaceted.z3ctable",
                target_language="fr",
            ),
            "Titre (lien)",
        )
        self.assertEqual(
            translate("Searches", domain="eea", target_language="fr"), "Recherches"
        )


class TestInstallDemo(IntegrationTestCase):
    """Test installation of collective.eeafaceted.dashboard into Plone."""

    layer = DEMO_INTEGRATION

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer["portal"]
        self.installer = get_installer(self.portal, self.layer["request"])

    def test_demo_profile_installed(self):
        """Test if collective.eeafaceted.dashboard is installed."""
        self.assertTrue(
            self.installer.is_product_installed("collective.eeafaceted.dashboard")
        )
        self.assertEqual(
            self.portal.dashboard.objectIds(),
            ["every-elements", "my-elements", "elements-to-review", "expired-elements"],
        )
        # setuphandlers.add_demo_data: faceted dashboard, left column hidden, default collection
        dashboard = self.portal.dashboard
        self.assertTrue(IFacetedNavigable.providedBy(dashboard))
        self.assertEqual(IFacetedLayout(dashboard).layout, "faceted-table-items")
        self.assertTrue(IHidePloneLeftColumn.providedBy(dashboard))
        self.assertEqual(
            getCollectionLinkCriterion(dashboard).default,
            dashboard["every-elements"].UID(),
        )
        self.assertEqual(
            [(c.id, c.showNumberOfItems) for c in dashboard.objectValues()],
            [
                ("every-elements", False),
                ("my-elements", False),
                ("elements-to-review", True),
                ("expired-elements", True),
            ],
        )
        self.assertEqual(
            dashboard["my-elements"].customViewFields,
            [
                "pretty_link",
                "Creator",
                "CreationDate",
                "ModificationDate",
                "review_state",
                "select_row",
            ],
        )
