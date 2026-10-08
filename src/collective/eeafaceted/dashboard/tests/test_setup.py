# -*- coding: utf-8 -*-
from collective.eeafaceted.collectionwidget.utils import getCollectionLinkCriterion
from collective.eeafaceted.dashboard import FacetedDashboardMessageFactory as _
from collective.eeafaceted.dashboard.testing import DEMO_INTEGRATION
from collective.eeafaceted.dashboard.testing import IntegrationTestCase
from eea.facetednavigation.interfaces import IFacetedLayout
from eea.facetednavigation.interfaces import IFacetedNavigable
from eea.facetednavigation.interfaces import IHidePloneLeftColumn
from plone import api
from plone.app.portlets.interfaces import IColumn
from plone.app.portlets.interfaces import IDashboard
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.behavior.interfaces import IBehavior
from plone.portlets.interfaces import IPortletType
from Products.CMFPlone.utils import getFSVersionTuple
from zope.component import queryUtility
from zope.i18n import translate


def registered_resources(portal):
    """Ids of the CSS and JS resources registered in the site."""
    if getFSVersionTuple()[0] < 5:
        return portal.portal_css.getResourceIds() + portal.portal_javascripts.getResourceIds()
    raise NotImplementedError("Plone 6: read the resource registry (MIGRATION.md phase 7)")


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

    # types.xml, types/DashboardPODTemplate.xml
    def test_types(self):
        fti = self.portal.portal_types.DashboardPODTemplate
        self.assertEqual(fti.meta_type, 'Dexterity FTI')
        self.assertEqual(fti.klass, 'collective.eeafaceted.dashboard.content.pod_template.DashboardPODTemplate')
        self.assertEqual(fti.schema, 'collective.eeafaceted.dashboard.content.pod_template.IDashboardPODTemplate')
        self.assertEqual(fti.add_permission, 'cmf.AddPortalContent')
        self.assertEqual(fti.default_view, 'view')
        self.assertTrue(fti.global_allow)
        self.assertEqual(
            tuple(fti.behaviors),
            ('plone.app.dexterity.behaviors.metadata.IBasic',
             'plone.app.content.interfaces.INameFromTitle',
             'collective.behavior.talcondition.behavior.ITALCondition'))
        # every behavior exists
        self.assertEqual([b for b in fti.behaviors if queryUtility(IBehavior, name=b) is None], [])
        # the add permission ("Add portal content") drives the add menu
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.assertNotIn('DashboardPODTemplate', [t.getId() for t in self.portal.allowedContentTypes()])
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        self.assertIn('DashboardPODTemplate', [t.getId() for t in self.portal.allowedContentTypes()])

    # portlets.xml
    def test_portlets(self):
        portlet_type = queryUtility(IPortletType, name='FacetedCollectionPortlet')
        self.assertEqual(portlet_type.addview, 'FacetedCollectionPortlet')
        self.assertEqual(portlet_type.title, 'Collection widget portlet')
        self.assertEqual(list(portlet_type.for_), [IColumn, IDashboard])

    # cssregistry.xml, jsregistry.xml
    def test_resources(self):
        resources = registered_resources(self.portal)
        for resource in (
                '++resource++collective.eeafaceted.dashboard/collective.eeafaceted.dashboard.css',
                '++resource++collective.eeafaceted.dashboard/collective.eeafaceted.dashboard.js'):
            self.assertIn(resource, resources)

    # locales
    def test_translations(self):
        self.assertEqual(translate(_('DashboardPODTemplate'), target_language='fr'),
                         u'Modèle de document POD pour tableau de bord')
        self.assertEqual(translate(_('Only the first ${nb} items will be generated', mapping={'nb': 500}),
                                   target_language='fr'),
                         u'Seuls les 500 premiers éléments seront pris en compte')
        self.assertEqual(translate('pretty_link', domain='collective.eeafaceted.z3ctable', target_language='fr'),
                         u'Titre (lien)')
        self.assertEqual(translate('Searches', domain='eea', target_language='fr'), u'Recherches')


class TestInstallDemo(IntegrationTestCase):
    """Test installation of collective.eeafaceted.dashboard into Plone."""

    layer = DEMO_INTEGRATION

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_demo_profile_installed(self):
        """Test if collective.eeafaceted.dashboard is installed with portal_quickinstaller."""
        self.assertTrue(self.installer.isProductInstalled('collective.eeafaceted.dashboard'))
        self.assertEqual(
            self.portal.dashboard.objectIds(),
            ['every-elements', 'my-elements', 'elements-to-review', 'expired-elements'])
        # setuphandlers.add_demo_data: faceted dashboard, left column hidden, default collection
        dashboard = self.portal.dashboard
        self.assertTrue(IFacetedNavigable.providedBy(dashboard))
        self.assertEqual(IFacetedLayout(dashboard).layout, 'faceted-table-items')
        self.assertTrue(IHidePloneLeftColumn.providedBy(dashboard))
        self.assertEqual(getCollectionLinkCriterion(dashboard).default, dashboard['every-elements'].UID())
        self.assertEqual(
            [(c.id, c.showNumberOfItems) for c in dashboard.objectValues()],
            [('every-elements', False), ('my-elements', False),
             ('elements-to-review', True), ('expired-elements', True)])
        self.assertEqual(
            dashboard['my-elements'].customViewFields,
            [u'pretty_link', u'Creator', u'CreationDate', u'ModificationDate', u'review_state', u'select_row'])
