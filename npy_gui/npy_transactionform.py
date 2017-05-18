"""Form for entering the transaction data."""

import npyscreen


class TitleMultiLineEdit(npyscreen.TitleText):
    """Titled MultiLineEdit."""

    _entry_type = npyscreen.MultiLineEdit
    scroll_exit = True

    def reformat(self):
        """Reformat the content."""
        self.entry_widget.full_reformat()


class TransactionForm(npyscreen.ActionFormWithMenus):
    """Transaction form for entering the transaction data."""

    def __init__(self, *arg, **kwargs):
        """Initialize the class."""
        super(TransactionForm, self).__init__(*arg, **kwargs)

        # set up key shortcuts
        self.add_handlers({
            '^O': self.on_ok,
            '^Q': self.on_cancel
        })

    def new_trans(self):
        """Make new transaction."""
        self.parentApp.tmpTrans_new = True
        self.beforeEditing()

    def show_settings(self):
        """Switch to settings form."""
        self.values_to_tmp()
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
        self.m.addItem(text='Settings', onSelect=self.show_settings, shortcut='s')
        self.m.addItem(text='Exit', onSelect=self.exit, shortcut='e')

        self.date = self.add(
            npyscreen.TitleDateCombo,
            name='Date:',
            begin_entry_at=20
        )
        self.state = self.add(
            npyscreen.TitleSelectOne,
            name='State:',
            begin_entry_at=20,
            values=['*', '!'],
            value=[0],
            slow_scroll=True,
            scroll_exit=True,
            max_height=2
        )
        self.code = self.add(
            npyscreen.TitleText,
            name='Code:',
            begin_entry_at=20
        )
        self.payee = self.add(
            npyscreen.TitleText,
            name='Payee',
            begin_entry_at=20
        )
        self.comments = self.add(
            TitleMultiLineEdit,
            name='Comments:',
            begin_entry_at=20,
            max_height=2,
            value=''
        )

        self.account_a = self.add(
            npyscreen.TitleText,
            name='Account a:',
            begin_entry_at=20
        )
        self.account_a_amount = self.add(
            npyscreen.TitleText,
            name='Account a amount:',
            begin_entry_at=20
        )
        self.account_a_comments = self.add(
            TitleMultiLineEdit,
            name='Acc a comments:',
            begin_entry_at=20,
            max_height=2,
            value=''
        )

        self.account_b = self.add(
            npyscreen.TitleText,
            name='Account b:',
            begin_entry_at=20
        )
        self.account_b_amount = self.add(
            npyscreen.TitleText,
            name='Account b amount:',
            begin_entry_at=20
        )
        self.account_b_comments = self.add(
            TitleMultiLineEdit,
            name='Acc b comments:',
            begin_entry_at=20,
            max_height=2,
            value=''
        )

        self.account_c = self.add(
            npyscreen.TitleText,
            name='Account c:',
            begin_entry_at=20
        )
        self.account_c_amount = self.add(
            npyscreen.TitleText,
            name='Account c amount:',
            begin_entry_at=20
        )
        self.account_c_comments = self.add(
            TitleMultiLineEdit,
            name='Acc c comments:',
            begin_entry_at=20,
            max_height=2,
            value=''
        )

        self.account_d = self.add(
            npyscreen.TitleText,
            name='Account d:',
            begin_entry_at=20
        )
        self.account_d_amount = self.add(
            npyscreen.TitleText,
            name='Account d amount:',
            begin_entry_at=20
        )
        self.account_d_comments = self.add(
            TitleMultiLineEdit,
            name='Acc d comments:',
            begin_entry_at=20,
            max_height=2,
            value=''
        )

    def beforeEditing(self):
        """Get values from temp / settings if new."""
        # generate transaction from settings defaults, if tmpTrans is new
        if self.parentApp.tmpTrans_new:
            self.parentApp.gen_tmptrans()

        self.date.value = self.parentApp.tmpTrans.get_date()
        self.state.value = [self.state.values.index(self.parentApp.tmpTrans.get_state())]
        self.code.value = self.parentApp.tmpTrans.code
        self.payee.value = self.parentApp.tmpTrans.payee
        self.comments.value = '\n'.join(self.parentApp.tmpTrans.get_comments())

        acc = self.parentApp.tmpTrans.get_postings()[0]
        self.account_a.value = acc.account
        self.account_a_amount.value = (
            '' if acc.get_no_amount() else str(acc.get_amount_str())
        )
        self.account_a_comments.value = '\n'.join(acc.get_comments())

        acc = self.parentApp.tmpTrans.get_postings()[1]
        self.account_b.value = acc.account
        self.account_b_amount.value = (
            '' if acc.get_no_amount() else str(acc.get_amount_str())
        )
        self.account_b_comments.value = '\n'.join(acc.get_comments())

        acc = self.parentApp.tmpTrans.get_postings()[2]
        self.account_c.value = acc.account
        self.account_c_amount.value = (
            '' if acc.get_no_amount() else str(acc.get_amount_str())
        )
        self.account_c_comments.value = '\n'.join(acc.get_comments())

        acc = self.parentApp.tmpTrans.get_postings()[3]
        self.account_d.value = acc.account
        self.account_d_amount.value = (
            '' if acc.get_no_amount() else str(acc.get_amount_str())
        )
        self.account_d_comments.value = '\n'.join(acc.get_comments())

    def values_to_tmp(self):
        """Store vlaues to temp."""
        self.parentApp.tmpTrans.set_date(self.date.value)
        self.parentApp.tmpTrans.set_state(
            self.state.values[self.state.value[0]]
        )
        self.parentApp.tmpTrans.code = self.code.value
        self.parentApp.tmpTrans.payee = self.payee.value
        self.parentApp.tmpTrans.set_comments(
            self.comments.value.splitlines()
        )

        # clear postigns to add them new from widgets
        self.parentApp.tmpTrans.clear_postings()

        self.parentApp.tmpTrans.add_posting(
            account=self.account_a.value,
            commodity=self.parentApp.S.def_commodity,
            amount=self.account_a_amount.value,
            comments=self.account_a_comments.value.splitlines()
        )

        self.parentApp.tmpTrans.add_posting(
            account=self.account_b.value,
            commodity=self.parentApp.S.def_commodity,
            amount=self.account_b_amount.value,
            comments=self.account_b_comments.value.splitlines()
        )

        self.parentApp.tmpTrans.add_posting(
            account=self.account_c.value,
            commodity=self.parentApp.S.def_commodity,
            amount=self.account_c_amount.value,
            comments=self.account_c_comments.value.splitlines()
        )

        self.parentApp.tmpTrans.add_posting(
            account=self.account_d.value,
            commodity=self.parentApp.S.def_commodity,
            amount=self.account_d_amount.value,
            comments=self.account_d_comments.value.splitlines()
        )

    def on_ok(self, keypress=None):
        """Press ok."""
        self.values_to_tmp()

        # switch to transaction check form
        self.parentApp.setNextForm('TransactionCheck')
        self.parentApp.switchFormNow()

    def on_cancel(self, keypress=None):
        """Press cancel - exit programm."""
        self.exit()
