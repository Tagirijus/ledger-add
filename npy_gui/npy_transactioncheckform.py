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

        # pager here

    def beforeEditing(self):
        """Get values from temp."""
        # get the values as ledger string and put them into the pager
        pass

    def on_ok(self, keypress=None):
        """Press ok."""
        pass

    def on_cancel(self, keypress=None):
        """Press cancel - go back."""
        self.parentApp.switchFormPrevious()
