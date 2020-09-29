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


class IDashboardGenerablePODTemplates(Interface):
    """
    Marker interface for dashboard generable POD templates adapter.
    """


class ICountableTab(Interface):
    """
    Marker interface for a tab to be affixed with a counter.
    """
