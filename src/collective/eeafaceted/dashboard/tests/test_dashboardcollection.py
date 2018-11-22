# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from plone import api
from collective.eeafaceted.collectionwidget.utils import getCollectionLinkCriterion
from collective.eeafaceted.dashboard.testing import IntegrationTestCase
from collective.eeafaceted.dashboard.utils import enableFacetedDashboardFor
from zope.component import queryUtility
from zope.schema.interfaces import IVocabularyFactory


class TestDashboardCollection(IntegrationTestCase):
    """Test the DashboardCollection content type."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.collection = api.content.create(
            id='c1',
            type='Collection',
            title='Collection 1',
            container=self.portal.folder
        )
        self.dashboardcollection = api.content.create(
            id='dc1',
            type='DashboardCollection',
            title='Dashboard collection 1',
            container=self.portal.folder
        )

    def test_MetaDataFieldsVocabulary(self):
        """For DashboardCollection, vocabulary is available collective.eeafaceted.z3ctable
           defined columns, but for classic Collections, the normal behaviour persists."""
        # test for presence of special metadata 'select_row'
        factory = queryUtility(IVocabularyFactory, u'plone.app.contenttypes.metadatafields')
        # classic Collection
        self.assertFalse('select_row' in factory(self.collection).by_token.keys())
        # DashboardCollection
        self.assertTrue('select_row' in factory(self.dashboardcollection).by_token.keys())

    def test_enableFacetedDashboardFor_with_default_UID(self):
        """ """
        collection_uid = self.collection.UID()
        enableFacetedDashboardFor(self.portal.folder, default_UID=collection_uid)
        self.assertEqual(getCollectionLinkCriterion(self.portal.folder).default, collection_uid)
