# encoding: utf-8

from Acquisition import aq_inner, aq_parent

from zope.interface import implements
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from Products.CMFPlone.utils import base_hasattr
from Products.CMFPlone.utils import getFSVersionTuple
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from eea.facetednavigation.criteria.interfaces import ICriteria
from eea.facetednavigation.subtypes.interfaces import IFacetedNavigable
from collective.eeafaceted.collectionwidget.interfaces import NoFacetedViewDefinedException
from collective.eeafaceted.collectionwidget.utils import getCollectionLinkCriterion
from collective.eeafaceted.collectionwidget.widgets.widget import CollectionWidget

from collective.eeafaceted.dashboard import FacetedDashboardMessageFactory as _
from collective.eeafaceted.dashboard.config import DEFAULT_PORTLET_TITLE

# in Plone5, portlet form is a z3c.form, in Plone4 it uses formlib
HAS_PLONE5 = bool(getFSVersionTuple()[0] >= 5)

if not HAS_PLONE5:
    from zope.formlib import form


class IFacetedCollectionPortlet(IPortletDataProvider):
    """ A portlet that shows controls for faceted with collections """


class Assignment(base.Assignment):
    implements(IFacetedCollectionPortlet)

    @property
    def title(self):
        return DEFAULT_PORTLET_TITLE


class Renderer(base.Renderer):

    def render(self):
        return ViewPageTemplateFile('templates/portlet_facetedcollection.pt')(self)

    @property
    def available(self):
        return bool(self._criteriaHolder)

    @property
    def widget_render(self):
        if getattr(self, 'rendered_widgets', None):
            return self.rendered_widgets
        # get the IFacetedNavigable element the criteria are define on
        criteriaHolder = self._criteriaHolder
        criteria = ICriteria(criteriaHolder)
        widgets = []
        for criterion in criteria.values():
            if criterion.widget != CollectionWidget.widget_type:
                continue
            widget_cls = criteria.widget(wid=criterion.widget)
            widget = widget_cls(criteriaHolder, self.request, criterion)
            widget.display_fieldset = False

            # if we are not on the criteriaHolder, it means
            # that the portlet is displayed on children, we use another template
            # for rendering the widget
            no_redirect = self._isPortletOutsideFaceted(self.context, self._criteriaHolder)
            if no_redirect:
                # avoid redirect
                self.request.set('no_redirect', '1')
            # initialize the widget
            rendered_widget = widget()
            # render the widget as "portlet outside facetednav"
            if no_redirect:
                # compute default criteria to display in the URL
                widget.base_url = self._buildBaseLinkURL(criteria)
                rendered_widget = ViewPageTemplateFile('templates/widget.pt')(widget)
            widgets.append(rendered_widget)
        self.rendered_widgets = ''.join([w for w in widgets])
        return self.rendered_widgets

    def getPortletTitle(self):
        """Return the collection widget display name"""
        try:
            criterion = getCollectionLinkCriterion(self._criteriaHolder)
        except NoFacetedViewDefinedException:
            return DEFAULT_PORTLET_TITLE

        title = criterion and criterion.title or DEFAULT_PORTLET_TITLE
        return title

    def _isPortletOutsideFaceted(self, context, criteriaHolder):
        """Are we outside the faceted?"""
        return (context != criteriaHolder or
                (self.request.get('PUBLISHED') and base_hasattr(self.request['PUBLISHED'], '__name__') and
                 self.request['PUBLISHED'].__name__ != 'facetednavigation_view'))

    def _buildBaseLinkURL(self, criteria):
        """Build the URL that will be used in the href when portlet is displayed
           on a sub element of the container on which is defined the faceted."""
        default_criteria = []
        for criterion in criteria.values():
            # keep default of criteria in the "default" section omitting the collection widget
            if criterion.section == u'default' and \
               not criterion.widget == CollectionWidget.widget_type \
               and criterion.default:
                default_criteria.append('{0}={1}'.format(criterion.__name__, criterion.default))
        base_query_url = '&'.join(default_criteria)
        return '{0}#{1}'.format(self._criteriaHolder.absolute_url(), base_query_url)

    @property
    def _criteriaHolder(self):
        '''Get the element the criteria are defined on.  This will look up parents until
           a folder providing IFacetedNavigable is found.'''
        parent = self.context
        # look up parents until we found the criteria holder or we reach the 'Plone Site'
        while parent and not parent.portal_type == 'Plone Site':
            if IFacetedNavigable.providedBy(parent):
                return parent
            parent = aq_parent(aq_inner(parent))


class AddForm(base.AddForm):
    if HAS_PLONE5:
        schema = IFacetedCollectionPortlet
    else:
        form_fields = form.Fields(IFacetedCollectionPortlet)
    label = _(u"Add Collection Criteria Portlet")
    description = _(u"This portlet shows controls for faceted with collections.")

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    if HAS_PLONE5:
        schema = IFacetedCollectionPortlet
    else:
        form_fields = form.Fields(IFacetedCollectionPortlet)
    label = _(u"Edit Collection Criteria Portlet")
    description = _(u"This portlet shows controls for faceted with collections.")
