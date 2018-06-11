# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IFacetedDashboardLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class ICustomViewFieldsVocabulary(Interface):
    """
      Adapter interface that manage override of the
      plone.app.collection Collection.customViewFields vocabulary.
    """

    def listMetaDataFields(self, exclude=True):
        """
          Get every IFacetedColumn z3c.table columns.
        """
