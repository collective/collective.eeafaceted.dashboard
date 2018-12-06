Changelog
=========

0.5 (unreleased)
----------------

- Remove contsraint on Products.ZCatalog.
  [sdelcourt]
- Always use latest versions of eea products.
  [gbastien]


0.4 (2018-11-29)
----------------

- Sort uniquely collection vocabulary columns names, because multiple columns
  with same name can be defined for different interfaces.
  [sgeulette]
- Added parameter `default_UID` to `utils.enableFacetedDashboardFor` to set
  default collection UID when enabling faceted on a folder.
  [gbastien]
- When calling `utils.enableFacetedDashboardFor`, set a value in the `REQUEST`
  `enablingFacetedDashboard` specifying that we are currently enabling a
  faceted dashboard.
  [gbastien]

0.3 (2018-11-20)
----------------

- Make sure overrided vocabulary `plone.app.contenttypes.metadatafields` is
  also used when adding a new DashboardCollection, so when current context is
  not a DashboardCollection but the parent.
  [gbastien]
- Added `demo` profile.
  [gbastien]
- Added parameter `show_left_column=True` to `utils.enableFacetedDashboardFor`
  to be able to not show the Plone left column when enabling dashboard on a
  faceted folder.
  [gbastien]
- Added `DashboardCollectionsVocabulary._render_term_title` to make it easy to
  override term title rendering.
  [gbastien]
- Override default eea.facetednavigation spinner (ajax-loader.gif).
  [gbastien]

0.2 (2018-09-04)
----------------

- Get current URL in JS to call the @@json_collections_count a way it works in
  both Plone4 and Plone5.
  [gbastien]
- Moved the `PrettyLinkColumn` and `RelationPrettyLinkColumn` to
  `collective.eeafaceted.z3ctable`.
  [gbastien]

0.1 (2018-06-21)
----------------
- Initial release.
  [gbastien]
