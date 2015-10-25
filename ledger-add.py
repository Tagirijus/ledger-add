# coding=utf-8

#
# Programm for adding simple ledger transactions.
# There's a preset system: Press 'p' to chose a preset and save one in the final prompt.
#

import os, sys, datetime




# some default values

default_transaction_name = 'Einkaufen'
default_account_one_name = 'Konto'
default_commodity = '€'



# get the actual path to the python script - for relative loading of the metronome sounds
path_to_project = os.path.dirname(os.path.realpath(__file__))



# check arguments and environment variable 'LEDGER_FILE_PATH' for ledger file
arguments = sys.argv
# no arguments? check environment variable
if len(arguments) < 2:
	try:
		ledger_file = os.environ['LEDGER_FILE_PATH'] + '/ledger_' + datetime.datetime.now().strftime('%Y') + '.journal'
	except Exception:
		# nothing set, quit programm
		print 'No arguments given and environment variable LEDGER_FILE_PATH is not set.'
		exit()
else:
	# using the argument as the file
	ledger_file = arguments[1]

# check if it's a real file
if not os.path.isfile(ledger_file):
	print 'Given \'ledger file\' is not a file.'
	exit()

# everything is fine, go on!
print 'Using', ledger_file, 'for computing.'



# functions and classes

def end(s):
	# exits the programm, if s is a dot - used in the functions of the ledger_class
	if s == '.':
		print
		exit()

def validate_date(d):
	# simple check, if the string d is a valid date format
	try:
		datetime.datetime.strptime(d, '%Y/%m/%d')
		return True
	except ValueError:
		return False

class ledgerer_class(object):
	def __init__(self, the_file):
		if not os.path.isfile(the_file):
			# exits the programm, if the given environment variable or argument is not a file
			print 'Given argument is not a file.'
			exit()


	def preset(self, what):
		# load preset file, if possible, create empty array otherwise
		if os.path.isfile(path_to_project + '/ledger-add.presets'):
			# load file into variable
			preset_file = open(path_to_project + '/ledger-add.presets', 'r')
			self.preset_file_raw = preset_file.readlines()
			self.preset_content = []
			for x in self.preset_file_raw:
				self.preset_content.append(x.rstrip().split('´'))
			preset_file.close()
		else:
			preset_file = open(path_to_project + '/ledger-add.presets', 'w')
			preset_file.write('')
			preset_file.close()
			self.preset_content = []

		# check if its preset chosing
		if what[0:2] == 'p ':

			# get preset name
			preset_name = what[2:]

			# chose preset, or return not-found message + False
			which = -1
			for y, x in enumerate(self.preset_content):
				if x[0] == preset_name:
					which = y
			if which < 0:
				print 'Preset not found.'
				return False

			# get its values from found preset
			# get name, comment and commodity
			self.str_name = self.preset_content[which][1]
			self.str_transaction_comment = self.preset_content[which][2]
			self.str_commodity = self.preset_content[which][3]

			# get accounts and accounts_amonut array
			self.str_accounts = []
			self.str_accounts_amount = []
			c = 1
			for x in xrange(4, len(self.preset_content[which]) ):
				if c == 1:
					self.str_accounts.append(self.preset_content[which][x])
					c += 1
				elif c == 2:
					self.str_accounts_amount.append(self.preset_content[which][x])
					c -= 1
			return True

		# or list / print out the presets
		elif what == 'list':
			print 'Presets: ' + ', '.join(str(x[0]) for x in self.preset_content)
			return False

		# otherwise return False
		return False


	def date(self):
		print

		# the actual date, used as a default template
		self.today = datetime.datetime.now().strftime('%Y/%m/%d')

		user = ''
		# repeat while the input is not a valid date (so it goes on, if the user inputs a correct date)
		input_correct = False
		while not input_correct:
			user = raw_input('Date [' + self.today + ']: ')
			# if user inputs nothing, use the default (today)
			if not user:
				user = self.today
				input_correct = validate_date(user)
			else:
				input_correct = validate_date(user)
			# or tell the user that it is wrong ... or end the programm if it's a '.'
			if not input_correct:
				end(user)
				print 'Wrong input.'
		self.str_date = user
		self.name()


	def name(self):
		# gets the name of the transcation. this is a string, no big checks are needed e.g. regarding the format.
		preset = self.preset('list')
		user = raw_input('Name or preset (\'p ...\') [' + default_transaction_name + ']: ')
		# check for preset command
		if len(user) > 2:
			if user[0:2] == 'p ':
				# input correct?
				preset = self.preset(user)
		if not user:
			user = default_transaction_name
		end(user)

		# preset or manual input?
		if preset:
			self.final_add()
		else:
			self.str_name = user
			self.transaction_comment()


	def transaction_comment(self):
		# gets the comment for the transaction. again: no big checks are needed, string only
		user = raw_input('Transaction comment: ')
		end(user)
		self.str_transaction_comment = user
		self.commodity()


	def commodity(self):
		# change the commodity
		user = raw_input('Commodity [' + default_commodity + ']: ')
		# no input? use default!
		if not user:
			user = default_commodity
		end(user)
		self.str_commodity = user
		self.accounts()


	def accounts(self):
		# set up an array for the transaction posts
		self.str_accounts = []
		self.str_accounts_amount = []

		# get the first transaction post
		user = raw_input('Account 1 name [' + default_account_one_name + ']: ')
		# no input? use default!
		if not user:
			user = default_account_one_name
		end(user)
		self.str_accounts.append(user)

		# gets the amount for the transaction. first transaction post needs an amount
		account_one_amount = False
		while not account_one_amount:
			user = raw_input('Account 1 amount: ')
			if not user:
				print 'First account needs an amount.'
			else:
				account_one_amount = True
		end(user)
		self.str_accounts_amount.append(user)

		# at least one more post is needed for transaction. repeat "while" until a correct input is done
		account_next = True
		account_next_atleast_one_amount = False
		account_next_number = len(self.str_accounts)+1
		while account_next:
			# since it can be more than 2 posts, repeat until the account / post name is blank ...
			user = raw_input('Account ' + str(account_next_number) + ': ' )
			if not user:
				# ... but repeat if there are not at least 2 posts at all
				if len(self.str_accounts) < 2:
					print 'Need at least 2 accounts.'
				else:
					account_next = False
			else:
				end(user)
				self.str_accounts.append(user)

				# also check for the specific amount
				account_next_amount = True
				while account_next_amount:
					user = raw_input('Account ' + str(account_next_number) + ' amount: ')
					# one post may have a blank amount (ledger auto calculate) the others must have an amount
					if not user and account_next_atleast_one_amount:
						print 'Only one account may not have an amount.'
					elif not user and not account_next_atleast_one_amount:
						account_next_atleast_one_amount = True
						account_next_amount = False
						account_next_number += 1
						end(user)
						self.str_accounts_amount.append(user)
					else:
						account_next_amount = False
						account_next_number += 1
						end(user)
						self.str_accounts_amount.append(user)

		self.final_add()


	def final_add(self):
		print
		print '- - - - -'

		# combine the variables to a single string
		# first the date and name of the transaction
		self.final_str = '\n\n' + self.str_date + ' ' + self.str_name + '\n'
		# add the comment, but only if there is a comment set
		if not self.str_transaction_comment == '':
			self.final_str += ' ; ' + self.str_transaction_comment + '\n'
		# add all the transactin posts, which are there
		for x in xrange(0, len(self.str_accounts) ):
			self.final_str += ' ' + self.str_accounts[x]
			# also add its amount, if there is one given
			if self.str_accounts_amount[x]:
				self.final_str += '  ' + self.str_commodity + ' ' + self.str_accounts_amount[x]
			if not x == len(self.str_accounts)-1:
				self.final_str += '\n'
		print self.final_str[4:]
		print '- - - - -'
		print

		# ask if output should be appended
		user = raw_input('Add this entry? (yes=appends to file, p=saves as a preset) [yes]: ')
		if user == 'n' or user == 'no':
			self.date()
		elif user == 'p' or user == 'preset':
			self.save_preset()
		else:
			end(user)
			self.append_file()


	def save_preset(self):
		# get the preset name
		user = raw_input('Preset name [preset]: ')
		if not user:
			new_preset_name = 'preset'
		else:
			new_preset_name = user
		end(user)

		# get the lines of the file
		self.preset('')

		# check if the new preset name is already in the file
		which = -1
		for y, x in enumerate(self.preset_content):
			if x[0] == new_preset_name:
				which = y

		# override existing preset or cancel
		if not which < 0:
			cancel = raw_input('Override existing preset [no]? ')
			if not cancel:
				print 'Canceling ...'
				self.date()

			# no cancelling, override data for chosen preset
			self.preset_file_raw[which] = new_preset_name
			self.preset_file_raw[which] += '´' + self.str_name
			self.preset_file_raw[which] += '´' + self.str_transaction_comment
			self.preset_file_raw[which] += '´' + self.str_commodity
			for x in xrange( 0, len(self.str_accounts) ):
				self.preset_file_raw[which] += '´' + self.str_accounts[x]
				self.preset_file_raw[which] += '´' + self.str_accounts_amount[x]

		else:
			# generate new data for new preset
			tmp = new_preset_name
			tmp += '´' + self.str_name
			tmp += '´' + self.str_transaction_comment
			tmp += '´' + self.str_commodity
			for x in xrange( 0, len(self.str_accounts) ):
				tmp += '´' + self.str_accounts[x]
				tmp += '´' + self.str_accounts_amount[x]
			self.preset_file_raw.append(tmp)

		# generate final output string
		final_output = ''
		for x in self.preset_file_raw:
			final_output += x.rstrip() + '\n'

		# override file
		preset_file = open(path_to_project + '/ledger-add.presets', 'w')
		preset_file.write(final_output)
		preset_file.close()
		print 'Saved to preset file.'

		# start from beginning
		self.date()


	def append_file(self):
		print 'Appending ...'

		# simple append to the given file and start from beginning
		with open(ledger_file, 'a') as my_file:
			my_file.write(self.final_str)
			my_file.close()
		print
		self.date()





# starting program

ledgerer = ledgerer_class(ledger_file)

ledgerer.date()