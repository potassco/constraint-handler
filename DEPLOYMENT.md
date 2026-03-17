# Deployment

Releases are deployed when matching version tags are pushed, and the Git tag is
the source of truth for the package version.

- A pushed tag `vMajor.Minor.Revision` is deployed to [pypi].
- A pushed tag `vMajor.Minor.Revision.devN` is deployed to [test.pypi].

The workflow triggers on pushed tags starting with `v`, validates the exact tag
format before building, and passes the tag into the build minus the leading
`v`, so the published package version is determined by the tag and remains a
standard PEP 440 version.

The destination index is determined by the tag format.

For this to work, the workflow has to be granted permission to deploy on the
two services.

[pypi]: https://pypi.org/
[test.pypi]: https://test.pypi.org/
