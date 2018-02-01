"""
This utility addresses the InegrityError that occurs when you try to add a new record to 
(probably a recently ported) postgres database while using Django, here's more . . . 

duplicate key value violates unique constraint "<app>_<table>_pkey"
DETAIL:  Key (id)=(2) already exists.

The problem here is that the Postgres sequence generators are out of sync with your data. 
Here's a good overview: http://www.vlent.nl/weblog/2011/05/06/integrityerror-duplicate-key-value-violates-unique-constraint/

I had a large number of tables and apps, so I wrote the script below to fix them all at once

Keep the alter_the_db flag set to False. Inspect the output, and only flip the flag when you are
certain all looks well.

Obviously, use the script at your own risk. It worked well for me, hope it saves others some time
"""

from django.db import connection
from south.db import db

tables = connection.introspection.table_names()
seen_models = connection.introspection.installed_models(tables)


def increase_last_value(appname):
	for t in tables:
		if appname in t:
			q = "select id from %s order by id desc limit 1;" % (t)
			highest_value = db.execute(q)[0][0]
			alter_statement = "alter sequence %s_id_seq restart with %d;" % (t, highest_value+1)
			# to inspect the "last_value" currently used by postgress, go to the psql prompt
			# or python manage.py dbshell and issue this command: \d <app>_<table>_id_seq 
			# e.g. => \d poll_question_id_seq
			print "tablename=> %s, highest_value_used=> %s, alter_statement=> %s" % (t, highest_value, alter_statement)
			
			# flip this flag when you are ready to make actualy changes to the db
			alter_the_db = False
			if alter_the_db:
				db.execute(alter_statement)

# substitue 'app[x]' with the name of your applications
increase_last_value('app1')
increase_last_value('app2')
increase_last_value('app3')
