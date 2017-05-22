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

    def beforeEditing(self):
        """Check transaction and journal and stuff."""
        infotext, self.journal, self.parentApp.tmpTransC = (
            ledgeradd.check_trans_in_journal(
                settings=self.parentApp.S,
                transaction=self.parentApp.tmpTransC
            )
        )

        # set form title, color and infotext
        self.name = self.parentApp.S.gen_ledger_filename(
            absolute=True,
            year=self.parentApp.tmpTransC.get_date().year
        ) + ' - CHECK'

        if 'transaction is already cleared' in infotext:
            self.color = 'DANGER'
        else:
            self.color = 'WARNING'

        self.check_me.values = infotext.split('\n')


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
