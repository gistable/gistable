def deploy():
    """ Checks out code, prepares venv, runs management commands,
    updates supervisor and nginx configuration. """

    now = datetime.datetime.today()
    now_string = now.strftime("%Y%m%d-%H%M%S")
    project_dir = "/home/hc/webapps/hc-%s" % now_string
    venv_dir = os.path.join(project_dir, "venv")

    svn_url = "https://github.com/healthchecks/healthchecks/trunk"
    run("svn export %s %s" % (svn_url, project_dir))

    with cd(project_dir):
        run("virtualenv --python=python3 --system-site-packages venv")
        # local_settings.py is where things like access keys go
        put("local_settings.py", ".")
        put("newrelic.ini", ".")

        with virtualenv(venv_dir):
            run("pip install -U gunicorn raven newrelic")
            run("pip install -r requirements.txt")
            run("python manage.py collectstatic --noinput")
            run("python manage.py compress")

            with settings(user="hc"):
                run("python manage.py migrate")
                run("python manage.py ensuretriggers")
                run("python manage.py clearsessions")

    switch(project_dir)

def switch(project_dir):
    # Supervisor
    upload_template("supervisor/hc.conf.tmpl",
                    "/etc/supervisor/conf.d/hc.conf",
                    context=locals(),
                    backup=False,
                    use_sudo=True)

    upload_template("supervisor/hc_sendalerts.conf.tmpl",
                    "/etc/supervisor/conf.d/hc_sendalerts.conf",
                    context=locals(),
                    backup=False,
                    use_sudo=True)

    # Nginx
    upload_template("nginx/hc.conf.tmpl",
                    "/etc/nginx/sites-enabled/hc.conf",
                    context=locals(),
                    backup=False,
                    use_sudo=True)

    sudo("supervisorctl reload")
    sudo("/etc/init.d/nginx reload")