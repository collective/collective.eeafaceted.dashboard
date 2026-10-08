# -*- coding: utf-8 -*-
from collective.eeafaceted.dashboard.browser.overrides import DashboardFacetedTableView
from collective.eeafaceted.dashboard.testing import IntegrationTestCase
from eea.facetednavigation.interfaces import IPossibleFacetedNavigable
from plone import api
from z3c.table.interfaces import IColumn
from zope.component import getAdapters


class TestDashboardFacetedTableView(IntegrationTestCase):
    def test__getViewFields(self):
        # faceted folder without current collection: every registered column
        view = self.folder.restrictedTraverse("faceted-table-view")
        self.assertIsInstance(view, DashboardFacetedTableView)
        self.assertIsNone(view.collection)
        fields = view._getViewFields()
        self.assertEqual(
            sorted(fields),
            sorted(
                name
                for name, column in getAdapters(
                    (self.folder, self.request, view), IColumn
                )
            ),
        )
        self.assertIn("pretty_link", fields)
        self.assertIn("select_row", fields)
        # faceted folder with a current collection: the columns selected on the collection, in its order
        dc = api.content.create(
            id="dc1",
            type="DashboardCollection",
            title="Dashboard collection 1",
            container=self.folder,
            query=[],
            sort_on="",
            sort_reversed=False,
            tal_condition="",
            roles_bypassing_talcondition=[],
            customViewFields=["select_row", "pretty_link", "review_state"],
        )
        self.request.form["c1[]"] = dc.UID()
        view = self.folder.restrictedTraverse("faceted-table-view")
        self.assertEqual(view.collection, dc)
        self.assertEqual(
            view._getViewFields(), ["select_row", "pretty_link", "review_state"]
        )
        # on a faceted collection (Collection type made faceted navigable): its own columns
        del self.request.form["c1[]"]
        fti = self.portal.portal_types.Collection
        fti._updateProperty(
            "behaviors", fti.behaviors + (IPossibleFacetedNavigable.__identifier__,)
        )
        collection = api.content.create(
            id="c1",
            type="Collection",
            title="Collection 1",
            container=self.portal,
            customViewFields=["Title", "Creator"],
        )
        collection.unrestrictedTraverse("@@faceted_subtyper").enable()
        view = collection.restrictedTraverse("faceted-table-view")
        self.assertIsInstance(view, DashboardFacetedTableView)
        self.assertEqual(view.collection, collection)
        self.assertEqual(view._getViewFields(), ["Title", "Creator"])
