# encoding: utf-8

from operator import attrgetter

from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from plone import api
from plone.app.uuid.utils import uuidToCatalogBrain
from plone.memoize import ram
from Products.CMFPlone.utils import safe_unicode

from collective.behavior.talcondition.interfaces import ITALConditionable
from collective.behavior.talcondition.utils import evaluateExpressionFor
from collective.eeafaceted.collectionwidget.vocabulary import CollectionVocabulary
from eea.faceted.vocabularies.catalog import CatalogIndexesVocabulary
from eea.facetednavigation.interfaces import IFacetedNavigable

from imio.helpers.cache import get_cachekey_volatile
from imio.dashboard.config import COMBINED_INDEX_PREFIX
from imio.dashboard.interfaces import IDashboardCollection

from Products.CMFCore.utils import getToolByName


class ConditionAwareCollectionVocabulary(CollectionVocabulary):

    def __call___cachekey(method, self, context):
        '''cachekey method for self.__call__.'''
        return self._cache_invalidation_key(context)

    def _cache_invalidation_key(self, context):
        '''The key will rely on :
           - by user, in case faceted is stored in the user personal folder;
           - a stored cache volatile that is destroyed if a DashboardCollection is modified somewhere;
           - the first facetednavigable context encountered when ascending context parents.'''
        user = api.user.get_current()
        date = get_cachekey_volatile('imio.dashboard.conditionawarecollectionvocabulary')
        parent = context
        while not IFacetedNavigable.providedBy(parent) and parent.meta_type != 'Plone Site':
            parent = parent.aq_parent
        return user, date, parent

    @ram.cache(__call___cachekey)
    def __call__(self, context):
        """Same behaviour as the original CollectionVocabulary
           but we will filter Collections regarding the defined tal_condition."""
        terms = super(ConditionAwareCollectionVocabulary, self).__call__(context)
        filtered_terms = []
        # compute extra_expr_ctx given to evaluateExpressionFor only once
        extra_expr_ctx = self._extra_expr_ctx()
        for term in terms:
            collection = term.value
            # if collection is ITALConditionable, evaluate the TAL condition
            # except if current user is Manager
            if ITALConditionable.providedBy(collection):
                if not evaluateExpressionFor(collection, extra_expr_ctx=extra_expr_ctx):
                    continue
            filtered_terms.append(term)
        return SimpleVocabulary(filtered_terms)

    def _extra_expr_ctx(self):
        """To be overrided, this way, extra_expr_ctx is given to the
           expression evaluated on the DashboardCollection."""
        return {}

ConditionAwareCollectionVocabularyFactory = ConditionAwareCollectionVocabulary()


class CreatorsVocabulary(object):
    implements(IVocabularyFactory)

    def __call__cachekey(method, self, context):
        '''cachekey method for self.__call__.'''
        catalog = getToolByName(context, 'portal_catalog')
        return context, catalog.uniqueValuesFor('Creator')

    def _get_user_fullname(self, login):
        """Get fullname without using getMemberInfo that is slow slow slow..."""
        storage = api.portal.get_tool('acl_users').mutable_properties._storage
        data = storage.get(login, None)
        if data is not None:
            return data.get('fullname', '') or login
        else:
            return login

    @ram.cache(__call__cachekey)
    def __call__(self, context):
        """ """
        catalog = getToolByName(context, 'portal_catalog')
        res = []
        for creator in catalog.uniqueValuesFor('Creator'):
            fullname = self._get_user_fullname(creator)
            res.append(SimpleTerm(creator,
                                  creator,
                                  safe_unicode(fullname))
                       )
        res = sorted(res, key=attrgetter('title'))
        return SimpleVocabulary(res)

CreatorsVocabularyFactory = CreatorsVocabulary()


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


class CombinedCatalogIndexesVocabulary(CatalogIndexesVocabulary):
    """ Return catalog indexes as vocabulary and dummy indexes prefixed
        with 'combined__' used to be combined at query time with the corresponding
        index not prefixed with 'combined__'.
    """

    def __call__(self, context):
        """ Call original indexes and append 'combined__' prefixed ones.
        """
        indexes = super(CombinedCatalogIndexesVocabulary, self).__call__(context)
        res = list(indexes)
        for index in indexes:
            if not index.value:
                # ignore the '' value
                continue
            key = COMBINED_INDEX_PREFIX + index.value
            value = '(Combined) ' + index.title
            res.append(SimpleTerm(key, key, value))
        return SimpleVocabulary(res)
