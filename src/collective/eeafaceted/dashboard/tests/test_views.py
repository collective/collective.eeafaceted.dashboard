# -*- coding: utf-8 -*-
"""Test views."""
import json

from plone import api

from collective.eeafaceted.dashboard.testing import IntegrationTestCase


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
            container=self.folder,
            tal_condition=u'',
            roles_bypassing_talcondition=[]
        )
        dashboardcol2 = api.content.create(
            id='dc2',
            type='DashboardCollection',
            title='Dashboard collection 2',
            container=self.folder,
            tal_condition=u'',
            roles_bypassing_talcondition=[]
        )
        dashboardcol3 = api.content.create(
            id='dc3',
            type='DashboardCollection',
            title='Dashboard collection 3',
            container=self.folder,
            tal_condition=u'',
            roles_bypassing_talcondition=[]
        )
        dashboardcoll.showNumberOfItems = True
        dashboardcol2.showNumberOfItems = False
        dashboardcol3.showNumberOfItems = True

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
            container=self.folder,
            tal_condition=u'',
            roles_bypassing_talcondition=[]
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

    def test_with_sub_elements(self):
        """Make sure especially the JSONCollectionsCount.get_context gets
           the faceted context when the view is called from a sub/sub element."""
        self.assertEqual(self.view.context, self.folder)
        self.assertEqual(self.view(), '{"criterionId": "c1", "countByCollection": []}')
        subfolder = api.content.create(
            id='subfolder',
            type='Folder',
            title='Subfolder',
            container=self.folder)
        self.view.context = subfolder
        self.assertEqual(self.view(), '{"criterionId": "c1", "countByCollection": []}')
        subsubfolder = api.content.create(
            id='subsubfolder',
            type='Folder',
            title='Subsubfolder',
            container=subfolder)
        self.view.context = subsubfolder
        self.assertEqual(self.view(), '{"criterionId": "c1", "countByCollection": []}')
