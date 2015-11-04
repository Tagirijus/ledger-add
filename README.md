# Ledger command line accounting - transaction adder in python

## Note

Use this program with care. I am no professional developer and I might have coded something that will destroy your ledger journal without intention. Always keep backups of your files!


## Short description

This is a simple program for adding ledger formatted transactions to a ledger journal. Advantages are *default values* and *presets* for fast entry of transactions.


## Configuration

The program can start with a *parameter* or with a new environment variable `LEDGER_FILE_PATH` set. The *parameter* should be an existing file, to which the transactions will be appended. The environment variable should be the path to such a file. The file has this format: `ledger_[current_year].journal`

The ledger-add program tries to load this file with an auto generated name. This means: you set up `ledger_2015.journal` manually for the year 2015. If you start the program between 2015-01-01 and 2015-12-31, the program will automatically load the file `$LEDGER_FILE_PATH/ledger_2015.journal`.


## Usage

Starting the program on 25th October 2015 with `LEDGER_FILE_PATH` set to `/home/user/ledger_files` and a file already created like `/home/user/ledger_files/ledger_2015.journal` will bring you to this screen:

	Using /home/user/ledger_files/ledger_2015.journal for computing.

	Date [2015/10/25]:

Now you either enter the date you want the transaction to have (maybe the 15th October 2015).

	Date [2015/10/25]: 2015/10/15

Or you enter the difference of days from *today* (maybe yesterday).

	Date [2015/10/25]: -1

This would result in '2015/10/24', or you simply press enter to use the default date (today). It will bring you to the next entry:

	Date [2015/10/25]:
	Presets:
	Name or preset ('p ...') [Einkaufen]:

You see `Presets:` without a list, since you do not have any presets yet. You will be able to create them after the whole procedure. The `Name or preset` entry shows `Einkaufen` in the brackets. It's a default entry you can change in the python code (maybe I will add the option to change it in a separate file / setting). By the way: it's german for 'Shopping' - a very common transaction.

Let's press enter to use `Einkaufen` as the transaction name. It will bring us to the next screen:

	Transaction comment:

Here you can enter a comment, which will be added before the transactin posts. We will leave it blank for now:

	Commodity [€]:

Here we can change the commodity for this actual transaction. Let's use `€` by just pressing enter without input:

	Account 1 name [Konto]:

You can now enter the name for the first account. By default I called it `Konto` which is german for *account*. Let's use it:

	Account 1 amount:

Now we should enter a value. Either it's `+` or `-`, but it has to be something. Maybe we were shopping for 10.00 €. We would just enter `10.00`:

	Account 1 amount: 10.00
	Account 2:

We now have to enter the name of the account which will receive this money. It can be the name of the shop for example - I will just use 'Markt' (german for *market*).

	Account 2: Markt
	Account 2 amount:

The next field can be blank. This way ledger will calculate the balance automatically. It will bring us to this:

	Account 2 amount:
	Account 3:

Since we do not want to add another account yet (we were just shopping at `Markt` for example), we just press enter:

	- - - - -
	2015/10/25 Einkaufen
	 Konto  € 10.00
	 Markt
	- - - - -

	Add this entry? (yes=appends to file, p=saves as a preset) [yes]:

This will show us a summary, which will be appended to the loaded file by just hitting `enter`. It is also possible to add this transaction (without the date) as some kind of preset. Let's do this by entering `p`:

	Preset name [preset]:

Let's call this preset `market`:

	Preset name [preset]: market

Voila! A new preset has been generated. Let's press `enter` again so we can see the saved preset and let's see what will be on the screen at all as well:

	Using /home/user/ledger_file/ledger_2015.journal for computing.

	Date [2015/10/25]:
	Presets:
	Name or preset ('p ...') [Einkaufen]:
	Transaction comment:
	Commodity [€]:
	Account 1 name [Konto]:
	Account 1 amount: 10.00
	Account 2: Markt
	Account 2 amount:
	Account 3:

	- - - - -
	2015/10/25 Einkaufen
	 Konto  € 10.00
	 Markt
	- - - - -

	Add this entry? (yes=appends to file, p=saves as a preset) [yes]: p
	Preset name [preset]: market
	Saved to preset file.

	Date [2015/10/25]:
	Presets: market
	Name or preset ('p ...') [Einkaufen]:

If you want to choose the preset now, you can enter `p market` (or delete it with `d market`):

	Name or preset ('p ...') [Einkaufen]: p market

You can enter `<` to go back to the last input.
You can exit the program by entering `.` in nearly any input.