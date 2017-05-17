"""Form for entering the transaction data."""

import npyscreen


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

    def show_settings(self):
        """Switch to settings form."""
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
        self.m.addItem(text='Settings', onSelect=self.show_settings, shortcut='s')
        self.m.addItem(text='Exit', onSelect=self.exit, shortcut='e')

        self.date = self.add(
            npyscreen.TitleDateCombo,
            name='Date:'
        )

    def beforeEditing(self):
        """Get values form temp."""
        self.date.value = self.parentApp.tmpTrans.date

    def on_ok(self, keypress=None):
        """Press ok."""
        pass

    def on_cancel(self, keypress=None):
        """Press cancel - exit programm."""
        self.exit()
