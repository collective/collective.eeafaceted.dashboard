# encoding: utf-8

from collective.eeafaceted.z3ctable.columns import RelationTitleColumn
from collective.eeafaceted.z3ctable.columns import TitleColumn

from imio.prettylink.interfaces import IPrettyLink


class PrettyLinkColumn(TitleColumn):
    """A column that displays the IPrettyLink.getLink column."""

    params = {}

    @property
    def cssClasses(self):
        """Generate a CSS class for each <th> so we can skin it if necessary."""
        cssClasses = super(PrettyLinkColumn, self).cssClasses.copy() or {}
        cssClasses.update({'td': 'pretty_link', })
        return cssClasses

    def getPrettyLink(self, obj):
        pl = IPrettyLink(obj)
        for k, v in self.params.items():
            setattr(pl, k, v)
        return pl.getLink()

    def renderCell(self, item):
        """ """
        return self.getPrettyLink(self._getObject(item))


class RelationPrettyLinkColumn(RelationTitleColumn, PrettyLinkColumn):
    """
    A column displaying related items with IPrettyLink.getLink
    """

    params = {}

    def target_display(self, obj):
        return PrettyLinkColumn.getPrettyLink(self, obj)
