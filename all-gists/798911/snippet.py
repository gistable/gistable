def start_replication():
    """
    Begin Postgresql standby
    """
    # Stop pg on the slave machine.
    with settings(host_string=env.db_slave):
        run('service postgresql-9.0 stop')

    # Create the backup on the master machine
    with settings(host_string=env.db_master):
        run('psql -U postgres -c "SELECT pg_start_backup(\'Starting replication\');"')
        with cd('/var/lib/pgsql/9.0'):
            cmd = (
                'RSYNC_RSH="ssh -i /var/lib/pgsql/.ssh/standby.key" '\
                'rsync -av --exclude pg_xlog --exclude postgresql.conf '\
                '--exclude postgresql.pid data/* '\
                'postgres@%s:/var/lib/pgsql/9.0/data'
            )
            run(cmd % env.db_slave)
        run("psql -U postgres -c 'SELECT pg_stop_backup();'")

        # Copy over the WAL files
        with cd('/var/lib/pgsql/9.0'):
            cmd = (
                'RSYNC_RSH="ssh -i /var/lib/pgsql/.ssh/standby.key" '\
                'rsync -av data/pg_xlog '\
                'postgres@%s:/var/lib/pgsql/9.0/data/'
            )
            run(cmd % env.db_slave)

    # Now start postgres on the slave.
    with settings(host_string=env.db_slave):
        run('service postgresql-9.0 start')