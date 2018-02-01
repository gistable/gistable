import sys
import csv
import os

rows = []
input_file = sys.argv[1]

rows.append([ 'Date', 'Payee', 'Category', 'Memo', 'Outflow', 'Inflow' ])

with open(input_file, 'rb') as f:
	reader = csv.reader(f)
	for row in reader:
		data = {
			'date': row[0].split()[0],
			'payee': row[2],
			'category': '',
			'memo': ''
		}

		amount = float(row[7])
		if amount < 0:
			data['inflow'] = amount * -1
			data['outflow'] = ''
		else:
			data['inflow'] = ''
			data['outflow'] = amount

		rows.append([
			data['date'],
			data['payee'],
			data['category'],
			data['memo'],
			data['outflow'],
			data['inflow']
		])


output_file = os.path.basename(input_file) + ' (YNAB format).csv'

with open(output_file, 'wb') as f:
    writer = csv.writer(f)
    writer.writerows(rows)
