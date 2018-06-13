# -*- coding: utf-8 -*-
import os
from eea.facetednavigation.interfaces import ICriteria
from eea.facetednavigation.interfaces import IFacetedLayout
from eea.facetednavigation.interfaces import IFacetedNavigable
from eea.facetednavigation.interfaces import IHidePloneLeftColumn

from collective.eeafaceted.collectionwidget.interfaces import NoFacetedViewDefinedException

from collective.eeafaceted.dashboard.testing import IntegrationTestCase
from collective.eeafaceted.dashboard.utils import enableFacetedDashboardFor
from collective.eeafaceted.dashboard.utils import getCriterionByTitle
from collective.eeafaceted.dashboard.utils import getCriterionByIndex


class TestUtils(IntegrationTestCase):
    """Test the utils."""

    def test_enableFacetedDashboardFor(self):
        """This method will enable the faceted navigation for a given folder."""
        # faceted can be enabled using the default widgets
        catalog = self.portal.portal_catalog
        folder2_id = self.portal.invokeFactory('Folder', 'folder2', title='Folder2')
        folder2 = getattr(self.portal, folder2_id)
        folder2.reindexObject()
        folder2UID = folder2.UID()
        # not enabled for now
        self.assertFalse(IFacetedNavigable.providedBy(folder2))
        self.assertTrue(catalog(UID=folder2UID))
        self.assertFalse(catalog(UID=folder2UID, object_provides=IFacetedNavigable.__identifier__))
        enableFacetedDashboardFor(folder2)
        # several things are done :
        # faceted is enabled
        self.assertTrue(IFacetedNavigable.providedBy(folder2))
        # used faceted layout is 'faceted-table-items'
        self.assertEquals(IFacetedLayout(folder2).layout, 'faceted-table-items')
        # left portlets are shown
        self.assertFalse(IHidePloneLeftColumn.providedBy(folder2))
        # folder2 was reindexed, especially provided interfaces
        self.assertTrue(catalog(UID=folder2UID, object_provides=IFacetedNavigable.__identifier__))
        # redirect is swallowed, indeed enabling faceted on a folder redirects to it
        self.assertEquals(self.portal.REQUEST.RESPONSE.status, 200)

        # a xmlpath parameter can be passed to use a specific widgets xml file
        # calling this on an already enabled faceted will do nothing
        xmlpath = os.path.dirname(__file__) + '/faceted_conf/testing_widgets.xml'
        enableFacetedDashboardFor(folder2, xmlpath=xmlpath)
        # only one 'c44' widget in testing_widgets.xml, not added here
        self.assertFalse(ICriteria(folder2).get('c44'))
        # create a new folder and apply faceted with xmlpath to it
        folder3_id = self.portal.invokeFactory('Folder', 'folder3', title='Folder3')
        folder3 = getattr(self.portal, folder3_id)
        folder3.reindexObject()
        # an Exception is raised if xmlpath does not exist
        wrong_xmlpath = os.path.dirname(__file__) + '/faceted_conf/wrong_testing_widgets.xml'
        self.assertRaises(Exception, enableFacetedDashboardFor, folder3, wrong_xmlpath)
        # apply correct xmlpath
        enableFacetedDashboardFor(folder3, xmlpath=xmlpath)
        # same things are done except that the widgets are taken from the given xmlpath
        self.assertEquals(len(ICriteria(folder3).criteria), 1)
        self.assertTrue(ICriteria(folder3).get('c44'))

    def test_getCriterionByTitle(self):
        """Test method returning criteria matching a given title."""
        sort_criterion = getCriterionByTitle(self.folder, 'Sort on')
        self.assertEquals(sort_criterion.title, u'Sort on')

        # calling it on a non faceted enabled folder will raise a NoFacetedViewDefinedException
        folder2_id = self.portal.invokeFactory('Folder', 'folder2', title='Folder2')
        folder2 = getattr(self.portal, folder2_id)
        folder2.reindexObject()
        self.assertRaises(NoFacetedViewDefinedException, getCriterionByTitle, folder2, 'Sort on')

    def test_getCriterionByIndex(self):
        """Test method returning criteria matching a given search index."""
        sort_criterion = getCriterionByIndex(self.folder, 'review_state')
        self.assertEquals(sort_criterion.index, u'review_state')

        # calling it on a non faceted enabled folder will raise a NoFacetedViewDefinedException
        folder2_id = self.portal.invokeFactory('Folder', 'folder2', title='Folder2')
        folder2 = getattr(self.portal, folder2_id)
        folder2.reindexObject()
        self.assertRaises(NoFacetedViewDefinedException, getCriterionByIndex, folder2, 'review_state')
