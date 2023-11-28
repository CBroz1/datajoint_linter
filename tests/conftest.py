import re

import pytest
from pylint import checkers
from pylint.checkers import BaseChecker
from pylint.lint import PyLinter
from pylint.reporters import BaseReporter


def _read_input(file):
    """Reads the input file and returns a list of test cases"""
    # TODO: Return dict with named cases or parametrize fixtures
    with open(file) as f:
        return [line.strip() for line in re.split(r"\s*# TEST \d{2}", f.read())]


@pytest.fixture
def test_cases_good():
    return _read_input("./tests/schema_good.py")


@pytest.fixture
def test_cases_bad():
    return _read_input("./tests/schema_bad.py")


@pytest.fixture
def linter(
    checker: BaseChecker,
    register: PyLinter,
    enable: str,
    disable: str,
    reporter: BaseReporter,
) -> PyLinter:
    """Returns a linter with the given checker registered."""
    _linter = PyLinter()
    _linter.set_reporter(reporter())
    checkers.initialize(_linter)
    if register:
        register(_linter)
    if checker:
        _linter.register_checker(checker(_linter))
    return _linter
