def switch(tag, project_dir):
    # Supervisor
    supervisor_conf_path = "/etc/supervisor/conf.d/hc_%s.conf" % tag
    upload_template("supervisor/hc.conf.tmpl",
                    supervisor_conf_path,
                    context=locals(),
                    backup=False,
                    use_sudo=True)

    upload_template("supervisor/hc_sendalerts.conf.tmpl",
                    "/etc/supervisor/conf.d/hc_sendalerts.conf",
                    context=locals(),
                    backup=False,
                    use_sudo=True)

    # Starts up gunicorn from the new virtualenv
    sudo("supervisorctl update")

    # Give it some time to start up
    time.sleep(5)

    # Let's check the new server is nominally working
    # gunicorn listens on UNIX socket so this is a bit contrived:
    l = ("GET /about/ HTTP/1.0\\r\\n"
         "Host: healthchecks.io\\r\\n"
         "\\r\\n")

    cmd = 'echo -e "%s" | nc -U /tmp/hc-%s.sock' % (l, tag)
    # Look for known string in response. If it's not found, something
    # is wrong with the new deployment and we abort
    assert "Monkey See Monkey Do" in run(cmd, quiet=True)

    # nginx
    upload_template("nginx/hc.conf.tmpl",
                    "/etc/nginx/sites-enabled/hc.conf",
                    context=locals(),
                    backup=False,
                    use_sudo=True)

    sudo("/etc/init.d/nginx reload")

    # should be live now - remove supervisor conf for previous versions
    s = sudo("for i in /etc/supervisor/conf.d/*.conf; do echo $i; done")
    for line in s.split("\n"):
        line = line.strip()
        if line == supervisor_conf_path:
            continue
        if line.startswith("/etc/supervisor/conf.d/hc_2"):
            sudo("rm %s" % line)

    # This stops gunicorn processes
    sudo("supervisorctl update")