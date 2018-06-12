# -*- coding: utf-8 -*-

from DateTime import DateTime
from plone import api

from collective.documentgenerator.helper.base import DisplayProxyObject
from collective.documentgenerator.helper.base import DocumentGenerationHelperView

from eea.facetednavigation.interfaces import ICriteria

from collective.eeafaceted.dashboard.testing import IntegrationTestCase


class TestDocumentGeneration(IntegrationTestCase):
    """Test the document-generation that has been overrided from
       collective.documentgenerator to be 'dashboard aware'."""

    def setUp(self):
        """ """
        super(TestDocumentGeneration, self).setUp()
        # create a folder2 that will be displayed in the dashboard
        self.folder2 = api.content.create(id='folder2',
                                          type='Folder',
                                          title='Folder 2',
                                          container=self.portal)
        self.folder2.creation_date = self.folder2.created() - 1
        self.folder2.reindexObject()
        self.dashboardtemplate = api.content.create(
            id='dashboardtemplate',
            type='DashboardPODTemplate',
            title='Dashboard template',
            enabled=True,
            context_variables=[{'name': 'details', 'value': '1'}],
            container=self.folder2,
        )
        self.view = self.folder.restrictedTraverse('@@document-generation')
        self.helper = self.view.get_generation_context_helper()

    def test_get_generation_context(self):
        """
        Changes are about 'uids' and 'brains' that are added to the
        pod template generation context if possible
        if nothing particular is done, every elements of the displayed
        dashboard are added to the template generation context.
        """
        # document-generator view is called outside dashboard from base viewlet
        gen_context = self.view._get_generation_context(self.helper, self.dashboardtemplate)
        self.assertIn('view', gen_context)
        self.assertNotIn('facetedQuery', gen_context)
        self.assertIn('details', gen_context)

        # document-generator view is called from dashboard viewlet
        self.request.form['facetedQuery'] = ''
        # order is respected so sort_on created
        # Date catalog queries are 1 minute sensitive...
        # make sure self.folder created is really older than self.folder2
        self.folder.creation_date = DateTime('2015/01/01 12:00')
        self.folder.reindexObject()
        self.assertEquals(ICriteria(self.folder).get('c0').widget,
                          u'sorting')
        self.request.form['c0[]'] = 'created'

        gen_context = self.view._get_generation_context(self.helper, self.dashboardtemplate)
        self.assertTrue('uids' in gen_context)
        self.assertEquals(len(gen_context['uids']), 3)
        self.assertTrue('brains' in gen_context)
        self.assertEquals(len(gen_context['brains']), 3)
        self.assertEqual(gen_context['details'], '1')
        # brains are sorted according to uids list
        self.assertEquals(gen_context['uids'],
                          [brain.UID for brain in gen_context['brains']])

        # we have 3 elements in the dashboard : self.folder and self.folder2
        self.assertListEqual(['Folder', 'Folder 2', 'Dashboard template'],
                             [brain.Title for brain in gen_context['brains']])

        # order of query is kept in brains
        self.request.form['reversed'] = 'on'
        gen_context = self.view._get_generation_context(self.helper, self.dashboardtemplate)
        self.assertListEqual(['Dashboard template', 'Folder 2', 'Folder'],
                             [brain.Title for brain in gen_context['brains']])

    def test_get_generation_context_filtered_query(self):
        """
        If a filter is used in the facetedQuery, elements displayed
        in the dashboard are correctly given to the template.
        """
        faceted_query = self.folder.restrictedTraverse('@@faceted_query')
        # for now 3 elements
        self.assertEquals(len(faceted_query.query()), 3)
        # filter on text, 'Folder 2'
        self.assertEquals(ICriteria(self.folder).get('c2').index,
                          u'SearchableText')
        self.request.form['c2[]'] = 'Folder 2'
        self.assertEquals(len(faceted_query.query()), 1)
        # generation context respect query
        self.request.form['facetedQuery'] = ''
        gen_context = self.view._get_generation_context(self.helper, self.dashboardtemplate)
        self.assertEquals(len(gen_context['uids']), 1)

        # facetedQuery is passed to the generation context as json
        # reset query, back to 3 elements found
        self.request.form = {}
        self.assertEquals(len(faceted_query.query()), 3)
        self.request.form['facetedQuery'] = ''
        gen_context = self.view._get_generation_context(self.helper, self.dashboardtemplate)
        self.assertEquals(len(gen_context['uids']), 3)
        # 'facetedQuery' is received as a serialized JSON of query criteria
        self.request.form['facetedQuery'] = '{"c2":"Folder 2"}'
        gen_context = self.view._get_generation_context(self.helper, self.dashboardtemplate)
        self.assertEquals(len(gen_context['uids']), 1)

    def test_get_generation_context_filtered_uids(self):
        """We may also filter 'uids' directly if set in the REQUEST."""
        # for now 2 elements
        self.request.form['facetedQuery'] = ''
        gen_context = self.view._get_generation_context(self.helper, self.dashboardtemplate)
        self.assertEquals(len(gen_context['uids']), 3)
        self.assertEquals(len(gen_context['brains']), 3)
        self.request.form['uids'] = self.folder.UID()
        gen_context = self.view._get_generation_context(self.helper, self.dashboardtemplate)
        self.assertEquals(len(gen_context['uids']), 1)
        self.assertEquals(len(gen_context['brains']), 1)

    def test_generation_context_with_use_objects(self):
        """Activate the field 'use_object' on the dashboard POD template"""
        self.request.form['facetedQuery'] = ''
        gen_context = self.view._get_generation_context(self.helper, self.dashboardtemplate)
        # so far, no objects in the generation context
        self.assertEquals(gen_context.get('objects'), None)

        # enable 'use_objects'
        self.dashboardtemplate.use_objects = True
        gen_context = self.view._get_generation_context(self.helper, self.dashboardtemplate)
        self.assertEquals(len(gen_context['objects']), 3)
        self.assertEquals(len(gen_context['all']), 3)

        objs = [b.getObject() for b in gen_context['brains']]
        for proxy_obj, helper in gen_context['objects']:
            self.assertTrue(isinstance(proxy_obj, DisplayProxyObject))
            self.assertTrue(isinstance(helper, DocumentGenerationHelperView))
            self.assertTrue(proxy_obj.context in objs)
            self.assertTrue(helper.real_context in objs)

        for brain, proxy_obj, helper in gen_context['all']:
            self.assertTrue(isinstance(proxy_obj, DisplayProxyObject))
            self.assertTrue(isinstance(helper, DocumentGenerationHelperView))
            self.assertTrue(proxy_obj.context == brain.getObject())
            self.assertTrue(helper.real_context == brain.getObject())
