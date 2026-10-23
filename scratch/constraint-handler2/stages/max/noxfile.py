"""Run tests against an installed distribution."""

import nox


@nox.session(python="3.15", venv_backend="uv")
def tests(session: nox.Session) -> None:
    """Install the package and run pytest with forwarded session arguments."""
    session.install(".", "pytest", "pytest-cov")
    session.run("pytest", *session.posargs)
