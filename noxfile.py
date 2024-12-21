import nox


@nox.session
def lint(session):
    session.install("flake8")
    session.run("flake8", "main.py")


@nox.session
def tests(session):
    session.install("pytest")
    session.install("pandas")
    session.run("pytest")
