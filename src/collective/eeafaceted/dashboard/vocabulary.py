# encoding: utf-8

from collective.eeafaceted.collectionwidget.interfaces import IDashboardCollection
from collective.eeafaceted.dashboard.interfaces import ICustomViewFieldsVocabulary
from eea.facetednavigation.interfaces import IFacetedNavigable
from operator import attrgetter
from plone import api
from plone.app.contenttypes.behaviors.collection import MetaDataFieldsVocabulary
from plone.app.uuid.utils import uuidToCatalogBrain
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class DashboardCollectionsVocabulary(object):
    """
    Vocabulary factory for 'dashboard_collections' field of DashboardPODTemplate.
    Just displays the collection title in the term.
    NOT USED BY DEFAULT, but there to be registered as
    "collective.eeafaceted.dashboard.dashboardcollectionsvocabulary" if necessary.
    """

    implements(IVocabularyFactory)

    def _render_term_title(self, brain):
        return brain.Title

    def __call__(self, context):
        catalog = api.portal.get_tool('portal_catalog')
        collection_brains = catalog(object_provides=IDashboardCollection.__identifier__)
        vocabulary = SimpleVocabulary(
            [SimpleTerm(b.UID, b.UID, self._render_term_title(b)) for b in collection_brains]
        )
        return vocabulary

DashboardCollectionsVocabularyFactory = DashboardCollectionsVocabulary()


class DashboardCategoryCollectionsVocabulary(object):
    """
    Vocabulary factory for 'dashboard_collections' field of DashboardPODTemplate.
    Displays the parent categories until the faceted container in the term.
    """

    implements(IVocabularyFactory)

    def _getParents(self, obj):
        ret = []
        while IFacetedNavigable.providedBy(obj.aq_inner.aq_parent):
            obj = obj.aq_inner.aq_parent
            ret.append(obj.UID())
        return ','.join(reversed(ret))

    def _brains(self):
        catalog = api.portal.get_tool('portal_catalog')
        return catalog(object_provides=IDashboardCollection.__identifier__)

    def __call__(self, context):
        collections = {}
        for brain in self._brains():
            obj = brain.getObject()
            parents = self._getParents(obj)
            if parents not in collections:
                collections[parents] = []
            collections[parents].append((brain.UID, brain.Title))
        terms = []
        for parents in collections:
            prefix = ' - '.join([uuidToCatalogBrain(p).Title for p in parents.split(',') if p])
            for term in collections[parents]:
                terms.append(SimpleTerm(term[0], term[0], prefix and "%s - %s" % (prefix, term[1]) or term[1]))
        terms.sort(key=attrgetter('title'))
        return SimpleVocabulary(terms)

DashboardCategoryCollectionsVocabularyFactory = DashboardCategoryCollectionsVocabulary()


@implementer(IVocabularyFactory)
class DashboardMetaDataFieldsVocabulary(MetaDataFieldsVocabulary):

    def _is_adding_new_dashboard_collection(self):
        """ """
        request = getRequest()
        published = request.get('PUBLISHED')
        if published and hasattr(published, '__name__') and published.__name__ == 'DashboardCollection':
            return True
        return False

    def __call__(self, context):
        if context.portal_type == 'DashboardCollection' or self._is_adding_new_dashboard_collection():
            return ICustomViewFieldsVocabulary(context)()
        else:
            # original behavior for plone.app.contenttypes Collection
            return super(DashboardMetaDataFieldsVocabulary, self).__call__(context)

DashboardMetaDataFieldsVocabularyFactory = DashboardMetaDataFieldsVocabulary()
