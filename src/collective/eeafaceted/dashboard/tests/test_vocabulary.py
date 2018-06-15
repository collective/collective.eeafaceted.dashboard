# -*- coding: utf-8 -*-
from zope.component import queryUtility
from zope.interface import alsoProvides
from zope.schema.interfaces import IVocabularyFactory
from plone import api
from collective.eeafaceted.dashboard.testing import IntegrationTestCase
from eea.facetednavigation.interfaces import IFacetedNavigable
from collective.eeafaceted.dashboard.vocabulary import DashboardCollectionsVocabulary


class TestConditionAwareVocabulary(IntegrationTestCase):
    """Test the ConditionAwareCollectionVocabulary vocabulary."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        # make sure we have a default workflow
        self.wfTool = self.portal.portal_workflow
        self.wfTool.setDefaultChain('simple_publication_workflow')
        self.folder = api.content.create(id='f', type='Folder', title='My category', container=self.portal)
        self.dashboardcollection = api.content.create(
            id='dc1',
            type='DashboardCollection',
            title='Dashboard collection 1',
            container=self.folder
        )
        alsoProvides(self.folder, IFacetedNavigable)

    def test_collectionsvocabulary(self):
        """This will return every DashboardCollections of the portal."""
        # one DashboardCollection
        factory = DashboardCollectionsVocabulary()
        self.assertEquals(len(factory(self.portal)), 1)
        term = factory(self.portal).getTerm(self.dashboardcollection.UID())
        self.assertEquals(term.token, term.value, self.dashboardcollection.UID())
        self.assertEquals(term.title, self.dashboardcollection.Title())

    def test_categorycollectionsvocabulary(self):
        """This will return every DashboardCollections of the portal prefixed by categories."""
        factory = queryUtility(IVocabularyFactory, u'collective.eeafaceted.dashboard.dashboardcollectionsvocabulary')
        # one DashboardCollection
        self.assertEquals(len(factory(self.portal)), 1)
        term = factory(self.portal).getTerm(self.dashboardcollection.UID())
        self.assertEquals(term.token, term.value, self.dashboardcollection.UID())
        self.assertEquals(term.title, '%s - %s' % (self.folder.Title(), self.dashboardcollection.Title()))
