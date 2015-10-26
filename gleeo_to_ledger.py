import os, datetime



# format of the Gleeo Time Tracker CSV
row_project      	= 0
row_task         	= 1
row_details      	= 2
row_start_date   	= 3
row_start_time   	= 4
row_end_date     	= 5
row_end_time     	= 6
row_duration     	= 7
row_duration_dec 	= 8
row_project_xtra1	= 9
row_project_xtra2	= 10
row_task_xtra1   	= 11
row_task_xtra2   	= 12
seperator 			= ','
first_line 			= False   #means that the first line is the head only, not important for content



# format of the ledger output
led_a = row_project_xtra1
led_b = row_project
led_c = row_task
led_d = row_details



# check if environment variable LEDGER_FILE_PATH is set
try:
	ledger_path = os.environ['LEDGER_FILE_PATH']
except Exception:
	# nothing set, quit programm
	print 'Environment variable LEDGER_FILE_PATH is not set.'
	exit()
print 'Working directory: ' + ledger_path
print


# get list of all CSV files in this directory
csv_files = []
for file in os.listdir(ledger_path):
	if file.endswith('.csv'):
		csv_files.append(ledger_path + '/' + file)
print 'Input file(s):'
for x in csv_files:
	print '   ' + x[x.rfind('/')+1:]
print



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
		tmp_a = x[led_a] if x[led_a] else 'Account'
		tmp_b = ':' + x[led_b] if x[led_b] else ''
		tmp_c = ':' + x[led_c] if x[led_c] else ''
		tmp_d = ':' + x[led_d] if x[led_d] else ''
		final_output += 'i ' + tmp_start + ' ' + tmp_a + tmp_b + tmp_c + tmp_d + '\n'
		final_output += 'o ' + tmp_ende
		if not y == len(origin) - 1:
			final_output += '\n' + '\n'

	# saving output to file
	print 'Saving ...'
	output_file = single_file[0:single_file.rfind('.')] + '.journal'
	output_file_name = output_file[output_file.rfind('/')+1:]
	f = open(output_file,'w')
	f.write(final_output)
	f.close()
	print 'Saved to \'' + output_file_name + '\''