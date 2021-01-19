# -*- coding: utf-8 -*-
from collective.documentgenerator.browser.generation_view import DocumentGenerationView
from collective.documentgenerator.viewlets.generationlinks import DocumentGeneratorLinksViewlet
from collective.eeafaceted.collectionwidget.interfaces import NotDashboardContextException
from collective.eeafaceted.collectionwidget.utils import getCollectionLinkCriterion
from collective.eeafaceted.collectionwidget.utils import getCurrentCollection
from collective.eeafaceted.dashboard.interfaces import IDashboardGenerablePODTemplates
from collective.eeafaceted.dashboard.utils import getDashboardQueryResult
from collective.eeafaceted.z3ctable.browser.views import FacetedTableView
from collective.eeafaceted.dashboard import FacetedDashboardMessageFactory as _
from eea.facetednavigation.interfaces import IFacetedNavigable
from plone.app.contenttypes.interfaces import ICollection
from plone.memoize.view import memoize
from zope.component import getAdapter

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
            collection = getCurrentCollection(self.context)
            return collection

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
        """Include brains/uids if we are on a dashboard."""
        if not IFacetedNavigable.providedBy(self.context):
            return super(DashboardDocumentGenerationView, self)._get_generation_context(
                helper_view, pod_template)

        generation_context = {'brains': [],
                              'uids': []}
        brains = getDashboardQueryResult(self.context) or []
        max_objects = getattr(pod_template, 'max_objects', None)
        if max_objects:
            brains = brains[:max_objects]
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

    @memoize
    def get_generable_templates(self):
        adapter = getAdapter(self.context, IDashboardGenerablePODTemplates)
        generable_templates = adapter.get_generable_templates()
        return generable_templates

    def available(self):
        """
        Check if we have a collectionwidget criterion
        """
        try:
            getCollectionLinkCriterion(self.context)
        except NotDashboardContextException:
            return False
        return super(DashboardDocumentGeneratorLinksViewlet, self).available()

    def get_links_info(self):
        links = super(DashboardDocumentGeneratorLinksViewlet, self).get_links_info()

        for link in links:
            template = link["template"]
            link["max"] = template.max_objects
            link["description"] = _("Only the first ${nb} items will be generated",
                                    mapping={
                                        u"nb": template.max_objects
                                    })
        return links
