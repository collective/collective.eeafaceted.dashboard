# -*- coding: utf-8 -*-

from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IImioDashboardLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IDashboardCollection(Interface):
    """DashboardCollection marker interface"""


class ICustomViewFieldsVocabulary(Interface):
    """
      Adapter interface that manage override of the
      plone.app.collection Collection.customViewFields vocabulary.
    """

    def listMetaDataFields(self, exclude=True):
        """
          Get every IFacetedColumn z3c.table columns.
        """
