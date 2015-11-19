import os, datetime, sys



# check if environment variable LEDGER_FILE_PATH is set
try:
	ledger_path = os.environ['LEDGER_FILE_PATH']
except Exception:
	# nothing set, quit programm
	print 'Environment variable LEDGER_FILE_PATH is not set.'
	exit()






#######
######## configuration ### ##### #####
#######

# paths to files
archive_file	= ledger_path + '/time_archive.journal'
default_csv		= ledger_path + '/export_all.csv'
convert_all_csv	= False


# format of the Gleeo Time Tracker CSV
row_domain			= 0
row_project      	= 1
row_task         	= 2
row_details      	= 3
row_start_date   	= 4
row_start_time   	= 5
row_end_date     	= 6
row_end_time     	= 7
row_duration     	= 8
row_duration_dec 	= 9
row_project_xtra1	= 10
row_project_xtra2	= 11
row_task_xtra1   	= 12
row_task_xtra2   	= 13
seperator 			= ','
first_line 			= False   # False means that the first line is the head only, not important for content


# format of the ledger output
led_a = row_domain
led_b = row_project
led_c = row_task
led_d = row_details


# super account, in this account are all other accounts
superacc = 'All'


#######
######## ##### ##### ##### ##### #####
#######






# check arguments, 'append' or 'a' will convert default_csv to a ledger journal and append it to archive_file
append_it = False
if len(sys.argv) > 1:
	if sys.argv[1] == 'append' or sys.argv[1] == 'a':
		append_it = True
	else:
		print 'Please use \'append\' or \'a\' for append-mode.'
		print
		exit()



# get list of all CSV files in this directory, if configuration for this is true
csv_files = []
if convert_all_csv:
	for file in os.listdir(ledger_path):
		if file.endswith('.csv'):
			csv_files.append(ledger_path + '/' + file)
	print 'Input file(s):'
	for x in csv_files:
		print '   ' + x[x.rfind('/')+1:]
	print
else:
	if os.path.isfile( default_csv ):
		csv_files.append( default_csv )
		print 'Input file: ' + default_csv
	else:
		print default_csv + ' is no file.'



# big loop for each file
for single_file in csv_files:

	# load the file
	print 'Loading \'' + single_file[single_file.rfind('/')+1:] + '\' ...'
	f = open(single_file, 'r')
	origin_raw = f.read().splitlines()
	if not first_line:
		origin_raw = origin_raw[1:]
	f.close()

	# generate the master variable
	origin = []
	for x in origin_raw:
		origin.append(x.split(seperator))

	# convert the entries to ledger format
	print 'Converting to ledger format ...'
	final_output = ''
	for y, x in enumerate(origin):
		tmp_start =	datetime.datetime.strptime( x[row_start_date] + ' ' + x[row_start_time], '%Y-%m-%d %H:%M' ).strftime('%Y/%m/%d %H:%M:00')
		tmp_ende  =	datetime.datetime.strptime( x[row_end_date] + ' ' + x[row_end_time], '%Y-%m-%d %H:%M' ).strftime('%Y/%m/%d %H:%M:00')
		tmp_a = x[led_a] if x[led_a] else x[led_b] if x[led_b] else 'Account'
		tmp_b = ':' + x[led_b] if (x[led_b] and x[led_a]) else ''
		tmp_c = ':' + x[led_c] if x[led_c] else ''
		tmp_d = ':' + x[led_d] if x[led_d] else ''
		final_output += 'i ' + tmp_start + ' ' + superacc + ':' + tmp_a + tmp_b + tmp_c + tmp_d + '\n'
		final_output += 'o ' + tmp_ende
		if not y == len(origin) - 1:
			final_output += '\n\n'

	if append_it:
		# appending output to archive_file
		print 'Appending ...'
		f = open(archive_file, 'a')
		f.write('\n\n' + final_output)
		f.close()
		print 'Appended to \'' + archive_file + '\''
		print 'Deleting appended original data ...'
		f = open( single_file[0:single_file.rfind('.')] + '.journal', 'w')
		f.write('')
		f.close()
	else:
		# saving output to file
		print 'Saving ...'
		output_file = single_file[0:single_file.rfind('.')] + '.journal'
		output_file_name = output_file[output_file.rfind('/')+1:]
		f = open(output_file,'w')
		f.write(final_output)
		f.close()
		print 'Saved to \'' + output_file_name + '\''