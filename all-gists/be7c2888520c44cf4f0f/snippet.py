# get existing queries results
users = get_query_result(132) # this one has {id, name}
events_by_users = get_query_result(131) # this one has {user_id, events count}

# actual merging. can be replaced with helper function and/or some Pandas code
events_dict = {}
for row in events_by_users['rows']:
  events_dict[row['user_id']] = row['count']

for row in users['rows']:
  row['events_count'] = events_dict.get(row['id'], 0)

# set the result to show
result = users
add_result_column(result, 'events_count', '', 'integer')