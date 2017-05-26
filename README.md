A programm for adding transactions to a ledger journal.

# Features

- Simple appending of transactions with a TUI / GUI or via command line parameters
- Preset system for simpler appending of recurring transactions
- German tax depreciation ('AfA') feature for automatic transaction generation according to the german tax law

The frontend is made with my tweaked version of [npyscreen](https://github.com/Tagirijus/npyscreen/tree/NotifyInput).

# Installation

To be honest: totally helpless here. I have installed my tweaked version of `npyscreen` in the system and my freelance script in my folder, which I start with `python3 run.py`, when in the folder (I made some shortcuts, of course). This is probably totally noob-alike. Maybe somebody is going to improve it some day?

# Usage

Start the programm and open the menu with `Ctrl+X`. Fill the fields and see what happens. Shortcuts are:

	- Ctrl+A : jump to the first account on the transaction form (Bug: works only the first time. Probably a bug of the npyscreen API)
	- Ctrl+DEL : delete the field, which has the focus
	- Ctrl+L : opens presets
	- Ctrl+O : ok button
	- Ctrl+Q : cancel button
	- INSERT : insert afa table entry
	- DELETE : delete afa table entry

# To do

- Old command line interface for people, who like the old interface more.
