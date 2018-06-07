# -*- coding: utf-8 -*-

from plone.app.contenttypes.behaviors.collection import Collection
from plone.app.contenttypes.behaviors.collection import ICollection
from plone.autoform import directives as form
from zope.component import adapter
from zope.interface import implementer
from zope.interface import provider
from z3c.form.browser.radio import RadioFieldWidget
from zope import schema

from Products.CMFPlone.interfaces.syndication import ISyndicatable
from plone.app.querystring.queryparser import parseFormquery
from plone.autoform.interfaces import IFormFieldProvider
from plone.dexterity.interfaces import IDexterityContent
from imio.dashboard.interfaces import ICustomViewFieldsVocabulary
from imio.dashboard import ImioDashboardMessageFactory as _


@provider(IFormFieldProvider, ISyndicatable)
class IDashboardCollection(ICollection):
    """ """

    form.widget('showNumberOfItems', RadioFieldWidget)
    showNumberOfItems = schema.Bool(
        title=_(u'Show number of items in filter'),
        default=True,
        required=False,)

    form.omitted('limit')
    form.omitted('item_count')


@implementer(ICollection)
@adapter(IDexterityContent)
class DashboardCollection(Collection):
    """A Collection used in our dashboards"""

    def listMetaDataFields(self, exclude=True):
        """
          Return a list of metadata fields from portal_catalog.
          Wrap the vocabulary in an adapter so it can be easily overrided by another package
          this is made so a package can add it's own custom columns, not only metadata.
        """
        return ICustomViewFieldsVocabulary(self).listMetaDataFields(exclude=exclude)

    def displayCatalogQuery(self):
        """
          Return the stored query as a readable catalog query."""
        return parseFormquery(self, self.query)
