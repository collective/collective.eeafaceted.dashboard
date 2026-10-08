# -*- coding: utf-8 -*-

from collective.documentgenerator.interfaces import IPODTemplateCondition
from collective.eeafaceted.collectionwidget.utils import getCollectionLinkCriterion
from collective.eeafaceted.dashboard.content.pod_template import (
    DashboardPODTemplateCondition,
)
from collective.eeafaceted.dashboard.testing import IntegrationTestCase
from plone import api
from zope.annotation import IAnnotations
from zope.component import queryMultiAdapter

import lxml.html


class TestDashboardPODTemplate(IntegrationTestCase):
    """The part that changed is the fact that we use another condition
    based on the 'dashboard_collections' field, so test this.
    Call same tests than in collective.documentgenerator TestConfigurablePODTemplateIntegration.
    """

    def setUp(self):
        """ """
        super(TestDashboardPODTemplate, self).setUp()
        # create a DashboardPODTemplate
        self.dashboardtemplate = api.content.create(
            id="dashboardtemplate",
            type="DashboardPODTemplate",
            title="Dashboard template",
            container=self.folder,
        )

    def test_add_form(self):
        """The add form renders the dashboard fields (dashboard_collections vocabulary registered)
        and max_objects accepts 0 (no limit)."""
        dc = api.content.create(
            id="dc1",
            type="DashboardCollection",
            title="Dashboard collection 1",
            container=self.folder,
        )
        html = lxml.html.fromstring(
            self.folder.restrictedTraverse("++add++DashboardPODTemplate")()
        )
        self.assertEqual(
            html.xpath('//input[@name="form.widgets.max_objects"]/@value'), ["500"]
        )
        self.assertEqual(
            len(html.xpath('//input[@name="form.widgets.use_objects"][@type="radio"]')),
            2,
        )
        checkbox = html.xpath(
            '//input[@name="form.widgets.dashboard_collections:list"][@type="checkbox"]'
        )
        self.assertEqual([c.get("value") for c in checkbox], [dc.UID()])
        self.assertEqual(
            html.xpath(
                'normalize-space(//label[@for="{0}"])'.format(checkbox[0].get("id"))
            ),
            "Folder - Dashboard collection 1",
        )

        def max_objects_errors(value):
            self.request.form["form.widgets.max_objects"] = value
            # the request copies its form in 'other', read first by z3c.form
            self.request.set("form.widgets.max_objects", value)
            add_form = self.folder.restrictedTraverse(
                "++add++DashboardPODTemplate"
            ).form_instance
            add_form.update()
            errors = add_form.extractData()[1]
            return [
                e
                for e in errors
                if e.widget is not None and e.widget.__name__ == "max_objects"
            ]

        self.assertEqual(max_objects_errors("0"), [])
        self.assertEqual(max_objects_errors("7"), [])
        self.assertEqual(len(max_objects_errors("-1")), 1)

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
            id="dc1",
            type="DashboardCollection",
            title="Dashboard collection 1",
            container=self.folder,
        )
        dashboardcollection2 = api.content.create(
            id="dc2",
            type="DashboardCollection",
            title="Dashboard collection 2",
            container=self.folder,
        )

        criterion_name = getCollectionLinkCriterion(self.folder).__name__
        self.request.form["{0}[]".format(criterion_name)] = dashboardcollection1.UID()
        self.assertTrue(self.dashboardtemplate.can_be_generated(self.folder))

        # now if restricted to dashboardcollection2, it is no more generable
        self.dashboardtemplate.dashboard_collections = [dashboardcollection2.UID()]
        self.assertFalse(self.dashboardtemplate.can_be_generated(self.folder))
        # except if it is the current collection
        self.request.form["{0}[]".format(criterion_name)] = dashboardcollection2.UID()
        # clear cache for collectionwidget.utils.getCurrentCollection
        cache_key = "collectionwidget-utils-getCurrentCollection-{0}".format(
            self.folder.UID()
        )
        del IAnnotations(self.request)[cache_key]
        self.assertTrue(self.dashboardtemplate.can_be_generated(self.folder))
