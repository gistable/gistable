#!/usr/bin/python3

import math, io, csv, zipfile, pickle

datadir = '/home/user/data/fec'

def fec_file(name, cycle):
	# read the comma-separated header field names
	with open('%s/%s_header_file.csv' % (datadir, name)) as header:
		fieldnames = list(csv.reader(header))[0]

	# read through the data file
	with zipfile.ZipFile('%s/%s%s.zip' % (datadir, name, cycle)) as data:
		stream = data.open(data.namelist()[0])
		stream = io.TextIOWrapper(stream, encoding="latin-1") # not actually sure of encoding
		for row in csv.DictReader(stream, fieldnames=fieldnames, delimiter='|', doublequote=False, quoting=csv.QUOTE_NONE):
			yield row

def load_committees():
	committees = set()
	for row in fec_file('cm', '12'):
		if row['CMTE_TP'] in ("H", "S"):
			committees.add(row['CMTE_ID'])
	return committees

def make_histogram(transaction_types, committees):
	# count up the contributions by exact amount
	counts = { }
	for row in fec_file('indiv', '12'):
		if row['AMNDT_IND'] != 'N': continue # skip amended filings
		if row['ENTITY_TP'] != 'IND': continue # should always be IND
		if transaction_types is not None and row['TRANSACTION_TP'] not in transaction_types: continue
		if row['CMTE_ID'] not in committees: continue # not a House/Senate committee
		# row['TRANSACTION_PGI'] is [PGOCRSE]YYYY (primary, general, etc. plus election year)

		amount = int(row['TRANSACTION_AMT'])
		if amount < 0: continue # not sure why we'd have a negative trasaction on a non-refund record, but whatever

		counts[amount] = counts.get(amount, 0) + 1

	return counts


# The transaction types we want are:
#
# 15: Contribution
# 15E: Earmarked Contribution (the target committee is the filer)
#
# The transaction types we exclude are:
#
# 10: Non-Federal Receipt from Person
# 11: Tribal Contribution
# 15C: Contribution from Candidate (I think that means in a self-funded campaign)
# 19: Electioneering Communication Donation Received (not sure why an individual would do this)
# 20Y, 21Y, 22Y: Refund: Non-Federal / Tribal / Individual Contribution
# 24I: Earmarked Intermediary Out (the intermediary is the filer, maybe OTHER_ID has the target?)
# 24T: Earmarked Intermediary Treasury Out
#
# The committee types we want are:
#
# H/S: House/Senate candidate committee

# Get the IDs of the committees for congressional candidates only.
committees = load_committees()

# Get the counts of contributions to those committees by countribution
# dollar amount.
counts = make_histogram( ('15', '15E'), committees)

#with open('data.pickle', 'wb') as f:
#	pickle.dump(counts, f, pickle.HIGHEST_PROTOCOL)
# ...or...
#counts = pickle.load(open("data.pickle", "rb"))

# Create smart buckets so that the bucket means line up with the most
# common contribution amounts ($250, $500, $1000, $2500). Actually all
# the contributions above the $1000 bucket have an average lower than
# $2500.
buckets = [250, 500, 1000, 2500, 9999999]
bucket_count = 0
bucket_sum = 0
for amount, count in sorted(counts.items()):
	bucket_count += count
	bucket_sum += amount * count
	bucket_average = int(round(float(bucket_sum) / float(bucket_count)))

	if bucket_average >= buckets[0]:
		extra_count = 0
		if bucket_average > buckets[0]:
			# this dollar amount stepped slightly too far, so include
			# in this bucket only some of the contributions at this amount
			prev_count = bucket_count-count
			prev_sum = bucket_sum-(amount*count)
			extra_count = count - (buckets[0]*prev_count - prev_sum) / (amount - buckets[0])
			bucket_count -= extra_count
			bucket_sum -= (amount*extra_count)
			bucket_average = int(round(float(bucket_sum) / float(bucket_count))) # re-take
		print("$%d\t%d\t$%d" % (bucket_average, bucket_count, bucket_sum))
		bucket_count = extra_count
		bucket_sum = extra_count*amount
		buckets.pop(0)
print("$%d\t%d\t$%d" % (bucket_average, bucket_count, bucket_sum))
