# -*- coding: utf-8 -*-
"""Test views."""
from collective.eeafaceted.collectionwidget.utils import getCollectionLinkCriterion
from collective.eeafaceted.collectionwidget.widgets.widget import CollectionWidget
from collective.eeafaceted.dashboard.config import CURRENT_CRITERION
from collective.eeafaceted.dashboard.interfaces import ICountableTab
from collective.eeafaceted.dashboard.testing import IntegrationTestCase
from plone import api
from zope.interface import alsoProvides

import json
import lxml.html


class TestRenderTermPortletView(IntegrationTestCase):
    def test_call(self):
        """The term as rendered by the portlet outside the faceted: a link to the dashboard."""
        dc = api.content.create(
            id="dc1",
            type="DashboardCollection",
            title="Dashboard collection 1",
            container=self.folder,
            query=[],
            sort_on="",
            sort_reversed=False,
            showNumberOfItems=True,
            tal_condition=u"",
            roles_bypassing_talcondition=[],
        )
        widget = CollectionWidget(
            self.folder, self.request, getCollectionLinkCriterion(self.folder)
        )
        widget.base_url = "http://nohost/plone/folder#c3=20"
        term = [t for t in widget.vocabulary() if t.token == dc.UID()][0]
        self.request.set("SESSION", {CURRENT_CRITERION: dc.UID()})

        def render():
            return lxml.html.fromstring(
                widget.render_term(
                    term, "", view_name="@@render_collection_widget_term_portlet"
                )
            )

        li = render()
        self.assertEqual(li.tag, "li")
        self.assertEqual(li.get("id"), "c1{0}".format(dc.UID()))
        self.assertEqual(li.get("value"), dc.UID())
        self.assertEqual(li.get("title"), "Dashboard collection 1")
        # collective.querynextprev not installed: the term of the SESSION is not selected
        self.assertEqual(li.get("class"), "folder-dc1 no-category-tag")
        self.assertEqual(
            li.xpath("a/@href"),
            ["http://nohost/plone/folder#c3=20&c1={0}".format(dc.UID())],
        )
        self.assertEqual(
            li.xpath('a/span[@class="term-label"]/text()'), ["Dashboard collection 1"]
        )
        # the count is computed later by the JS (@@json_collections_count)
        self.assertEqual(li.xpath('a/span/span[@class="term-count"]/text()'), ["..."])
        # collective.querynextprev installed (it is not in the test env, mark it installed):
        # the current criterion of the SESSION is selected
        api.portal.get_tool("portal_quickinstaller").notifyInstalled(
            "collective.querynextprev"
        )
        self.assertEqual(
            render().get("class"), "folder-dc1 faceted-tag-selected no-category-tag"
        )
        # in a category, without count
        dc.showNumberOfItems = False
        li = lxml.html.fromstring(
            widget.render_term(
                term,
                "category_uid",
                view_name="@@render_collection_widget_term_portlet",
            )
        )
        self.assertEqual(li.get("class"), "folder-dc1 faceted-tag-selected")
        self.assertEqual(li.xpath('a/span/span[@class="term-count"]'), [])


class TestJSONListCountableTabs(IntegrationTestCase):
    def test_call(self):
        view = self.portal.unrestrictedTraverse("@@json_list_countable_tabs")
        self.assertEqual(json.loads(view()), {"urls": []})
        folder2 = api.content.create(
            id="folder2", type="Folder", title="Folder 2", container=self.portal
        )
        for tab in (self.folder, folder2):
            alsoProvides(tab, ICountableTab)
            tab.reindexObject(idxs=["object_provides"])
        self.assertEqual(
            sorted(json.loads(view())["urls"]),
            ["http://nohost/plone/folder", "http://nohost/plone/folder2"],
        )


class TestJSONCollectionsCount(IntegrationTestCase):
    def setUp(self):
        super(TestJSONCollectionsCount, self).setUp()
        self.view = self.folder.unrestrictedTraverse("@@json_collections_count")

    def test_folder_empty(self):
        expected = json.dumps({"criterionId": "c1", "countByCollection": []})
        self.assertEqual(self.view(), expected)

    def test_with_dashboard_collections(self):
        dashboardcoll = api.content.create(
            id="dc1",
            type="DashboardCollection",
            title="Dashboard collection 1",
            container=self.folder,
            tal_condition=u"",
            roles_bypassing_talcondition=[],
            sort_reversed=False,
            query=[],
        )
        dashboardcol2 = api.content.create(
            id="dc2",
            type="DashboardCollection",
            title="Dashboard collection 2",
            container=self.folder,
            tal_condition=u"",
            roles_bypassing_talcondition=[],
            sort_reversed=False,
            query=[],
        )
        dashboardcol3 = api.content.create(
            id="dc3",
            type="DashboardCollection",
            title="Dashboard collection 3",
            container=self.folder,
            tal_condition=u"",
            roles_bypassing_talcondition=[],
            sort_reversed=False,
            query=[],
        )
        dashboardcoll.showNumberOfItems = True
        dashboardcol2.showNumberOfItems = False
        dashboardcol3.showNumberOfItems = True

        dashboardcoll.query = [
            {
                "i": "portal_type",
                "o": "plone.app.querystring.operation.selection.is",
                "v": [
                    "DashboardCollection",
                ],
            },
        ]
        expected = {
            "criterionId": "c1",
            "countByCollection": [
                {"uid": dashboardcoll.UID(), "count": 3},
                {"uid": dashboardcol3.UID(), "count": 0},
            ],
        }
        self.assertEqual(self.view(), json.dumps(expected))

    def test_with_collections(self):
        col = api.content.create(
            id="col1",
            type="Collection",
            title="collection 1",
            container=self.folder,
            tal_condition=u"",
            roles_bypassing_talcondition=[],
        )

        col.query = [
            {
                "i": "portal_type",
                "o": "plone.app.querystring.operation.selection.is",
                "v": [
                    "Collection",
                ],
            },
        ]
        expected = {"criterionId": "c1", "countByCollection": []}
        self.assertEqual(self.view(), json.dumps(expected))

    def test_with_sub_elements(self):
        """Make sure especially the JSONCollectionsCount.get_context gets
        the faceted context when the view is called from a sub/sub element."""
        self.assertEqual(self.view.context, self.folder)
        self.assertEqual(self.view(), '{"criterionId": "c1", "countByCollection": []}')
        subfolder = api.content.create(
            id="subfolder", type="Folder", title="Subfolder", container=self.folder
        )
        self.view.context = subfolder
        self.assertEqual(self.view(), '{"criterionId": "c1", "countByCollection": []}')
        subsubfolder = api.content.create(
            id="subsubfolder", type="Folder", title="Subsubfolder", container=subfolder
        )
        self.view.context = subsubfolder
        self.assertEqual(self.view(), '{"criterionId": "c1", "countByCollection": []}')
