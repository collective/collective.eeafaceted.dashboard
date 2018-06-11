# encoding: utf-8

from operator import attrgetter

from zope.interface import implements
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from plone import api
from plone.app.contenttypes.behaviors.collection import MetaDataFieldsVocabulary
from plone.app.uuid.utils import uuidToCatalogBrain
from plone.memoize import ram


from collective.eeafaceted.collectionwidget.vocabulary import CollectionVocabulary
from eea.facetednavigation.interfaces import IFacetedNavigable

from imio.helpers.cache import get_cachekey_volatile
from collective.eeafaceted.collectionwidget.interfaces import IDashboardCollection
from collective.eeafaceted.dashboard.interfaces import ICustomViewFieldsVocabulary


class CachedCollectionVocabulary(CollectionVocabulary):

    def __call___cachekey(method, self, context):
        '''cachekey method for self.__call__.'''
        return self._cache_invalidation_key(context)

    def _cache_invalidation_key(self, context):
        '''The key will rely on :
           - by user, in case faceted is stored in the user personal folder;
           - a stored cache volatile that is destroyed if a DashboardCollection is modified somewhere;
           - the first facetednavigable context encountered when ascending context parents.'''
        user = api.user.get_current()
        date = get_cachekey_volatile('collective.eeafaceted.dashboard.conditionawarecollectionvocabulary')
        parent = context
        while not IFacetedNavigable.providedBy(parent) and parent.meta_type != 'Plone Site':
            parent = parent.aq_parent
        return user, date, parent

    @ram.cache(__call___cachekey)
    def __call__(self, context):
        """Same behaviour as the original CollectionVocabulary
           but we will filter Collections regarding the defined tal_condition."""
        terms = super(CachedCollectionVocabulary, self).__call__(context)
        return terms


CachedCollectionVocabularyFactory = CachedCollectionVocabulary()


class DashboardCollectionsVocabulary(object):
    """
    Vocabulary factory for 'dashboard_collections' field of DashboardPODTemplate.
    """

    implements(IVocabularyFactory)

    def __call__(self, context):
        catalog = api.portal.get_tool('portal_catalog')
        collection_brains = catalog(object_provides=IDashboardCollection.__identifier__)
        vocabulary = SimpleVocabulary(
            [SimpleTerm(b.UID, b.UID, b.Title) for b in collection_brains]
        )
        return vocabulary

DashboardCollectionsVocabularyFactory = DashboardCollectionsVocabulary()


class DashboardCategoryCollectionsVocabulary(object):
    """
    Vocabulary factory for 'dashboard_collections' field of DashboardPODTemplate.
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

    def __call__(self, context):
        if context.portal_type == 'DashboardCollection':
            return ICustomViewFieldsVocabulary(context)()
        else:
            # original behavior for plone.app.contenttypes Collection
            return super(DashboardMetaDataFieldsVocabulary, self).__call__(context)

DashboardMetaDataFieldsVocabularyFactory = DashboardMetaDataFieldsVocabulary()
