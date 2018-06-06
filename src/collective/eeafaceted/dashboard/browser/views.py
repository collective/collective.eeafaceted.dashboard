# -*- coding: utf-8 -*-
import json
import pkg_resources

from zope.globalrequest import getRequest
from plone import api
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.eeafaceted.collectionwidget.browser.views import RenderTermView as BaseRenderTermView
from collective.eeafaceted.collectionwidget.utils import getCollectionLinkCriterion
from collective.eeafaceted.collectionwidget.widgets.widget import CollectionWidget

from imio.dashboard.adapters import CURRENT_CRITERION
from imio.dashboard.interfaces import IDashboardCollection


class RenderTermView(BaseRenderTermView):

    index = ViewPageTemplateFile(
        pkg_resources.resource_filename(
            'collective.eeafaceted.collectionwidget',
            'browser/templates/term.pt'))

    def display_number_of_items(self):
        """Display number of items in the collection."""
        if not IDashboardCollection.providedBy(self.context):
            return False
        return self.context.getShowNumberOfItems() or False


class RenderTermPortletView(BaseRenderTermView):

    selected_term = ''

    def display_number_of_items(self):
        """Display number of items in the collection."""
        if not IDashboardCollection.providedBy(self.context):
            return False
        return self.context.getShowNumberOfItems() or False

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

    def __call__(self):
        data = getCollectionLinkCriterion(self.context)
        widget = CollectionWidget(self.context, self.request, data)
        voc = widget._generate_vocabulary()
        info = []
        for category in voc.itervalues():
            for term in category['collections']:
                collection = api.content.get(UID=term.token)
                if IDashboardCollection.providedBy(collection) \
                        and collection.getShowNumberOfItems():
                    view = collection.unrestrictedTraverse(
                        '@@render_collection_widget_term_portlet')
                    info.append({
                        'uid': term.token,
                        'count': view.number_of_items()
                        })
        return json.dumps({
            'criterionId': data.__name__,
            'countByCollection': info
            })
