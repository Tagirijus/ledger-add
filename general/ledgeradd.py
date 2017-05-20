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
    settings=None
):
    """Load the journal object."""
    # cancel if no valid settings file is given
    if type(settings) is not Settings:
        return False

    # get filenames and paths etc
    path = settings.gen_ledger_filename(path_only=True)
    absolute = settings.gen_ledger_filename(absolute=True)

    # simply load the given file, if split files it False
    if not settings.get_split_years_to_files():
        return ledgerparse.Journal(journal_file=absolute)

    # otherwise: iter through the files accordingly
    # and create a temporary ledger file, which includes the others
    # wrtie them as "include [FILE]" into a temp ledger journal and load this
    # and remove it afterwards
    # crappy solution for my problem

    # first init the absolute filename list
    files = set()

    # generate the regex to search in the path
    regex = re.compile(settings.ledger_file.replace('.', '_.*\.'))

    # iter through the files
    for f in os.listdir(path):

        # and append fitting files to the list
        if regex.match(f):
            files |= set([os.path.abspath(regex.match(f).group())])

    # create content of temp ledger journal
    content = ''
    for f in files:
        content += 'include {}\n'.format(f)

    # create a temp ledger journal file
    f = open(path + 'TEMP_LEDGER_JOURNAL.journal', 'w')
    f.write(content)
    f.close()

    # load this journal now
    out_journal = ledgerparse.Journal(
        journal_file=path + 'TEMP_LEDGER_JOURNAL.journal'
    )

    # delete the temp file
    os.remove(path + 'TEMP_LEDGER_JOURNAL.journal')

    # output the journal
    return out_journal


def save_journal(
    filename=None,
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
