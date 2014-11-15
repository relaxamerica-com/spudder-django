###
# Script for parsing zip codes data sheet (CSV file) and storing only zips which first 4 digits are unique.
# For example: given two zips: 01022 and 01023 only first one will be stored.
# Some zip codes can have only 4 digits - in that case 0 needs to be added as prefix
###

import csv

input_file = open('original.csv', 'rb')
reader = csv.reader(input_file, delimiter=',')

zip_codes = []
reduced_codes = []
count = 0

for row in reader:
	count += 1
	if count == 1:
		continue

	zip_code = row[0]

	if not zip_code:
		print 'Empty zip code at line %s' % count
		continue

	if len(zip_code) == 4:
		zip_code = '0' + zip_code
	
	code = zip_code[:4]
	if code not in reduced_codes:
		reduced_codes.append(code)
		zip_codes.append(zip_code)

input_file.close()

# Writing reduced set of data
output_file = open('filtered_zips.csv', 'wb')
count = 0
for zip_code in zip_codes:
	count += 1
	output_file.write('%s\n' % zip_code)

print 'Wrote %s rows...' % count

output_file.close()