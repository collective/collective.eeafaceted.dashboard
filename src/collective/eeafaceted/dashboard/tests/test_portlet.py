# -*- coding: utf-8 -*-
import lxml
from zope.annotation import IAnnotations
from zope.component import getUtility
from zope.component import getMultiAdapter
from eea.facetednavigation.criteria.interfaces import ICriteria
from collective.eeafaceted.collectionwidget.interfaces import NoCollectionWidgetDefinedException
from collective.eeafaceted.collectionwidget.utils import getCollectionLinkCriterion
from collective.eeafaceted.collectionwidget.widgets.widget import CollectionWidget
from plone import api
from plone.portlets.interfaces import IPortletManager, IPortletRenderer

from collective.eeafaceted.dashboard.browser import facetedcollectionportlet as portlet
from collective.eeafaceted.dashboard.config import DEFAULT_PORTLET_TITLE
from collective.eeafaceted.dashboard.testing import IntegrationTestCase


class TestPortlet(IntegrationTestCase):
    """Test the faceted collection portlet."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.folder = self.portal.folder
        self.request = self.portal.REQUEST
        self.request.SESSION = {}
        self.view = self.portal.restrictedTraverse('@@plone')
        self.manager = getUtility(IPortletManager,
                                  name='plone.leftcolumn',
                                  context=self.portal)
        self.assignment = portlet.Assignment()
        self.renderer = self._get_portlet_renderer()
        self.subtyper = getMultiAdapter((self.folder, self.request), name=u'faceted_subtyper')

    def _get_portlet_renderer(self):
        """ """
        renderer = getMultiAdapter(
            (self.folder,
             self.request,
             self.view,
             self.manager,
             self.assignment), IPortletRenderer)
        return renderer

    def test_portlet_available_when_faceted_enabled(self):
        """The portlet will display when a faceted navigation is enabled on the folder."""
        # for now, the portlet is not displayed because the faceted is not applied
        self.assertTrue(not self.renderer.available)
        # now apply the faceted view on self.folder
        self.subtyper.enable()
        # now it is available
        self.assertTrue(self.renderer.available)

    def test_portlet_criteriaHolder(self):
        """The portlet will be displayed in folders contained by the folder
           on which the faceted nav is applied but the _criteriaHolder will always be
           the folder on which the faceted is really applied."""
        # faceted not applied, _criteriaHolder returns None
        self.assertTrue(not self.subtyper.is_faceted)
        self.assertTrue(self.renderer._criteriaHolder is None)
        # enable faceted, now the folder will be found
        self.subtyper.enable()
        self.assertTrue(self.renderer._criteriaHolder == self.folder)
        # if we add a sub folder, the _criteriaHolder will still be self.folder
        subfolder = api.content.create(
            id='subfolder',
            type='Folder',
            title='Subfolder',
            container=self.folder
        )
        renderer = getMultiAdapter((subfolder,
                                    self.request,
                                    self.view,
                                    self.manager,
                                    self.assignment),
                                   IPortletRenderer)
        self.assertTrue(renderer._criteriaHolder == self.folder)

    def test_portlet_widget_render(self):
        """The portlet will render collection-link widgets defined
           on the faceted config.  This portlet has 2 behaviours :
           - classic faceted widget behaviour when displayed directly on the folder
             on which the faceted is applied : it uses the faceted js onclick to update the faceted;
           - 'fake' widget displayed as the real widget but instead of controlling the faceted
             it has a link on every disiplayed collection that will move to the faceted
             correctly initialized."""
        self.subtyper.enable()
        criteria = ICriteria(self.renderer._criteriaHolder)
        # remove the collection-link widget
        collcriterion = getCollectionLinkCriterion(self.renderer._criteriaHolder)
        ICriteria(self.renderer._criteriaHolder).delete(collcriterion.getId())
        # by defaut no collection-link widget so nothing is rendered
        self.assertTrue(not [criterion for criterion in criteria.values()
                             if criterion.widget == CollectionWidget.widget_type])
        with self.assertRaises(NoCollectionWidgetDefinedException):
            getCollectionLinkCriterion(self.renderer._criteriaHolder)
        self.assertTrue(not self.renderer.widget_render)
        # add a collection-link widget
        data = {'vocabulary': 'collective.eeafaceted.collectionwidget.collectionvocabulary',
                'hidealloption': True}
        ICriteria(self.folder).add('collection-link', 'top', **data)
        # still displaying nothing as the collection widget does not find any collection
        self.assertTrue(not self.renderer.widget_render.strip())
        # add a DashboardCollection in self.folder
        collection = api.content.create(
            id='dashboardcollection1',
            type='DashboardCollection',
            title='Dashboard collection 1',
            container=self.folder,
            query='',
            sort_on='',
            sort_reversed=False,
            showNumberOfItems=True,
            tal_condition=u'',
            roles_bypassing_talcondition=[])
        # clean memoize for widget.categories,
        # it was memoized when calling _generate_vocabulary here above
        del IAnnotations(self.request)['plone.memoize']
        # now it is displayed and as we are on the faceted, it behaves like the collection widget
        # a <form> with an action
        # get the '<ul>' displaying collections
        # update renderer
        self.renderer = self._get_portlet_renderer()
        self.assertTrue("<form" in self.renderer.widget_render)
        ul_tag = lxml.html.fromstring(self.renderer.widget_render)[0][0]
        # only 1 children, the collection and the href is as special javascript call that does nothing
        self.assertTrue(len(ul_tag.getchildren()) == 1)
        div_tag = ul_tag.getchildren()[0]
        li_tag = div_tag.getchildren()[0]
        self.assertTrue(li_tag.attrib['value'] == collection.UID())
        self.assertTrue(len(li_tag.getchildren()) == 1)
        a_tag = li_tag.getchildren()[0]
        self.assertTrue(a_tag.attrib['href'] == 'javascript:;')

        # now get the portlet from a sub element so it behaves differently
        # it is no more a faceted widget but and the href will redirect to the faceted with default parameters
        subrenderer = getMultiAdapter((collection,
                                       self.request,
                                       self.view,
                                       self.manager,
                                       self.assignment),
                                      IPortletRenderer)
        # no more <form> this time
        self.assertTrue("<form" not in subrenderer.widget_render)
        ul_tag = lxml.html.fromstring(subrenderer.widget_render)[0]
        # only 1 children, the collection and the href is a link back to the href with correct default parameters
        self.assertTrue(len(ul_tag.getchildren()) == 1)
        li_tag = ul_tag.getchildren()[0]
        self.assertTrue(li_tag.attrib['value'] == collection.UID())
        self.assertTrue(len(li_tag.getchildren()) == 1)
        a_tag = li_tag.getchildren()[0]
        # the URL is generated and contains every default values and relevant collection UID
        url = "http://nohost/plone/folder#c3=20&c1={0}".format(collection.UID())
        self.assertEquals(a_tag.attrib['href'], url)

    def test_portlet_render(self):
        """The portlet will be rendered without a fieldset and will contains rendered widgets."""
        self.subtyper.enable()
        rendered = self.renderer.render()
        # portlet will render the widget but without surrounding fieldset
        self.assertTrue("<fieldset" not in rendered)
        self.assertTrue(self.renderer.widget_render in rendered)

    def test_portlet_title(self):
        """ """
        self.assertTrue(self.assignment.title == DEFAULT_PORTLET_TITLE)
