# -*- coding: utf-8 -*-
from zope.component import queryUtility
from zope.event import notify
from zope.interface import alsoProvides
from zope.lifecycleevent import ObjectModifiedEvent
from zope.schema.interfaces import IVocabularyFactory
from Products.CMFCore.utils import getToolByName
from plone.app.testing import login
from plone.app.testing import TEST_USER_NAME
from plone import api
from imio.dashboard.testing import IntegrationTestCase
from collective.behavior.talcondition.interfaces import ITALConditionable
from eea.facetednavigation.interfaces import IFacetedNavigable
from ..vocabulary import DashboardCollectionsVocabulary


class TestConditionAwareVocabulary(IntegrationTestCase):
    """Test the ConditionAwareCollectionVocabulary vocabulary."""

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        # make sure we have a default workflow
        self.wfTool = self.portal.portal_workflow
        self.wfTool.setDefaultChain('simple_publication_workflow')
        self.folder = api.content.create(id='f', type='Folder', title='My category', container=self.portal)
        self.dashboardcollection = api.content.create(
            id='dc1',
            type='DashboardCollection',
            title='Dashboard collection 1',
            container=self.folder
        )
        alsoProvides(self.folder, IFacetedNavigable)

    def test_conditionawarecollectionvocabulary(self):
        """This vocabulary is condition aware, it means
           that it will take into account condition defined in the
           'tal_condition' field added by ITALConditionable."""
        # add on non Manager user
        api.user.create(
            username='user_not_manager',
            password='user_not_manager',
            email="imio@dashboard.org",
            roles=['Member'])
        self.assertTrue(ITALConditionable.providedBy(self.dashboardcollection))
        factory = queryUtility(IVocabularyFactory, u'imio.dashboard.conditionawarecollectionvocabulary')
        # for now, no condition defined on the collection so it is in the vocabulary
        self.assertEqual(self.dashboardcollection.tal_condition, u'')
        vocab = factory(self.portal)
        self.assertTrue(self.dashboardcollection.UID() in vocab.by_token)
        # now define a condition and by pass for Manager
        self.dashboardcollection.tal_condition = u'python:False'
        self.dashboardcollection.roles_bypassing_talcondition = [u"Manager"]
        notify(ObjectModifiedEvent(self.dashboardcollection))
        # No more listed except for Manager
        vocab = factory(self.portal)
        self.assertTrue(self.dashboardcollection.UID() in vocab.by_token)
        login(self.portal, 'user_not_manager')
        # cache is user aware
        vocab = factory(self.portal)
        self.assertFalse(self.dashboardcollection.UID() in vocab.by_token)
        # Now, desactivate bypass for manager
        login(self.portal, TEST_USER_NAME)
        self.dashboardcollection.roles_bypassing_talcondition = []
        # ObjectModified event on DashboardCollection invalidate the vocabulary caching
        notify(ObjectModifiedEvent(self.dashboardcollection))
        vocab = factory(self.portal)
        self.assertFalse(self.dashboardcollection.UID() in vocab.by_token)
        # If condition is True, it is listed
        self.dashboardcollection.tal_condition = u'python:True'
        notify(ObjectModifiedEvent(self.dashboardcollection))
        vocab = factory(self.portal)
        self.assertTrue(self.dashboardcollection.UID() in vocab.by_token)

        # cache invalidated when transition triggered
        # show this by editing title then changing state
        self.assertTrue((self.dashboardcollection.title, '') in [term.title for term in vocab._terms])
        self.dashboardcollection.title = u'Edited title'
        vocab = factory(self.portal)
        self.assertFalse((self.dashboardcollection.title, '') in [term.title for term in vocab._terms])
        self.wfTool.doActionFor(self.dashboardcollection, 'publish')
        vocab = factory(self.portal)
        self.assertTrue((self.dashboardcollection.title, '') in [term.title for term in vocab._terms])

    def test_creatorsvocabulary(self):
        """This will return every users that created a content in the portal."""
        factory = queryUtility(IVocabularyFactory, u'imio.dashboard.creatorsvocabulary')
        self.assertEquals(len(factory(self.portal)), 1)
        self.assertTrue('test_user_1_' in factory(self.portal))
        # no fullname, title is the login
        self.assertEquals(factory(self.portal).getTerm('test_user_1_').title, 'test_user_1_')
        # add another user, create content and test again
        membershipTool = getToolByName(self.portal, 'portal_membership')
        membershipTool.addMember('test_user_2_', 'password', ['Manager'], [])
        user2 = membershipTool.getMemberById('test_user_2_')
        user2.setMemberProperties({'fullname': 'User 2'})
        self.assertEquals(user2.getProperty('fullname'), 'User 2')
        login(self.portal, 'test_user_2_')
        # vocabulary cache not cleaned
        self.assertEquals(len(factory(self.portal)), 1)
        self.portal.invokeFactory('Folder', id='folder2')
        # vocabulary cache cleaned
        self.assertEquals(len(factory(self.portal)), 2)
        self.assertEquals(factory(self.portal).getTerm('test_user_2_').title, 'User 2')

    def test_collectionsvocabulary(self):
        """This will return every DashboardCollections of the portal."""
        # factory = queryUtility(IVocabularyFactory, u'imio.dashboard.collectionsvocabulary')
        # one DashboardCollection
        factory = DashboardCollectionsVocabulary()
        self.assertEquals(len(factory(self.portal)), 1)
        term = factory(self.portal).getTerm(self.dashboardcollection.UID())
        self.assertEquals(term.token, term.value, self.dashboardcollection.UID())
        self.assertEquals(term.title, self.dashboardcollection.Title())

    def test_categorycollectionsvocabulary(self):
        """This will return every DashboardCollections of the portal prefixed by categories."""
        factory = queryUtility(IVocabularyFactory, u'imio.dashboard.collectionsvocabulary')
        # one DashboardCollection
        self.assertEquals(len(factory(self.portal)), 1)
        term = factory(self.portal).getTerm(self.dashboardcollection.UID())
        self.assertEquals(term.token, term.value, self.dashboardcollection.UID())
        self.assertEquals(term.title, '%s - %s' % (self.folder.Title(), self.dashboardcollection.Title()))
