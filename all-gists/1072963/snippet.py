############################## django-auth-ldap ##############################
if DEBUG:
    import logging, logging.handlers
    logfile = "/tmp/django-ldap-debug.log"
    my_logger = logging.getLogger('django_auth_ldap')
    my_logger.setLevel(logging.DEBUG)

    handler = logging.handlers.RotatingFileHandler(
       logfile, maxBytes=1024 * 500, backupCount=5)

    my_logger.addHandler(handler)
############################ end django-auth-ldap ############################
