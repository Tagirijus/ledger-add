"""Form for preset choosing."""

import curses
from general.ledgerparse import Transaction
import npyscreen


class PresetList(npyscreen.MultiLineAction):
    """The list holding the choosable presets."""

    def __init__(self, *args, **kwargs):
        """Initialize the class."""
        super(PresetList, self).__init__(*args, **kwargs)

        # set up key shortcuts
        self.add_handlers({
            curses.KEY_DC: self.delete
        })

        # set up additional multiline options
        self.slow_scroll = True

    def actionHighlighted(self, act_on_this, keypress=None):
        """Do something, because a key was pressed."""
        # cancel if there are no values
        if len(self.values) < 1:
            return False

        # get the transaction
        self.parent.parentApp.tmpTrans = Transaction(
            transaction_string=act_on_this['transaction']
        )

        # try to get force_add
        try:
            self.parent.parentApp.tmpTrans.set_force_add(act_on_this['force_add'])
        except Exception:
            pass

        # get date back
        self.parent.parentApp.tmpTrans.set_date(
            self.parent.parentApp.tmpTransC.get_date()
        )

        # show infotext, if it exists
        if act_on_this['info'] != '':
            npyscreen.notify_confirm(
                act_on_this['info']
            )

        # switch back to transaction form
        self.parent.parentApp.switchFormPrevious()

    def delete(self, keypress=None):
        """Ask and delete entry."""
        # cancel if there are no values
        if len(self.values) < 1:
            return False

        entry = self.values[self.cursor_line]

        really = npyscreen.notify_yes_no(
            'Really delete the entry "{}"?'.format(entry['name']),
            form_color='CRITICAL'
        )

        if really:
            deleted = self.parent.parentApp.P.remove_trans(name=entry['name'])

            if not deleted:
                npyscreen.notify_confirm(
                    'Could not delete the entry!',
                    form_color='WARNING'
                )
            else:
                self.update_values()

    def update_values(self):
        """Update the values."""
        self.values = sorted(
            self.parent.parentApp.P.trans_list,
            key=lambda x: x['name']
        )

        self.display()

        # clear filter for not showing doubled entries (npyscreen bug?)
        self.clear_filter()

    def display_value(self, vl):
        """Display values."""
        return '{}'.format(vl['name'])


class PresetForm(npyscreen.ActionFormWithMenus):
    """Form for choosing a preset."""

    def __init__(self, *args, **kwargs):
        """Initialize the class."""
        super(PresetForm, self).__init__(*args, **kwargs)

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
        """Create the widgets."""
        # the menu
        self.m = self.new_menu(name='Menu')
        self.m.addItem(text='Exit', onSelect=self.exit, shortcut='e')

        # the list
        self.preset_list = self.add(
            PresetList,
            name='Presets'
        )

    def beforeEditing(self):
        """Load stuff into the list."""
        self.preset_list.update_values()

    def on_ok(self, keypress=None):
        """Do on ok.."""
        self.parentApp.switchFormPrevious()

    def on_cancel(self, keypress=None):
        """Do the same as on ok.."""
        self.on_ok()
