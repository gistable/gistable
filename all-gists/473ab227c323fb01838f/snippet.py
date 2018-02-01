#!/usr/bin/env python

from __future__ import print_function

import json
import logging

from urllib2 import Request, urlopen, URLError, HTTPError
from base64 import b64decode

log = logging.getLogger(__name__)


class SlackOnCall(object):
    # The Slack API token to use for authentication to the Slack WebAPI
    slack_token = None
    
    # The Pager Duty API token to use for authentication into the PagerDuty API
    pager_duty_token = None
    
    # The domain prefix for the PagerDuty installation (acme.pagerduty.com will be "acme")
    pager_duty_domain_prefix = None
    
    # The Slack @user-group to update (Default: oncall)
    slack_user_group_handle = 'oncall'

    # The maximum escalation level to add to the group
    # (eg. if escalation level = 2, then levels 1 and 2 will be a part of the group
    # but not any levels 3 and above.
    escalation_level = 2

    def __init__(self, slack_token, pager_duty_token, pager_duty_domain_prefix,
                 slack_user_group_handle=slack_user_group_handle, log_level='INFO',
                 escalation_level=escalation_level):
       
        self.slack_token = slack_token
        self.pager_duty_token = pager_duty_token
        self.pager_duty_domain_prefix = pager_duty_domain_prefix
        self.slack_user_group_handle = slack_user_group_handle
        self.escalation_level = escalation_level

        self._slack_user_group = None
        self._on_call_email_addresses = None
        self._all_slack_users = None

        log.setLevel(log_level)

    def run(self):
        """
        Gets user group information and on-call information then updates the
        on-call user group in slack to be the on-call users for escalation
        levels 1 and 2.
        """
        slack_users = self.slack_users_by_email(self.on_call_email_addresses)
        if not slack_users:
            log.warning('No Slack users found for email addresses: %s', ','.join(self.on_call_email_addresses))
            return

        slack_user_ids = [u['id'] for u in slack_users]

        if set(slack_user_ids) == set(self.slack_user_group['users']):
            log.info('User group %s already set to %s', self.slack_user_group_handle, slack_user_ids)
            return

        self.update_on_call(slack_users)
        log.info('Job Complete')

    @staticmethod
    def _make_request(url, body=None, headers={}):
        req = Request(url, body, headers)
        log.info('Making request to %s', url)

        try:
            response = urlopen(req)
            body = response.read()
            try:
                return json.loads(body)
            except ValueError:
                return body

        except HTTPError as e:
            log.error("Request failed: %d %s", e.code, e.reason)
        except URLError as e:
            log.error("Server connection failed: %s", e.reason)

    @property
    def slack_user_group(self):
        """
        :return: the Slack user group matching the slack_user_group_handle
        specified in the configuration
        """
        if self._slack_user_group is not None:
            return self._slack_user_group

        url = 'https://slack.com/api/usergroups.list?token={}&include_users=1'.format(self.slack_token)
        groups = self._make_request(url)['usergroups']
        for group in groups:
            if group['handle'] == self.slack_user_group_handle:
                self._slack_user_group = group
                return group

        raise ValueError('No user groups found that match {}'.format(self.slack_user_group_handle))

    @property
    def on_call_email_addresses(self):
        """
        Hits the PagerDuty API and gets level 1 and level 2 escalation
        on-call users and returns their email addresses
        :return: All on-call email addresses within the escalation bounds
        """
        if self._on_call_email_addresses is not None:
            return self._on_call_email_addresses

        url = 'https://{}.pagerduty.com/api/v1/users/on_call'.format(self.pager_duty_domain_prefix)
        on_call = self._make_request(url, headers={'Authorization': 'Token token=' + self.pager_duty_token})
        users = set()  # users can be in multiple schedule, this will de-dupe

        for user in on_call['users']:
            for schedule in user['on_call']:
                if schedule['level'] <= self.escalation_level:
                    users.add(user['email'])

        log.info('Found %d users on-call', len(users))
        self._on_call_email_addresses = users
        return users

    @property
    def all_slack_users(self):
        if self._all_slack_users is not None:
            return self._all_slack_users

        url = 'https://slack.com/api/users.list?token={}'.format(self.slack_token)
        users = self._make_request(url)['members']
        log.info('Found %d total Slack users', len(users))
        self._all_slack_users = users
        return users

    def slack_users_by_email(self, emails):
        """
        Finds all slack users by their email address
        :param emails: List of email address to find users
        :return: List of Slack user objects found in :emails:
        """
        users = []
        for user in self.all_slack_users:
            if user['profile'].get('email') in emails:
                users.append(user)

        return users

    def update_on_call(self, slack_users):
        """
        Updates the specified user-group
        :param slack_users: Slack users to modify the group with
        """
        user_ids = [u['id'] for u in slack_users]
        url = 'https://slack.com/api/usergroups.users.update?token={0}&usergroup={1}&users={2}'.format(
            self.slack_token,
            self.slack_user_group['id'],
            ','.join(user_ids)
        )

        log.info('Updating user group %s from %s to %s',
                 self.slack_user_group_handle, self.slack_user_group['users'], user_ids)
        self._make_request(url)


def lambda_handler(*_):
    """
    Main entry point for AWS Lambda.

    Variables can not be passed in to AWS Lambda, the configuration
    parameters below are encrypted using AWS IAM Keys.
    """

    # Boto is always available in AWS lambda, but may not be available in
    # standalone mode
    import boto3

    # To generate the encrypted values, go to AWS IAM Keys and Generate a key
    # Then grant decryption using the key to the IAM Role used for your lambda
    # function.
    #
    # Use the command `aws kms encrypt --key-id alias/<key-alias> --plaintext <value-to-encrypt>
    # Put the encrypted value in the configuration dictionary below
    encrypted_config = {
        'slack_token':              '<ENCRYPTED VALUE>',
        'pager_duty_token':         '<ENCRYPTED VALUE>'
        'pager_duty_domain_prefix': '<ENCRYPTED VALUE>'
    }

    kms = boto3.client('kms')
    config = {x: kms.decrypt(CiphertextBlob=b64decode(y))['Plaintext'] for x, y in encrypted_config.iteritems()}
    return SlackOnCall(**config).run()


def main():
    """
    Runs the Slack PagerDuty OnCall group updater as a standalone script
    """
    from argparse import ArgumentParser

    parser = ArgumentParser(usage=main.__doc__)
    parser.add_argument('-st', '--slack-token', required=True, dest='slack_token',
                        help='Slack token to use for auth into the Slack WebAPI')
    parser.add_argument('-su', '--slack-user-group', dest='slack_user_group_handle', default='oncall',
                        help='Slack user group to add on-call users to. (Default: oncall)')
    parser.add_argument('-pt', '--pager-duty-token', required=True, dest='pager_duty_token',
                        help='PagerDuty token to use for auth into the PagerDuty API')
    parser.add_argument('-pd', '--pager-duty-domain-prefix', required=True, dest='pager_duty_domain_prefix',
                        help='Your domain prefix for PagerDuty')
    parser.add_argument('-el', '--max-escalation-level', dest='escalation_level', default=2, type=int,
                        help='Max escalation level to add on-call users for group. (Default: 2)')

    logging.basicConfig()
    args = vars(parser.parse_args())
    SlackOnCall(**args).run()


if __name__ == '__main__':
    main()
