import datetime
import logging
import socket
import ssl

YOUR_DOMAIN = 'serverlesscode.com'
WARNING_BUFFER = 14

logger = logging.getLogger()
logger.setLevel(logging.INFO)

ssl_date_fmt = r'%b %d %H:%M:%S %Y %Z'

class AlreadyExpired(Exception):
    pass

def ssl_expires_in(hostname, buffer_days=14):
    """Gets the SSL cert from a given hostname and checks if it expires within buffer_days days"""
    context = ssl.create_default_context()
    conn = context.wrap_socket(
        socket.socket(socket.AF_INET),
        server_hostname=hostname,
    )
    # 3 second timeout because Lambda has runtime limitations
    conn.settimeout(3.0)

    conn.connect((hostname, 443))
    ssl_info = conn.getpeercert()
    expires = datetime.datetime.strptime(ssl_info['notAfter'], ssl_date_fmt)

    # if the cert expires in less than two weeks, we should reissue it
    if expires < (datetime.datetime.utcnow() + datetime.timedelta(days=buffer_days)):
        # expires sooner than the buffer
        return True
    elif expires < datetime.datetime.utcnow():
        # cert has already expired - uhoh!
        raise AlreadyExpired("Cert expired at %s" % ssl_info['notAfter'])
    else:
        # everything is fine
        return False
                      

def lambda_handler(event, context):
    try:
        if not ssl_expires_in(YOUR_DOMAIN, WARNING_BUFFER):
            logger.info("SSL certificate doesn't expire for a while - you're set!")
            return {"success": True, "cert_status": "valid"}
        else:
            logger.warning("SSL certificate expires soon")
            return {"success": True, "cert_status": "expiring soon"}
    except AlreadyExpired as e:
        logger.exception("Certificate is expired, get worried!")
        return {"success": True, "cert_status": "expired"}
    except Exception as e:
        logger.exception("Failed to get certificate info")
        return {"success": False, "cert_status": "unknown"}