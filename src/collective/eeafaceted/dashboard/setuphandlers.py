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
        "pretty_link",
        "Creator",
        "CreationDate",
        "ModificationDate",
        "review_state",
        "select_row",
    ]
    portal = context.getSite()
    # create container and searches
    folder = api.content.create(container=portal, type="Folder", title="Dashboard")
    default_collection = api.content.create(
        container=folder,
        type="DashboardCollection",
        title="Every elements",
        query=[
            {
                "i": "path",
                "o": "plone.app.querystring.operation.string.path",
                "v": "",
            }
        ],
        customViewFields=CUSTOM_VIEW_FIELDS,
        showNumberOfItems=False,
        tal_condition="",
        roles_bypassing_talcondition=[],
        sort_on=None,
        sort_reversed=False,
    )
    api.content.create(
        container=folder,
        type="DashboardCollection",
        title="My elements",
        query=[
            {
                "i": "path",
                "o": "plone.app.querystring.operation.string.path",
                "v": "",
            },
            {
                "i": "Creator",
                "o": "plone.app.querystring.operation.string.currentUser",
                "v": "",
            },
        ],
        customViewFields=CUSTOM_VIEW_FIELDS,
        showNumberOfItems=False,
        tal_condition="",
        roles_bypassing_talcondition=[],
        sort_on=None,
        sort_reversed=False,
    )
    api.content.create(
        container=folder,
        type="DashboardCollection",
        title="Elements to review",
        query=[
            {
                "i": "review_state",
                "o": "plone.app.querystring.operation.selection.is",
                "v": "pending",
            }
        ],
        customViewFields=CUSTOM_VIEW_FIELDS,
        showNumberOfItems=True,
        tal_condition="",
        roles_bypassing_talcondition=[],
        sort_on=None,
        sort_reversed=False,
    )
    api.content.create(
        container=folder,
        type="DashboardCollection",
        title="Expired elements",
        query=[
            {
                "i": "expires",
                "o": "plone.app.querystring.operation.date.beforeToday",
                "v": "",
            }
        ],
        customViewFields=CUSTOM_VIEW_FIELDS,
        showNumberOfItems=True,
        tal_condition="",
        roles_bypassing_talcondition=[],
        sort_on=None,
        sort_reversed=False,
    )
    # enable faceted and configure
    enableFacetedDashboardFor(folder, show_left_column=False)
    _updateDefaultCollectionFor(folder, default_collection.UID())
