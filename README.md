A programm for adding transactions to a ledger journal.

# Features

- Simple appending of transactions with a TUI / GUI or via command line parameters
- Preset system for simpler appending of recurring transactions
- German tax depreciation ('AfA') feature for automatic transaction generation according to the german tax law

The frontend is made with my tweaked version of [npyscreen](https://github.com/Tagirijus/npyscreen/tree/NotifyInput).

# Installation

To be honest: totally helpless here. I made it the noob-way, I think:

1. Cloned my tweaked version of [npyscreen](https://github.com/Tagirijus/npyscreen/tree/NotifyInput) - especially the `NotifyInput` branch and switched to this branch, locally! (`git clone https://github.com/Tagirijus/npyscreen`, `git checkout NotifyInput`, `git pull origin NotifyInput`)
2. Went to the folder and typed `sudo pip3 install . -e` to install this branch in the Python3 modules.
3. Set up an alias in the `.bashrc` to my `run.py` of ledger-add.


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
- Fix bug, which completely can destroy the journal, if it has a transaction without cleared / not cleared status in it (`*` or `!` has to exist in a transaction)!