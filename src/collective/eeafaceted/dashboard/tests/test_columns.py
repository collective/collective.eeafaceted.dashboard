# -*- coding: utf-8 -*-

from zope.component import getUtility
from zope.intid.interfaces import IIntIds
from z3c.relationfield.relation import RelationValue

from plone import api

from imio.dashboard.columns import ActionsColumn
from imio.dashboard.columns import PrettyLinkColumn
from imio.dashboard.columns import RelationPrettyLinkColumn
from imio.dashboard.testing import IntegrationTestCase


class TestColumns(IntegrationTestCase):

    def test_PrettyLinkColumn(self):
        """Test the PrettyLinkColumn, it will render IPrettyLink.getLink."""
        table = self.faceted_table
        column = PrettyLinkColumn(self.portal, self.portal.REQUEST, table)
        column.attrName = 'Title'
        table.nameColumn(column, 'Title')
        # we will use the 'folder' as a brain
        brain = self.portal.portal_catalog(UID=self.folder.UID())[0]
        self.assertEquals(column.renderCell(brain),
                          u"<a class='pretty_link' title='Folder' href='http://nohost/plone/folder' target='_self'>"
                          u"<span class='pretty_link_content'>Folder</span></a>")
        # we define a parameter
        column.params['target'] = '_blank'
        self.assertEquals(column.renderCell(brain),
                          u"<a class='pretty_link' title='Folder' href='http://nohost/plone/folder' target='_blank'>"
                          u"<span class='pretty_link_content'>Folder</span></a>")
        # a pretty_link class is defined for the tg
        self.assertEquals(column.cssClasses, {'td': 'pretty_link', 'th': 'th_header_Title'})

    def test_ActionsColumn(self):
        """Render the @@actions_panel view."""
        table = self.faceted_table
        column = ActionsColumn(self.portal, self.portal.REQUEST, table)
        brain = self.portal.portal_catalog(UID=self.folder.UID())[0]
        # it is a BrowserViewCallColumn with some fixed parameters
        self.assertEquals(column.view_name, 'actions_panel')
        rendered_column = column.renderCell(brain)
        # common parts are there : 'edit', 'Delete', 'history'
        self.assertIn("/edit", rendered_column)
        self.assertIn("javascript:confirmDeleteObject", rendered_column)
        self.assertIn("history.gif", rendered_column)

    def test_RelationPrettyLinkColumn(self):
        """Test the RelationPrettyLinkColumn, it will render IPrettyLink.getLink."""
        table = self.faceted_table
        column = RelationPrettyLinkColumn(self.portal, self.portal.REQUEST, table)
        fold1 = api.content.create(container=self.portal, type='Folder', id='fold1', title="Folder 1")
        fold2 = api.content.create(container=self.portal, type='Folder', id='fold2', title="Folder 2")
        intids = getUtility(IIntIds)
        rel1 = RelationValue(intids.getId(fold1))
        rel2 = RelationValue(intids.getId(fold2))
        tt = api.content.create(container=self.portal, type='testingtype', id='testingtype',
                                title='My testing type', rel_item=rel1, rel_items=[rel1, rel2])
        brain = self.portal.portal_catalog(UID=tt.UID())[0]
        column.attrName = 'rel_item'
        self.assertEqual(u"<a class='pretty_link' title='Folder 1' href='http://nohost/plone/fold1' target='_self'>"
                         "<span class='pretty_link_content'>Folder 1</span></a>",
                         column.renderCell(brain))
        column.params = {'showContentIcon': True}
        self.assertEqual(u"<a class='pretty_link contenttype-Folder' title='Folder 1' href='http://nohost/plone/fold1' "
                         "target='_self'><span class='pretty_link_content'>Folder 1</span></a>",
                         column.renderCell(brain))
        column.params = {}
        column.attrName = 'rel_items'
        self.assertEqual(u"<ul>\n<li><a class='pretty_link' title='Folder 1' href='http://nohost/plone/fold1' target='_self'>"
                         "<span class='pretty_link_content'>Folder 1</span></a></li>\n"
                         "<li><a class='pretty_link' title='Folder 2' href='http://nohost/plone/fold2' target='_self'>"
                         "<span class='pretty_link_content'>Folder 2</span></a></li>\n</ul>",
                         column.renderCell(brain))
        # a pretty_link class is defined for the td
        table.nameColumn(column, 'rel_items')
        self.assertEquals(column.cssClasses, {'td': 'pretty_link', 'th': 'th_header_rel_items'})
