"""The ledgeradd backend."""


from datetime import datetime
import os
from general.ledgerparse import Transaction


# DO I NEED THIS VARIABLE?
path_to_project = os.path.dirname(os.path.realpath(__file__))


class ReplacementDict(dict):
    """A dict with a __missing__ method."""

    def __missing__(self, key):
        """Return the key instead."""
        return '{' + str(key).replace('#', '') + '}'


def gen_journal_filename(
    ledger_path='',
    ledger_filename='ledgeradd_ledger.journal',
    year=None,
    split_years_to_files=True
):
    """Generate the absolute path to the ledger journal file."""
    # get the year
    try:
        year = int(year)
        year = str(year)
    except Exception:
        year = datetime.now().strftime('%Y')

    # generate the name, if a file for every year is wanted
    if split_years_to_files:
        # append the year, if no {year} in filename pattern
        if '{year}' not in ledger_filename:
            filename = ledger_filename.replace('.', '_{}.'.format(year))

        # {year} exists in pattern, replace it with the year
        else:
            filename = ledger_filename.format(year=year)

    # no year splitting enabled, use the pattern instead
    else:
        filename = ledger_filename

    # return path to relative file, if no path is given
    if ledger_path == '':
        return filename

    # check if path ends with /
    if ledger_path[-1:] != '/':
        ledger_path += '/'

    # return absolute path to file
    return ledger_path + filename


def replace(text=None, trans=None):
    """Return replaced string."""
    text = str(text)

    if type(trans) is not Transaction:
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
