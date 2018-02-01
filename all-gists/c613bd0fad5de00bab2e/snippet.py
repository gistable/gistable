# -*- coding: utf-8 -*-

"""
Verify the given mail id is valid or not without sending mail. Verifying the email id directly from mail exchange server.
"""

import argparse
import smtplib
import dns.resolver
import re
import logging

__author__ = 'arul'


class MXEmailVerifier():
    FROM_ADDRESSES = ["info@gmail.com", "contact@gmail.com", "contact@yahoo.com", "info@yahoo.com",
                      "support@google.com"]

    def __init__(self):
        self.init_logging()

    def init_logging(self):
        """
        Initialize the logs
        """
        global logger
        logger = logging.getLogger('EmailVerifier')
        logger.setLevel(logging.DEBUG)
        # create console handler with a higher log level
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        # create formatter and add it to the handlers
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console.setFormatter(formatter)
        # add the handlers to logger
        logger.addHandler(console)

    def __parse__(self, _email_):
        """
        Parse and find the email id from the string using regex.
        :param _email_:
        :return:
        """
        p_email = re.findall(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}\b", _email_, re.I)
        if p_email and len(p_email) > 0:
            return p_email[0]
        else:
            raise ValueError("Not a valid email id %s." % _email_)
        return None

    def __find_mx_host__(self, _email_):
        """
        It returns the mail exchange servers sorted by preference for the given mail id.
        :param _email_:
        :return:
        """
        _host_ = _email_.split("@")[1]
        answers = dns.resolver.query(_host_, 'MX')
        # Sorting based on the preference
        answers = sorted(answers, key=lambda answer: answer.preference)
        hosts = list()
        for rdata in answers:
            hosts.append(rdata.exchange.to_text())
        if hosts and len(hosts) > 0:
            return hosts
        else:
            raise ValueError("MX server for host '%s' not able to find." % _host_)
        return None

    def verify(self, _email_):
        """
        Verify the given email id is present in their mail exchange server.
        :param _email_:
        :return:
        """
        # parsing given input as email id
        parsed_email_id = self.__parse__(_email_)
        logger.info("Parsed Email id : %s" % parsed_email_id)

        # Finding mail exchange server of the parsed mail id
        _mx_hosts_ = self.__find_mx_host__(parsed_email_id)

        for _mx_host_ in _mx_hosts_:
            _mx_host_ = _mx_host_[:-1] if _mx_host_[-1] == "." else _mx_host_
            logger.debug("MX host is %s " % _mx_host_)

            # Login into the mail exchange server
            try:
                smtp = smtplib.SMTP()
                smtp.connect(_mx_host_)
            except smtplib.SMTPConnectError, e:
                logger.error(e)
                continue

            try:
                smtp.ehlo_or_helo_if_needed()
            except Exception, e:
                logger.error(e)
                continue

            # First Try to verify with VRFY
            # 250 is success code. 400 or greater is error.
            v_code, v_message = smtp.verify(_email_)
            logger.debug("VERIFY %s, %r" % (v_code, v_message))
            if v_code and v_code != 250:
                for _from_ in self.FROM_ADDRESSES:
                    f_code, f_message = smtp.mail(_from_)
                    logger.debug("FROM %s, %r" % (f_code, f_message))
                    # Then use RCPT to verify
                    if f_code and f_code == 250:
                        r_code, r_message = smtp.rcpt(_email_)
                        logger.debug("RCPT %s, %r" % (r_code, r_message))
                        if r_code and r_code == 250:
                            return True, r_message
                        if r_code and r_code == 550:
                            return False, r_message
                    else:
                        continue
            else:
                return True, v_message
            smtp.quit()
            break
        return None, None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Verify the given mail id is valid or not.")
    parser.add_argument("-e", "--email",  help='Enter the email id', required=True)
    args = parser.parse_args()

    verifier = MXEmailVerifier()
    try:
        verified, message = verifier.verify(args.email)
        logger.info("%s, %s, %r" % (args.email, verified, message))
    except Exception, e:
        logger.error(e)