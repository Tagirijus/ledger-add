"""Form for the afa feature."""

from general import ledgeradd
import npyscreen


class AfaTypeChooseList(npyscreen.MultiLineAction):
    """The list holding the choosable afa types."""

    def actionHighlighted(self, act_on_this, keypress):
        """Do something, because a key was pressed."""
        # generate a list of transactions according to chosen values
        self.parent.parentApp.tmpTransList = ledgeradd.afa_generate_transactions(
            settings=self.parent.parentApp.S,
            afa_type=act_on_this,
            transaction=self.parent.parentApp.tmpTransC,
            posting=self.parent.parentApp.tmpPosting
        )

        # get infotext and list of journals
        infotext, self.parent.parentApp.tmpJournals = ledgeradd.afa_generate_journals(
            settings=self.parent.parentApp.S,
            transaction_list=self.parent.parentApp.tmpTransList
        )

        # store infotext in afa pager
        self.parent.parentApp.getForm('AfaCheck').check_me.values = infotext.split('\n')

        # switch form
        self.parent.parentApp.setNextForm('AfaCheck')
        self.parent.parentApp.switchFormNow()

    def display_value(self, vl):
        """Display the value."""
        return '{} ({} years)'.format(vl['name'], vl['years'])


class AfaTypeChooseForm(npyscreen.ActionPopup):
    """Form for choosing the type of the afa depreciation."""

    def __init__(self, *arg, **kwargs):
        """Initialize the class."""
        super(AfaTypeChooseForm, self).__init__(*arg, **kwargs)

        # set up key shortcuts
        self.add_handlers({
            '^O': self.on_ok,
            '^Q': self.on_cancel
        })

        self.color = 'STANDOUT'

    def create(self):
        """Create the form."""
        # create the input widgets
        self.list = self.add(
            AfaTypeChooseList
        )

    def on_ok(self, keypress=None):
        """Cancel and go back."""
        self.parentApp.setNextForm('MAIN')
        self.parentApp.switchFormNow()

    def on_cancel(self, keypress=None):
        """Cancel and go back."""
        self.on_ok(keypress)


class AfaPostingChooseList(npyscreen.MultiLineAction):
    """The list holding the choosable postings."""

    def actionHighlighted(self, act_on_this, keypress):
        """Do something, because a key was pressed."""
        # store chosen posting to temp
        self.parent.parentApp.tmpPosting = act_on_this

        # switch to type chooser
        self.parent.parentApp.setNextForm('AfaTypeChoose')
        self.parent.parentApp.switchFormNow()

    def display_value(self, vl):
        """Display the value."""
        return '{}'.format(vl.account)


class AfaPostingChooseForm(npyscreen.ActionPopup):
    """Form for choosing the posting of the transaction."""

    def __init__(self, *arg, **kwargs):
        """Initialize the class."""
        super(AfaPostingChooseForm, self).__init__(*arg, **kwargs)

        # set up key shortcuts
        self.add_handlers({
            '^O': self.on_ok,
            '^Q': self.on_cancel
        })

        self.color = 'STANDOUT'

    def create(self):
        """Create the form."""
        # create the input widgets
        self.list = self.add(
            AfaPostingChooseList
        )

    def on_ok(self, keypress=None):
        """Cancel and go back."""
        self.parentApp.setNextForm('MAIN')
        self.parentApp.switchFormNow()

    def on_cancel(self, keypress=None):
        """Cancel and go back."""
        self.on_ok(keypress)


class AfaCheckForm(npyscreen.ActionFormWithMenus):
    """Form for checking the afa feature."""

    def __init__(self, *arg, **kwargs):
        """Initialize the class."""
        super(AfaCheckForm, self).__init__(*arg, **kwargs)

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

    def add_history(self):
        """Add transaction to the history."""
        for trans in self.parentApp.tmpTransList:
            # add separator, if there already are history entries
            if self.parentApp.History != '':
                self.parentApp.History += (
                    '\n\n--- --- --- --- --- --- --- --- --- --- --- ---\n\n'
                )

            # add the transaction to it
            self.parentApp.History += trans.to_str()

    def on_ok(self, keypress=None):
        """Append it and save the new journals."""
        # save the journals
        saved = ledgeradd.afa_save_journal_list(
            settings=self.parentApp.S,
            journal_dict=self.parentApp.tmpJournals
        )

        if not saved:
            # did not work
            npyscreen.notify_confirm(
                'Saving went wrong, sorry ...',
                form_color='WARNING'
            )
        else:
            self.add_history()

        # switch back to main
        self.on_cancel()

    def on_cancel(self, keypress=None):
        """Switch back."""
        self.parentApp.setNextForm('MAIN')
        self.parentApp.switchFormNow()
