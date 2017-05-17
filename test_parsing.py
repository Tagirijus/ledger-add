"""Test the parser with test journals."""

from datetime import datetime
import ledgerparse


def test_parse_test_journal():
    """Parse a test journal."""
    journal = ledgerparse.Journal(journal_file='index.journal')
    print(journal.balance(account='.*konto'))

test_parse_test_journal()