# -*- coding: utf-8 -*-

from collective.behavior.talcondition.utils import applyExtender


def isNotCurrentProfile(context):
    return context.readDataFile("imiodashboard_marker.txt") is None


def post_install(context):
    """Post install script"""
    if isNotCurrentProfile(context):
        return

    # we need to apply the ITALConditionable extender on existing elements
    portal = context.getSite()
    applyExtender(portal, ('DashboardCollection', ))
