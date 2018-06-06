# -*- coding: utf-8 -*-
"""Setup/installation tests for this package."""

import os
from zope.component import queryUtility
from zope.schema.interfaces import IVocabularyFactory
from plone import api
from collective.eeafaceted.collectionwidget.utils import getCollectionLinkCriterion
from eea.facetednavigation.interfaces import ICriteria
from imio.dashboard.config import COMBINED_INDEX_PREFIX
from imio.dashboard.testing import IntegrationTestCase
from imio.dashboard.tests.indexes import contained_types_and_states
from imio.helpers.catalog import addOrUpdateIndexes


class TestCombinedIndex(IntegrationTestCase):
    """Test the Combined index functionnality."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        super(TestCombinedIndex, self).setUp()
        # add the 'contained_types_and_states' to portal_catalog
        addOrUpdateIndexes(self.portal, {'contained_types_and_states': ('KeywordIndex', {})})
        # make sure we have a default workflow
        self.portal.portal_workflow.setDefaultChain('simple_publication_workflow')
        self.dashboardcollection = api.content.create(
            id='dc1',
            type='DashboardCollection',
            title='Dashboard collection 1',
            container=self.portal
        )
        # this will by default query Folders
        self.dashboardcollection.query = [
            {'i': 'portal_type',
             'o': 'plone.app.querystring.operation.selection.is',
             'v': ['Folder', ]},
        ]
        # create 3 folders :
        # - first is empty;
        # - second contains one private Document and one published Document;
        # - third contains a private Folder.

        # folder1
        self.folder1 = api.content.create(
            id='folder1',
            type='Folder',
            title='Folder 1',
            container=self.portal
        )
        self.privatedoc = api.content.create(
            id='privatedoc',
            type='Document',
            title='Private document',
            container=self.portal.folder1
        )
        self.publicdoc = api.content.create(
            id='publicdoc',
            type='Document',
            title='Published document',
            container=self.portal.folder1
        )
        api.content.transition(self.publicdoc, 'publish')
        # folder2
        self.folder2 = api.content.create(
            id='folder2',
            type='Folder',
            title='Folder 2',
            container=self.portal
        )
        # folder3
        self.folder3 = api.content.create(
            id='folder3',
            type='Folder',
            title='Folder 3',
            container=self.portal
        )
        self.privatefolder = api.content.create(
            id='privatefolder',
            type='Folder',
            title='Private folder',
            container=self.portal.folder3
        )
        self.privatedoc2 = api.content.create(
            id='privatedoc2',
            type='Document',
            title='Private document 2',
            container=self.portal.folder3
        )
        # first check that contained_types_and_states index is correct
        self.folder1.reindexObject(idxs=['contained_types_and_states'])
        self.folder2.reindexObject(idxs=['contained_types_and_states'])
        self.folder3.reindexObject(idxs=['contained_types_and_states'])
        self.assertEquals(contained_types_and_states(self.folder1)(),
                          ['Document', 'Document__private', 'Document__published',
                           'private', 'published'])
        self.assertEquals(contained_types_and_states(self.folder2)(), [])
        self.assertEquals(contained_types_and_states(self.folder3)(),
                          ['Document', 'Document__private',
                           'Folder', 'Folder__private', 'private'])

    def test_combined_index(self):
        """We made an index that index portal_type and review_state
           of contained elements, here we will query folders containing
           'Document' in state 'private'."""
        # set a correct collection in the REQUEST
        criterion = getCollectionLinkCriterion(self.folder)
        criterion_name = '{0}[]'.format(criterion.__name__)
        self.request.form[criterion_name] = self.dashboardcollection.UID()
        # add new widgets
        # c10 and c11 widgets are missing for now
        self.assertFalse(ICriteria(self.folder).get('c10'))
        self.assertFalse(ICriteria(self.folder).get('c11'))
        xmlpath = os.path.dirname(__file__) + '/faceted_conf/combined_index_widgets.xml'
        self.folder.unrestrictedTraverse('@@faceted_exportimport').import_xml(
            import_file=open(xmlpath))
        self.assertEquals(ICriteria(self.folder).get('c10').index,
                          u'contained_types_and_states')
        self.assertEquals(ICriteria(self.folder).get('c11').index,
                          COMBINED_INDEX_PREFIX + u'contained_types_and_states')
        # by default the dashboardcollection will return the every found folders, aka 6
        faceted_query = self.folder.restrictedTraverse('@@faceted_query')
        self.assertEquals(len(faceted_query.query()), 5)

        # filter on 'review_state', get the private elements
        self.request.form['c10[]'] = ''
        self.request.form['c11[]'] = 'private'
        self.assertEquals(faceted_query.criteria()['contained_types_and_states']['query'],
                          'private')
        # we get folder1 and folder3
        uids = [brain.UID for brain in faceted_query.query()]
        self.assertEquals(len(faceted_query.query()), 2)
        self.assertTrue(self.folder1.UID() in uids and
                        self.folder3.UID() in uids)
        # filter on 'portal_type', get 'Document'
        self.request.form['c10[]'] = 'Document'
        self.request.form['c11[]'] = ''
        self.assertEquals(faceted_query.criteria()['contained_types_and_states']['query'],
                          'Document')
        # we get folder1 and folder3
        uids = [brain.UID for brain in faceted_query.query()]
        self.assertEquals(len(faceted_query.query()), 2)
        self.assertTrue(self.folder1.UID() in uids and
                        self.folder3.UID() in uids)
        # but if we filter 'review_state' published, we only get folder1
        self.request.form['c10[]'] = 'Document'
        self.request.form['c11[]'] = 'published'
        self.assertEquals(faceted_query.criteria()['contained_types_and_states']['query'],
                          ['Document__published'])
        uids = [brain.UID for brain in faceted_query.query()]
        self.assertEquals(len(faceted_query.query()), 1)
        self.assertTrue(self.folder1.UID() in uids)

        # query 'review_state' private and portal_type 'Document' and 'Folder'
        self.request.form['c10[]'] = ['Document', 'Folder']
        self.request.form['c11[]'] = 'private'
        self.assertEquals(faceted_query.criteria()['contained_types_and_states']['query'],
                          ['Document__private', 'Folder__private'])
        uids = [brain.UID for brain in faceted_query.query()]
        self.assertEquals(len(faceted_query.query()), 2)
        self.assertTrue(self.folder1.UID() in uids and
                        self.folder3.UID() in uids)

    def test_catalog_indexes_vocabulary(self):
        """The default 'eea.faceted.vocabularies.CatalogIndexes' id overrided
           to add 'combined__' indexes."""
        vocab = queryUtility(IVocabularyFactory,
                             'eea.faceted.vocabularies.CatalogIndexes')(self.portal)
        tokens = [term.token for term in vocab._terms]
        # we have one single empty selection...
        self.assertTrue(tokens[0] == '')
        self.assertEquals(tokens.count(''), 1)
        # ... then every indexes duplicated
        real_indexes = [token for token in tokens if token and not token.startswith(COMBINED_INDEX_PREFIX)]
        combined_indexes = [token for token in tokens if token and token.startswith(COMBINED_INDEX_PREFIX)]
        self.assertEquals(len(real_indexes), len(combined_indexes))
        for real_index in real_indexes:
            self.assertTrue(COMBINED_INDEX_PREFIX + real_index in combined_indexes)
