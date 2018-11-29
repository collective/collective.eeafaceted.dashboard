# -*- coding: utf-8 -*-
from collective.eeafaceted.collectionwidget.config import NO_FACETED_EXCEPTION_MSG
from collective.eeafaceted.collectionwidget.interfaces import NoFacetedViewDefinedException
from collective.eeafaceted.collectionwidget.utils import _updateDefaultCollectionFor
from eea.facetednavigation.criteria.interfaces import ICriteria
from eea.facetednavigation.interfaces import IHidePloneLeftColumn
from eea.facetednavigation.layout.interfaces import IFacetedLayout
from eea.facetednavigation.subtypes.interfaces import IFacetedNavigable
from os import path
from plone import api
from zope.interface import noLongerProvides

import json
import logging


logger = logging.getLogger('collective.eeafaceted.dashboard: utils')


def enableFacetedDashboardFor(obj, xmlpath=None, show_left_column=True, default_UID=None):
    """Mark in REQUEST that we are enabling a dashboard, sometimes useful for subprocesses."""
    obj.REQUEST.set('enablingFacetedDashboard', True)
    _enableFacetedDashboardFor(obj, xmlpath, show_left_column, default_UID)
    obj.REQUEST.set('enablingFacetedDashboard', False)


def _enableFacetedDashboardFor(obj, xmlpath=None, show_left_column=True, default_UID=None):
    """Enable a faceted view on obj and import a
       specific xml if given p_xmlpath."""
    # already a faceted?
    if IFacetedNavigable.providedBy(obj):
        logger.error("Faceted navigation is already enabled for '%s'" %
                     '/'.join(obj.getPhysicalPath()))
        return

    # do not go further if xmlpath does not exist
    if xmlpath and not path.exists(xmlpath):
        raise Exception("Specified xml file '%s' doesn't exist" % xmlpath)
    # .enable() here under will redirect to enabled faceted
    # we cancel this, safe previous RESPONSE status and location
    response_status = obj.REQUEST.RESPONSE.getStatus()
    response_location = obj.REQUEST.RESPONSE.getHeader('location')
    obj.unrestrictedTraverse('@@faceted_subtyper').enable()

    # use correct layout in the faceted
    IFacetedLayout(obj).update_layout('faceted-table-items')
    # show the left portlets
    if show_left_column and IHidePloneLeftColumn.providedBy(obj):
        noLongerProvides(obj, IHidePloneLeftColumn)
    # import configuration
    if xmlpath:
        obj.unrestrictedTraverse('@@faceted_exportimport').import_xml(
            import_file=open(xmlpath))
    # define default collection UID
    if default_UID:
        _updateDefaultCollectionFor(obj, default_UID)
    obj.reindexObject()
    obj.REQUEST.RESPONSE.status = response_status
    obj.REQUEST.RESPONSE.setHeader('location', response_location or '')


def getDashboardQueryResult(faceted_context):
    """
    Return dashboard selelected items of a faceted query.
    """
    if not IFacetedNavigable.providedBy(faceted_context):
        raise NoFacetedViewDefinedException(NO_FACETED_EXCEPTION_MSG)

    request = faceted_context.REQUEST
    uids = request.form.get('uids', '')
    faceted_query = request.form.get('facetedQuery', None)

    brains = []
    # maybe we have a facetedQuery? aka the meeting view was filtered and we want to print this result
    if not uids:
        if faceted_query:
            # put the facetedQuery criteria into the REQUEST.form
            for k, v in json.JSONDecoder().decode(faceted_query).items():
                # we receive list of elements, if we have only one elements, remove it from the list
                if isinstance(v, list) and len(v) == 1:
                    v = v[0]
                request.form['{0}[]'.format(k)] = v
        faceted = faceted_context.restrictedTraverse('@@faceted_query')
        brains = faceted.query(batch=False)
    # if we have uids, let 'brains' be directly available in the template context too
    # brains could already fetched, if it is the case, use it, get it otherwise
    elif uids:
        uids = uids.split(',')
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog(UID=uids)

        # we need to sort found brains according to uids
        def getKey(item):
            return uids.index(item.UID)
        brains = sorted(brains, key=getKey)
    return brains


def _get_criterion_by_attr(faceted_context, attr_name, value_to_match):
    """
    """
    if not IFacetedNavigable.providedBy(faceted_context):
        raise NoFacetedViewDefinedException(NO_FACETED_EXCEPTION_MSG)

    criterions = ICriteria(faceted_context)
    for criterion in criterions.values():
        if not hasattr(criterion, attr_name):
            continue
        else:
            attr = getattr(criterion, attr_name)
            value = hasattr(attr, '__call__') and attr() or attr
            if value == value_to_match:
                return criterion


def getCriterionByTitle(faceted_context, title):
    """
    Return criterion with title 'title'.
    """
    return _get_criterion_by_attr(faceted_context, 'title', title)


def getCriterionByIndex(faceted_context, index):
    """
    Return criterion with index named 'index'.
    """
    return _get_criterion_by_attr(faceted_context, 'index', index)
