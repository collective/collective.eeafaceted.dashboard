# -*- coding: utf-8 -*-

from collective.documentgenerator.content.condition import ConfigurablePODTemplateCondition
from collective.documentgenerator.content.pod_template import ConfigurablePODTemplate
from collective.documentgenerator.content.pod_template import IConfigurablePODTemplate
from collective.eeafaceted.collectionwidget.interfaces import NotDashboardContextException
from collective.eeafaceted.collectionwidget.utils import getCurrentCollection
from collective.eeafaceted.dashboard import FacetedDashboardMessageFactory as _

from plone.autoform import directives as form

from z3c.form.browser.checkbox import CheckBoxFieldWidget
from z3c.form.browser.radio import RadioFieldWidget
from zope import schema
from zope.interface import implements


import logging
logger = logging.getLogger('collective.eeafaceted.dashboard: DashboardPODTemplate')


class IDashboardPODTemplate(IConfigurablePODTemplate):
    """
    DashboardPODTemplate dexterity schema.
    """

    form.widget('use_objects', RadioFieldWidget)
    use_objects = schema.Bool(
        title=_(u'Use objects as generation context'),
        description=_(u'If selelected, receive awoken objects wrapped into their '
                      u' helper view rather than brains as generation context'),
        default=False,
        required=False,
    )

    form.widget('dashboard_collections', CheckBoxFieldWidget, multiple='multiple', size=15)
    dashboard_collections = schema.List(
        title=_(u'Allowed dashboard collections'),
        description=_(u'Select for which dashboard collections the template will be available. '
                      u'If nothing is selected, the template will be available on every dashboards.'),
        value_type=schema.Choice(source='collective.eeafaceted.dashboard.dashboardcollectionsvocabulary'),
        required=True,
    )
    form.omitted('pod_portal_types')


class DashboardPODTemplate(ConfigurablePODTemplate):
    """
    DashboardPODTemplate dexterity class.
    """

    implements(IDashboardPODTemplate)


class DashboardPODTemplateCondition(ConfigurablePODTemplateCondition):
    """
    """

    def evaluate(self):
        """
        Check:
        - That we are on an allowed dashboard collection (if any defined);
        - Original ConfigurablePODTemplateCondition conditions.
        """
        try:
            current_collection = getCurrentCollection(self.context)
        except NotDashboardContextException:
            return False

        allowed_collections = self.pod_template.dashboard_collections
        if not current_collection or \
           (allowed_collections and not current_collection.UID() in allowed_collections):
            return False

        return super(DashboardPODTemplateCondition, self).evaluate()
