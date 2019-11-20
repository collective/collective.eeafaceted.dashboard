# -*- coding: utf-8 -*-

from collective.documentgenerator.viewlets.generationlinks import DocumentGeneratorLinksViewlet
from collective.eeafaceted.collectionwidget.utils import getCurrentCollection
from collective.eeafaceted.dashboard.browser.overrides import DashboardDocumentGeneratorLinksViewlet
from collective.eeafaceted.dashboard.testing import IntegrationTestCase
from eea.facetednavigation.criteria.interfaces import ICriteria
from eea.facetednavigation.interfaces import IFacetedNavigable
from plone import api
from zope.annotation import IAnnotations


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
        self.assertEquals(len(viewlet.get_generable_templates()), 1)
        self.assertEquals(viewlet.get_generable_templates()[0].UID(),
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
        self.assertEquals(getCurrentCollection(self.folder), dashboardcoll)
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
        self.assertEquals(len(viewlet.get_generable_templates()), 1)
        self.assertEquals(viewlet.get_generable_templates()[0].UID(),
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
