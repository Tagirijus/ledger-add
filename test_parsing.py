"""Test the parser with test journals."""

from datetime import datetime
from general.ledgerparse import Journal


def test_parse_test_journal():
    """Parse a test journal."""
    journal = Journal(journal_file='test.journal')
    print(journal.to_str())


def test_get_journal_for_year():
    """Journal shoudl return a new Journal with only transactions of given year."""
    journal = Journal(journal_file='test.journal')

    new_j = journal.get_journal_for_year(year=2018)
    assert len(new_j.get_transactions()) == 1

    new_j = journal.get_journal_for_year(year=2016)
    assert len(new_j.get_transactions()) == 3
    print(new_j.to_str())

test_parse_test_journal()