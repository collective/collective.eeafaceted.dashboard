# encoding: utf-8

from collective.documentgenerator.adapters import GenerablePODTemplatesAdapter
from collective.eeafaceted.dashboard.content.pod_template import IDashboardPODTemplate
from collective.eeafaceted.z3ctable.interfaces import IFacetedColumn
from plone import api
from zope.component import getGlobalSiteManager
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class CustomViewFieldsVocabularyAdapter(object):
    """Handles customViewFields for default plone.app.contenttypes collection."""

    def __init__(self, context):
        self.context = context
        self.request = getRequest()

    def __call__(self):
        """See docstring in interfaces.py."""

        gsm = getGlobalSiteManager()
        columns = [adapter.name for adapter in list(gsm.registeredAdapters())
                   if issubclass(adapter.provided, IFacetedColumn)]

        terms = [
            SimpleTerm(
                name,
                name,
                translate(name,
                          'collective.eeafaceted.z3ctable',
                          context=self.request)) for name in sorted(set(columns))]

        return SimpleVocabulary(terms)


class DashboardGenerablePODTemplatesAdapter(GenerablePODTemplatesAdapter):
    """ """

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
