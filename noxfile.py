import os
import sys

import nox

nox.options.sessions = ("test",)
# nox.options.sessions = "lint_pylint", "typecheck", "test"

EDITABLE_TESTS = True
if "GITHUB_ACTIONS" in os.environ:
    EDITABLE_TESTS = False


@nox.session
def doc(session):
    """
    Build the documentation.

    Accepts the following arguments:
    - serve: open documentation after build
    - further arguments are passed to mkbuild
    """

    options = session.posargs[:]
    open_doc = "serve" in options
    if open_doc:
        options.remove("serve")

    session.install("-e", ".[doc]")

    if open_doc:
        open_cmd = "xdg-open" if sys.platform == "linux" else "open"
        session.run(open_cmd, "http://localhost:8000/systems/constraint_handler/")
        session.run("mkdocs", "serve", *options)
    else:
        session.run("mkdocs", "build", *options)


@nox.session
def dev(session):
    """
    Create a development environment in editable mode.

    Activate it by running `source .nox/dev/bin/activate`.
    """
    session.install("-e", ".[dev]")


@nox.session
def lint_pylint(session):
    """
    Run pylint.
    """
    session.install("-e", ".[lint_pylint]")
    session.run("pylint", "constraint_handler", "tests")


@nox.session
def typecheck(session):
    """
    Typecheck the code using mypy.
    """
    session.install("-e", ".[typecheck]")
    session.run("mypy", "--strict", "-p", "constraint_handler", "-p", "tests")


@nox.session
def test(session):
    """
    Run pytest.

    """

    args = [".[test]"]
    if EDITABLE_TESTS:
        args.insert(0, "-e")
    session.install(*args)
    if session.posargs:
        session.run("pytest", session.posargs[0], "-vvv")
    else:
        session.run("pytest", "-vvv")
