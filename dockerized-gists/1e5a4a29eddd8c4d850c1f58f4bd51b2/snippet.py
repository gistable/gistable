#
# Simple query object for combining multiple redash queries
#
# Example usage:
# Find all users who have logged in in the last 8 weeks who have sent an email by analysing the logstash logs
# Then group the results by the week they signed up on and their emailed yes/no status
#
# import requery
# userQuery = 'SELECT * FROM user WHERE lastSeen > DATE_SUB(NOW(), INTERVAL 8 WEEK)'
# emailQuery = '{ "index" : "logstash-*", "query": { "query_string": { "query": "action:sendEmail" } }, "size" : 1000 }
# result = requery.Query(execute_query) \
# .execute('MySQL-Live', seedUsersQuery) \
# .join('ElasticSearch-Live', emailQuery, 'id=userId') \
# .add_column('emailed', lambda row: 'yes' if row['action'] != '' else 'no') \
# .group_by(['weekJoined', 'emailed'], 'count') \
# .get()
#
#

class Query(object):

	def __init__(self, execute_query):
		# Store the redash 'execute_query' method, so we can use it later
		self.execute_query = execute_query
		self.result = { 'rows': [], 'columns': [], 'log': [] }

	def execute(self, data_source, query):
		self.result = self.execute_query(data_source, query)
		if 'log' not in self.result:
			self.result['log'] = []
		return self

	def join(self, data_source, query, on):

		null_row = {}
		lookup = {}
		(key_self, key_join) = on.split('=')

		result_join = self.execute_query(data_source, query)

		for column in result_join['columns']:
			null_row[column['name']] = ''

		for row in result_join['rows']:
			lookup[str(row[key_join])] = row

		for row in self.result['rows']:
			key = str(row[key_self])
			if key in lookup:
				row.update(lookup[key])
			else:
				row.update(null_row)

		self.result['columns'].extend(result_join['columns'])
		if 'log' in result_join:
			self.result['log'].extend(result_join['log'])
		return self

	def group_by(self, keys, column_name):

		rows = []
		columns = []
		result = { 'rows': rows, 'columns': columns }
		for k in keys:
			columns.append(self.get_column(k))

		columns.append({ 'name': column_name, 'friendly_name': column_name, 'type': 'integer' })

		grouping = {}
		for row in self.result['rows']:
			group_key = ''
			for k in keys:
				group_key += row[k] + ':'
			try:
				grouping[group_key] += 1
			except:
				grouping[group_key] = 1

		for key, value in grouping.iteritems():
			row = {}
			group_values = key.split(':')
			for i in xrange(len(keys)):
				row[keys[i]] = group_values[i]
			row[column_name] = value
			rows.append(row)

		self.result = result
		return self

	def add_column(self, name, func, type='string'):
		for row in self.result['rows']:
			row[name] = func(row)
		if self.get_column(name) is None:
			self.result['columns'].append({ 'name': name, 'friendly_name': name, 'type': type })
		return self

	def get(self):
		return self.result

	def get_column(self, name):
		for c in self.result['columns']:
			if c['name'] == name:
				return c

		return None

	def column_to_string(self, result, name):

		for row in result['rows']:
			row[name] = str(row[name])

		self.get_column(result, name)['type'] = 'string'