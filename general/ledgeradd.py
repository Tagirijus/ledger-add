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


def default_transaction(settings=None):
    """Return Transaction object filled by settings defaults."""
    if type(settings) is not Settings:
        return ledgerparse.Transaction(transaction_string='')

    trans = ledgerparse.Transaction(
        decimal_sep=settings.dec_separator,
        date_sep=settings.date_separator,
        date=settings.date,
        aux_date=settings.date,
        state=settings.def_state,
        code=settings.def_code,
        payee=settings.def_payee,
        comments=settings.def_comments
    )

    trans.add_posting(
        account=settings.def_account_a,
        commodity=settings.def_commodity,
        amount=settings.def_account_a_amt,
        comments=settings.def_account_a_com
    )

    trans.add_posting(
        account=settings.def_account_b,
        commodity=settings.def_commodity,
        amount=settings.def_account_b_amt,
        comments=settings.def_account_b_com
    )

    trans.add_posting(
        account=settings.def_account_c,
        commodity=settings.def_commodity,
        amount=settings.def_account_c_amt,
        comments=settings.def_account_c_com
    )

    trans.add_posting(
        account=settings.def_account_d,
        commodity=settings.def_commodity,
        amount=settings.def_account_d_amt,
        comments=settings.def_account_d_com
    )

    trans.add_posting(
        account=settings.def_account_e,
        commodity=settings.def_commodity,
        amount=settings.def_account_e_amt,
        comments=settings.def_account_e_com
    )

    return trans

def trans_add(settings=None, journal=None, transaction=None):
    """Add transaction to journal and generate infotext."""
    is_settings = type(settings) is Settings
    is_journal = type(journal) is ledgerparse.Journal
    is_trans = type(transaction) is ledgerparse.Transaction

    # cancel if one object is wrong
    if not is_settings or not is_journal or not is_trans:
        return 'Invalid arguments given in trans_add()!'

    # add transaction
    journal.add_transaction(
        transaction_string=transaction.to_str()
    )

    infotext = '---\n'
    infotext += transaction.to_str()
    infotext += '\n---\n'
    infotext += '\n'
    infotext += 'Money flow: {}\n'.format(str(sum(
        [
            p.balance() for p in transaction.get_postings()
            if p.balance() > 0
        ]
    )))
    infotext += '\n\n'
    infotext += 'Add this transaction to the journal?\n'

    return infotext


def trans_modify(settings=None, journal=None, transaction=None):
    """Return modify transaction and return infotext."""
    is_settings = type(settings) is Settings
    is_journal = type(journal) is ledgerparse.Journal
    is_trans = type(transaction) is ledgerparse.Transaction

    # cancel if one object is wrong
    if not is_settings or not is_journal or not is_trans:
        return 'Invalid arguments given in trans_modify()!'

    # get original transaction
    trans = journal.trans_exists(code=transaction.code)

    # get aux date from actual transaction
    trans.set_aux_date(transaction.get_date())

    # check if cleared and add extra warning
    is_cleared = trans.get_state() == '*'

    # clear it
    trans.set_state('*')

    # "fill" original transaction back
    transaction = trans

    infotext = '---\n'
    infotext += transaction.to_str()
    infotext += '\n---\n'
    infotext += '\n'
    infotext += 'Money flow: {}\n'.format(str(sum(
        [
            p.balance() for p in transaction.get_postings()
            if p.balance() > 0
        ]
    )))
    infotext += '\n\n'
    infotext += 'Modify this transaction from the journal?\n'

    if is_cleared:
        infotext += '\n'
        infotext += (
            'Attention: transaction is already cleared. '
            'Would just change the date now!\n'
        )

    return infotext


def check_trans_in_journal(settings=None, transaction=None):
    """
    Modify journal with transaction and return tuple.

    Tuple looks like this:
        (infotext, journal, transaction)
    """
    is_settings = type(settings) is Settings
    is_trans = type(transaction) is ledgerparse.Transaction

    # cancel if one object is wrong
    if not is_settings or not is_trans:
        return (
            'Invalid arguments given in check_trans_in_journal()!',
            ledgerparse.Journal(journal_string=''),
            ledgerparse.Transaction(transaction_string='')
        )

    # beginn checking the transaction in the last year and actual year according
    # to the transactions date

    # first check, if a code is given
    if transaction.code != '':

        # check last year and search for the code
        journal = load_journal(
            settings=settings,
            year=transaction.get_date().year - 1
        )
        if journal.trans_exists(code=transaction.code):
            infotext = trans_modify(
                settings=settings,
                journal=journal,
                transaction=transaction
            )
            return (infotext, journal, transaction)

        # load actual year and search for the code
        journal = load_journal(
            settings=settings,
            year=transaction.get_date().year
        )
        if journal.trans_exists(code=transaction.code):
            infotext = trans_modify(
                settings=settings,
                journal=journal,
                transaction=transaction
            )
            return (infotext, journal, transaction)

    # else it's just adding (to the actual year)
    journal = load_journal(
        settings=settings,
        year=transaction.get_date().year
    )

    infotext = trans_add(
        settings=settings,
        journal=journal,
        transaction=transaction
    )

    return (infotext, journal, transaction)


def non_gui_application(settings=None):
    """Start the non-GUI application of ledgeradd."""
    if type(settings) is not Settings:
        print('Something went wrong, sorry.')
        exit()

    # get the transaction
    trans = default_transaction(settings=settings)

    # check transaction and journal and stuff
    infotext, journal, trans = check_trans_in_journal(
        settings=settings,
        transaction=trans
    )

    # ask user for change, if not settings.args.force is True
    if not settings.args.force:
        print(infotext)
        user = input('[yes|y|no|n]: ')
        if user.lower() not in ['yes', 'y']:
            # cancel
            print('Canceled ...')
            exit()

    # do it, if input is yes|y or settings.args.force is True
    saved = save_journal(
        settings=settings,
        journal=journal,
        year=trans.get_date().year
    )

    if not saved:
        print('Saving went wrong. Wrong file?')
    else:
        print('Done!')
