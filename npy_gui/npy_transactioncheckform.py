"""Form for entering the transaction data."""

from general import ledgeradd
import npyscreen


class TransactionCheckForm(npyscreen.ActionFormWithMenus):
    """Transaction form for checking the entered transaction data."""

    def __init__(self, *arg, **kwargs):
        """Initialize the class."""
        super(TransactionCheckForm, self).__init__(*arg, **kwargs)

        # set up key shortcuts
        self.add_handlers({
            '^O': self.on_ok,
            '^Q': self.on_cancel
        })

        self.journal = None

    def exit(self):
        """Exit the programm."""
        self.parentApp.setNextForm(None)
        self.parentApp.switchFormNow()

    def create(self):
        """Create the form."""
        # create the menu
        self.m = self.new_menu(name='Menu')
        self.m.addItem(text='Exit', onSelect=self.exit, shortcut='e')

        self.check_me = self.add(npyscreen.Pager)
        self.check_me.autowrap = True

    def trans_add(self):
        """Add to journal and generate ask text."""
        # get title for form according to filename
        self.name = self.parentApp.S.gen_ledger_filename(
            absolute=True,
            year=self.parentApp.tmpTransC.get_date().year
        ) + ' - CHECK'

        # add transaction
        self.journal.add_transaction(
            transaction_string=self.parentApp.tmpTransC.to_str()
        )

        pager = ['---']
        pager += self.parentApp.tmpTransC.to_str().split('\n')
        pager += ['---']
        pager += ['']
        pager += ['Sum: {}'.format(str(sum(
            [p.get_amount() for p in self.parentApp.tmpTransC.get_postings()]
        )))]
        pager += ['']
        pager += ['']
        pager += ['Add this transaction to the journal?']

        return pager

    def trans_modify(self):
        """Return modify summary."""
        # get original transaction
        trans = self.journal.trans_exists(code=self.parentApp.tmpTransC.code)

        # get title for form according to filename
        self.name = self.parentApp.S.gen_ledger_filename(
            absolute=True,
            year=trans.get_date().year
        ) + ' - CHECK'

        # get aux date from actual transaction
        trans.set_aux_date(self.parentApp.tmpTransC.get_date())

        # check if cleared and add extra warning
        is_cleared = trans.get_state() == '*'

        # clear it
        trans.set_state('*')

        # fill tmp again
        self.parentApp.tmpTransC = trans

        pager = ['---']
        pager += self.parentApp.tmpTransC.to_str().split('\n')
        pager += ['---']
        pager += ['']
        pager += ['Sum: {}'.format(str(sum(
            [p.get_amount() for p in self.parentApp.tmpTransC.get_postings()]
        )))]
        pager += ['']
        pager += ['']
        pager += ['Modify this transaction from the journal?']

        if is_cleared:
            pager += ['']
            pager += [
                'Attention: transaction is already cleared. '
                'Would just change the date now!'
            ]
            self.color = 'DANGER'

        return pager

    def beforeEditing(self):
        """Get values from temp."""
        # first load the journal
        self.journal = ledgeradd.load_journal(
            settings=self.parentApp.S
        )

        # check if entered transactions code and payee exist (will go into modify mode)
        if self.journal.trans_exists(code=self.parentApp.tmpTransC.code):
            pager = self.trans_modify()

        else:
            pager = self.trans_add()

        # get the values as ledger string and put them into the pager
        self.check_me.values = (pager)

    def add_history(self):
        """Add transaction to the history."""
        # add separator, if there already are history entries
        if self.parentApp.History != '':
            self.parentApp.History += (
                '\n\n--- --- --- --- --- --- --- --- --- --- --- ---\n\n'
            )

        # add the transaction to it
        self.parentApp.History += self.parentApp.tmpTransC.to_str()

    def on_ok(self, keypress=None):
        """Press ok."""
        # fill history
        self.add_history()

        # save the journal
        saved = ledgeradd.save_journal(
            settings=self.parentApp.S,
            journal=self.journal,
            year=self.parentApp.tmpTransC.get_date().year
        )

        if not saved:
            npyscreen.notify_confirm(
                'Saving went wrong. Wrong file?',
                form_color='DANGER'
            )

        else:
            # switch back form
            self.parentApp.gen_tmptrans()
            self.parentApp.switchFormPrevious()

    def on_cancel(self, keypress=None):
        """Press cancel - go back."""
        self.parentApp.switchFormPrevious()
