#!/usr/bin/env python

import subprocess

import itertools
import sys

from south.migration import all_migrations
from south.models import MigrationHistory

def get_migrations():
	from multiprocessing import Process, Queue
	queue = Queue()
	p = Process(target=get_migrations_task, args=(queue,))
	p.start()
	p.join()
	return queue.get()

def get_migrations_task(queue):
	from collections import defaultdict
	southified_apps = list(all_migrations())
	available_migrations = defaultdict(list)
	for migration in itertools.chain.from_iterable(southified_apps):
		available_migrations[migration.app_label()].append(get_migration_location(migration))
	
	applied_migrations = defaultdict(list)
	for history in MigrationHistory.objects.filter(app_name__in=[app.app_label() for app in southified_apps]).order_by('migration'):
		migration = history.get_migration()
		applied_migrations[migration.app_label()].append(get_migration_location(migration))
	queue.put((dict(available_migrations), dict(applied_migrations)))

def get_migration_location(migration):
	return migration.name()

def get_current_branch():
	return subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).strip()

def checkout(branch):
	subprocess.check_call(["git",  "checkout", "%s" % branch])

def migrate(app, migration):
	subprocess.check_call(["./manage.py", "migrate", app, migration])

def migrate_all():
	subprocess.check_call(["./manage.py", "migrate"])

def migrate_branch(target='main', source=None):
	from collections import defaultdict
	if not source:
		source = get_current_branch()
	checkout(target)
	dest_avail, dest_applied = get_migrations()
	checkout(source)
	source_avail, source_applied = get_migrations()
	
	rollbacks = defaultdict(list)
	for app, migrations in source_applied.items():
		if app not in dest_avail:
			rollbacks[app].extend(migrations)
			continue
		for migration in migrations:
			if migration not in dest_avail[app]:
				rollbacks[app].append(migration)
	for app in rollbacks.keys():
		migration = dest_avail.get(app, [None])[-1]
		if not migration:
			continue
		migrate(app, migration)
	checkout(target)
	migrate_all()

if __name__ == '__main__':
	target = sys.argv[1]
	source = None
	if len(sys.argv) > 2:
		source = sys.argv[2]
	migrate_branch(target, source)