# -*- coding: utf-8 -*-

from zope.component import queryMultiAdapter
from plone import api
from collective.documentgenerator.interfaces import IPODTemplateCondition
from collective.eeafaceted.collectionwidget.utils import getCollectionLinkCriterion
from collective.eeafaceted.dashboard.content.pod_template import DashboardPODTemplateCondition
from collective.eeafaceted.dashboard.testing import IntegrationTestCase


class TestDashboardPODTemplate(IntegrationTestCase):
    """The part that changed is the fact that we use another condition
       based on the 'dashboard_collections' field, so test this.
       Call same tests than in collective.documentgenerator TestConfigurablePODTemplateIntegration."""

    def setUp(self):
        """ """
        super(TestDashboardPODTemplate, self).setUp()
        # create a DashboardPODTemplate
        self.dashboardtemplate = api.content.create(id='dashboardtemplate',
                                                    type='DashboardPODTemplate',
                                                    title='Dashboard template',
                                                    container=self.folder)

    def test_generation_condition_registration(self):
        """ """
        context = self.portal
        condition_obj = queryMultiAdapter(
            (self.dashboardtemplate, context),
            IPODTemplateCondition,
        )
        self.assertTrue(isinstance(condition_obj, DashboardPODTemplateCondition))

    def test_can_be_generated(self):
        """Using same condition than ConfigurablePODTemplate and check
           also field 'dashboard_collections'."""
        # if not restricted to any 'dashboard_collections', available everywhere
        self.dashboardtemplate.dashboard_collections = []
        dashboardcollection1 = api.content.create(
            id='dc1',
            type='DashboardCollection',
            title='Dashboard collection 1',
            container=self.folder
        )
        dashboardcollection2 = api.content.create(
            id='dc2',
            type='DashboardCollection',
            title='Dashboard collection 2',
            container=self.folder
        )

        criterion_name = getCollectionLinkCriterion(self.folder).__name__
        self.request.form['{0}[]'.format(criterion_name)] = dashboardcollection1.UID()
        self.assertTrue(self.dashboardtemplate.can_be_generated(self.folder))

        # now if restricted to dashboardcollection2, it is no more generable
        self.dashboardtemplate.dashboard_collections = [dashboardcollection2.UID()]
        self.assertFalse(self.dashboardtemplate.can_be_generated(self.folder))
        # except if it is the current collection
        self.request.form['{0}[]'.format(criterion_name)] = dashboardcollection2.UID()
        self.assertTrue(self.dashboardtemplate.can_be_generated(self.folder))
