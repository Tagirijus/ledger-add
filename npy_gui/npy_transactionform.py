"""Form for entering the transaction data."""

from general import ledgeradd
from general.functions import acc_list_to_multiline
from general.functions import multiline_to_acc_list
from general.functions import move_list_entry
from general.ledgerparse import Transaction
import npyscreen


class PostingList(npyscreen.MultiLineEditable):
    """PostingList holding teh posts."""

    def __init__(self, *arg, **kwargs):
        """Initialize the class."""
        super(PostingList, self).__init__(*arg, **kwargs)

        # set up key shortcuts
        self.add_handlers({
            '+': self.move_up,
            '-': self.move_down
        })

        # set up additional multiline options
        self.scroll_exit = True

    def move_up(self, keypress=None):
        """Move selected offer up in the list."""
        lis = self.values

        # cancel if list is < 2
        if len(lis) < 2:
            return False

        # move selected item up
        new_index = move_list_entry(
            lis=lis,
            index=self.cursor_line,
            direction=1
        )

        self.cursor_line = new_index

    def move_down(self, keypress=None):
        """Move selected offer down in the list."""
        lis = self.values

        # cancel if list is < 2
        if len(lis) < 2:
            return False

        # move selected item up
        new_index = move_list_entry(
            lis=lis,
            index=self.cursor_line,
            direction=-1
        )

        self.cursor_line = new_index


class TitleMultiLineEdit(npyscreen.TitleText):
    """Titled MultiLineEdit"""

    _entry_type = PostingList


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
            '^A': self.select_account,
            '^L': self.show_presets
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
            - a widget above account[0] is selected:
                > ONE widget above account[0] is beeing selected
            - a widget below account[0] is selected:
                > ONE widget below account[0] is beeing selected
        """
        # disable old editing if it's not the account[0]
        self.get_widget(self.editw).entry_widget.editing = False
        self.set_editing(self.postings)

    def new_trans(self):
        """Make new transaction."""
        self.parentApp.tmpTrans_new = True
        self.beforeEditing()

    def afa_feature(self):
        """Start the afa feature."""
        # cancel if there is no afa table in the settings
        if len(self.parentApp.S.get_afa_table()) == 0:
            npyscreen.notify_confirm(
                'No afa table exists. Add entries in the settings.',
                form_color='WARNING'
            )
            return False

        # save the entered transaction
        self.values_to_tmp(message=False)

        trans = ledgeradd.afa_check_trans_in_journal(
            settings=self.parentApp.S,
            transaction=self.parentApp.tmpTransC
        )

        # got no transaction, but error message
        if type(trans) is str:
            npyscreen.notify_confirm(
                trans,
                form_color='WARNING'
            )
            return False

        # seems ok, go on to the first afa form
        posts = ledgeradd.afa_get_postings(transaction=trans)

        # cancle if no posts were found
        if len(posts) == 0:
            npyscreen.notify_confirm(
                'No postings found for afa feature, canceling ...',
                form_color='WARNING'
            )

        # otherwise go on

        # fill the chooseforms
        self.parentApp.getForm('AfaPostingChoose').list.values = posts
        self.parentApp.getForm('AfaTypeChoose').list.values = (
            self.parentApp.S.get_afa_table()
        )

        # switch to the posting chooser first
        self.parentApp.setNextForm('AfaPostingChoose')
        self.parentApp.switchFormNow()

    def show_history(self):
        """Sow the history."""
        npyscreen.notify_confirm(
            self.parentApp.History
        )

    def show_presets(self, keypress=None):
        """Show presets."""
        self.values_to_tmp(message=False)
        self.parentApp.setNextForm('Presets')
        self.parentApp.switchFormNow()

    def add_preset(self):
        """Add current trans to presets."""
        self.values_to_tmp(message=False)

        # get name for preset
        name = npyscreen.notify_input(
            'Name for preset'
        )

        if not name:
            return

        # get info for preset
        info = npyscreen.notify_input(
            'Infotext'
        )

        if info is False:
            return

        # try to add it to the presets
        added = self.parentApp.P.add_trans(
            name=name,
            info=info,
            transaction=self.parentApp.tmpTrans
        )

        if not added:
            npyscreen.notify_confirm(
                'Could not add preset. Name probably already exists.',
                form_color='WARNING'
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
        self.m.addItem(text='Afa feature', onSelect=self.afa_feature, shortcut='a')
        self.m.addItem(text='History', onSelect=self.show_history, shortcut='h')
        self.m.addItem(text='Show presets', onSelect=self.show_presets, shortcut='p')
        self.m.addItem(text='Add to presets', onSelect=self.add_preset, shortcut='P')
        self.m.addItem(text='Settings', onSelect=self.show_settings, shortcut='s')
        self.m.addItem(text='Exit', onSelect=self.exit, shortcut='e')

        self.date = self.add_widget_intelligent(
            npyscreen.TitleDateCombo,
            name='Date:',
            begin_entry_at=22
        )
        self.state = self.add_widget_intelligent(
            npyscreen.TitleSelectOne,
            name='State:',
            begin_entry_at=22,
            values=['*', '!'],
            value=[0],
            slow_scroll=True,
            scroll_exit=True,
            max_height=2
        )
        self.code = self.add_widget_intelligent(
            npyscreen.TitleText,
            name='Code:',
            begin_entry_at=22
        )
        self.payee = self.add_widget_intelligent(
            npyscreen.TitleText,
            name='Payee',
            begin_entry_at=22
        )
        self.comments = self.add_widget_intelligent(
            TitleMultiLineEdit,
            name='Comments:',
            begin_entry_at=22,
            max_height=2
        )

        self.postings = self.add_widget_intelligent(
            TitleMultiLineEdit,
            name='Postings:',
            begin_entry_at=22,
            max_height=8
        )

        self.force_add = self.add_widget_intelligent(
            npyscreen.TitleMultiSelect,
            name='Force adding:',
            begin_entry_at=22,
            values=['enabled'],
            max_height=2,
            scroll_exit=True
        )

    def beforeEditing(self):
        """Get values from temp / settings if new."""
        # get title for form according to filename
        self.name = self.parentApp.S.gen_ledger_filename(absolute=True)

        # generate transaction from settings defaults, if tmpTrans is new
        if self.parentApp.tmpTrans_new:
            self.parentApp.gen_tmptrans()

        self.date.value = self.parentApp.tmpTrans.get_date()
        self.date.entry_widget.dateFmt = self.parentApp.S.date_fmt
        self.state.value = [self.state.values.index(self.parentApp.tmpTrans.get_state())]
        self.code.value = self.parentApp.tmpTrans.code
        self.payee.value = self.parentApp.tmpTrans.payee
        self.comments.entry_widget.values = self.parentApp.tmpTrans.get_comments()
        self.postings.entry_widget.values = acc_list_to_multiline(
            self.parentApp.tmpTrans.postings_to_lists()
        )
        self.force_add.value = (
            [0] if self.parentApp.tmpTrans.get_force_add() else []
        )

    def values_to_tmp(self, message=True):
        """Store values to temp."""
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
            self.comments.entry_widget.values
        )
        self.parentApp.tmpTransC.set_comments(
            [
                ledgeradd.replace(
                    text=x,
                    trans=self.parentApp.tmpTrans
                )
                for x in self.comments.entry_widget.values
            ]
        )

        # force add
        self.parentApp.tmpTrans.set_force_add(
            True if self.force_add.value == [0] else False
        )
        self.parentApp.tmpTransC.set_force_add(
            True if self.force_add.value == [0] else False
        )

        # add accounts and also add them with replaced values to the copy

        self.parentApp.tmpTrans.lists_to_postings(
            multiline_to_acc_list(self.postings.entry_widget.values),
            commodity=self.parentApp.S.def_commodity
        )

        self.parentApp.tmpTransC.lists_to_postings(
            multiline_to_acc_list([
                ledgeradd.replace(text=x, trans=self.parentApp.tmpTrans)
                for x in self.postings.entry_widget.values
            ]),
            commodity=self.parentApp.S.def_commodity
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
                    'Cannot balance accounts!',
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
