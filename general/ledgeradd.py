"""The ledgeradd backend."""


from datetime import datetime
from decimal import Decimal
from general import ledgerparse
from general.settings import Settings
from general.preset import Preset
import os
import shutil


# DO I NEED THIS VARIABLE?
path_to_project = os.path.dirname(os.path.realpath(__file__))


class ReplacementDict(dict):
    """A dict with a __missing__ method."""

    def __missing__(self, key):
        """Return the key instead."""
        return '{' + str(key).replace('#', '') + '}'


def get_top_account(account=''):
    """
    Return top account name.

    ledger account names are separated by ':'. So for this string
        Expenses:Car:Gas
    this function would return
        Gas
    """
    if len(str(account).split(':')) > 1:
        return str(account).split(':')[-1]
    else:
        return str(account)


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
    return ledgerparse.Journal(
        journal_file=absolute,
        decimal_sep=settings.dec_separator,
        date_sep=settings.date_separator
    )


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

    trans.lists_to_postings(
        settings.get_def_postings(),
        settings.def_commodity
    )

    return trans


def trans_add(
    infotext='',
    settings=None,
    journal=None,
    transaction=None,
    skip_last_info_part=False
):
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

    infotext += '---\n'
    infotext += transaction.to_str()
    infotext += '\n---\n'
    infotext += '\n'
    infotext += 'Money flow pos: {}\n'.format(str(sum(
        [
            p.balance() for p in transaction.get_postings()
            if p.balance() > 0
        ]
    )))
    infotext += 'Money flow neg: {}\n'.format(str(sum(
        [
            p.balance() for p in transaction.get_postings()
            if p.balance() < 0
        ]
    )))
    infotext += 'Account {}: {}\n'.format(
        ''.join([p.account for p in transaction.get_postings() if p.get_no_amount()]),
        str(sum(
            [
                p.balance() for p in transaction.get_postings()
                if p.get_no_amount()
            ]
        ))
    )
    if not skip_last_info_part:
        infotext += '\n\n'
        infotext += 'Add this transaction to the journal?\n'

    return infotext


def trans_modify(settings=None, journal=None, transaction=None):
    """Modify transaction and return infotext."""
    is_settings = type(settings) is Settings
    is_journal = type(journal) is ledgerparse.Journal
    is_trans = type(transaction) is ledgerparse.Transaction

    # cancel if one object is wrong
    if not is_settings or not is_journal or not is_trans:
        return 'Invalid arguments given in trans_modify()!'

    vorher = str(transaction)

    # get original transaction
    trans = journal.trans_exists(code=transaction.code)

    # tweak the dates

    # nothign is set, take the default settings date as new aux date (today)
    if settings.date is None and settings.aux_date is None:
        trans.set_aux_date(transaction.get_date())

    # date is set, take this as new aux date
    elif settings.date is None and settings.aux_date is not None:
        trans.set_aux_date(settings.aux_date)

    # date and aux date are set: alter the dates accordingly
    elif settings.date is not None and settings.aux_date is not None:
        trans.set_date(settings.date)
        trans.set_aux_date(settings.aux_date)

    # check if cleared and add extra warning
    is_cleared = trans.get_state() == '*'

    # un/clear it
    if settings.args.uncleared:
        trans.set_state('!')
    else:
        trans.set_state('*')

    # fill back the transaction
    transaction._to_transaction(transaction_string=trans.to_str())

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

    # cancel if one object is wrong
    if not is_settings:
        return (
            'Invalid arguments given in check_trans_in_journal()!',
            ledgerparse.Journal(journal_string=''),
            ledgerparse.Transaction(transaction_string='')
        )

    # get the transaction
    if type(transaction) is not ledgerparse.Transaction:
        transaction = default_transaction(settings=settings)

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


def replace_settings_defaults(settings=None):
    """Return new Settings object with replaced defaults."""
    is_settings = type(settings) is Settings

    if not is_settings:
        return settings

    # replace the account stuff

    for a in settings.get_def_postings():
        # name
        if len(a) > 0:
            a[0] = replace(
                text=a[0],
                trans=default_transaction(settings=settings)
            )

        # comments
        if len(a) > 2:
            a[2] = replace(
                text=a[2],
                trans=default_transaction(settings=settings)
            )

    return settings


def non_gui_presets_replace(settings=None, transaction=None):
    """Replace preset trans with given argument values."""
    is_settings = type(settings) is Settings
    is_trans = type(transaction) is ledgerparse.Transaction

    if not is_settings or not is_trans:
        return transaction

    # get the date form settings
    transaction.set_date(settings.date)
    transaction.set_aux_date(settings.date)

    # get the state form the settings
    if settings.args.uncleared:
        transaction.set_state('!')

    # get code
    if settings.args.code is not None:
        transaction.code = settings.args.code

    # get payee
    if settings.args.payee is not None:
        transaction.payee = settings.args.payee

    transaction.payee = replace(text=transaction.payee, trans=transaction)

    # get commodity
    if settings.args.commodity is not None:
        transaction.commodity = settings.args.commodity

    # get comments
    comments = '\n'.join(transaction.get_comments())

    if settings.args.comments is not None:
        comments = settings.args.comments

    transaction.set_comments(
        replace(
            text=comments,
            trans=transaction
        ).splitlines()
    )

    # replace posting comments
    for p in transaction.get_postings():
        for i, c in enumerate(p.get_comments()):
            p.get_comments()[i] = replace(
                text=c,
                trans=transaction
            )

    return transaction

def non_gui_preset(settings=None, presets=None):
    """Preset handling for non-GUI version."""
    is_settings = type(settings) is Settings
    is_preset = type(presets) is Preset

    if not is_settings or not is_preset:
        print('Something went wrong, sorry.')
        exit()

    # priority is
    #   1. preset add
    #   2. preset (use)
    #   3. preset del

    # preset add
    if settings.args.preset_add is not None:

        # ask name
        name = settings.args.preset_add

        # ask infotext
        if not settings.args.force:
            infotext = input('Infotext for preset: ')
        else:
            infotext = ''

        # append transaction
        worked = presets.add_trans(
            name=name,
            info=infotext,
            transaction=default_transaction(settings=settings)
        )

        if not worked:
            if not settings.args.quiet:
                print(
                    'Could not add the preset to the presets! It probably exists already'
                )
            exit()
        else:
            if not settings.args.quiet:
                print('Preset "{}" added to the presets!'.format(name))
            exit()

    # preset (use)
    if settings.args.preset is not None:

        # get transaction preset (dict)
        trans_preset = presets.get_trans(name=settings.args.preset)

        # cancel if preset does not exist
        if not trans_preset:
            if not settings.args.quiet:
                print('Preset {} does not exist!'.format(settings.args.preset))
            exit()

        # show infotext
        if not settings.args.quiet and trans_preset['info'] != '':
            print('Infotext:')
            print(trans_preset['info'])
            print()

        # get transaction
        trans = ledgerparse.Transaction(
            transaction_string=trans_preset['transaction']
        )

        # replace it by arguments
        trans = non_gui_presets_replace(
            settings=settings,
            transaction=trans
        )

        # append / modify this preset to the journal
        non_gui_append_or_modify(
            settings=settings,
            transaction=trans
        )

    # preset del
    if settings.args.preset_del is not None:

        if not settings.args.force:
            # ask user
            really = input('Really delete the preset "{}" [yes|y|no|n]: '.format(
                settings.args.preset_del
            ))

            if really.lower() != 'yes' and really.lower() != 'y':
                if not settings.args.quiet:
                    print('Canceling ...')
                exit()

            # try to delete the preset
            worked = presets.remove_trans(name=settings.args.preset_del)

            if not worked:
                if not settings.args.quiet:
                    print('Could not delete the preset!')
            else:
                if not settings.args.quiet:
                    print('Preset deleted!')

            exit()


def non_gui_append_or_modify(settings=None, transaction=None):
    """Append or modify transaction."""
    is_settings = type(settings) is Settings

    if not is_settings:
        print('Something went wrong ...')
        exit()

    # handle replacement function for non-gui application
    settings = replace_settings_defaults(settings=settings)

    # check transaction and journal and stuff
    infotext, journal, trans = check_trans_in_journal(
        settings=settings,
        transaction=transaction,
    )

    # check if transaction works
    check = trans.check()
    if check['need_more_accounts']:
        if not settings.args.quiet:
            print('Need more accounts.')

    if check['cannot_balance']:
        if not settings.args.quiet:
            print('Cannot balance accounts.')

    if check['need_more_accounts'] or check['cannot_balance']:
        if not settings.args.quiet:
            print('Canceling ...')
        exit()

    # also get the filename
    filename = settings.gen_ledger_filename(
        absolute=True,
        year=trans.get_date().year
    )

    # show infotext with filename
    if not settings.args.quiet:
        print('Working with:')
        print(filename)
        print()
        print(infotext)

    # ask user for change, if not settings.args.force is True
    if not settings.args.force:
        user = input('[yes|y|no|n]: ')
        if user.lower() not in ['yes', 'y']:
            # cancel
            if not settings.args.quiet:
                print('Canceled ...')
            exit()

    # do it, if input is yes|y or settings.args.force is True
    saved = save_journal(
        settings=settings,
        journal=journal,
        year=trans.get_date().year
    )

    if not saved:
        if not settings.args.quiet:
            print('Saving went wrong. Wrong file?')
            exit()
    else:
        if not settings.args.quiet:
            print('Done!')
            exit()


def non_gui_application(settings=None, presets=None):
    """Start the non-GUI application of ledgeradd."""
    is_settings = type(settings) is Settings
    is_preset = type(presets) is Preset

    if not is_settings or not is_preset:
        print('Something went wrong, sorry.')
        exit()

    # just list presets
    if settings.args.presets_show:
        print(', '.join([p['name'] for p in presets.trans_list]))
        exit()

    # preset handling
    if (
        settings.args.preset_add is not None or
        settings.args.preset_del is not None or
        settings.args.preset is not None
    ):
        non_gui_preset(settings=settings, presets=presets)

    non_gui_append_or_modify(settings=settings)


def afa_get_postings(transaction=None):
    """Return postings with amount > 0 from transaction in list."""
    if type(transaction) is not ledgerparse.Transaction:
        return []

    return [
        p for p in transaction.get_postings()
        if p.balance() > 0
    ]


def afa_single_transaction(
    year=None,
    transaction=None,
    posting=None,
    afa_account=None,
    amount=None
):
    """Generate a single afa transaction."""
    is_year = type(year) is int
    is_trans = type(transaction) is ledgerparse.Transaction
    is_posting = type(posting) is ledgerparse.Posting
    afa_account = str(afa_account)
    is_amount = type(amount) is Decimal

    # return empty transaction, if an argument is invalid
    if not is_year or not is_trans or not is_posting or not is_amount:
        return ledgerparse.Transaction(transaction_string='')

    # generate a new transaction with given data
    new_trans = ledgerparse.Transaction(
        date=datetime(year=year, month=12, day=31),  # afa transaction is end of the year
        aux_date=datetime(year=year, month=12, day=31),
        state='*',
        code=transaction.code,
        payee=transaction.payee,
        comments=transaction.get_comments()
    )

    # add the depreciation posting to the transaction
    new_trans.add_posting(
        account=posting.account,
        commodity=posting.commodity,
        amount=amount,
        comments=posting.get_comments()
    )

    # add the afa account posting to the transaction
    new_trans.add_posting(
        account=afa_account + ':' + get_top_account(account=posting.account)
    )

    return new_trans


def afa_generate_transactions(
    settings=None,
    afa_type=None,
    transaction=None,
    posting=None
):
    """Generate list with transactions for the afa feature."""
    is_settings = type(settings) is Settings
    is_afa_type = type(afa_type) is dict
    is_trans = type(transaction) is ledgerparse.Transaction
    is_posting = type(posting) is ledgerparse.Posting

    # return empty list, if any argument is invalid
    if not is_settings or not is_afa_type or not is_trans or not is_posting:
        return []

    # calculate the shit!

    # check if postings amount is < settings afa threshold amount
    if posting.get_amount() < settings.get_afa_threshold_amount():
        # return a list with only one transaction
        return [
            afa_single_transaction(
                year=transaction.get_date().year,
                transaction=transaction,
                posting=posting,
                afa_account=afa_type['account'],
                amount=posting.get_amount() * -1
            )
        ]

    # otherwise split the transactions over the years

    # init output variable
    all_trans = []

    # calculate the depreciation amount per month
    per_year_amount = round(posting.get_amount() / afa_type['years'], 2)
    per_month_amount = round(per_year_amount / 12, 2)

    # get starting value for item
    remaining_amount = posting.get_amount()
    depreciate_amount = Decimal('0.00')

    # get starting year of the transactions
    year = transaction.get_date().year
    start_year = year

    # generate and append afa transactions, while amount is > 0
    while remaining_amount > 0:

        # depreciate the remaining_amount for actual year
        # only happens for the buy-year of the item
        if year == start_year:
            month_left = 13 - transaction.get_date().month
            remaining_amount -= per_month_amount * month_left
            depreciate_amount += per_month_amount * month_left

        # go on with the other years, while remaining_amount >= per_year_amount
        elif year > start_year and remaining_amount >= per_year_amount:
            remaining_amount -= per_year_amount
            depreciate_amount += per_year_amount

        # or just depreciate the remaining
        else:
            depreciate_amount = remaining_amount
            remaining_amount = 0

        # generate an afa transaction for this year
        all_trans.append(afa_single_transaction(
            year=year,
            transaction=transaction,
            posting=posting,
            afa_account=afa_type['account'],
            amount=depreciate_amount * -1
        ))

        # go into the next year and reset depreciation
        year += 1
        depreciate_amount = Decimal('0.00')

    return all_trans


def afa_check_trans_in_journal(settings=None, transaction=None):
    """
    Check if transaction exists in journal.

    Return original transaction or error code as string.
    """
    is_settings = type(settings) is Settings

    # cancel on invalid argument
    if not is_settings:
        return 'check_trans_in_journal_afa() got wrong argument.'

    # get the transaction
    if type(transaction) is not ledgerparse.Transaction:
        transaction = default_transaction(settings=settings)

    # cancel if the transaction has no code
    if transaction.code == '':
        return 'Given transaction is missing a code!'

    # get trans for actual year
    found_trans = load_journal(
        settings=settings,
        year=transaction.get_date().year
    ).trans_exists(code=transaction.code)

    # or search it in the last year, if it was not found
    if not found_trans:
        found_trans = load_journal(
            settings=settings,
            year=transaction.get_date().year - 1
        ).trans_exists(code=transaction.code)

    # cancel if it as not found in the last year either
    if not found_trans:
        return 'No transaction with this code found in this or the last year.'

    # or retun the transaction otherwise
    return found_trans


def afa_generate_journals(settings=None, transaction_list=None):
    """
    Generate new journals with given list, which holds transactions.

    Outputs a tuple like this:
        (infotext, {year: Journal object})
    """
    is_settings = type(settings) is Settings
    is_list = type(transaction_list) is list

    # return empty stuff, if one argument is invalid
    if not is_settings or not is_list:
        return (
            'Invalid arguments given in afa_generate_journals().',
            {}
        )

    # also cancel if list is empty
    if len(transaction_list) == 0:
        return (
            'No afa transactions generated.',
            {}
        )

    # init variables
    journals = {}
    infotext = ''

    # cycle through the transactions
    for t in transaction_list:

        # split_years is enabled
        if settings.get_split_years_to_files():
            key = t.get_date().year
        else:
            # any year ... but static!
            key = 1987

        # it's the first transaction for this year
        if key not in journals.keys():
            journals[key] = load_journal(
                settings=settings,
                year=key
            )

        # add the transaction to the journal
        journals[key].add_transaction(
            transaction_string=t.to_str()
        )

        # append infotext
        infotext += '\n'
        infotext += journals[key].journal_file
        infotext += '\n---\n'
        infotext += t.to_str()
        infotext += '\n---\n\n'

    infotext += 'Append these transaction/s to the journal/s ?'

    return (
        infotext,
        journals
    )


def afa_save_journal_list(settings=None, journal_dict=None):
    """Save the journal_list to file/s."""
    is_settings = type(settings) is Settings
    is_dict = type(journal_dict) is dict

    # cancel if invalid argument is given
    if not is_settings or not is_dict:
        return False

    # also cancel if dict is empty
    if len(journal_dict.keys()) == 0:
        return False

    # cycle through dict and save every journal
    check = True
    for year in journal_dict.keys():
        saved = save_journal(
            settings=settings,
            journal=journal_dict[year],
            year=year
        )

        check = saved

    return check


def non_gui_afa_feature(settings=None):
    """Start german tax depreciation feature (no-gui version!)."""
    is_settings = type(settings) is Settings

    # cancel if one object is wrong
    if not is_settings:
        print('Something went wrong, sorry.')
        exit()

    # cancel if no afa table exists
    if len(settings.get_afa_table()) == 0:
        if not settings.args.quiet:
            print('No afa table exists. Add entries in the GUI version of this programm.')
            print('Canceling ...')
        exit()

    # check if transaction (code) exists and return the original transaction
    trans = afa_check_trans_in_journal(settings=settings)

    # cancel with "error" code, if no transaction was found
    if type(trans) is str:
        if not settings.args.quiet:
            print(trans)
        exit()

    # get postings which amount is > 0
    posts = afa_get_postings(transaction=trans)

    # cancel if there are no postings
    if len(posts) == 0:
        if not settings.args.quiet:
            print('No postings found for afa feature, canceling ...')
        exit()

    if not settings.args.force:
        # list the postings
        for i, p in enumerate(posts):
            print('{}: {}'.format(i, p.account))

        # ask user which posting / account should be used
        user = input('Which account for afa [0]: ')

        # on wrong input, use 0 as default
        try:
            use_posting = posts[int(user)]
        except Exception:
            use_posting = posts[0]
    else:
        use_posting = posts[0]

    if not settings.args.quiet and not settings.args.force:
        print()

    if not settings.args.force:
        # list afa table from settings
        for i, x in enumerate(settings.get_afa_table()):
            print('{}: {} ({} years)'.format(i, x['name'], x['years']))

        # ask user which afa type it is
        user = input('Which afa type is it [0]: ')

        # on wrong input, use first afa_table type
        try:
            use_afa = settings.get_afa_table()[int(user)]
        except Exception:
            use_afa = settings.get_afa_table()[0]
    else:
        use_afa = settings.get_afa_table()[0]

    # generate a list of transactions according to chosen values
    afa_trans_list = afa_generate_transactions(
        settings=settings,
        afa_type=use_afa,
        transaction=trans,
        posting=use_posting
    )

    # get infotext and list of journals
    infotext, journals = afa_generate_journals(
        settings=settings,
        transaction_list=afa_trans_list
    )

    if not settings.args.force:
        # ask user to append or not
        print(infotext)
        print()

        user = input('[yes|y|no|n]: ')

        if user.lower() not in ['yes', 'y']:
            # cancel
            if not settings.args.quiet:
                print('Canceled ...')
            exit()

    # save the journals
    saved = afa_save_journal_list(
        settings=settings,
        journal_dict=journals
    )

    if not saved:
        if not settings.args.quiet:
            print('Saving went wrong, sorry ...')
    else:
        if not settings.args.quiet:
            print('Done!')
