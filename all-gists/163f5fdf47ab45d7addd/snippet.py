#!/usr/bin/env python

import argparse
from collections import defaultdict
import os
import sys
import time

from novaclient import client
from novaclient import exceptions

# States which we can migrate
STATES_MIGRATABLE = set(['ACTIVE', 'SHUTOFF'])

# States which indicate a migration is in progress
STATES_MIGRATING = set(['MIGRATING', 'RESIZE'])

# States which should go away if we wait
STATES_EPHEMERAL = set(['REBOOT', 'HARD_REBOOT', 'REBUILD', 'REVERT_RESIZE'])


class MissingClientOpt(Exception):
    pass


class InvalidHost(Exception):
    pass


class InstancesRemaining(Exception):
    def __init__(self, instances):
        self.instances = instances
        super(InstancesRemaining, self).__init__()


def _get_client():
    opts = {
        'username': 'OS_USERNAME',
        'api_key': 'OS_PASSWORD',
        'project_id': 'OS_TENANT_NAME',
        'auth_url': 'OS_AUTH_URL',
    }

    vals = {}
    for opt, env in opts.iteritems():
        vals[opt] = val = os.environ.get(env)
        if val is None:
            raise MissingClientOpt('environment variable %s not set' % env)

    return client.Client('2', **vals)


def _migrate_single(instance, force_cold):
    if not force_cold[instance.id] and instance.status == 'ACTIVE':
        try:
            instance.live_migrate()
        except exceptions.BadRequest as ex:
            # We have no robust way of knowing what this exception is beyond a
            # 400, so we're just going to guess that it failed because of
            # shared storage and try again with block_migration set. This
            # potentially hides a real error, but we don't have any way to tell
            # when we have a real error.
            instance.live_migrate(block_migration=True)
        return False
    elif force_cold[instance.id] or instance.status == 'SHUTOFF':
        instance.migrate()
        return True


def _migrate_multiple(instances, max_migrations, cold_fallback,
                      attempts, force_cold, verify):
    busy = set()
    migrating = set()
    for instance in instances:
        # Instance is already migrating
        if instance.status in STATES_MIGRATING:
            migrating.add(instance)
            continue

        # Instance is busy with something, and we should wait
        if instance.status in STATES_EPHEMERAL:
            busy.add(instance)
            continue

        # If we've tried 3 times to live migrate a guest and the user has
        # specified cold fallback, shut the guest down and try a cold migration
        if (cold_fallback and attempts[instance.id] == 3 and
                instance.status == 'ACTIVE' and not force_cold[instance.id]):
            print ('WARNING: falling back to cold migration of %s' %
                   _pretty_instance(instance))
            force_cold[instance.id] = True
            attempts[instance.id] = 0

        # For safety, we don't attempt to do anything with an instance which is
        # in a state we don't explicitly handle. Note that we can't safely
        # handle PAUSED, SUSPENDED, and RESCUED in any case, as migration
        # requires moving the instance out of this state, and we don't have the
        # context to do that safely.
        elif (instance.status not in STATES_MIGRATABLE or
                attempts[instance.id] == 3):
            continue

        if len(migrating) < max_migrations:
            migrating.add(instance)
            attempts[instance.id] += 1
            try:
                resize = _migrate_single(instance, force_cold)
            except Exception as ex:
                # Almost everything is a 'BadRequest'. This covers such a wide
                # variety of errors, some of them ephemeral, that we just retry
                # here regardless
                continue

            if resize:
                verify.add(instance.id)

    return migrating, busy


def _pretty_instance(instance):
    return '%s(%s)' % (instance.name, instance.id)


def _migrate_host(nova, host, max_migrations, poll_interval, cold_fallback):
    host_filter = {'host': host}

    # The number of times we've attempted to migrate an instance
    attempts = defaultdict(int)

    verify = set()
    force_cold = defaultdict(bool)

    # Display 
    instances = nova.servers.list(search_opts=host_filter)
    if len(instances) > 0:
        print 'Found instances on host:'
        for instance in instances:
            print '  %s' % _pretty_instance(instance)

    # Repeatedly attempt to evacuate the host until completion
    while True:
        # Attempt to migrate instances on the host
        migrating, busy = _migrate_multiple(instances,
            max_migrations, cold_fallback, attempts, force_cold, verify)

        remaining_instance_ids = set([instance.id for instance in instances])

        # If we successfully cold migrated an instance, it will be left in
        # VERIFY_RESIZE on a new host. Here we auto-confirm it, as it was a
        # simple copy. This may involve an expensive data-scrubbing operation,
        # so we start it as soon as possible.
        verified = set()
        for instance_id in verify:
            # Instances in VERIFY_RESIZE have moved to a different host, so
            # they won't be in instances, which only contains instances from
            # the target host.
            if instance_id in remaining_instance_ids:
                continue

            instance = nova.servers.get(instance_id)
            if instance.status == 'VERIFY_RESIZE':
                instance.confirm_resize()
            elif instance.status in STATES_MIGRATABLE:
                verified.add(instance_id)
            elif instance.status == 'RESIZE':
                # Haven't finished on the target host
                pass
            else:
                # Instance is in unexpected state on target host. Warn, and
                # don't wait any longer.
                print ('WARNING: Instance %s has migrated to host %s. '
                       'Expected status VERIFY_RESIZE, but status is %s'
                       % (_pretty_instance(instance),
                          getattr(instance, 'OS-EXT-SRV-ATTR:host'),
                          instance.status))
                verified.add(instance_id)
        verify.difference_update(verified)

        # Finish when we didn't do anything, and we're not waiting on anything
        if len(migrating) == 0 and len(busy) == 0 and len(verify) == 0:
            break

        # Report status on every round
        if len(migrating) > 0:
            print 'Migrating:'
            for instance in migrating:
                print '  %s' % _pretty_instance(instance)
        if len(busy) > 0:
            print 'Busy:'
            for instance in busy:
                print '  %s: %s' % (_pretty_instance(instance),
                                    instance.status)

        time.sleep(poll_interval)
        instances = nova.servers.list(search_opts=host_filter)

    if len(instances) > 0:
        raise InstancesRemaining(instances)


def nova_compute_maintenance(nova, host, max_migrations=2, poll_interval=5,
                             cold_fallback=False):
    # Disable the service in the scheduler to prevent new instances being sent
    # there
    try:
        nova.services.disable(host, 'nova-compute')
    except exceptions.NotFound:
        raise InvalidHost

    _migrate_host(nova, host, max_migrations, poll_interval, cold_fallback)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Disable a nova compute service and move all its '
                    'instances to other hosts')

    parser.add_argument('host',
        help='The nova compute host to evacuate for maintenance')
    parser.add_argument('--max-migrations', '-m', type=int,
        help='The maximum number of simultaneous migrations to perform')
    parser.add_argument('--poll-interval', '-p', type=int,
        help='The frequency at which we poll the status of the compute '
             'service')
    parser.add_argument('--cold-fallback', '-c', action='store_true',
        help='Fall back to cold migration if live migration fails')

    opts = vars(parser.parse_args())
    host = opts.pop('host')

    # Filter out unset options so they're defaulted by nova_compute_maintenance
    opts = {k:v for k, v in opts.iteritems() if v is not None}

    try:
        nova = _get_client()
    except MissingClientOpt as ex:
        print ex.message
        sys.exit(1)

    try:
        nova_compute_maintenance(nova, host, **opts)

        print 'Success: No instances left on host'
        sys.exit(0)
    except InvalidHost:
        print "%s is not a nova compute host" % host
    except InstancesRemaining as ex:
        print 'Failed to migrate the following instances:'
        for instance in ex.instances:
            print '  %s: %s %s' % (_pretty_instance(instance),
                                   instance.status,
                                   getattr(instance, 'fault', ''))
        print 'See logs for details'

    sys.exit(1)
