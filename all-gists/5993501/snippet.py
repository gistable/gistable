from fabric.api import task
from envassert import file, process, package, port

@task
def apache2():
    assert package.installed("apache2")

    assert service.is_enabled("apache2")
    assert service.is_up("apache2")

    assert port.is_listening(80)

    assert file.is_file("/etc/apache2/httpd.conf")
    assert file.has_line("/etc/apache2/httpd.conf", "ServerName localhost")