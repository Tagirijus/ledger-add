"""
A simple ledger-cli parser.

This programm can parse a ledger journal into a python object using simple regex.
Why? The native ledger module is python2 only and beancount is too difficult to
install / understand for me.

Attention: to_str() output will delete the thousands separators!

Maybe in later versions this parser will also be able to calculate things.

Author: Manuel Senfft (www.tagirijus.de)


TODO:
    - calculation / balancing
    - query / search with date and amount values
"""

from datetime import datetime
from decimal import Decimal
import re
import os


class ReplacementDict(dict):
    """A dict with a __missing__ method."""

    def __missing__(self, key):
        """Return the key instead."""
        return str(key)


class Journal(object):
    """Journal which holds the ledger transactions."""

    def __init__(
        self,
        journal_string=None,
        journal_file=None,
        decimal_sep=None,
        date_sep=None
    ):
        """Initialize the class."""
        self._aliases = ReplacementDict()
        self._transactions = []             # [ list with Transaction() objects ]
        self._times = []                    # [ list with Time() objects ]
        self._is_time = False
        self.non_transactions = ''
        self.dec_sep = ',' if decimal_sep is None else decimal_sep
        self.date_sep = '-' if date_sep is None else date_sep

        self.journal_string = journal_string
        self.journal_file = journal_file

        # no file is given, but a string
        if journal_file is None and journal_string is not None:
            self.journal_string = journal_string

        # only a file is given
        elif journal_file is not None and journal_string is None:
            self.journal_string = self._file_to_string(
                journal_file=journal_file
            )

        # regex
        self.re_transaction = re.compile(
            # 4 digits in the beginning, and stuff with leading whitespace after newline
            r'(\d{4,}.+(?:\n[ ]+.+)+)'
        )

        self.re_time = re.compile(
            # starts with i, ends with o + stuff
            r'(i[ ]+.+\no.+)'
        )

        # init methods
        self._add_aliases_from_string()
        self._to_transactions()
        self._to_non_transactions()

    def _file_to_string(self, journal_file):
        """Gather all include files as well and return one big string."""
        out = ''

        # check if file exists and load it
        if os.path.isfile(journal_file):
            f = open(journal_file, 'r')
            the_file = f.readlines()
            f.close()
            # and get its path
            path = os.path.dirname(os.path.abspath(journal_file))
        else:
            return ''

        # append it to the final output, till "include" occurs
        for line in the_file:
            if line.lower().find('include ') != 0:
                out += line
            # otherwise try to load the given file
            else:
                # get filename
                include_me = os.path.basename(
                    line.replace('include ', '').replace('Include ', '').strip()
                ) + '(\n|$)'

                # cycle through the files, if there are some and append their content
                # also replace wildcard with regex-wildcard
                regex = include_me.replace('.', '\.').replace('*', '.*')
                got_a_file = 0
                for filename in os.listdir(path):
                    # file found
                    if re.match(regex, filename):
                        # append two newlines, if it's not the first entry
                        if got_a_file > 0:
                            out += '\n\n'
                        got_a_file += 1

                        # load the file and append it to the output
                        f = open(os.path.join(path, filename), 'r')
                        out += f.read()
                        f.close()

                # newlines at the end of the found "include ..." if there is one
                out += '\n\n' if '\n' in line else ''

        return out

    def _add_aliases_from_string(self, journal_string=None):
        """Get aliases from the journal_string."""
        if journal_string is None:
            journal_string = self.journal_string

        # cycle through ledger journal lines and find "alias" in the beginning
        for l in journal_string.splitlines():
            if l[0:5] == 'alias':
                # get the alias
                tmp = l.replace('alias ', '').split('=')
                if len(tmp) == 2:
                    self._aliases[tmp[0].strip()] = tmp[1].strip()

    def _to_transactions(self, journal_string=None):
        """Convert the journal_string to transaction objects."""
        if journal_string is None:
            journal_string = self.journal_string

        # it's a financial journal
        if self.re_transaction.findall(journal_string):
            self._is_time = False
            # get transaction matches and add the transaction to _transactions
            for trans in self.re_transaction.findall(journal_string):
                self.add_transaction(
                    aliases=self._aliases,
                    decimal_sep=self.dec_sep,
                    date_sep=self.date_sep,
                    transaction_string=trans
                )

        # it's a time journal
        elif self.re_time.findall(journal_string):
            self._is_time = True
            # get time matches and add them to the _times list
            for time in self.re_time.findall(journal_string):
                self.add_time(time_string=time)

    def _to_non_transactions(self, journal_string=None):
        # returns a string with all non-transactions (aliases, comments, etc.)
        if journal_string is None:
            journal_string = self.journal_string

        # clear previous non_transactions string
        self.non_transactions = ''

        output = journal_string

        # iterate every financial transaction and delete it from the output string
        for trans in self.re_transaction.findall(journal_string):
            # delete this transaction from the output
            output = output.replace(trans, '')

        # do the same for the time entries
        for time in self.re_time.findall(journal_string):
            # delete this from the output
            output = output.replace(time, '')

        # strip and set new output
        self.non_transactions = output.strip()

    def add_transaction(
        self,
        journal=None,
        aliases=None,
        decimal_sep=None,
        date_sep=None,
        transaction_string=None,
        date=None,
        aux_date=None,
        state=None,
        code=None,
        payee=None,
        comments=None,
        postings=None
    ):
        """Add a transaction to the _tranactions."""
        if journal is None:
            journal = self

        if aliases is None:
            aliases = self._aliases

        if decimal_sep is None:
            decimal_sep = self.dec_sep

        if date_sep is None:
            date_sep = self.date_sep

        self._transactions.append(Transaction(
            journal=journal,
            aliases=aliases,
            decimal_sep=decimal_sep,
            date_sep=date_sep,
            transaction_string=transaction_string,
            date=date,
            aux_date=aux_date,
            state=state,
            code=code,
            payee=payee,
            comments=comments,
            postings=postings
        ))

    def get_transactions(self):
        """Get _transactions."""
        return self._transactions

    def add_time(
        self,
        journal=None,
        aliases=None,
        date_sep=None,
        time_string=None,
        start=None,
        end=None,
        account=None
    ):
        """Add a transaction to the _tranactions."""
        self._times.append(Time(
            journal=self,
            aliases=aliases,
            date_sep=date_sep,
            time_string=time_string,
            start=start,
            end=end,
            account=account
        ))

    def get_times(self):
        """Get _times."""
        return self._times

    def set_is_time(self, value):
        """Set is_time."""
        self._is_time = bool(value)

    def get_is_time(self):
        """Get is_time."""
        return self._is_time

    def to_str(self, alias=False, sort_date=False):
        """Return journal as readable string."""
        output = ''

        # append the non transactions
        if self.non_transactions != '':
            output += self.non_transactions + '\n\n'

        # get transactions
        if sort_date:
            transactions = sorted(
                [t for t in self._transactions],
                key=lambda x: x._date
            )
        else:
            transactions = [t for t in self._transactions]

        # get times
        if sort_date:
            times = sorted(
                [t for t in self._times],
                key=lambda x: x._start
            )
        else:
            times = [t for t in self._times]

        # append all the transactions
        output += '\n\n'.join([t.to_str(alias=alias) for t in transactions])

        # append all the times
        if len(times) > 0:
            output += '\n\n' + '\n\n'.join([t.to_str(alias=alias) for t in times])

        return output

    def posts(
        self,
        state=None,
        code=None,
        payee=None,
        comment=None,
        account=None
    ):
        """Return list with postings with the given search arguments."""
        #
        # TODO: date query and amount query (non string search)
        #

        # initialize the search regex
        state = '.*' if state is None else state
        code = '.*' if code is None else code
        payee = '.*' if payee is None else payee
        comment = '.*' if comment is None else comment
        account = '.*' if account is None else account

        # gather the postings if journal is financial
        if not self._is_time:
            return [
                p for t in self._transactions for p in t._postings if
                re.match(state, t._state) and
                re.match(code, t.code) and
                re.match(payee, t.payee) and
                re.match(comment, str(t.get_comments())) and
                re.match(account, p.replace_alias(p.account), re.I)
            ]

        # gather postings if journal is time journal
        else:
            return [
                p for p in self._times if
                re.match(account, p.replace_alias(p.account), re.I)
            ]

    def trans(self, *args, **kwargs):
        """Return list with transactions with the given search arguments."""
        if not self._is_time:
            # it's financial
            return list(set([p.trans() for p in self.posts(*args, **kwargs)]))
        else:
            # it's time
            return [p for p in self.posts(*args, **kwargs)]

    def balance(self, account=None):
        """
        Return balance of given account.

        Todo:
            - allow search querries like <= date or > amount etc.
                --> like a ledger querry with '-p ...'
        """
        account = '.*' if account is None else account

        # search in financial transactions
        if not self._is_time:
            return sum(
                [
                    p.balance() for t in self._transactions for p in t._postings
                    if re.match(account, p.replace_alias(p.account), re.I)
                ]
            )

        # search in times
        else:
            return sum(
                [
                    p.hours() for p in self._times
                    if re.match(account, p.replace_alias(p.account), re.I)
                ]
            )

    def trans_exists(self, code=None):
        """Return trans, with the given code."""
        if code == '':
            return False

        for t in self._transactions:
            if t.code == str(code):
                return t

        return False

    def get_journal_for_year(self, year=None):
        """
        Return Journal object holding transactions for given year only.

        When no year is given, it returns a complete copy of the Journal.
        Otherwise it returns a new Journal holding only the transactions
        in this specific year.
        """
        new_journal = Journal(
            journal_string=self.to_str()
        )

        # get simple copy
        if type(year) is not int:
            return new_journal

        # get copy with years transactions
        new_journal._transactions = [
            t for t in new_journal._transactions
            if t._date.year == year
        ]

        return new_journal


class Transaction(object):
    """A ledger transaction object."""

    def __init__(
        self,
        journal=None,
        aliases=None,
        decimal_sep=None,
        date_sep=None,
        transaction_string=None,
        date=None,
        aux_date=None,
        state=None,
        code=None,
        payee=None,
        comments=None,
        postings=None
    ):
        """Initialize the class."""
        self._journal = journal
        self._aliases = ReplacementDict() if aliases is None else aliases
        self._comments = [] if comments is None else comments
        self._postings = [] if postings is None else postings

        self.dec_sep = ',' if decimal_sep is None else decimal_sep
        self.date_sep = '-' if date_sep is None else date_sep
        self.transaction_string = transaction_string

        self._date = datetime.now()
        self.set_date(date)
        self._aux_date = datetime.now()
        self.set_aux_date(aux_date)
        self._state = '*'
        self.set_state(state)
        self.code = '' if code is None else str(code)
        self.payee = '' if payee is None else str(payee)

        # regex
        self.re_transaction_data = re.compile(
            # 4 digit year, 2 digit month and 2 digit day
            r'^(?P<year>\d{4})[/|-](?P<month>\d{2})[/|-](?P<day>\d{2})'
            # same for aux_date, but with leading '=' or nothing
            r'(?:=(?P<year_aux>\d{4})[/|-](?P<month_aux>\d{2})[/|-](?P<day_aux>\d{2}))?'
            # leading whitespace with * or ! or only whitespace
            r'[ ]+(?P<state>[\*|!])?'
            # leading white space + code inside '()' + whitespace or only withespace
            r'[ ]+?(\((?P<code>[^\)].*)\)[ ]+)?'
            # string for payee
            r'(?P<payee>.+)'
        )

        self.re_comment = re.compile(
            # string with leading whitespace and ';'
            r'^[ ]+;(.+)'
        )

        # init methods
        # fill from string, if it's given
        if self.transaction_string is not None:
            self._to_transaction()

        # otherwise assume other values are given and we need the transaction_string
        else:
            self._to_transaction_string()

    def _to_transaction(self, transaction_string=None):
        """Convert the transaction_string into a transaction object."""
        if transaction_string is None:
            transaction_string = self.transaction_string

        # reset postings
        self.clear_postings()

        # cycle through the lines of the given transaction_string
        is_trans = True
        for line in transaction_string.splitlines():

            # get matches
            m_trans = self.re_transaction_data.match(line)
            m_comment = self.re_comment.match(line)

            # it's a transaction header
            if m_trans:

                # get the date
                self._date = datetime(
                    int(m_trans.group('year')),
                    int(m_trans.group('month')),
                    int(m_trans.group('day'))
                )

                # get the aux date
                if (
                    m_trans.group('year_aux') is not None and
                    m_trans.group('month_aux') is not None and
                    m_trans.group('day_aux') is not None
                ):
                    self._aux_date = datetime(
                        int(m_trans.group('year_aux')),
                        int(m_trans.group('month_aux')),
                        int(m_trans.group('day_aux'))
                    )
                else:
                    self._aux_date = self._date

                # get the state
                if m_trans.group('state') is not None:
                    self._state = m_trans.group('state')
                else:
                    self._state = '*'

                # get the code
                if m_trans.group('code') is not None:
                    self.code = m_trans.group('code')
                else:
                    self.code = ''

                # get the payee
                self.payee = m_trans.group('payee')

            # it's a comment of the transaction
            elif m_comment and is_trans:
                self.add_comment(m_comment.group(1))

            # it's a comment of the last added account
            elif m_comment and not is_trans:
                # safety add
                if len(self._postings) > 0:
                    # choose the last account and add the comment
                    self._postings[len(self._postings) - 1].add_comment(
                        m_comment.group(1)
                    )

            # it's an account - from now no more transaction related comments
            else:
                is_trans = False
                self.add_posting(posting_string=line)

    def _to_transaction_string(self):
        """Convert given variables to the _transaction_string."""
        self.transaction_string = self.to_str()

    def journal(self):
        """Get journal."""
        return self._journal

    def add_comment(self, text=''):
        """Add a comment to the _coments."""
        self._comments.append(text)

    def set_comments(self, value):
        """Set comments."""
        if type(value) is list:
            self._comments = [str(e) for e in value]

    def get_comments(self):
        """Return list with comments."""
        return self._comments

    def add_posting(
        self,
        transaction=None,
        aliases=None,
        decimal_sep=',',
        posting_string=None,
        account=None,
        commodity=None,
        no_amount=None,
        amount=None,
        comments=None
    ):
        """Add an account to the transaction object."""
        if transaction is None:
            transaction = self

        if aliases is None:
            aliases = self._aliases

        if decimal_sep is None:
            decimal_sep = self.decimal_sep

        self._postings.append(Posting(
            transaction=transaction,
            aliases=aliases,
            decimal_sep=decimal_sep,
            posting_string=posting_string,
            account=account,
            commodity=commodity,
            no_amount=no_amount,
            amount=amount,
            comments=comments
        ))

    def clear_postings(self):
        """Clear the postings."""
        self._postings = []

    def get_postings(self):
        """Return list with postings."""
        return self._postings

    def set_date(self, value):
        """Set date."""
        if type(value) is datetime:
            self._date = value
        else:
            try:
                self._date = value.strptime('%Y-%m-%d')
            except Exception:
                pass

    def get_date(self):
        """Get date."""
        return self._date

    def set_aux_date(self, value):
        """Set aux_date."""
        if type(value) is datetime:
            self._aux_date = value
        else:
            try:
                self._aux_date = value.strptime('%Y-%m-%d')
            except Exception:
                pass

    def get_aux_date(self):
        """Get aux_date."""
        return self._aux_date

    def set_state(self, value):
        """Set state."""
        if str(value) == '*' or str(value) == '!':
            self._state = str(value)

    def get_state(self):
        """Get state."""
        return self._state

    def check(self):
        """
        Return a check, if something is missing.

        Possible checks are:
            check['need_more_accounts'] = True|False
            check['cannot_balance'] = True|False
        """
        out = {}

        out['code_exists'] = self.code != ''

        out['need_more_accounts'] = len(
            [p for p in self._postings if p.account != '']
        ) < 2

        out['cannot_balance_no_amount'] = len(
            [p for p in self._postings if p._no_amount and p.account != '']
        ) > 1

        out['cannot_balance_values'] = self.balance() != 0

        out['cannot_balance'] = (
            out['cannot_balance_no_amount'] or out['cannot_balance_values']
        )

        return out

    def to_str(self, alias=False):
        """Convert attributes to readable ledger transaction string."""
        # get date
        tmp_date = self._date.strftime(
            '%Y' + self.date_sep + '%m' + self.date_sep + '%d'
        )

        # get aux date
        tmp_aux_date = (
            '=' + self._aux_date.strftime(
                '%Y' + self.date_sep + '%m' + self.date_sep + '%d'
            ) if self._aux_date.date() != self._date.date() else ''
        )

        # get state
        tmp_state = ' ' + self._state

        # get code
        tmp_code = ' (' + self.code + ')' if self.code else ''

        # get payee
        tmp_payee = ' ' + self.payee

        # get comments
        if len(self._comments) > 0:
            tmp_comments = '\n ;' + '\n ;'.join(self._comments)
        else:
            tmp_comments = ''

        # get postings with its comments - but only with given account
        tmp_postings = '\n' + '\n'.join(
            [p.to_str(alias=alias) for p in self._postings if p.account != '']
        )

        return (
            tmp_date + tmp_aux_date + tmp_state + tmp_code + tmp_payee + tmp_comments +
            tmp_postings
        )

    def balance(self, account=None):
        """Return account with balanced amount according to other accounts."""
        # for all accounts
        if account is None:
            return sum(
                [
                    p.balance() for p in self._postings
                    if p.account != ''
                ]
            )

        # for this account only
        else:
            return Decimal('0.00') - sum(
                [
                    p.balance() for p in self._postings
                    if p.account != account and
                    p.account != ''
                ]
            )

    def postings_to_lists(self):
        """Return postings as [account, amount, comments] lists."""
        return [
            p.to_list() for p in self._postings
        ]

    def lists_to_postings(self, value, commodity=None):
        """Get postings from list in list."""
        if type(value) is not list:
            return False

        # first clear the postings
        self.clear_postings()

        # now add the postings from the list
        for p in value:
            account = None
            acc_added = False
            amount = None
            amt_added = False
            no_amount = True
            comments = []

            # cycle through the entries
            for e in p:
                # no ; in string and no account was added
                if not acc_added and not ';' in e:
                    account = e
                    acc_added = True

                # no ; in string and no amount was added
                elif not amt_added and not ';' in e:
                    amount = e
                    amt_added = True
                    no_amount = False

                # ; in string
                if ';' in e:
                    comments += [e.replace(';', '')]

            self.add_posting(
                transaction=self,
                aliases=self._aliases,
                decimal_sep=self.dec_sep,
                account=account,
                commodity=commodity,
                no_amount=no_amount,
                amount=amount,
                comments=comments
            )


class Posting(object):
    """A ledger posting object."""

    def __init__(
        self,
        transaction=None,
        aliases=None,
        decimal_sep=',',
        posting_string=None,
        account=None,
        commodity=None,
        no_amount=None,
        amount=None,
        comments=None
    ):
        """Initialize the class."""
        self._transaction = transaction
        self._aliases = ReplacementDict() if aliases is None else aliases
        self._comments = [] if comments is None else comments

        self.dec_sep = ',' if decimal_sep is None else decimal_sep
        self.posting_string = posting_string

        self.account = str(account)
        self.commodity = '€' if commodity is None else str(commodity)

        # handle not_amount
        self.set_no_amount(no_amount)
        if amount is None or amount == '':
            self.set_no_amount(True)

        self._amount = Decimal('0.00')
        self.set_amount(amount)

        # regex
        self.re_posting = re.compile(
            # start of string, whitespace, characters but ";", few as possible
            # till two whitespaces or more
            r'^[ ]+(?P<account>[^\;]+?)[ ]{2,}'
            # commodity which is no number and one following whitespace or nothing
            r'(?:(?P<commodity_front>\D+?)[ ]+)?'
            # the amount with +/- or not and a number with ',' or '.' as seperators
            r'(?P<amount>[-+]?\d+(?:[,|\.]?\d+)?)?'
            # commodity or not which is no number and one leading whitespace
            r'(?:[ ]+(?P<commodity_back>\D+?))?'
        )

        self.re_posting_only = re.compile(
            # the account with one leading whitespace
            r'^[ ]+(?P<account>[^;]+)'
        )

        # init methods
        # fill from string, if it's given
        if self.posting_string is not None:
            self._to_posting()

        # otherwise assume other values are given and we need the account_string
        else:
            self._to_postings_string()

    def _to_posting(self, posting_string=None):
        """Convert the posting_string to a ledger posting object."""
        if posting_string is None:
            posting_string = self.posting_string

        # get matches
        m_posting = self.re_posting.match(posting_string)
        m_posting_only = self.re_posting_only.match(posting_string)

        # what is the match?
        if m_posting:
            # get its account name
            self.account = m_posting.group('account')

            # get the commodity
            if m_posting.group('commodity_front') is not None:
                self.commodity = m_posting.group('commodity_front')
            elif m_posting.group('commodity_back') is not None:
                self.commodity = m_posting.group('commodity_back')
            else:
                self.commodity = ''

            # get the amount
            if self.dec_sep == ',':
                # get rid of thousand separator
                # and replace ',' with '.'
                tmp_amount = m_posting.group('amount').replace('.', '').replace(
                    ',', '.'
                )
            else:
                # only get rid of thousand separator
                tmp_amount = m_posting.group('amount').replace(',', '')

            # toggle no_amonut to False
            self._no_amount = False

            self.set_amount(tmp_amount)

        # it's an posting without amount
        elif m_posting_only:
            # get its name
            self.account = m_posting_only.group('account')

            # get the commodity
            self.commodity = ''

            # get the amount
            self.set_amount('0.00')

            # get no_amount
            self.set_no_amount(True)

    def _to_postings_string(self):
        """Get posting_string from data."""
        self.posting_string = self.to_str()

    def trans(self):
        """Refer to the linked transaction."""
        return self._transaction

    def replace_alias(self, original):
        """Replace the account name with the aliases."""
        # check if there are subaccounts and use these first
        if ':' in original:
            work_with_me = original[0:original.find(':')]
            append = original[original.find(':'):]
        # or just use the original string
        else:
            work_with_me = original
            append = ''

        # return it
        return self._aliases[work_with_me] + append

    def add_comment(self, text=''):
        """Add a comment to _comments."""
        self._comments.append(text)

    def set_comments(self, value):
        """Set comments."""
        if type(value) is list:
            self._comments = [str(e) for e in value]

    def get_comments(self):
        """Get comments."""
        return self._comments

    def set_amount(self, value):
        """Set amount."""
        try:
            # try to convert it to a Decimal
            self._amount = Decimal(str(value).replace(self.dec_sep, '.'))
        except Exception:
            pass

    def get_amount(self):
        """Get amount."""
        return self._amount

    def get_amount_str(self):
        """Get amout with correct decimal separator."""
        return str(self._amount).replace('.', self.dec_sep)

    def set_no_amount(self, value):
        """Set no_amount."""
        self._no_amount = bool(value)

    def get_no_amount(self):
        """Get no_amount."""
        return self._no_amount

    def balance(self):
        """Return account with balanced amount according to other accounts of trans."""
        if self._no_amount:
            return Decimal('0.00') - sum(
                [
                    p._amount for p in self._transaction._postings
                    if p.account != self.account
                ]
            )
        else:
            return round(self._amount, 2)

    def to_str(self, alias=False):
        """Return readable ledger posting string."""
        # get the account name
        tmp_name = self.replace_alias(self.account) if alias else self.account

        # empty if no_amount
        if self._no_amount:
            tmp_commodity = ''
            tmp_amount = ''

        # not empty
        else:
            # get the commodity
            tmp_commodity = '  {} '.format(self.commodity) if self.commodity else '  '

            """
            Following block will add one or two zeros after the decimal separator,
            if zeros are missing, but it won't add zeros, of the decimal number
            already has two or more digits. So:
            0 will become 0.00
            0.0 will beomce 0.00
            but 0.00 will stay 0.00
            and 0.000 will stay 0.000
            """
            amount = str(self._amount)
            if len(amount.split('.')) > 1:
                amt_int = amount.split('.')[0]
                amt_dec = amount.split('.')[1]
                add_zeros = '0' * (2 - len(amount.split('.')[1]))
                amt_dec += add_zeros
            else:
                amt_int = amount
                amt_dec = '00'

            tmp_amount = '{}{}{}'.format(
                amt_int,
                self.dec_sep,
                amt_dec
            )

        # get comments
        tmp_comments = (
            '\n ;' + '\n ;'.join(self._comments) if len(self._comments) > 0 else ''
        )

        # return string for this account
        return ' ' + tmp_name + tmp_commodity + tmp_amount + tmp_comments

    def to_list(self):
        """Return a list [account, amount as string, comments as string]."""
        # account
        out = [self.account]

        # amount, if it has one
        if not self._no_amount:
            out += [str(self._amount)]

        # comments
        out += [';{}'.format(x) for x in self._comments]

        return out


class Time(object):
    """Object holding a single time data of a time journal."""

    def __init__(
        self,
        journal=None,
        aliases=None,
        date_sep=None,
        time_string=None,
        start=None,
        end=None,
        account=None
    ):
        """Initialize the class."""
        if type(journal) is not Journal:
            print('No proper journal linked to the time post.')
            exit()

        self._journal = journal
        self._aliases = ReplacementDict() if aliases is None else aliases

        self.date_sep = '-' if date_sep is None else date_sep
        self.time_string = time_string

        self._start = datetime.now()
        self.set_start(start)
        self._end = datetime.now()
        self.set_end(end)
        self.account = str(account)

        # regex
        self.re_time_data = re.compile(
            # starts with i + whitspace
            r'i[ ]+'
            # 4 digit year + sep + 2 digit month + sep + 2 digit day + whitespace
            r'(?P<s_year>\d{4})[/|-](?P<s_month>\d{2})[/|-](?P<s_day>\d{2})[ ]+'
            # 2 digit hour + : + 2 digit minute + : + 2 digit second + whitespace
            r'(?P<s_hour>\d{2}):(?P<s_minute>\d{2}):(?P<s_second>\d{2})[ ]+'
            # account string till end of line
            r'(?P<account>.+)[\S\n\r]'
            # starts with o + whitespace
            r'o[ ]+'
            # 4 digit year + sep + 2 digit month + sep + 2 digit day + whitespace
            r'(?P<e_year>\d{4})[/|-](?P<e_month>\d{2})[/|-](?P<e_day>\d{2})[ ]+'
            # 2 digit hour + : + 2 digit minute + : + 2 digit second
            r'(?P<e_hour>\d{2}):(?P<e_minute>\d{2}):(?P<e_second>\d{2})'
        )

        # init method
        self._to_time()

    def _to_time(self, time_string=None):
        """Convert string to time object."""
        if time_string is None:
            time_string = self.time_string

        m_time = self.re_time_data.match(time_string)

        if m_time:
            # fill the data
            self._start = datetime(
                year=int(m_time.group('s_year')),
                month=int(m_time.group('s_month')),
                day=int(m_time.group('s_day')),
                hour=int(m_time.group('s_hour')),
                minute=int(m_time.group('s_minute')),
                second=int(m_time.group('s_second'))
            )

            self.account = m_time.group('account')

            self._end = datetime(
                year=int(m_time.group('e_year')),
                month=int(m_time.group('e_month')),
                day=int(m_time.group('e_day')),
                hour=int(m_time.group('e_hour')),
                minute=int(m_time.group('e_minute')),
                second=int(m_time.group('e_second'))
            )

    def set_start(self, value):
        """Set start."""
        if type(value) is datetime:
            self._start = value
        else:
            try:
                self._start = value.strptime('%Y-%m-%d')
            except Exception:
                pass

    def get_start(self):
        """Get start."""
        return self._start

    def set_end(self, value):
        """Set end."""
        if type(value) is datetime:
            self._end = value
        else:
            try:
                self._end = value.strptime('%Y-%m-%d')
            except Exception:
                pass

    def get_end(self):
        """Get end."""
        return self._end

    def replace_alias(self, original):
        """Replace the account name with the aliases."""
        # check if there are subaccounts and use these first
        if ':' in original:
            work_with_me = original[0:original.find(':')]
            append = original[original.find(':'):]
        # or just use the original string
        else:
            work_with_me = original
            append = ''

        # return it
        return self._aliases[work_with_me] + append

    def to_str(self, alias=False):
        """Return the string in ledger format."""
        # get account
        account = self.replace_alias(self.account) if alias else self.account

        # starting
        output = 'i {} {}\n'.format(
            self._start.strftime('%Y{s}%m{s}%d %H:%M:%S'.format(s=self.date_sep)),
            account
        )

        # ending
        output += 'o {}'.format(
            self._end.strftime('%Y{s}%m{s}%d %H:%M:%S'.format(s=self.date_sep))
        )

        return output

    def time(self):
        """Return timedelta."""
        return self._end - self._start

    def hours(self):
        """Return hours as Decimal."""
        return Decimal(self.time().total_seconds() / 3600)
