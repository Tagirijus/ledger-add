"""The form for the settings."""

import curses
from general.functions import can_be_dir
from general.functions import acc_list_to_multiline
from general.functions import multiline_to_acc_list
from general.functions import move_list_entry
import npyscreen


class AfaListAction(npyscreen.MultiLineAction):
    """List holding the afa templates."""

    def __init__(self, *args, **kwargs):
        """Initialize the class."""
        super(AfaListAction, self).__init__(*args, **kwargs)

        # set up key shortcuts
        self.add_handlers({
            curses.KEY_IC: self.add_afa_entry,
            curses.KEY_DC: self.delete_afa_entry
        })

    def update_values(self):
        """Update values and refresh view."""
        self.values = self.parent.parentApp.S.get_afa_table()

        self.display()
        self.clear_filter()

    def add_afa_entry(self, keypress=None):
        """Add AfA entry."""
        # get the input from user
        name = npyscreen.notify_input(
            'Name of AfA entry:'
        )

        if not name:
            return

        account = npyscreen.notify_input(
            'Account string:',
            pre_text='afa'
        )

        if not account:
            return

        years = npyscreen.notify_input(
            'Years for AfA:'
        )

        if not years:
            return

        got_it = self.parent.parentApp.S.add_afa_table(
            name=name,
            account=account,
            years=years
        )

        if not got_it:
            npyscreen.notify_confirm(
                'Could not add the AfA table entry, sorry.',
                form_color='WARNING'
            )

        self.update_values()

    def delete_afa_entry(self, keypress=None):
        """Delete AfA entry."""
        # cancel if there are no values
        if len(self.values) < 1:
            return False

        selected = self.values[self.cursor_line]

        really = npyscreen.notify_yes_no(
            'Really delete template "{}"?'.format(selected['name'])
        )

        if really:
            deleted = self.parent.parentApp.S.del_afa_table(index=self.cursor_line)

            if not deleted:
                npyscreen.notify_confirm(
                    'Could not delete the entry, sorry!',
                    form_color='WARNING'
                )

            self.update_values()

    def display_value(self, vl):
        """Display the value."""
        return '[{}]'.format(vl['name'])

    def actionHighlighted(self, act_on_this, keypress):
        """Do something, because a key was pressed."""
        # cancel if there are no values
        if len(self.values) < 1:
            return False

        # get the input from user
        name = npyscreen.notify_input(
            'Name of AfA entry:',
            pre_text=act_on_this['name']
        )

        if not name:
            return

        account = npyscreen.notify_input(
            'Account string:',
            pre_text=act_on_this['account']
        )

        if not account:
            return

        years = npyscreen.notify_input(
            'Years for AfA:',
            pre_text=str(act_on_this['years'])
        )

        if not years:
            return

        got_it = self.parent.parentApp.S.add_afa_table(
            name=name,
            account=account,
            years=years
        )

        if not got_it:
            npyscreen.notify_confirm(
                'Could not modify the AfA table entry, sorry.',
                form_color='WARNING'
            )
        else:
            # delete the old entry
            deleted = self.parent.parentApp.S.del_afa_table(index=self.cursor_line)

            if not deleted:
                npyscreen.notify_confirm(
                    'Something went wrong, sorry!',
                    form_color='WARNING'
                )

        self.update_values()


class TitleAfaList(npyscreen.TitleMultiLine):
    """Inherit from TitleMultiLine, but get MultiLineAction."""

    _entry_type = AfaListAction


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


class SettingsForm(npyscreen.FormMultiPageActionWithMenus):
    """Form for the settings."""

    def __init__(self, *args, **kwargs):
        """Initialize the class."""
        super(SettingsForm, self).__init__(*args, **kwargs)

        # set up key shortcuts
        self.add_handlers({
            '^O': self.on_ok,
            '^Q': self.on_cancel
        })

    def add_afa(self):
        """Add afa table entry."""
        self.afa_table.entry_widget.add_afa_entry()

    def del_afa(self):
        """Delete afa table entry."""
        self.afa_table.entry_widget.delete_afa_entry()

    def exit(self):
        """Exit the programm."""
        self.parentApp.setNextForm(None)
        self.parentApp.switchFormNow()

    def create(self):
        """Create the form."""
        # create the menu
        self.m = self.new_menu(name='Menu')
        self.m.addItem(text='Add afa entry', onSelect=self.add_afa, shortcut='a')
        self.m.addItem(text='Del afa entry', onSelect=self.del_afa, shortcut='d')
        self.m.addItem(text='Exit', onSelect=self.exit, shortcut='e')

        # create input widgets
        self.data_path = self.add_widget_intelligent(
            npyscreen.TitleFilenameCombo,
            name='Data path:',
            begin_entry_at=26
        )
        self.ledger_path = self.add_widget_intelligent(
            npyscreen.TitleFilenameCombo,
            name='Ledger path:',
            begin_entry_at=26
        )
        self.def_state = self.add_widget_intelligent(
            npyscreen.TitleSelectOne,
            name='Default state:',
            begin_entry_at=26,
            values=['*', '!'],
            value=[0],
            slow_scroll=True,
            scroll_exit=True,
            max_height=2
        )
        self.def_code = self.add_widget_intelligent(
            npyscreen.TitleText,
            name='Default code:',
            begin_entry_at=26
        )
        self.def_payee = self.add_widget_intelligent(
            npyscreen.TitleText,
            name='Default payee:',
            begin_entry_at=26
        )
        self.def_commodity = self.add_widget_intelligent(
            npyscreen.TitleText,
            name='Default commodity:',
            begin_entry_at=26
        )
        self.def_postings = self.add_widget_intelligent(
            TitleMultiLineEdit,
            name='Default postings:',
            begin_entry_at=26,
            max_height=4
        )
        self.def_force_add = self.add_widget_intelligent(
            npyscreen.TitleMultiSelect,
            name='Force adding:',
            begin_entry_at=26,
            values=['enabled'],
            max_height=2,
            scroll_exit=True
        )
        self.dec_separator = self.add_widget_intelligent(
            npyscreen.TitleText,
            name='Decimal separator:',
            begin_entry_at=26
        )
        self.date_separator = self.add_widget_intelligent(
            npyscreen.TitleText,
            name='Date separator:',
            begin_entry_at=26
        )
        self.date_fmt = self.add_widget_intelligent(
            npyscreen.TitleText,
            name='Date format:',
            begin_entry_at=26
        )
        self.ledger_file = self.add_widget_intelligent(
            npyscreen.TitleText,
            name='Ledger file:',
            begin_entry_at=26
        )
        self.split_years_to_files = self.add_widget_intelligent(
            npyscreen.TitleMultiSelect,
            name='Split years to files:',
            begin_entry_at=26,
            values=['enabled'],
            max_height=2,
            scroll_exit=True
        )
        self.afa_threshold_amount = self.add_widget_intelligent(
            npyscreen.TitleText,
            name='AfA threshold amount:',
            begin_entry_at=26
        )
        self.afa_table = self.add_widget_intelligent(
            TitleAfaList,
            name='AfA table:',
            begin_entry_at=26,
            scroll_exit=True
        )

    def beforeEditing(self):
        """Get values from settings object."""
        # change name and color according to the settings
        if self.parentApp.S._got_arguments:
            self.name = (
                'Ledgeradd > Settings (arguments altered settings - cannot save!'
            )
            self.color = 'DANGER'
        else:
            self.name = 'Ledgeradd > Settings'
            self.color = 'FORMDEFAULT'

        self.data_path.value = self.parentApp.S.data_path
        self.ledger_path.value = self.parentApp.S.ledger_path
        self.def_state.value = [self.def_state.values.index(self.parentApp.S.def_state)]
        self.def_code.value = self.parentApp.S.def_code
        self.def_payee.value = self.parentApp.S.def_payee
        self.def_commodity.value = self.parentApp.S.def_commodity

        self.def_postings.entry_widget.values = acc_list_to_multiline(
            self.parentApp.S.get_def_postings()
        )

        self.def_force_add.value = (
            [0] if self.parentApp.S.get_def_force_add() else []
        )

        self.dec_separator.value = self.parentApp.S.dec_separator
        self.date_separator.value = self.parentApp.S.date_separator
        self.date_fmt.value = self.parentApp.S.date_fmt
        self.ledger_file.value = self.parentApp.S.ledger_file
        self.split_years_to_files.value = (
            [0] if self.parentApp.S.get_split_years_to_files() else []
        )
        self.afa_threshold_amount.value = str(self.parentApp.S.get_afa_threshold_amount())
        self.afa_table.entry_widget.update_values()

    def on_ok(self, keypress=None):
        """Do something because user pressed ok."""
        # get values into temp variables
        data_path = self.data_path.value.rstrip('/')
        ledger_path = self.ledger_path.value.rstrip('/')

        # check correctness of values
        data_path_correct = can_be_dir(data_path)
        ledger_path_correct = can_be_dir(ledger_path)

        # dir is not creatable
        if not data_path_correct or not ledger_path_correct:
            message = npyscreen.notify_ok_cancel(
                'Data/ledger path is no valid folder name! Please change it!',
                title='Wrong folder names!',
                form_color='WARNING'
            )
            if message:
                # ok, I will edit them again
                self.editing = True
            else:
                # no, I will go back to main screen
                self.editing = False
                # swtich back
                self.parentApp.setNextForm('MAIN')
                self.parentApp.switchFormNow()

        # it is creatable, set new values to settings object
        else:
            # new values
            self.parentApp.S.data_path = data_path
            self.parentApp.S.ledger_path = ledger_path

            # defaults
            self.parentApp.S.def_state = self.def_state.values[self.def_state.value[0]]
            self.parentApp.S.def_code = self.def_code.value
            self.parentApp.S.def_payee = self.def_payee.value
            self.parentApp.S.def_commodity = self.def_commodity.value
            self.parentApp.S.set_def_postings(
                multiline_to_acc_list(self.def_postings.entry_widget.values)
            )
            self.parentApp.S.set_def_force_add(
                True if self.def_force_add.value == [0] else False
            )

            # formatting
            self.parentApp.S.dec_separator = self.dec_separator.value
            self.parentApp.S.date_separator = self.date_separator.value
            self.parentApp.S.date_fmt = self.date_fmt.value

            # file
            self.parentApp.S.ledger_file = self.ledger_file.value
            self.parentApp.S.set_split_years_to_files(
                True if self.split_years_to_files.value == [0] else False
            )

            # afa
            self.parentApp.S.set_afa_threshold_amount(self.afa_threshold_amount.value)
            self.parentApp.S.set_afa_table(self.afa_table.entry_widget.values)

            # store it
            self.parentApp.S.save_settings_to_file()

            # switch back
            self.parentApp.setNextForm('MAIN')
            self.parentApp.switchFormNow()

    def on_cancel(self, keypress=None):
        """Go back without changing a thing."""
        # swtich back
        self.parentApp.setNextForm('MAIN')
        self.parentApp.switchFormNow()
