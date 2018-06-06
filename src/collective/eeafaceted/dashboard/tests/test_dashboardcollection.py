# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

from plone import api
from imio.dashboard.testing import IntegrationTestCase
from imio.dashboard.interfaces import ICustomViewFieldsVocabulary


class TestDashboardCollection(IntegrationTestCase):
    """Test the DashboardCollection content type."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.dashboardcollection = api.content.create(
            id='dc1',
            type='DashboardCollection',
            title='Dashboard collection 1',
            container=self.portal
        )

    def test_listMetaDataFields(self):
        """Test the overrided listMetaDataFields method that will
           list available metadata as base Collection but that will
           also add to it's vocabulary, elements returned by an
           CustomViewFieldsVocabularyAdapter adapter."""
        # classic metadata, coming from collective.eeafaceted.z3ctable
        default_columns = ['Title', 'CreationDate', 'ModificationDate',
                           'Creator', 'review_state', 'getText']
        # additional fields
        additional_columns = ['pretty_link', 'actions', 'select_row', ]
        # complete list from adapter
        self.assertTrue(set(ICustomViewFieldsVocabulary(self.dashboardcollection).listMetaDataFields().keys()) ==
                        set(default_columns + additional_columns))
        # listMetaDataFields is now using adapter
        self.assertTrue(set(self.dashboardcollection.listMetaDataFields().keys()) ==
                        set(default_columns + additional_columns))

    def test_selectedViewFields(self):
        """Test the overrided selectedViewFields method that will make sure
           additional values selected in the customViewFields field will be
           purged of every columns that are not metadata (added by the override listMetaDataFields)
           or it breaks the tabular_view."""
        # select the 'actions' value in the customViewFields, this is not a metadata
        self.dashboardcollection.setCustomViewFields(['Title', 'Creator', 'actions'])
        # selectedViewFields returns [('Title', u'Title'), ('Creator', 'Creator')]
        self.assertTrue([elt[0] for elt in self.dashboardcollection.selectedViewFields()] == ['Title', 'Creator', ])

    def test_displayCatalogQuery(self):
        """This will display a readable version if the catalog query."""
        self.dashboardcollection.query = [
            {'i': 'portal_type', 'o': 'plone.app.querystring.operation.selection.is', 'v': ['Folder', ]},
        ]
        self.assertEquals(self.dashboardcollection.displayCatalogQuery(),
                          {'portal_type': {'query': ['Folder']}})

    def test_showNumberOfItems_field(self):
        """Test showNumberOfItems field."""
        self.dashboardcollection.setShowNumberOfItems(True)
        self.assertEqual(self.dashboardcollection.getShowNumberOfItems(), True)

    def test_limit_field(self):
        """Test default value on limit field."""
        self.assertEqual(self.dashboardcollection.limit, 0)

    def test_non_visible_fields(self):
        """Test non visible fields."""
        non_visible = ('b_size', 'limit')
        for field in self.dashboardcollection.schema.fields():
            if field.getName() in non_visible:
                self.assertEqual(field.widget.visible, -1)
