# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from plone import api
from plone.app.contenttypes.interfaces import ICollection
from eea.facetednavigation.interfaces import IFacetedNavigable

from collective.documentgenerator.browser.generation_view import DocumentGenerationView
from collective.documentgenerator.viewlets.generationlinks import DocumentGeneratorLinksViewlet
from collective.eeafaceted.collectionwidget.widgets.widget import CollectionWidget
from collective.eeafaceted.z3ctable.browser.views import FacetedTableView

from collective.eeafaceted.dashboard.content.pod_template import IDashboardPODTemplate
from collective.eeafaceted.dashboard.utils import getDashboardQueryResult

# necessary for now for elements using ICollection from plone.app.collection
HAS_PAC = True
try:
    from plone.app.collection.interfaces import ICollection as pac_ICollection
except ImportError:
    HAS_PAC = False


class DashboardFacetedTableView(FacetedTableView):

    ignoreColumnWeight = True

    def __init__(self, context, request):
        super(DashboardFacetedTableView, self).__init__(context, request)
        self.collection = self._set_collection()

    def _set_collection(self):
        if ICollection.providedBy(self.context) or \
           (HAS_PAC and pac_ICollection.providedBy(self.context)):
            return self.context
        else:
            # if we can get the collection we are working with,
            # use customViewFields defined on it if any
            for criterion in self.criteria.values():
                if criterion.widget == CollectionWidget.widget_type:
                    # value is stored in the request with ending [], like 'c4[]'
                    collectionUID = self.request.get('{0}[]'.format(criterion.getId()))
                    if not collectionUID:
                        continue
                    catalog = getToolByName(self.context, 'portal_catalog')
                    collection = catalog(UID=collectionUID)
                    if collection:
                        return collection[0].getObject()

    def _getViewFields(self):
        """Returns fields we want to show in the table."""

        # if the context is a collection, get customViewFields on it
        if self.collection:
            selectedViewFields = self.collection.selectedViewFields()
            # selectedViewFields is a list of tuples (id, title)
            return [elt[0] for elt in selectedViewFields]

        # else get default column names
        return super(DashboardFacetedTableView, self)._getViewFields()


class DashboardDocumentGenerationView(DocumentGenerationView):
    """Override the 'get_generation_context' properly so 'get_base_generation_context'
       is available for sub-packages that want to extend the template generation context."""

    def _get_generation_context(self, helper_view, pod_template):
        """ """
        # if we are in base viewlet (not dashboard), return the base context
        if 'facetedQuery' not in self.request.form:
            return super(DashboardDocumentGenerationView, self)._get_generation_context(helper_view, pod_template)

        generation_context = {'brains': [],
                              'uids': []}

        if IFacetedNavigable.providedBy(self.context):
            brains = getDashboardQueryResult(self.context)
            generation_context['brains'] = brains
            if getattr(pod_template, 'use_objects', False):
                wrapped_objects = []
                brain_and_objects = []
                for brain in brains:
                    generation_context['uids'].append(brain.UID)
                    obj = brain.getObject()
                    helper = obj.unrestrictedTraverse('@@document_generation_helper_view')
                    wrapped_objects.append((helper.context, helper))
                    brain_and_objects.append((brain, helper.context, helper))
                generation_context['objects'] = wrapped_objects
                generation_context['all'] = brain_and_objects
            else:
                generation_context['uids'] = [brain.UID for brain in brains]

        generation_context.update(
            super(DashboardDocumentGenerationView, self)._get_generation_context(
                helper_view, pod_template))
        return generation_context


class DashboardDocumentGeneratorLinksViewlet(DocumentGeneratorLinksViewlet):
    """For displaying on dashboards."""

    def get_all_pod_templates(self):
        """
        Override to only return dashboard templates.
        """
        catalog = api.portal.get_tool(name='portal_catalog')
        brains = catalog.unrestrictedSearchResults(
            object_provides=IDashboardPODTemplate.__identifier__,
            sort_on='getObjPositionInParent'
        )
        pod_templates = [self.context.unrestrictedTraverse(brain.getPath()) for brain in brains]

        return pod_templates
