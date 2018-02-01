def incremental_map_reduce(
		map_f, 
		reduce_f, 
		db, 
		source_table_name, 
		target_table_name, 
		source_queued_date_field_name, 
		counter_table_name = "IncrementalMRCounters", 
		counter_key = None,
		max_datetime = None, 
		reset = False,
		force = False):

	""" This method performs an incremental map-reduce on any new data in 'source_table_name' 
	into 'target_table_name'.  It can be run in a cron job, for instance, and on each execution will
	process only the new, unprocessed records.  

	The set of data to be processed incrementally is determined non-invasively (meaning the source table is not 
	written to) by using the queued_date field 'source_queued_date_field_name'. When a record is ready to be processed, 
	simply set its queued_date (which should be indexed for efficiency). When incremental_map_reduce() is run, any documents 
	with queued_dates between the counter in 'counter_key' and 'max_datetime' will be map/reduced.

	If reset is True, it will clear 'target_table_name' and do a map reduce across all records older 
	than max_datetime.

	If unspecified/None, counter_key defaults to counter_table_name:LastMaxDatetime.
	"""

	now = datetime.datetime.now()
	if max_datetime is None:
		max_datetime = now

	if reset:
		logging.debug("Resetting, dropping table " + target_table_name)
		db.drop_collection(target_table_name)

	time_limits = { "$lt" :  max_datetime } 
	if counter_key is None:
		counter_key = target_table_name + ":LastMaxDatetime"
	
	# If we've run before, filter out anything that we've processed already.
	last_max_datetime = None

	last_max_datetime_record = db[counter_table_name].find_and_modify(
		{'_id': counter_key},
		{'$set': { 'inprogress': True}, '$push': { 'm': now } },
		upsert = True		
	)

	if force or last_max_datetime_record is None or not last_max_datetime_record.has_key('inprogress'):
		# first time ever run, or forced to go ahead anyway
		pass
	else:
		if last_max_datetime_record['inprogress']:
			if last_max_datetime_record['m'][0] < now - datetime.timedelta(hours = 2):
				# lock timed out, so go ahead...
				logging.error(target_table_name + " lock is old.  Ignoring it, but something was broken that caused it to not be unlocked...")
			else:
				logging.warning(target_table_name + " mapreduce already in progress, skipping...")
				raise RuntimeError(target_table_name + " locked since %s.  Skipping..." % last_max_datetime_record['m'][0])

	if not reset:
		if last_max_datetime_record is not None:
			try:
				last_max_datetime = last_max_datetime_record['value']
				time_limits['$gt'] = last_max_datetime
				logging.debug('~FR limit last_max_datetime = %s' % (last_max_datetime,))
			except KeyError:
				# This happened on staging.  i guess it crashed somehow
				# between the find_and_modify and the final update?
				logging.error("~FR no value on message!")

	query = { source_queued_date_field_name: time_limits }
	ret = db[source_table_name].map_reduce(
		map_f, 
		reduce_f,
		out = { 'reduce' : target_table_name },
		query = query,
		full_response = True
	)

	num_processed = ret['counts']['input']

	# Update our counter so we remember for the next pass.
	already_processed_through = db[counter_table_name].update(
		{'_id': counter_key},
		{'$set': { 'inprogress': False, 'value': max_datetime }, '$unset': {'m': 1}},
		upsert = False,
		multi = False,
		safe = True)

	logging.debug("Processed %d completed surveys from %s through %s.\nmap_reduce details: %s" % (num_processed, last_max_datetime, max_datetime, ret))

	return ret