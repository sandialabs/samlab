Feature: Documentation

    Scenario: Python module documentation
        Given all Python modules
        And the Python reference documentation
        Then every Python module must have a section in the Python reference documentation
        And every section in the Python reference documentation must match a Python module

    @wip
    Scenario: Javascript module documentation
        Given all Javascript modules
        And the Javascript reference documentation
        Then every Javascript module must have a section in the Javascript reference documentation
        And every section in the Javascript reference documentation must match a Javascript module

