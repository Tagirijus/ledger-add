"""The ledgeradd backend."""


from datetime import datetime
import os
import ledgerparse


# DO I NEED THIS VARIABLE?
path_to_project = os.path.dirname(os.path.realpath(__file__))


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
    if split_journal_into_years:
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
