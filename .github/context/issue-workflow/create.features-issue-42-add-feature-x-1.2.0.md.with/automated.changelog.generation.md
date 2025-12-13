## Automated Changelog Generation

When feature or bugfix branches are pushed, the `update-changelog.yml` workflow automatically:

1. Reads the current version from `setup.cfg`
2. Finds all plan files targeting that version (checks filename and CHANGES section header)
3. Extracts CHANGES sections from each plan file
4. Combines them into a single changelog entry following `CHANGES-TEMPLATE.md` guidelines
5. Updates or replaces the version entry in `CHANGELOG.md`
6. Commits the changes with `[skip ci]` to avoid triggering additional workflows

**The workflow runs after Test and Packaging workflows complete successfully.**

This ensures `CHANGELOG.md` stays current as development progresses and is ready for release without manual consolidation.