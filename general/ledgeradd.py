"""The ledgeradd backend."""


import re
from datetime import datetime
from general import ledgerparse
from general.settings import Settings
import os
import shutil


# DO I NEED THIS VARIABLE?
path_to_project = os.path.dirname(os.path.realpath(__file__))


class ReplacementDict(dict):
    """A dict with a __missing__ method."""

    def __missing__(self, key):
        """Return the key instead."""
        return '{' + str(key).replace('#', '') + '}'


def load_journal(
    settings=None,
    year=None
):
    """Load the journal object."""
    # cancel if there is one wrong important argument given
    is_settings = type(settings) is Settings

    if not is_settings:
        return False

    # get actual year, if nothing is set
    if year is None:
        year = datetime.now().year

    # get filenames and paths etc
    absolute = settings.gen_ledger_filename(
        absolute=True,
        year=year
    )

    # simply load the given file
    return ledgerparse.Journal(journal_file=absolute)


def save_journal(
    settings=None,
    journal=None,
    year=None
):
    """Save the journal object."""
    # cancel if there is one wrong important argument given
    is_settings = type(settings) is Settings
    is_journal = type(journal) is ledgerparse.Journal

    if not is_settings or not is_journal:
        return False

    # get actual year, if nothing is set
    if year is None:
        year = datetime.now().year

    # get filenames and paths etc
    absolute = settings.gen_ledger_filename(
        absolute=True,
        year=year
    )

    # save a backup, if file already exists
    if os.path.isfile(absolute):
        shutil.copy2(absolute, absolute + '_bu')

    # simply save the given transaction to one journal, if split files it False
    if not settings.get_split_years_to_files():

        # write journal to file
        f = open(absolute, 'w')
        f.write(journal.to_str(sort_date=True))
        f.close()

        return True

    # or to the years journal
    else:

        # write journal to file
        f = open(absolute, 'w')
        f.write(journal.get_journal_for_year(year=year).to_str(sort_date=True))
        f.close()

        return True

    # if anything should go wrong, return False
    return False


def replace(text=None, trans=None):
    """Return replaced string."""
    text = str(text)

    if type(trans) is not ledgerparse.Transaction:
        return text

    # replacer
    replacer = ReplacementDict()

    # fill the date stuff
    replacer['YEAR'] = datetime.now().year
    replacer['MONTH'] = datetime.now().month
    replacer['DAY'] = datetime.now().day
    replacer['TRANS_YEAR'] = trans.get_date().year
    replacer['TRANS_MONTH'] = trans.get_date().month
    replacer['TRANS_DAY'] = trans.get_date().day
    replacer['TRANS_AUX_YEAR'] = trans.get_aux_date().year
    replacer['TRANS_AUX_MONTH'] = trans.get_aux_date().month
    replacer['TRANS_AUX_DAY'] = trans.get_aux_date().day

    # othe rvalues from transaction
    replacer['PAYEE'] = trans.payee

    # replace the text
    return text.format(**replacer)
