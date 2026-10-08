# -*- coding: utf-8 -*-

from collective.documentgenerator.viewlets.generationlinks import DocumentGeneratorLinksViewlet
from collective.eeafaceted.collectionwidget.utils import getCurrentCollection
from collective.eeafaceted.dashboard.browser.overrides import DashboardDocumentGeneratorLinksViewlet
from collective.eeafaceted.dashboard.testing import IntegrationTestCase
from eea.facetednavigation.criteria.interfaces import ICriteria
from eea.facetednavigation.interfaces import IFacetedNavigable
from plone import api
from zope.annotation import IAnnotations

import lxml.html


class TestViewlets(IntegrationTestCase):

    def setUp(self):
        super(TestViewlets, self).setUp()
        # add a non faceted folder
        self.folder2 = api.content.create(id='folder2',
                                          type='Folder',
                                          title='Folder without faceted navigation',
                                          container=self.portal)

    def test_PODTemplateViewlet(self):
        """Test the IDDocumentGeneratorLinksViewlet
        that list available PODTemplates."""

        # by default, viewlet is not displayed as no template to display
        viewlet = DocumentGeneratorLinksViewlet(self.folder2,
                                                self.request,
                                                None,
                                                None)
        viewlet.update()
        self.assertFalse(viewlet.available())
        self.assertFalse(viewlet.get_generable_templates())

        # add a DashboardPODTemplate, still not available
        api.content.create(id='dashtemplate',
                           type='DashboardPODTemplate',
                           title='Dashboard template',
                           container=self.portal)
        # need to clean memoize because available() calls
        # get_generable_templates that use it
        del IAnnotations(self.request)['plone.memoize']
        self.assertFalse(viewlet.available())
        self.assertFalse(viewlet.get_generable_templates())

        # add a PODTemplate, this time it is available
        template = api.content.create(id='template',
                                      type='PODTemplate',
                                      title='POD template',
                                      container=self.portal)
        # clean memoize
        del IAnnotations(self.request)['plone.memoize']
        self.assertTrue(viewlet.available())
        self.assertEqual(len(viewlet.get_generable_templates()), 1)
        self.assertEqual(viewlet.get_generable_templates()[0].UID(),
                          template.UID())

        # this viewlet will not be displayed if current context is a faceted
        self.assertFalse(IFacetedNavigable.providedBy(self.folder2))
        self.assertTrue(IFacetedNavigable.providedBy(self.folder))
        viewlet = DocumentGeneratorLinksViewlet(self.folder,
                                                self.request,
                                                None,
                                                None)
        viewlet.update()
        del IAnnotations(self.request)['plone.memoize']
        self.assertTrue(viewlet.available())
        # no matter there are pod templates
        self.assertTrue(viewlet.get_generable_templates())

    def test_DashboardPODTemplateViewlet(self):
        """Test the IDDashboardDocumentGeneratorLinksViewlet
        that list available DashboardPODTemplates."""

        # by default, viewlet is not displayed as no template to display
        # but it needs a faceted enabled folder and to be able to getCurrentCollection
        self.assertTrue(IFacetedNavigable.providedBy(self.folder))
        dashboardcoll = api.content.create(
            id='dc1',
            type='DashboardCollection',
            title='Dashboard collection 1',
            container=self.folder
        )
        self.request.form['c1[]'] = dashboardcoll.UID()
        self.assertEqual(getCurrentCollection(self.folder), dashboardcoll)
        viewlet = DashboardDocumentGeneratorLinksViewlet(self.folder,
                                                         self.request,
                                                         None,
                                                         None)
        viewlet.update()
        self.assertFalse(viewlet.available())
        self.assertFalse(viewlet.get_generable_templates())

        # add a PODTemplate, still not available
        api.content.create(id='template',
                           type='PODTemplate',
                           title='POD template',
                           container=self.portal)
        # need to clean memoize because available() calls
        # get_generable_templates that use it
        del IAnnotations(self.request)['plone.memoize']
        self.assertFalse(viewlet.available())
        self.assertFalse(viewlet.get_generable_templates())

        # add a DashboardPODTemplate, this time it is available
        dashtemplate = api.content.create(id='dashtemplate',
                                          type='DashboardPODTemplate',
                                          title='Dashboard template',
                                          container=self.portal)
        # clean memoize
        del IAnnotations(self.request)['plone.memoize']
        self.assertTrue(viewlet.available())
        self.assertEqual(len(viewlet.get_generable_templates()), 1)
        self.assertEqual(viewlet.get_generable_templates()[0].UID(),
                          dashtemplate.UID())

        # this viewlet will not be displayed if current context is not a faceted
        self.assertFalse(IFacetedNavigable.providedBy(self.folder2))
        self.assertTrue(IFacetedNavigable.providedBy(self.folder))
        # not faceted context
        viewlet = self._get_viewlet(context=self.folder2, manager_name='collective.eeafaceted.z3ctable.topabovenav',
                                    viewlet_name='dashboard-document-generation-link')
        self.assertIsNone(viewlet)
        # collection criterion not found
        viewlet = self._get_viewlet(context=self.folder, manager_name='collective.eeafaceted.z3ctable.topabovenav',
                                    viewlet_name='dashboard-document-generation-link')
        self.assertIsNotNone(viewlet)
        del IAnnotations(self.request)['plone.memoize']
        self.assertTrue(viewlet.available())
        criteria = ICriteria(self.folder).criteria
        index = [i for i, crit in enumerate(criteria) if crit.widget == u'collection-link'][0]
        del criteria[index]  # we remove collectionwidget criterion
        self.assertFalse(viewlet.available())
        # no matter there are pod templates
        self.assertTrue(viewlet.get_generable_templates())

    def _get_generation_links_viewlet(self):
        api.content.create(id='dashtemplate', type='DashboardPODTemplate', title='Dashboard template',
                           container=self.portal, pod_formats=['odt', 'pdf'])
        viewlet = self._get_viewlet(context=self.folder, manager_name='collective.eeafaceted.z3ctable.topabovenav',
                                    viewlet_name='dashboard-document-generation-link')
        viewlet.update()
        return viewlet

    def test_get_links_info(self):
        viewlet = self._get_generation_links_viewlet()
        links = viewlet.get_links_info()
        self.assertEqual(list(links.keys()), ['Dashboard template'])
        self.assertEqual([link['output_format'] for link in links['Dashboard template']], ['odt', 'pdf'])
        for link in links['Dashboard template']:
            self.assertEqual(link['max'], 500)
            self.assertEqual(link['description'], u'Only the first ${nb} items will be generated')
            self.assertEqual(link['description'].domain, 'collective.eeafaceted.dashboard')
            self.assertEqual(link['description'].mapping, {u'nb': 500})
        # no limit
        self.portal.dashtemplate.max_objects = 0
        self.assertEqual([link['max'] for link in viewlet.get_links_info()['Dashboard template']], [0, 0])

    def test_render(self):
        """generationlinks.pt: the POST form filled by generatePodDocument and a link by format."""
        viewlet = self._get_generation_links_viewlet()
        template_uid = self.portal.dashtemplate.UID()
        html = lxml.html.fromstring(viewlet.render())
        self.assertEqual(html.get('id'), 'doc-generation-view')
        form = html.xpath('form[@name="podTemplateForm"]')[0]
        self.assertEqual(form.get('action'), 'http://nohost/plone/folder/document-generation')
        self.assertEqual(form.get('method'), 'POST')
        self.assertEqual(form.get('target'), '_blank')
        self.assertEqual(form.xpath('input[@type="hidden"]/@name'),
                         ['template_uid', 'output_format', 'uids', 'facetedQuery'])
        self.assertEqual(form.xpath('.//li[@class="template-link"]/span[@class="template-link-title"]/text()'),
                         ['Dashboard template'])
        links = form.xpath('.//li[@class="template-link"]//a')
        self.assertEqual(
            [a.get('onclick') for a in links],
            ["event.preventDefault();javascript:generatePodDocument('{0}','{1}', this)".format(template_uid, fmt)
             for fmt in ('odt', 'pdf')])
        self.assertEqual([a.get('title') for a in links], ['Only the first 500 items will be generated'] * 2)
        self.assertEqual(
            [a.xpath('img[@class="svg-icon"]/@src')[0] for a in links],
            ['http://nohost/plone/++resource++collective.documentgenerator/odt.svg',
             'http://nohost/plone/++resource++collective.documentgenerator/pdf.svg'])
        self.assertEqual([a.xpath('img/@alt')[0] for a in links], ['Dashboard template ODT', 'Dashboard template PDF'])
        self.assertEqual([a.xpath('normalize-space(.//span[@class="highlightValue"])') for a in links],
                         ['500 max', '500 max'])
        # no limit: no max displayed
        self.portal.dashtemplate.max_objects = 0
        html = lxml.html.fromstring(viewlet.render())
        self.assertEqual(len(html.xpath('.//li[@class="template-link"]//a')), 2)
        self.assertEqual(html.xpath('.//span[@class="highlightValue"]'), [])
