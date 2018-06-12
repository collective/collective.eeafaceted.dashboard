# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from plone import api
from collective.eeafaceted.dashboard.testing import IntegrationTestCase
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
            container=self.portal
        )
        self.dashboardcollection = api.content.create(
            id='dc1',
            type='DashboardCollection',
            title='Dashboard collection 1',
            container=self.portal
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
