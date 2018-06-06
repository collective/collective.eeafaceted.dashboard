# -*- coding: utf-8 -*-

from plone.app.contenttypes.behaviors.collection import Collection
from plone.app.contenttypes.behaviors.collection import ICollection
from plone.autoform import directives as form
from zope.interface import implements
from z3c.form.browser.radio import RadioFieldWidget
from zope import schema

from Products.CMFCore.utils import getToolByName
from plone.app.collection.config import ATCT_TOOLNAME
from plone.app.querystring.queryparser import parseFormquery
from imio.dashboard.interfaces import ICustomViewFieldsVocabulary
from imio.dashboard import ImioDashboardMessageFactory as _


class IDashboardCollection(ICollection):
    """ """

    form.widget('showNumberOfItems', RadioFieldWidget)
    showNumberOfItems = schema.Bool(
        title=_(u'Show number of items in filter'),
        default=True,
        required=False,)

    form.omitted('limit')
    form.omitted('item_count')


class DashboardCollection(Collection):
    """A Collection used in our dashboards"""
    implements(IDashboardCollection)

    def listMetaDataFields(self, exclude=True):
        """
          Return a list of metadata fields from portal_catalog.
          Wrap the vocabulary in an adapter so it can be easily overrided by another package
          this is made so a package can add it's own custom columns, not only metadata.
        """
        return ICustomViewFieldsVocabulary(self).listMetaDataFields(exclude=exclude)

    def selectedViewFields(self):
        """
          Get which metadata field are selected.
          Override as it is used by the tabular_view and there, we do not display
          the additional fields or it breaks the view."""
        tool = getToolByName(self, ATCT_TOOLNAME)
        metadatas = [metadata.index for metadata in tool.getEnabledMetadata()]
        _mapping = {}
        for field in self.listMetaDataFields().items():
            if not field[0] in metadatas:
                continue
            _mapping[field[0]] = field
        return [_mapping[field] for field in self.customViewFields if field in metadatas]

    def displayCatalogQuery(self):
        """
          Return the stored query as a readable catalog query."""
        return parseFormquery(self, self.query)
