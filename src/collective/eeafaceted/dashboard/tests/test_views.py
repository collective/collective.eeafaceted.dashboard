# -*- coding: utf-8 -*-
"""Test views."""
import json

from plone import api

from imio.dashboard.testing import IntegrationTestCase


class TestJSONCollectionsCount(IntegrationTestCase):

    def setUp(self):
        super(TestJSONCollectionsCount, self).setUp()
        self.view = self.folder.unrestrictedTraverse('@@json_collections_count')

    def test_folder_empty(self):
        expected = json.dumps({'criterionId': 'c1', 'countByCollection': []})
        self.assertEqual(self.view(), expected)

    def test_with_dashboard_collections(self):
        dashboardcoll = api.content.create(
            id='dc1',
            type='DashboardCollection',
            title='Dashboard collection 1',
            container=self.folder
        )
        dashboardcol2 = api.content.create(
            id='dc2',
            type='DashboardCollection',
            title='Dashboard collection 2',
            container=self.folder
        )
        dashboardcol3 = api.content.create(
            id='dc3',
            type='DashboardCollection',
            title='Dashboard collection 3',
            container=self.folder
        )
        dashboardcoll.setShowNumberOfItems(True)
        dashboardcol2.setShowNumberOfItems(False)
        dashboardcol3.setShowNumberOfItems(True)

        dashboardcoll.query = [
            {
                'i': 'portal_type',
                'o': 'plone.app.querystring.operation.selection.is',
                'v': ['DashboardCollection', ]
            },
        ]
        expected = {
            'criterionId': 'c1',
            'countByCollection': [
                {'uid': dashboardcoll.UID(), 'count': 3},
                {'uid': dashboardcol3.UID(), 'count': 0},
            ]
        }
        self.assertEqual(self.view(), json.dumps(expected))

    def test_with_collections(self):
        col = api.content.create(
            id='col1',
            type='Collection',
            title='collection 1',
            container=self.folder
        )

        col.query = [
            {
                'i': 'portal_type',
                'o': 'plone.app.querystring.operation.selection.is',
                'v': ['Collection', ]
            },
        ]
        expected = {
            'criterionId': 'c1',
            'countByCollection': []
        }
        self.assertEqual(self.view(), json.dumps(expected))
