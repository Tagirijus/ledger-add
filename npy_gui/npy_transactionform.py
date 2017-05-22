"""Form for entering the transaction data."""

from general import ledgeradd
from general.ledgerparse import Transaction
import npyscreen


class TitleMultiLineEdit(npyscreen.TitleText):
    """Titled MultiLineEdit."""

    _entry_type = npyscreen.MultiLineEdit
    scroll_exit = True

    def reformat(self):
        """Reformat the content."""
        self.entry_widget.full_reformat()


class TransactionForm(npyscreen.FormMultiPageActionWithMenus):
    """Transaction form for entering the transaction data."""

    def __init__(self, *arg, **kwargs):
        """Initialize the class."""
        super(TransactionForm, self).__init__(*arg, **kwargs)

        # set up key shortcuts
        self.add_handlers({
            '^O': self.on_ok,
            '^Q': self.on_cancel,
            '^F': self.clear_widget,
            '^A': self.select_account
        })

    def clear_widget(self, keypress=None):
        """Clear widget."""
        self.get_widget(self.editw).value = ''

    def select_account(self, keypress=None):
        """
        Switch to account widget.

        Buggy! npyscreen switches to the widget correctly directly after
        first usage. After that it chooses the wrong widget according
        to following pattern:
            - a widget above account_a is selected:
                > ONE widget above account_a is beeing selected
            - a widget below account_a is selected:
                > ONE widget below account_a is beeing selected
        """
        # disable old editing if it's not the account_a
        self.get_widget(self.editw).entry_widget.editing = False
        # set account_a into focus
        self.set_editing(self.account_a)

    def new_trans(self):
        """Make new transaction."""
        self.parentApp.tmpTrans_new = True
        self.beforeEditing()

    def show_history(self):
        """Sow the history."""
        npyscreen.notify_confirm(
            self.parentApp.History
        )

    def show_settings(self):
        """Switch to settings form."""
        self.values_to_tmp(message=False)
        self.parentApp.setNextForm('Settings')
        self.parentApp.switchFormNow()

    def exit(self):
        """Exit the programm."""
        self.parentApp.setNextForm(None)
        self.parentApp.switchFormNow()

    def create(self):
        """Create the form."""
        # create the menu
        self.m = self.new_menu(name='Menu')
        self.m.addItem(text='New', onSelect=self.new_trans, shortcut='n')
        self.m.addItem(text='History', onSelect=self.show_history, shortcut='h')
        self.m.addItem(text='Settings', onSelect=self.show_settings, shortcut='s')
        self.m.addItem(text='Exit', onSelect=self.exit, shortcut='e')

        self.date = self.add_widget_intelligent(
            npyscreen.TitleDateCombo,
            name='Date:',
            begin_entry_at=20
        )
        self.state = self.add_widget_intelligent(
            npyscreen.TitleSelectOne,
            name='State:',
            begin_entry_at=20,
            values=['*', '!'],
            value=[0],
            slow_scroll=True,
            scroll_exit=True,
            max_height=2
        )
        self.code = self.add_widget_intelligent(
            npyscreen.TitleText,
            name='Code:',
            begin_entry_at=20
        )
        self.payee = self.add_widget_intelligent(
            npyscreen.TitleText,
            name='Payee',
            begin_entry_at=20
        )
        self.comments = self.add_widget_intelligent(
            TitleMultiLineEdit,
            name='Comments:',
            begin_entry_at=20,
            max_height=2,
            value=''
        )

        self.account_a = self.add_widget_intelligent(
            npyscreen.TitleText,
            name='Account a:',
            begin_entry_at=20
        )
        self.account_a_amount = self.add_widget_intelligent(
            npyscreen.TitleText,
            name='Account a amount:',
            begin_entry_at=20
        )
        self.account_a_comments = self.add_widget_intelligent(
            TitleMultiLineEdit,
            name='Acc a comments:',
            begin_entry_at=20,
            max_height=2,
            value=''
        )

        self.account_b = self.add_widget_intelligent(
            npyscreen.TitleText,
            name='Account b:',
            begin_entry_at=20
        )
        self.account_b_amount = self.add_widget_intelligent(
            npyscreen.TitleText,
            name='Account b amount:',
            begin_entry_at=20
        )
        self.account_b_comments = self.add_widget_intelligent(
            TitleMultiLineEdit,
            name='Acc b comments:',
            begin_entry_at=20,
            max_height=2,
            value=''
        )

        self.account_c = self.add_widget_intelligent(
            npyscreen.TitleText,
            name='Account c:',
            begin_entry_at=20
        )
        self.account_c_amount = self.add_widget_intelligent(
            npyscreen.TitleText,
            name='Account c amount:',
            begin_entry_at=20
        )
        self.account_c_comments = self.add_widget_intelligent(
            TitleMultiLineEdit,
            name='Acc c comments:',
            begin_entry_at=20,
            max_height=2,
            value=''
        )

        self.account_d = self.add_widget_intelligent(
            npyscreen.TitleText,
            name='Account d:',
            begin_entry_at=20
        )
        self.account_d_amount = self.add_widget_intelligent(
            npyscreen.TitleText,
            name='Account d amount:',
            begin_entry_at=20
        )
        self.account_d_comments = self.add_widget_intelligent(
            TitleMultiLineEdit,
            name='Acc d comments:',
            begin_entry_at=20,
            max_height=2,
            value=''
        )

        self.account_e = self.add_widget_intelligent(
            npyscreen.TitleText,
            name='Account e:',
            begin_entry_at=20
        )
        self.account_e_amount = self.add_widget_intelligent(
            npyscreen.TitleText,
            name='Account e amount:',
            begin_entry_at=20
        )
        self.account_e_comments = self.add_widget_intelligent(
            TitleMultiLineEdit,
            name='Acc e comments:',
            begin_entry_at=20,
            max_height=2,
            value=''
        )

    def beforeEditing(self):
        """Get values from temp / settings if new."""
        # get title for form according to filename
        self.name = self.parentApp.S.gen_ledger_filename(absolute=True)

        # generate transaction from settings defaults, if tmpTrans is new
        if self.parentApp.tmpTrans_new:
            self.parentApp.gen_tmptrans()

        self.date.value = self.parentApp.tmpTrans.get_date()
        self.state.value = [self.state.values.index(self.parentApp.tmpTrans.get_state())]
        self.code.value = self.parentApp.tmpTrans.code
        self.payee.value = self.parentApp.tmpTrans.payee
        self.comments.value = '\n'.join(self.parentApp.tmpTrans.get_comments())

        if len(self.parentApp.tmpTrans.get_postings()) > 0:
            acc = self.parentApp.tmpTrans.get_postings()[0]
            self.account_a.value = acc.account
            self.account_a_amount.value = (
                '' if acc.get_no_amount() else str(acc.get_amount_str())
            )
            self.account_a_comments.value = '\n'.join(acc.get_comments())

        if len(self.parentApp.tmpTrans.get_postings()) > 1:
            acc = self.parentApp.tmpTrans.get_postings()[1]
            self.account_b.value = acc.account
            self.account_b_amount.value = (
                '' if acc.get_no_amount() else str(acc.get_amount_str())
            )
            self.account_b_comments.value = '\n'.join(acc.get_comments())

        if len(self.parentApp.tmpTrans.get_postings()) > 2:
            acc = self.parentApp.tmpTrans.get_postings()[2]
            self.account_c.value = acc.account
            self.account_c_amount.value = (
                '' if acc.get_no_amount() else str(acc.get_amount_str())
            )
            self.account_c_comments.value = '\n'.join(acc.get_comments())

        if len(self.parentApp.tmpTrans.get_postings()) > 3:
            acc = self.parentApp.tmpTrans.get_postings()[3]
            self.account_d.value = acc.account
            self.account_d_amount.value = (
                '' if acc.get_no_amount() else str(acc.get_amount_str())
            )
            self.account_d_comments.value = '\n'.join(acc.get_comments())

        if len(self.parentApp.tmpTrans.get_postings()) > 4:
            acc = self.parentApp.tmpTrans.get_postings()[4]
            self.account_e.value = acc.account
            self.account_e_amount.value = (
                '' if acc.get_no_amount() else str(acc.get_amount_str())
            )
            self.account_e_comments.value = '\n'.join(acc.get_comments())

    def values_to_tmp(self, message=True):
        """Store vlaues to temp."""
        self.parentApp.tmpTransC = Transaction()

        self.parentApp.tmpTrans.set_date(self.date.value)
        self.parentApp.tmpTransC.set_date(self.date.value)

        self.parentApp.tmpTrans.set_aux_date(self.date.value)
        self.parentApp.tmpTransC.set_aux_date(self.date.value)

        self.parentApp.tmpTrans.set_state(
            self.state.values[self.state.value[0]]
        )
        self.parentApp.tmpTransC.set_state(
            self.state.values[self.state.value[0]]
        )

        self.parentApp.tmpTrans.code = self.code.value
        self.parentApp.tmpTransC.code = self.code.value

        self.parentApp.tmpTrans.payee = self.payee.value
        self.parentApp.tmpTransC.payee = self.payee.value

        self.parentApp.tmpTrans.set_comments(
            self.comments.value.splitlines()
        )
        self.parentApp.tmpTransC.set_comments(
            ledgeradd.replace(
                text=self.comments.value,
                trans=self.parentApp.tmpTrans
            ).splitlines()
        )

        # clear postigns to add them new from widgets
        self.parentApp.tmpTrans.clear_postings()
        self.parentApp.tmpTransC.clear_postings()

        # add accounts and also ad them with replaced values to the copy
        self.parentApp.tmpTrans.add_posting(
            account=self.account_a.value,
            commodity=self.parentApp.S.def_commodity,
            amount=self.account_a_amount.value,
            comments=self.account_a_comments.value.splitlines()
        )
        self.parentApp.tmpTransC.add_posting(
            account=ledgeradd.replace(
                text=self.account_a.value,
                trans=self.parentApp.tmpTrans
            ),
            commodity=self.parentApp.S.def_commodity,
            amount=self.account_a_amount.value,
            comments=ledgeradd.replace(
                text=self.account_a_comments.value,
                trans=self.parentApp.tmpTrans
            ).splitlines()
        )

        self.parentApp.tmpTrans.add_posting(
            account=self.account_b.value,
            commodity=self.parentApp.S.def_commodity,
            amount=self.account_b_amount.value,
            comments=self.account_b_comments.value.splitlines()
        )
        self.parentApp.tmpTransC.add_posting(
            account=ledgeradd.replace(
                text=self.account_b.value,
                trans=self.parentApp.tmpTrans
            ),
            commodity=self.parentApp.S.def_commodity,
            amount=self.account_b_amount.value,
            comments=ledgeradd.replace(
                text=self.account_b_comments.value,
                trans=self.parentApp.tmpTrans
            ).splitlines()
        )

        self.parentApp.tmpTrans.add_posting(
            account=self.account_c.value,
            commodity=self.parentApp.S.def_commodity,
            amount=self.account_c_amount.value,
            comments=self.account_c_comments.value.splitlines()
        )
        self.parentApp.tmpTransC.add_posting(
            account=ledgeradd.replace(
                text=self.account_c.value,
                trans=self.parentApp.tmpTrans
            ),
            commodity=self.parentApp.S.def_commodity,
            amount=self.account_c_amount.value,
            comments=ledgeradd.replace(
                text=self.account_c_comments.value,
                trans=self.parentApp.tmpTrans
            ).splitlines()
        )

        self.parentApp.tmpTrans.add_posting(
            account=self.account_d.value,
            commodity=self.parentApp.S.def_commodity,
            amount=self.account_d_amount.value,
            comments=self.account_d_comments.value.splitlines()
        )
        self.parentApp.tmpTransC.add_posting(
            account=ledgeradd.replace(
                text=self.account_d.value,
                trans=self.parentApp.tmpTrans
            ),
            commodity=self.parentApp.S.def_commodity,
            amount=self.account_d_amount.value,
            comments=ledgeradd.replace(
                text=self.account_d_comments.value,
                trans=self.parentApp.tmpTrans
            ).splitlines()
        )

        self.parentApp.tmpTrans.add_posting(
            account=self.account_e.value,
            commodity=self.parentApp.S.def_commodity,
            amount=self.account_e_amount.value,
            comments=self.account_e_comments.value.splitlines()
        )
        self.parentApp.tmpTransC.add_posting(
            account=ledgeradd.replace(
                text=self.account_e.value,
                trans=self.parentApp.tmpTrans
            ),
            commodity=self.parentApp.S.def_commodity,
            amount=self.account_e_amount.value,
            comments=ledgeradd.replace(
                text=self.account_e_comments.value,
                trans=self.parentApp.tmpTrans
            ).splitlines()
        )

        # check if accounts are valid for ledger

        # a code is given - only needed for modify feature
        if self.parentApp.tmpTrans.check()['code_exists']:
            return True

        # otherwise check things
        check_passed = True
        if self.parentApp.tmpTrans.check()['need_more_accounts']:
            if message:
                npyscreen.notify_confirm(
                    'Need at least two accounts for a valid ledger transaction.',
                    form_color='WARNING'
                )
            check_passed = False
        if self.parentApp.tmpTrans.check()['cannot_balance']:
            if message:
                npyscreen.notify_confirm(
                    'Only one account may have no amount!',
                    form_color='WARNING'
                )
            check_passed = False

        return check_passed

    def on_ok(self, keypress=None):
        """Press ok."""
        if self.values_to_tmp():

            # switch to transaction check form
            self.parentApp.setNextForm('TransactionCheck')
            self.parentApp.switchFormNow()

    def on_cancel(self, keypress=None):
        """Press cancel - exit programm."""
        self.exit()
