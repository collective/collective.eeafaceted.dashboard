Changelog
=========

0.3 (unreleased)
----------------

- Make sure overrided vocabulary `plone.app.contenttypes.metadatafields` is
  also used when adding a new DashboardCollection, so when current context is
  not a DashboardCollection but the parent.
  [gbastien]
- Added `demo` profile.
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

