# -*- coding: utf-8 -*-
#
# File: indexes.py
#
# Copyright (c) 2015 by Imio.be
#
# GNU General Public License (GPL)
#

from plone import api
from plone.indexer import indexer
from Products.ATContentTypes.interfaces import IATFolder


@indexer(IATFolder)
def contained_types_and_states(folder):
    """
      Index the portal_type and review_state of contained objects like :
      ['Document_private', 'Document_published', 'Image_private'].
    """
    res = []
    for obj in folder.objectValues():
        # add also portal_type alone so it can be queried
        if obj.portal_type not in res:
            res.append(obj.portal_type)
        # add also review_state alone so it can be queried
        if api.content.get_state(obj) not in res:
            res.append(api.content.get_state(obj))
        # then add the combined value
        value = obj.portal_type + '__' + api.content.get_state(obj)
        if value not in res:
            res.append(value)
    res.sort()
    return res
