"""Form for entering the transaction data."""

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

    def simple_add(self):
        """Return simple add summary."""
        pager = ['---']
        pager += self.parentApp.tmpTrans.to_str().split('\n')
        pager += ['---']
        pager += ['']
        pager += ['Sum: {}'.format(str(sum(
            [p.get_amount() for p in self.parentApp.tmpTrans.get_postings()]
        )))]
        pager += ['']
        pager += ['']
        pager += ['Add this transaction to the journal?']

        return pager

    def beforeEditing(self):
        """Get values from temp."""
        pager = self.simple_add()

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
        self.parentApp.History += self.parentApp.tmpTrans.to_str()

    def on_ok(self, keypress=None):
        """Press ok."""
        self.add_history()
        self.parentApp.gen_tmptrans()
        self.parentApp.switchFormPrevious()

    def on_cancel(self, keypress=None):
        """Press cancel - go back."""
        self.parentApp.switchFormPrevious()
