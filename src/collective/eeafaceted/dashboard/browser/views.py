# -*- coding: utf-8 -*-
from collective.eeafaceted.collectionwidget.browser.views import RenderTermView as BaseRenderTermView
from collective.eeafaceted.collectionwidget.interfaces import IDashboardCollection
from collective.eeafaceted.collectionwidget.utils import getCollectionLinkCriterion
from collective.eeafaceted.collectionwidget.widgets.widget import CollectionWidget
from collective.eeafaceted.dashboard.config import CURRENT_CRITERION
from collective.eeafaceted.dashboard.interfaces import ICountableTab
from eea.facetednavigation.subtypes.interfaces import IFacetedNavigable
from plone import api
from Products.Five.browser import BrowserView
from zope.globalrequest import getRequest

import json


class RenderTermPortletView(BaseRenderTermView):

    selected_term = ''
    compute_count_on_init = False

    def __call__(self, term, category, widget):
        self.request = getRequest()
        self.term = term
        self.category = category
        self.widget = widget
        pqi = api.portal.get_tool('portal_quickinstaller')
        if pqi.isProductInstalled('collective.querynextprev'):
            session = self.request.get('SESSION', {})
            if session.has_key(CURRENT_CRITERION):  # noqa
                self.selected_term = session[CURRENT_CRITERION]

        return self.index()


class JSONCollectionsCount(BrowserView):

    """Produce json to update counts."""

    def get_context(self, faceted_context):
        while not IFacetedNavigable.providedBy(faceted_context) and \
                not faceted_context.meta_type == 'Plone Site':
            return self.get_context(faceted_context.aq_inner.aq_parent)
        return faceted_context

    def __call__(self):
        # view may be called on a faceted context or a sub-element, if it is a sub-element
        # get the first parent that is a faceted
        res = {}
        faceted_context = self.get_context(self.context)
        if faceted_context.meta_type != 'Plone Site':
            data = getCollectionLinkCriterion(faceted_context)
            widget = CollectionWidget(faceted_context, self.request, data)
            voc = widget._generate_vocabulary()
            info = []
            portal = api.portal.get()
            for category in voc.itervalues():
                for term in category['collections']:
                    collection = portal.unrestrictedTraverse(term.value)
                    if IDashboardCollection.providedBy(collection) \
                            and collection.showNumberOfItems:
                        view = collection.unrestrictedTraverse(
                            '@@render_collection_widget_term_portlet')
                        info.append({
                            'uid': term.token,
                            'count': view.number_of_items()
                        })
            res = {'criterionId': data.__name__,
                   'countByCollection': info}
        return json.dumps(res)


class JSONListCountableTabs(BrowserView):

    """Produce json to list all portal tabs that require a counter of items to take care of."""

    def __call__(self):
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog.unrestrictedSearchResults(object_provides=ICountableTab.__identifier__)
        return json.dumps({'urls': [brain.getURL() for brain in brains]})
