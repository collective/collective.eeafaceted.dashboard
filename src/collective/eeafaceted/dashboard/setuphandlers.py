# -*- coding: utf-8 -*-
from collective.eeafaceted.collectionwidget.utils import _updateDefaultCollectionFor
from collective.eeafaceted.dashboard.utils import enableFacetedDashboardFor
from plone import api


def isNotCurrentProfile(context):
    return context.readDataFile("faceteddashboard_marker.txt") is None


def post_install(context):
    """Post install script"""
    if isNotCurrentProfile(context):
        return


def add_demo_data(context):
    """ """
    CUSTOM_VIEW_FIELDS = [
        u'pretty_link', u'Creator', u'CreationDate',
        u'ModificationDate', u'review_state', u'select_row']
    portal = context.getSite()
    # create container and searches
    folder = api.content.create(
        container=portal, type='Folder', title='Dashboard')
    default_collection = api.content.create(
        container=folder,
        type='DashboardCollection',
        title='Every elements',
        query=[{u'i': u'path',
                u'o': u'plone.app.querystring.operation.string.absolutePath',
                u'v': u''}],
        customViewFields=CUSTOM_VIEW_FIELDS,
        showNumberOfItems=False)
    api.content.create(
        container=folder,
        type='DashboardCollection',
        title='My elements',
        query=[
            {u'i': u'path',
                u'o': u'plone.app.querystring.operation.string.absolutePath',
                u'v': u''},
            {u'i': u'Creator',
             u'o': u'plone.app.querystring.operation.string.currentUser',
             u'v': u''}],
        customViewFields=CUSTOM_VIEW_FIELDS,
        showNumberOfItems=False)
    api.content.create(
        container=folder,
        type='DashboardCollection',
        title='Elements to review',
        query=[{u'i': u'review_state',
                u'o': u'plone.app.querystring.operation.selection.any',
                u'v': [u'pending']}],
        customViewFields=CUSTOM_VIEW_FIELDS,
        showNumberOfItems=True)
    api.content.create(
        container=folder,
        type='DashboardCollection',
        title='Expired elements',
        query=[{u'i': u'expires',
                u'o': u'plone.app.querystring.operation.date.beforeToday',
                u'v': u''}],
        customViewFields=CUSTOM_VIEW_FIELDS,
        showNumberOfItems=True)
    # enable faceted and configure
    enableFacetedDashboardFor(folder, show_left_column=False)
    _updateDefaultCollectionFor(folder, default_collection.UID())
