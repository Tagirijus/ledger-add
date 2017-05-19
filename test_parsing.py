"""Test the parser with test journals."""

from datetime import datetime
from general.ledgerparse import Journal


def test_parse_test_journal():
    """Parse a test journal."""
    journal = Journal(journal_file='test.journal')
    print(journal.to_str())

test_parse_test_journal()