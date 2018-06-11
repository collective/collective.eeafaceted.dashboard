# -*- coding: utf-8 -*-
#
# File: events.py
#
# Copyright (c) 2018 by Imio.be
#
# GNU General Public License (GPL)
#

from imio.helpers.cache import invalidate_cachekey_volatile_for


def onDashboardCollectionModified(obj, event):
    '''Called whenever a DashboardCollection is modified.'''
    invalidate_cachekey_volatile_for('collective.eeafaceted.dashboard.cachedcollectionvocabulary')


def onDashboardCollectionTransition(obj, event):
    '''Called whenever a WF transition was triggered on a DashboardCollection.'''
    invalidate_cachekey_volatile_for('collective.eeafaceted.dashboard.cachedcollectionvocabulary')
